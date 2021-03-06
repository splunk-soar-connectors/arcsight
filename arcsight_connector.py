# File: arcsight_connector.py
#
# Copyright (c) 2017-2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#
#
# Phantom imports
import phantom.app as phantom

from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# THIS Connector imports
from arcsight_consts import *

from datetime import datetime
import requests
import re
import socket
import struct
from bs4 import BeautifulSoup
import json

_container_common = {}
_artifact_common = {}


def _validate_range(input_range, action_result):

    try:
        mini, maxi = (int(x) for x in input_range.split('-'))
    except:
        return action_result.set_status(phantom.APP_ERROR,
                                        "Unable to parse the range. Please specify the range as min_offset-max_offset")

    if (mini < 0) or (maxi < 0):
        return action_result.set_status(phantom.APP_ERROR, "Invalid min or max offset value specified in range", )

    if mini > maxi:
        return action_result.set_status(phantom.APP_ERROR,
                                        "Invalid range value, min_offset greater than max_offset")

    return phantom.APP_SUCCESS


def _to_mac(input_mac):

    if not input_mac:
        return ''

    input_mac = int(input_mac)

    if input_mac == ARCSIGHT_64VAL_NOT_FILLED:
        return ''

    hex_str = "%x" % input_mac

    hex_str = hex_str[:12]

    return ':'.join(s.encode('hex') for s in hex_str.decode('hex'))


def _to_ip(input_ip):

    if not input_ip:
        return ''

    input_ip = int(input_ip)

    if input_ip == ARCSIGHT_64VAL_NOT_FILLED:
        return ''

    return socket.inet_ntoa(struct.pack('!L', input_ip))


def _to_port(port):

    if not port:
        return ''

    port = int(port)

    if port == ARCSIGHT_32VAL_NOT_FILLED:
        return ''

    return port


def _get_str_from_epoch(epoch_milli):

    if epoch_milli is None:
        return ''

    if not str(epoch_milli).strip():
        return ''

    # 2015-07-21T00:27:59Z
    return datetime.fromtimestamp(int(epoch_milli) / 1000.0).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def _parse_error(response):

    pres = None
    description = None
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        pres = soup.findAll('pre')
        error_text = '\r\n'.join([str(x) for x in pres])
    except:
        error_text = "Cannot parse error details"

    # Try to parse description
    try:
        for paragraph in soup.find_all('p'):
            description_tag = paragraph.find_all('b')
            if description_tag and description_tag[0].text == 'description':
                description = paragraph.find_all('u')[0].text
                break
    except:
        pass

    # Try to parse some more
    try:
        if pres:
            error_text = str(pres[0]).split('\n')[0].replace('<pre>', '')
    except:
        pass

    if error_text and description:
        message = f'API failed. Status Code: {response.status_code}. Error Description: {description} Error Details: {error_text}'
    elif error_text:
        message = f'API failed. Status Code: {response.status_code}. Error Details: {error_text}'
    elif description:
        message = f'API failed. Status Code: {response.status_code}. Error Description: {description}'
    else:
        try:
            # Remove the script, style, footer and navigation part from the HTML message
            for element in soup(["script", "style", "footer", "nav"]):
                element.extract()
            error_text = soup.text
            split_lines = error_text.split('\n')
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = '\n'.join(split_lines)
        except:
            error_text = "Cannot parse error details"

        if not error_text:
            error_text = "Empty response and no information received"
        message = f"API failed. Status Code: {response.status_code}. Error Details: {error_text}"
        message = message.replace('{', '{{').replace('}', '}}')

    return message


class ArcsightConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(ArcsightConnector, self).__init__()

        self._base_url = None
        self._auth_token = None

    def initialize(self):

        # Base URL
        config = self.get_config()

        self._base_url = config[ARCSIGHT_JSON_BASE_URL].rstrip('/')

        return phantom.APP_SUCCESS

    def _get_error_message_from_exception(self, e):
        """
        Get appropriate error message from the exception.

        :param e: Exception object
        :return: error message
        """
        error_code = ERR_CODE_MSG
        error_msg = ERR_MSG_UNAVAILABLE

        try:
            if hasattr(e, "args"):
                if len(e.args) > 1:
                    error_code = e.args[0]
                    error_msg = e.args[1]
                elif len(e.args) == 1:
                    error_code = ERR_CODE_MSG
                    error_msg = e.args[0]
        except:
            pass

        try:
            if error_code in ERR_CODE_MSG:
                error_text = "Error Message: {}".format(error_msg)
            else:
                error_text = "Error Code: {}. Error Message: {}".format(error_code, error_msg)
        except:
            self.debug_print(PARSE_ERR_MSG)
            error_text = PARSE_ERR_MSG

        return error_text

    def _validate_version(self, action_result):

        # get the version from the device
        ret_val, version = self._get_version(action_result)

        if phantom.is_fail(ret_val):
            action_result.append_to_message("Product version validation failed")
            return action_result.get_status()

        # get the version of the device
        device_version = version.get('cas.getESMVersionResponse', {}).get('cas.return')

        if not device_version:
            return action_result.set_status(phantom.APP_ERROR, "Unable to get version from the device")

        self.save_progress("Got device version: {0}".format(device_version))

        # get the configured version regex
        version_regex = self.get_product_version_regex()
        if not version_regex:
            # assume that it matches
            return phantom.APP_SUCCESS

        match = re.match(version_regex, device_version)

        if not match:
            message = "Version validation failed for App supported version '{0}'".format(version_regex)
            return action_result.set_status(phantom.APP_ERROR, message)

        self.save_progress("Version validation done")

        return phantom.APP_SUCCESS

    def _login(self, action_result):

        if self._auth_token is not None:
            return phantom.APP_SUCCESS

        config = self.get_config()

        self.save_progress('Logging into device/server')

        request_data = {
            "log.login": {"log.login": config[ARCSIGHT_JSON_USERNAME], "log.password": config[ARCSIGHT_JSON_PASSWORD]}}

        ret_val, resp = self._make_rest_call(ACRSIGHT_LOGIN_ENDPOINT, action_result, json=request_data, method="post")

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # parse the response and set the auth key
        try:
            self._auth_token = resp['log.loginResponse']['log.return']
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            self.debug_print(f"Handled exception while parsing auth token. {error_msg}")
            return action_result.set_status(phantom.APP_ERROR, "Error parsing login response")

        # validate the version
        ret_val = self._validate_version(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        return phantom.APP_SUCCESS

    def _get_version(self, action_result):

        endpoint = "{0}/getESMVersion".format(ARCSIGHT_CASESERVICE_ENDPOINT)

        params = {'authToken': self._auth_token}

        ret_val, resp = self._make_rest_call(endpoint, action_result, params)

        if phantom.is_fail(ret_val):
            return phantom.APP_ERROR, resp

        self.debug_print(resp)

        return phantom.APP_SUCCESS, resp

    def _make_rest_call(self, endpoint, action_result, params=None, data=None, json=None, headers=None, method="get"):

        config = self.get_config()

        request_func = getattr(requests, method)

        if not request_func:
            action_result.set_status(phantom.APP_ERROR, ARCSIGHT_ERR_API_UNSUPPORTED_METHOD, method=method)

        url = f'{self._base_url}{endpoint}'

        self.debug_print("Making REST Call {0} on {1}".format(method.upper(), url))

        _headers = {'Accept': 'application/json'}

        if headers:
            _headers.update(headers)

        try:
            response = request_func(url, params=params, data=data, json=json, headers=_headers,
                                    verify=config[phantom.APP_JSON_VERIFY])

        except requests.exceptions.ConnectionError as e:
            self.debug_print(self._get_error_message_from_exception(e))
            error_message = f"Error connecting to server. Connection refused from server for {url}"
            return action_result.set_status(phantom.APP_ERROR, error_message), None
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            self.debug_print(f"REST call Failed: {error_msg}")
            return action_result.set_status(phantom.APP_ERROR, f"{ARCSIGHT_ERR_SERVER_CONNECTION}. {error_msg}"), None

        if (response.status_code != requests.codes.ok) or ('html' in response.headers.get('Content-Type', '')):  # pylint: disable=E1101
            message = _parse_error(response)
            self.debug_print(message)
            return action_result.set_status(phantom.APP_ERROR, message), None

        reply = response.text

        action_result.add_debug_data(reply)

        try:
            response_dict = response.json()
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            self.debug_print(f"Unable to parse response dict. {error_msg}")
            self.save_progress(ARCSIGHT_ERR_UNABLE_TO_PARSE_REPLY)
            return action_result.set_status(phantom.APP_ERROR, ARCSIGHT_ERR_UNABLE_TO_PARSE_REPLY), None

        return phantom.APP_SUCCESS, response_dict

    def _get_case_events(self, event_ids, action_result):

        if not isinstance(event_ids, (list, tuple)):
            event_ids = [event_ids]

        ret_val, events_details = self._get_events_details(event_ids, action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status(), None

        if not isinstance(events_details, (list, tuple)):
            events_details = [events_details]

        return phantom.APP_SUCCESS, events_details

    def _get_events_details(self, event_ids, action_result):

        endpoint = "{0}/getSecurityEvents".format(ARCSIGHT_SECURITYEVENTSERVICE_ENDPOINT)

        # params = {'authToken': self._auth_token, 'ids': event_id, 'startMillis': '-1', 'endMillis': '-1'}
        request_data = {
            "sev.getSecurityEvents": {
                "sev.authToken": self._auth_token,
                "sev.ids": event_ids,
                "sev.startMillis": "-1",
                "sev.endMillis": "-1"}}

        ret_val, resp = self._make_rest_call(endpoint, action_result, params=None, data=None, json=request_data,
                                             headers=None, method="post")

        if phantom.is_fail(ret_val):
            return phantom.APP_ERROR, None

        # parse the response and get the ids of all the cases
        self.debug_print(resp)

        try:
            events_details = resp.get('sev.getSecurityEventsResponse', {}).get('sev.return', {})
        except:
            events_details = {}

        return phantom.APP_SUCCESS, events_details

    def _get_case_details(self, case_id, action_result):

        endpoint = "{0}/getResourceById".format(ARCSIGHT_CASESERVICE_ENDPOINT)

        params = {'authToken': self._auth_token, 'resourceId': case_id}

        ret_val, resp = self._make_rest_call(endpoint, action_result, params)

        if phantom.is_fail(ret_val):
            return phantom.APP_ERROR, {}

        # parse the response and get the ids of all the cases
        self.debug_print(resp)
        try:
            case_details = resp.get('cas.getResourceByIdResponse', {}).get('cas.return', {})
        except:
            case_details = {}

        return phantom.APP_SUCCESS, case_details

    def _get_all_case_ids(self, param, action_result):

        endpoint = "{0}/findAllIds".format(ARCSIGHT_CASESERVICE_ENDPOINT)

        params = {'authToken': self._auth_token}

        ret_val, resp = self._make_rest_call(endpoint, action_result, params)

        if phantom.is_fail(ret_val):
            return phantom.APP_ERROR, []

        # parse the response and get the ids of all the cases
        self.debug_print(resp)

        try:
            case_ids = resp.get('cas.findAllIdsResponse', {}).get('cas.return', [])
        except:
            case_ids = []

        if not isinstance(case_ids, (list, tuple)):
            case_ids = [case_ids]

        return phantom.APP_SUCCESS, case_ids

    def _get_case(self, case_id, action_result):

        ret_val, case_details = self._get_case_details(case_id, action_result)

        if phantom.is_fail(ret_val):
            self.save_progress("Ignoring Case ID: {0}, could not get details.".format(case_id))
            return action_result.get_status(), None, None

        self.send_progress("Processing Case ID: {0}".format(case_id))

        # create a container
        container = {
            'source_data_identifier': case_id, 'name': case_details['name'],
            'description': case_details.get('description'),
            'data': {
                'case_detail': case_details
            },
            'start_time': _get_str_from_epoch(case_details.get('createdTimestamp'))
        }

        event_ids = case_details.get('eventIDs')

        if not event_ids:
            self.save_progress("Ignoring Case: {0}({1}) since it has no events".format(case_details['name'], case_id))
            return action_result.get_status(), container, None

        # now get the events for this container
        ret_val, events = self._get_case_events(case_details['eventIDs'], action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status(), container, None

        artifacts = []

        for i, event in enumerate(events):
            self.send_progress("Processing Event ID: {0}".format(event['eventId']))
            artifact = {
                'source_data_identifier': event['eventId'],
                'name': event.get('name', 'Artifact # {0}'.format(i)), 'data': event,
                'start_time': _get_str_from_epoch(event.get('startTime')),
                'end_time': _get_str_from_epoch(event.get('endTime'))
            }

            cef = {}

            # source details
            source = event.get('source')
            if source:
                cef['sourceUserName'] = source.get('userName')
                cef['sourceAddress'] = _to_ip(source.get('address'))
                cef['sourceMacAddress'] = _to_mac(source.get('maxAddress'))
                cef['sourcePort'] = _to_port(source.get('port'))
                cef['sourceHostName'] = source.get('hostName')

            # destination details
            destination = event.get('destination')
            if destination:
                cef['destinationUserName'] = destination.get('userName')
                cef['destinationAddress'] = _to_ip(destination.get('address'))
                cef['destinationMacAddress'] = _to_mac(destination.get('maxAddress'))
                cef['destinationPort'] = _to_port(destination.get('port'))
                cef['destinationHostName'] = destination.get('hostName')

            cef = {k: v for k, v in list(cef.items()) if v}

            if not cef:
                continue

            artifact['cef'] = cef

            artifacts.append(artifact)

        return phantom.APP_SUCCESS, container, artifacts

    def _parse_results(self, results, param):

        container_count = param.get(phantom.APP_JSON_CONTAINER_COUNT, ARCSIGHT_DEFAULT_CONTAINER_COUNT)
        artifact_count = param.get(phantom.APP_JSON_ARTIFACT_COUNT, ARCSIGHT_DEFAULT_ARTIFACT_COUNT)

        results = results[:container_count]

        for i, result in enumerate(results):

            container = result.get('container')

            if not container:
                continue

            container.update(_container_common)

            (ret_val, message, container_id) = self.save_container(container)
            self.debug_print(
                "save_container returns, value: {0}, reason: {1}, id: {2}".format(ret_val, message, container_id))

            artifacts = result.get('artifacts')
            if not artifacts:
                continue

            artifacts = artifacts[:artifact_count]

            len_artifacts = len(artifacts)

            for j, artifact in enumerate(artifacts):

                if not artifact:
                    continue

                # add the container id to the artifact
                artifact['container_id'] = container_id
                artifact.update(_artifact_common)

                # if it is the last artifact of the last container
                if (j + 1) == len_artifacts:
                    # mark it such that active playbooks get executed
                    artifact['run_automation'] = True

                ret_val, status_string, artifact_id = self.save_artifact(artifact)
                self.debug_print(
                    "save_artifact returns, value: {0}, reason: {1}, id: {2}".format(ret_val, status_string,
                                                                                     artifact_id))

        return self.set_status(phantom.APP_SUCCESS)

    def _ingest_cases(self, case_ids, param):

        results = []

        for case_id in case_ids:

            case_act_res = ActionResult()

            ret_val, container, artifacts = self._get_case(case_id, case_act_res)

            if phantom.is_fail(ret_val):
                continue

            if container and artifacts:
                results.append({'container': container, 'artifacts': artifacts})

        self.send_progress("Done Processing Cases and Events")

        self.save_progress("Ingesting results into Containers and Artifacts")

        self._parse_results(results, param)

        return phantom.APP_SUCCESS

    def _poll_now(self, param):

        action_result = self.add_action_result(ActionResult(param))

        ret_val = self._login(action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        container_id = param.get(phantom.APP_JSON_CONTAINER_ID)

        if container_id:
            case_ids = param[phantom.APP_JSON_CONTAINER_ID]
            case_ids = case_ids.split(',')
        else:
            ret_val, case_ids = self._get_all_case_ids(param, action_result)
            if phantom.is_fail(ret_val):
                return action_result.get_status()

        self.debug_print("Case IDS:", case_ids)

        self._ingest_cases(case_ids, param)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _on_poll(self, param):

        action_result = self.add_action_result(ActionResult(param))

        ret_val = self._login(action_result)

        if phantom.is_fail(ret_val):
            self.save_progress("On Poll Action Failed")
            return action_result.get_status()

        self.save_progress("On Poll Action Passed")
        return action_result.set_status(phantom.APP_ERROR)

    def _test_connectivity(self, param):

        action_result = self.add_action_result(ActionResult(param))

        ret_val = self._login(action_result)

        if phantom.is_fail(ret_val):
            self.save_progress("Test Connectivity Failed")
            return action_result.get_status()

        self.save_progress("Test Connectivity Passed")

        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_group_details(self, group_uri, action_result):

        endpoint = "{0}/getGroupByURI".format(ARCSIGHT_GROUPSERVICE_ENDPOINT)

        request_data = {
            "gro.getGroupByURI": {
                "gro.authToken": self._auth_token,
                "gro.uri": group_uri}}

        ret_val, resp = self._make_rest_call(endpoint, action_result, json=request_data, method="post")

        if phantom.is_fail(ret_val):
            return phantom.APP_ERROR, {}

        try:
            group_details = resp.get('gro.getGroupByURIResponse', {}).get('gro.return', {})
        except:
            group_details = {}

        return phantom.APP_SUCCESS, group_details

    def _get_child_id_by_name(self, parent_group_id, case_name, action_result):

        # Child not present, let's insert it
        endpoint = "{0}/getChildIDByChildNameOrAlias".format(ARCSIGHT_GROUPSERVICE_ENDPOINT)

        request_data = {
            "gro.getChildIDByChildNameOrAlias": {
                "gro.authToken": self._auth_token,
                "gro.groupId": parent_group_id,
                "gro.name": case_name}}

        ret_val, resp = self._make_rest_call(endpoint, action_result, json=request_data, method="post")

        if phantom.is_fail(ret_val):
            return action_result.get_status(), None

        try:
            case_id = resp.get('gro.getChildIDByChildNameOrAliasResponse', {}).get('gro.return', {})
        except:
            # If the case is not present, the response ....Response is not a dict
            case_id = None

        return phantom.APP_SUCCESS, case_id

    def _create_ticket(self, param):

        action_result = self.add_action_result(ActionResult(param))

        ret_val = self._login(action_result)

        if phantom.is_fail(ret_val):
            self.save_progress(ARCSIGHT_ERR_UNABLE_TO_LOGIN)
            return action_result.get_status()

        parent_group = param.get(ARCSIGHT_JSON_PARENT_GROUP, ARCSIGHT_DEFAULT_PARENT_GROUP)

        if not parent_group.startswith('/'):
            parent_group = f'/{parent_group}'

        parent_group = parent_group.rstrip('/')

        case_name = param[ARCSIGHT_JSON_CASE_NAME]

        # First get the id of the group
        ret_val, group_details = self._get_group_details(parent_group, action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        group_id = group_details.get('resourceid')

        if not group_id:
            return action_result.set_status(phantom.APP_ERROR,
                                            "Unable to get the group id of Group: '{0}'".format(parent_group))

        self.save_progress('Got parent group ID: {0}'.format(group_id))

        # init the summary as if the case was created
        summary = action_result.set_summary({'case_created': True})

        # Try to see if there is already a case with that name

        ret_val, case_id = self._get_child_id_by_name(group_id, case_name, action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        if case_id:
            # Child is already present
            summary['case_created'] = False
            ret_val, case_details = self._get_case_details(case_id, action_result)
            if phantom.is_fail(ret_val):
                action_result.append_to_message(ARCSIGHT_ERR_UNABLE_TO_GET_CASE_INFO)
                return action_result.get_status()
            case_id = case_details.get('resourceid')

            if case_id:
                summary['case_id'] = case_id

            action_result.add_data(case_details)
            return action_result.set_status(phantom.APP_SUCCESS, "Case already existed")

        # Child not present, let's insert it
        endpoint = "{0}/insertResource".format(ARCSIGHT_CASESERVICE_ENDPOINT)

        request_data = {
            "cas.insertResource": {
                "cas.authToken": self._auth_token,
                "cas.resource": {'name': case_name},
                "cas.parentId": group_id}}

        ret_val, resp = self._make_rest_call(endpoint, action_result, json=request_data, method="post")

        if phantom.is_fail(ret_val):
            summary['case_created'] = False
            return action_result.get_status()

        summary['case_created'] = True

        try:
            case_details = resp.get('cas.insertResourceResponse', {}).get('cas.return', {})
        except:
            case_details = {}

        case_id = case_details.get('resourceid')

        if case_id:
            summary['case_id'] = case_id

        action_result.add_data(case_details)

        return action_result.set_status(phantom.APP_SUCCESS, "New case created")

    def _update_ticket(self, param):

        action_result = self.add_action_result(ActionResult(param))

        ret_val = self._login(action_result)

        if phantom.is_fail(ret_val):
            self.save_progress(ARCSIGHT_ERR_UNABLE_TO_LOGIN)
            return action_result.get_status()

        # Validate the fields param json
        update_fields = param[ARCSIGHT_JSON_UPDATE_FIELDS]

        # try to load it up
        try:
            update_fields = json.loads(update_fields)
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR,
                                            f"Unable to load the input 'update_fields' json. {error_msg}")

        # Get the case info
        case_id = param[ARCSIGHT_JSON_CASE_ID]
        ret_val, case_details = self._get_case_details(case_id, action_result)

        if phantom.is_fail(ret_val):
            action_result.append_to_message(ARCSIGHT_ERR_UNABLE_TO_GET_CASE_INFO)
            return action_result.get_status()

        # update the dictionary that we got with the one that was inputted
        case_details.update(update_fields)

        request_data = {
            "cas.update": {
                "cas.authToken": self._auth_token,
                "cas.resource": case_details}}

        endpoint = "{0}/update".format(ARCSIGHT_CASESERVICE_ENDPOINT)

        ret_val, resp = self._make_rest_call(endpoint, action_result, json=request_data, method="post")

        if phantom.is_fail(ret_val):
            return phantom.APP_ERROR, {}

        try:
            case_details = resp.get('cas.updateResponse', {}).get('cas.return', {})
        except:
            case_details = {}

        action_result.add_data(case_details)

        action_result.update_summary({'case_id': case_details.get('resourceid')})

        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_ticket(self, param):

        action_result = self.add_action_result(ActionResult(param))

        ret_val = self._login(action_result)

        if phantom.is_fail(ret_val):
            self.save_progress(ARCSIGHT_ERR_UNABLE_TO_LOGIN)
            return action_result.get_status()

        # Get the case info
        case_id = param[ARCSIGHT_JSON_CASE_ID]
        ret_val, case_details = self._get_case_details(case_id, action_result)

        if phantom.is_fail(ret_val):
            action_result.append_to_message(ARCSIGHT_ERR_UNABLE_TO_GET_CASE_INFO)
            return action_result.get_status()

        action_result.add_data(case_details)

        action_result.update_summary({'case_id': case_details.get('resourceid')})

        return action_result.set_status(phantom.APP_SUCCESS)

    def _run_query(self, param):

        action_result = self.add_action_result(ActionResult(param))

        ret_val = self._login(action_result)

        if phantom.is_fail(ret_val):
            self.save_progress(ARCSIGHT_ERR_UNABLE_TO_LOGIN)
            return action_result.get_status()

        query_string = param[ARCSIGHT_JSON_QUERY]

        query_type = param.get(ARCSIGHT_JSON_TYPE, "all").lower()

        if query_type != 'all':
            query_string = "type:{0} and {1}".format(query_type, query_string)

        result_range = param.get(ARCSIGHT_JSON_RANGE, "0-10")

        ret_val = _validate_range(result_range, action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Range
        mini, maxi = (int(x) for x in result_range.split('-'))
        request_data = {
            "mss.search": {
                "mss.authToken": self._auth_token,
                "mss.queryStr": query_string,
                "mss.startPosition": mini,
                "mss.pageSize": (maxi - mini) + 1}}

        endpoint = "{0}/search".format(ARCSIGHT_MANAGERSEARCHSERVICE_ENDPOINT)

        ret_val, resp = self._make_rest_call(endpoint, action_result, json=request_data, method="post")

        if phantom.is_fail(ret_val):
            return phantom.APP_ERROR, {}

        try:
            search_result = resp.get('mss.searchResponse', {}).get('mss.return', {})
        except:
            search_result = {}

        search_hits = search_result.get('searchHits', [])

        if not isinstance(search_hits, list):
            search_result['searchHits'] = [search_hits]
            # this variable is used downstream, so set it up again
            search_hits = search_result.get('searchHits', [])

        action_result.add_data(search_result)

        action_result.update_summary(
            {'total_items': search_result.get('hitCount'), 'total_items_returned': len(search_hits)})

        return action_result.set_status(phantom.APP_SUCCESS)

    def handle_action(self, param):
        """
        Get current action identifier and call member function of its own to handle the action.

        :param param: dictionary which contains information about the actions to be executed
        :return: status success/failure
        """
        result = None
        action = self.get_action_identifier()

        if action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY:
            result = self._test_connectivity(param)
        elif action == ACTION_ID_CREATE_TICKET:
            result = self._create_ticket(param)
        elif action == ACTION_ID_UPDATE_TICKET:
            result = self._update_ticket(param)
        elif action == ACTION_ID_GET_TICKET:
            result = self._get_ticket(param)
        elif action == ACTION_ID_RUN_QUERY:
            result = self._run_query(param)

        return result


def main():
    import pudb
    import argparse

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument("input_test_json", help="Input Test JSON file")
    argparser.add_argument("-u", "--username", help="username", required=False)
    argparser.add_argument("-p", "--password", help="password", required=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password

    if username is not None and password is None:
        # User specified a username but not a password, so ask
        import getpass

        password = getpass.getpass("Password: ")

    csrftoken = None
    headers = None
    if username and password:
        try:
            login_url = ArcsightConnector._get_phantom_base_url() + "/login"

            print("Accessing the Login page")
            r = requests.get(login_url, verify=False)
            csrftoken = r.cookies["csrftoken"]

            data = dict()
            data["username"] = username
            data["password"] = password
            data["csrfmiddlewaretoken"] = csrftoken

            headers = dict()
            headers["Cookie"] = "csrftoken=" + csrftoken
            headers["Referer"] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=False, data=data, headers=headers)
            session_id = r2.cookies["sessionid"]
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = ArcsightConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json["user_session_token"] = session_id
            if csrftoken and headers:
                connector._set_csrf_info(csrftoken, headers["Referer"])

        json_string = json.dumps(in_json)
        ret_val = connector._handle_action(json_string, None)
        print(json.dumps(json.loads(ret_val), indent=4))

    exit(0)


if __name__ == "__main__":
    main()
