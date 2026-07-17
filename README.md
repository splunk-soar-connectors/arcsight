# ArcSight ESM

Publisher: Splunk Community <br>
Connector Version: 2.0.0 <br>
Product Vendor: HPE <br>
Product Name: ArcSight ESM <br>
Minimum Product Version: 4.9.39220

This app implements creating and updating cases on ArcSight

### Configuration variables

This table lists the configuration variables required to operate ArcSight ESM. These variables are specified when configuring a ArcSight ESM asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**base_url** | required | string | Device Base URL |
**verify_server_cert** | optional | boolean | Verify server certificate |
**username** | required | string | Username |
**password** | required | password | Password |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity <br>
[create ticket](#action-create-ticket) - Create a case <br>
[update ticket](#action-update-ticket) - Update a case on ArcSight <br>
[get ticket](#action-get-ticket) - Get case information <br>
[run query](#action-run-query) - Search for a text in resources

## action: 'test connectivity'

Validate the asset configuration for connectivity

Type: **test** <br>
Read only: **True**

This action runs a quick query on the server to check the connection and credentials.

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'create ticket'

Create a case

Type: **generic** <br>
Read only: **False**

If the <b>parent_group</b> parameter is not specified, the action defaults to <i>/All Cases/All Cases</i>. ArcSight does not allow multiple cases with the same name to exist within the same group. This action will succeed if a case with the same name already exists within the given <b>parent_group</b>. However, the data path <b>action_result.summary.case_created</b> will be set to <i>False</i> to denote that a case was not created.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**parent_group** | optional | Group | string | `arcsight group` |
**name** | required | Name | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.name | string | | test case name |
action_result.parameter.parent_group | string | `arcsight group` | /All Cases/All Cases |
action_result.data.\*.URI | string | | |
action_result.data.\*.attributeInitializationInProgress | boolean | | True False |
action_result.data.\*.createdTime.day | numeric | | |
action_result.data.\*.createdTime.hour | numeric | | |
action_result.data.\*.createdTime.milliSecond | numeric | | |
action_result.data.\*.createdTime.minute | numeric | | |
action_result.data.\*.createdTime.month | numeric | | |
action_result.data.\*.createdTime.second | numeric | | |
action_result.data.\*.createdTime.timezoneID | string | | |
action_result.data.\*.createdTime.year | numeric | | |
action_result.data.\*.createdTimestamp | numeric | | |
action_result.data.\*.creatorName | string | | |
action_result.data.\*.deprecated | boolean | | True False |
action_result.data.\*.disabled | boolean | | True False |
action_result.data.\*.displayID | numeric | | |
action_result.data.\*.inCache | boolean | | True False |
action_result.data.\*.inactive | boolean | | True False |
action_result.data.\*.initialized | boolean | | True False |
action_result.data.\*.isAdditionalLoaded | boolean | | True False |
action_result.data.\*.localID | numeric | | |
action_result.data.\*.modificationCount | numeric | | |
action_result.data.\*.modifiedTime.day | numeric | | |
action_result.data.\*.modifiedTime.hour | numeric | | |
action_result.data.\*.modifiedTime.milliSecond | numeric | | |
action_result.data.\*.modifiedTime.minute | numeric | | |
action_result.data.\*.modifiedTime.month | numeric | | |
action_result.data.\*.modifiedTime.second | numeric | | |
action_result.data.\*.modifiedTime.timezoneID | string | | |
action_result.data.\*.modifiedTime.year | numeric | | |
action_result.data.\*.modifiedTimestamp | numeric | | |
action_result.data.\*.modifierName | string | | |
action_result.data.\*.name | string | | |
action_result.data.\*.numberOfOccurrences | numeric | | |
action_result.data.\*.reference.id | string | `arcsight case id` | |
action_result.data.\*.reference.isModifiable | boolean | | True False |
action_result.data.\*.reference.managerID | string | | |
action_result.data.\*.reference.referenceName | string | | |
action_result.data.\*.reference.referenceString | string | | |
action_result.data.\*.reference.referenceType | numeric | | |
action_result.data.\*.reference.uri | string | | |
action_result.data.\*.reportingLevel | numeric | | |
action_result.data.\*.resourceid | string | `arcsight case id` | |
action_result.data.\*.state | numeric | | |
action_result.data.\*.type | numeric | | |
action_result.data.\*.typeName | string | | |
action_result.status | string | | success failed |
action_result.summary.case_created | boolean | | True False |
action_result.summary.case_id | string | `arcsight case id` | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'update ticket'

Update a case on ArcSight

Type: **generic** <br>
Read only: **False**

ArcSight uses a Resource ID (for example, <i>7Vvj0W1UBABCbNut33qjiZw==</i> ) to represent a single resource item. Use a case's Resource ID as the <b>id</b> parameter value.<br>The <b>update_fields</b> parameter should be a valid JSON, the keys of which should contain the fields that need to be updated for the particular case. Note that the keys displayed in the ArcSight UI are different from the key names that should be specified in the <b>update_fields</b> parameters.<br>For example, the <i>External ID</i> field is represented in the ArcSight system by the <i>externalID</i> key value. One way to figure the mapping is to connect to https://\[arcsight_device\]:8443/www/manager-service/services/CaseService?wsdl and look at the <i>Resource</i> and <i>Case</i> complexType values.<br>As an example, to set the <i>External ID</i> value of a case, use the <b>update_fields</b> parameter as <b>{"externalID": "INC1231413"}</b><br>The ArcSight API will not throw any error for the invalid field used in the <b>update_fields</b> JSON.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Case ID | string | `arcsight case id` |
**update_fields** | required | JSON containing field values | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.id | string | `arcsight case id` | 7Vvj0W1UBABCbNut33qjiZw== |
action_result.parameter.update_fields | string | | {"externalID": "INC1231413"} |
action_result.data.\*.URI | string | | |
action_result.data.\*.action | string | | |
action_result.data.\*.actionsTaken | string | | |
action_result.data.\*.alias | string | | |
action_result.data.\*.associatedImpact | string | | |
action_result.data.\*.attackAgent | string | | |
action_result.data.\*.attackMechanism | string | | |
action_result.data.\*.attributeInitializationInProgress | boolean | | True False |
action_result.data.\*.consequenceSeverity | string | | |
action_result.data.\*.createdTime.day | numeric | | |
action_result.data.\*.createdTime.hour | numeric | | |
action_result.data.\*.createdTime.milliSecond | numeric | | |
action_result.data.\*.createdTime.minute | numeric | | |
action_result.data.\*.createdTime.month | numeric | | |
action_result.data.\*.createdTime.second | numeric | | |
action_result.data.\*.createdTime.timezoneID | string | | |
action_result.data.\*.createdTime.year | numeric | | |
action_result.data.\*.createdTimestamp | numeric | | |
action_result.data.\*.creatorName | string | | |
action_result.data.\*.deprecated | boolean | | True False |
action_result.data.\*.description | string | | |
action_result.data.\*.disabled | boolean | | True False |
action_result.data.\*.displayID | numeric | | |
action_result.data.\*.externalID | string | | |
action_result.data.\*.frequency | string | | |
action_result.data.\*.inCache | boolean | | True False |
action_result.data.\*.inactive | boolean | | True False |
action_result.data.\*.incidentSource1 | string | | |
action_result.data.\*.initialized | boolean | | True False |
action_result.data.\*.isAdditionalLoaded | boolean | | True False |
action_result.data.\*.localID | numeric | | |
action_result.data.\*.modificationCount | numeric | | |
action_result.data.\*.modifiedTime.day | numeric | | |
action_result.data.\*.modifiedTime.hour | numeric | | |
action_result.data.\*.modifiedTime.milliSecond | numeric | | |
action_result.data.\*.modifiedTime.minute | numeric | | |
action_result.data.\*.modifiedTime.month | numeric | | |
action_result.data.\*.modifiedTime.second | numeric | | |
action_result.data.\*.modifiedTime.timezoneID | string | | |
action_result.data.\*.modifiedTime.year | numeric | | |
action_result.data.\*.modifiedTimestamp | numeric | | |
action_result.data.\*.modifierName | string | | |
action_result.data.\*.name | string | | |
action_result.data.\*.numberOfOccurrences | numeric | | |
action_result.data.\*.operationalImpact | string | | |
action_result.data.\*.reference.id | string | `arcsight case id` | |
action_result.data.\*.reference.isModifiable | boolean | | True False |
action_result.data.\*.reference.managerID | string | | |
action_result.data.\*.reference.referenceName | string | | |
action_result.data.\*.reference.referenceString | string | | |
action_result.data.\*.reference.referenceType | numeric | | |
action_result.data.\*.reference.uri | string | | |
action_result.data.\*.reportingLevel | numeric | | |
action_result.data.\*.resistance | string | | |
action_result.data.\*.resourceid | string | `arcsight case id` | |
action_result.data.\*.securityClassification | string | | |
action_result.data.\*.securityClassificationCode | string | | |
action_result.data.\*.sensitivity | string | | |
action_result.data.\*.stage | string | | |
action_result.data.\*.state | numeric | | |
action_result.data.\*.ticketType | string | | |
action_result.data.\*.type | numeric | | |
action_result.data.\*.typeName | string | | |
action_result.data.\*.vulnerability | string | | |
action_result.data.\*.vulnerabilityType1 | string | | |
action_result.data.\*.vulnerabilityType2 | string | | |
action_result.status | string | | success failed |
action_result.summary.case_id | string | `arcsight case id` | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get ticket'

Get case information

Type: **investigate** <br>
Read only: **True**

ArcSight uses a Resource ID (for example, <i>7Vvj0W1UBABCbNut33qjiZw==</i>) to represent a single resource item. Use a case's Resource ID as the <b>id</b> parameter value.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Case ID | string | `arcsight case id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.id | string | `arcsight case id` | 7Vvj0W1UBABCbNut33qjiZw== |
action_result.data.\*.URI | string | | |
action_result.data.\*.action | string | | |
action_result.data.\*.actionsTaken | string | | |
action_result.data.\*.alias | string | | |
action_result.data.\*.associatedImpact | string | | |
action_result.data.\*.attackAgent | string | | |
action_result.data.\*.attackMechanism | string | | |
action_result.data.\*.attributeInitializationInProgress | boolean | | True False |
action_result.data.\*.consequenceSeverity | string | | |
action_result.data.\*.createdTime.day | numeric | | |
action_result.data.\*.createdTime.hour | numeric | | |
action_result.data.\*.createdTime.milliSecond | numeric | | |
action_result.data.\*.createdTime.minute | numeric | | |
action_result.data.\*.createdTime.month | numeric | | |
action_result.data.\*.createdTime.second | numeric | | |
action_result.data.\*.createdTime.timezoneID | string | | |
action_result.data.\*.createdTime.year | numeric | | |
action_result.data.\*.createdTimestamp | numeric | | |
action_result.data.\*.creatorName | string | | |
action_result.data.\*.deprecated | boolean | | True False |
action_result.data.\*.description | string | | |
action_result.data.\*.disabled | boolean | | True False |
action_result.data.\*.displayID | numeric | | |
action_result.data.\*.externalID | string | | |
action_result.data.\*.frequency | string | | |
action_result.data.\*.inCache | boolean | | True False |
action_result.data.\*.inactive | boolean | | True False |
action_result.data.\*.incidentSource1 | string | | |
action_result.data.\*.initialized | boolean | | True False |
action_result.data.\*.isAdditionalLoaded | boolean | | True False |
action_result.data.\*.localID | numeric | | |
action_result.data.\*.modificationCount | numeric | | |
action_result.data.\*.modifiedTime.day | numeric | | |
action_result.data.\*.modifiedTime.hour | numeric | | |
action_result.data.\*.modifiedTime.milliSecond | numeric | | |
action_result.data.\*.modifiedTime.minute | numeric | | |
action_result.data.\*.modifiedTime.month | numeric | | |
action_result.data.\*.modifiedTime.second | numeric | | |
action_result.data.\*.modifiedTime.timezoneID | string | | |
action_result.data.\*.modifiedTime.year | numeric | | |
action_result.data.\*.modifiedTimestamp | numeric | | |
action_result.data.\*.modifierName | string | | |
action_result.data.\*.name | string | | |
action_result.data.\*.numberOfOccurrences | numeric | | |
action_result.data.\*.operationalImpact | string | | |
action_result.data.\*.reference.id | string | `arcsight case id` | |
action_result.data.\*.reference.isModifiable | boolean | | True False |
action_result.data.\*.reference.managerID | string | | |
action_result.data.\*.reference.referenceName | string | | |
action_result.data.\*.reference.referenceString | string | | |
action_result.data.\*.reference.referenceType | numeric | | |
action_result.data.\*.reference.uri | string | | |
action_result.data.\*.reportingLevel | numeric | | |
action_result.data.\*.resistance | string | | |
action_result.data.\*.resourceid | string | `arcsight case id` | |
action_result.data.\*.securityClassification | string | | |
action_result.data.\*.securityClassificationCode | string | | |
action_result.data.\*.sensitivity | string | | |
action_result.data.\*.stage | string | | |
action_result.data.\*.state | numeric | | |
action_result.data.\*.ticketType | string | | |
action_result.data.\*.type | numeric | | |
action_result.data.\*.typeName | string | | |
action_result.data.\*.vulnerability | string | | |
action_result.data.\*.vulnerabilityType1 | string | | |
action_result.data.\*.vulnerabilityType2 | string | | |
action_result.status | string | | success failed |
action_result.summary.case_id | string | `arcsight case id` | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'run query'

Search for a text in resources

Type: **investigate** <br>
Read only: **True**

This action implements the ArcSight console's search feature. It searches for the text (specified in the <b>query</b> parameter) in the specified resource <b>type</b>.<br>Multiple search strings can be separated by spaces. Enclose the string in quotes to search for the exact string containing spaces. For example, to search for resources containing <i>foo</i> <b>or</b> <i>bar</i>, use <b>foo bar</b>.<br>To search for the word foo followed by bar and separated by space, use the string <b>"foo bar"</b>.<br>ArcSight executes searches on the <i>stem</i> of each word. For example, if the word searched is <i>going</i>, ArcSight will actually search for <i>go</i>. The same rules apply for quoted phrases. For example, if the <b>query</b> parameter is <b>"going description"</b>, the actual query executed will be <b>"go descript"</b>.<br>The action's widget displays the <b>Internal Query String</b> that ArcSight ends up using. Use this string to verify the text being searched. Using quotes around the query string makes the search more deterministic.<br>The Action Run dialog displays a drop-down list of possible values for the <b>type</b> parameter. However, playbooks allow a user to specify values other than the one listed in the Action Run dialog.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**type** | optional | Resource type | string | |
**query** | required | Query Text | string | `arcsight search string` |
**range** | optional | Items range to return (min_offset-max_offset) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.query | string | `arcsight search string` | foo bar |
action_result.parameter.range | string | | 0-10 |
action_result.parameter.type | string | | ActiveChannel |
action_result.data.\*.elapsed | numeric | | |
action_result.data.\*.hitCount | numeric | | |
action_result.data.\*.rewrittenQueryString | string | | |
action_result.data.\*.searchHits.\*.name | string | | |
action_result.data.\*.searchHits.\*.score | numeric | | |
action_result.data.\*.searchHits.\*.uri | string | | |
action_result.data.\*.searchHits.\*.uuid | string | `arcsight resource id` | |
action_result.data.\*.statusString | string | | |
action_result.status | string | | success failed |
action_result.summary.total_items | numeric | | |
action_result.summary.total_items_returned | numeric | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
