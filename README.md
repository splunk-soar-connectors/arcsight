[comment]: # "Auto-generated SOAR connector documentation"
# ArcSight ESM

Publisher: Splunk Community  
Connector Version: 2\.0\.1  
Product Vendor: HPE  
Product Name: ArcSight ESM  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.9\.39220  

This app implements creating and updating cases on ArcSight

### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a ArcSight ESM asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**base\_url** |  required  | string | Device Base URL
**verify\_server\_cert** |  optional  | boolean | Verify server certificate
**username** |  required  | string | Username
**password** |  required  | password | Password

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity  
[create ticket](#action-create-ticket) - Create a case  
[update ticket](#action-update-ticket) - Update a case on ArcSight  
[get ticket](#action-get-ticket) - Get case information  
[run query](#action-run-query) - Search for a text in resources  

## action: 'test connectivity'
Validate the asset configuration for connectivity

Type: **test**  
Read only: **True**

This action runs a quick query on the server to check the connection and credentials\.

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'create ticket'
Create a case

Type: **generic**  
Read only: **False**

If the <b>parent\_group</b> parameter is not specified, the action defaults to <i>/All Cases/All Cases</i>\. ArcSight does not allow multiple cases with the same name to exist within the same group\. This action will succeed if a case with the same name already exists within the given <b>parent\_group</b>\. However, the data path <b>action\_result\.summary\.case\_created</b> will be set to <i>False</i> to denote that a case was not created\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**parent\_group** |  optional  | Group | string |  `arcsight group` 
**name** |  required  | Name | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.name | string | 
action\_result\.parameter\.parent\_group | string |  `arcsight group` 
action\_result\.data\.\*\.URI | string | 
action\_result\.data\.\*\.attributeInitializationInProgress | boolean | 
action\_result\.data\.\*\.createdTime\.day | numeric | 
action\_result\.data\.\*\.createdTime\.hour | numeric | 
action\_result\.data\.\*\.createdTime\.milliSecond | numeric | 
action\_result\.data\.\*\.createdTime\.minute | numeric | 
action\_result\.data\.\*\.createdTime\.month | numeric | 
action\_result\.data\.\*\.createdTime\.second | numeric | 
action\_result\.data\.\*\.createdTime\.timezoneID | string | 
action\_result\.data\.\*\.createdTime\.year | numeric | 
action\_result\.data\.\*\.createdTimestamp | numeric | 
action\_result\.data\.\*\.creatorName | string | 
action\_result\.data\.\*\.deprecated | boolean | 
action\_result\.data\.\*\.disabled | boolean | 
action\_result\.data\.\*\.displayID | numeric | 
action\_result\.data\.\*\.inCache | boolean | 
action\_result\.data\.\*\.inactive | boolean | 
action\_result\.data\.\*\.initialized | boolean | 
action\_result\.data\.\*\.isAdditionalLoaded | boolean | 
action\_result\.data\.\*\.localID | numeric | 
action\_result\.data\.\*\.modificationCount | numeric | 
action\_result\.data\.\*\.modifiedTime\.day | numeric | 
action\_result\.data\.\*\.modifiedTime\.hour | numeric | 
action\_result\.data\.\*\.modifiedTime\.milliSecond | numeric | 
action\_result\.data\.\*\.modifiedTime\.minute | numeric | 
action\_result\.data\.\*\.modifiedTime\.month | numeric | 
action\_result\.data\.\*\.modifiedTime\.second | numeric | 
action\_result\.data\.\*\.modifiedTime\.timezoneID | string | 
action\_result\.data\.\*\.modifiedTime\.year | numeric | 
action\_result\.data\.\*\.modifiedTimestamp | numeric | 
action\_result\.data\.\*\.modifierName | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.numberOfOccurrences | numeric | 
action\_result\.data\.\*\.reference\.id | string |  `arcsight case id` 
action\_result\.data\.\*\.reference\.isModifiable | boolean | 
action\_result\.data\.\*\.reference\.managerID | string | 
action\_result\.data\.\*\.reference\.referenceName | string | 
action\_result\.data\.\*\.reference\.referenceString | string | 
action\_result\.data\.\*\.reference\.referenceType | numeric | 
action\_result\.data\.\*\.reference\.uri | string | 
action\_result\.data\.\*\.reportingLevel | numeric | 
action\_result\.data\.\*\.resourceid | string |  `arcsight case id` 
action\_result\.data\.\*\.state | numeric | 
action\_result\.data\.\*\.type | numeric | 
action\_result\.data\.\*\.typeName | string | 
action\_result\.status | string | 
action\_result\.summary\.case\_created | boolean | 
action\_result\.summary\.case\_id | string |  `arcsight case id` 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'update ticket'
Update a case on ArcSight

Type: **generic**  
Read only: **False**

ArcSight uses a Resource ID \(for example, <i>7Vvj0W1UBABCbNut33qjiZw==</i> \) to represent a single resource item\. Use a case's Resource ID as the <b>id</b> parameter value\.<br>The <b>update\_fields</b> parameter should be a valid JSON, the keys of which should contain the fields that need to be updated for the particular case\. Note that the keys displayed in the ArcSight UI are different from the key names that should be specified in the <b>update\_fields</b> parameters\.<br>For example, the <i>External ID</i> field is represented in the ArcSight system by the <i>externalID</i> key value\. One way to figure the mapping is to connect to https\://\[arcsight\_device\]\:8443/www/manager\-service/services/CaseService?wsdl and look at the <i>Resource</i> and <i>Case</i> complexType values\.<br>As an example, to set the <i>External ID</i> value of a case, use the <b>update\_fields</b> parameter as <b>\{"externalID"\: "INC1231413"\}</b><br>The ArcSight API will not throw any error for the invalid field used in the <b>update\_fields</b> JSON\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Case ID | string |  `arcsight case id` 
**update\_fields** |  required  | JSON containing field values | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.id | string |  `arcsight case id` 
action\_result\.parameter\.update\_fields | string | 
action\_result\.data\.\*\.URI | string | 
action\_result\.data\.\*\.action | string | 
action\_result\.data\.\*\.actionsTaken | string | 
action\_result\.data\.\*\.alias | string | 
action\_result\.data\.\*\.associatedImpact | string | 
action\_result\.data\.\*\.attackAgent | string | 
action\_result\.data\.\*\.attackMechanism | string | 
action\_result\.data\.\*\.attributeInitializationInProgress | boolean | 
action\_result\.data\.\*\.consequenceSeverity | string | 
action\_result\.data\.\*\.createdTime\.day | numeric | 
action\_result\.data\.\*\.createdTime\.hour | numeric | 
action\_result\.data\.\*\.createdTime\.milliSecond | numeric | 
action\_result\.data\.\*\.createdTime\.minute | numeric | 
action\_result\.data\.\*\.createdTime\.month | numeric | 
action\_result\.data\.\*\.createdTime\.second | numeric | 
action\_result\.data\.\*\.createdTime\.timezoneID | string | 
action\_result\.data\.\*\.createdTime\.year | numeric | 
action\_result\.data\.\*\.createdTimestamp | numeric | 
action\_result\.data\.\*\.creatorName | string | 
action\_result\.data\.\*\.deprecated | boolean | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.disabled | boolean | 
action\_result\.data\.\*\.displayID | numeric | 
action\_result\.data\.\*\.externalID | string | 
action\_result\.data\.\*\.frequency | string | 
action\_result\.data\.\*\.inCache | boolean | 
action\_result\.data\.\*\.inactive | boolean | 
action\_result\.data\.\*\.incidentSource1 | string | 
action\_result\.data\.\*\.initialized | boolean | 
action\_result\.data\.\*\.isAdditionalLoaded | boolean | 
action\_result\.data\.\*\.localID | numeric | 
action\_result\.data\.\*\.modificationCount | numeric | 
action\_result\.data\.\*\.modifiedTime\.day | numeric | 
action\_result\.data\.\*\.modifiedTime\.hour | numeric | 
action\_result\.data\.\*\.modifiedTime\.milliSecond | numeric | 
action\_result\.data\.\*\.modifiedTime\.minute | numeric | 
action\_result\.data\.\*\.modifiedTime\.month | numeric | 
action\_result\.data\.\*\.modifiedTime\.second | numeric | 
action\_result\.data\.\*\.modifiedTime\.timezoneID | string | 
action\_result\.data\.\*\.modifiedTime\.year | numeric | 
action\_result\.data\.\*\.modifiedTimestamp | numeric | 
action\_result\.data\.\*\.modifierName | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.numberOfOccurrences | numeric | 
action\_result\.data\.\*\.operationalImpact | string | 
action\_result\.data\.\*\.reference\.id | string |  `arcsight case id` 
action\_result\.data\.\*\.reference\.isModifiable | boolean | 
action\_result\.data\.\*\.reference\.managerID | string | 
action\_result\.data\.\*\.reference\.referenceName | string | 
action\_result\.data\.\*\.reference\.referenceString | string | 
action\_result\.data\.\*\.reference\.referenceType | numeric | 
action\_result\.data\.\*\.reference\.uri | string | 
action\_result\.data\.\*\.reportingLevel | numeric | 
action\_result\.data\.\*\.resistance | string | 
action\_result\.data\.\*\.resourceid | string |  `arcsight case id` 
action\_result\.data\.\*\.securityClassification | string | 
action\_result\.data\.\*\.securityClassificationCode | string | 
action\_result\.data\.\*\.sensitivity | string | 
action\_result\.data\.\*\.stage | string | 
action\_result\.data\.\*\.state | numeric | 
action\_result\.data\.\*\.ticketType | string | 
action\_result\.data\.\*\.type | numeric | 
action\_result\.data\.\*\.typeName | string | 
action\_result\.data\.\*\.vulnerability | string | 
action\_result\.data\.\*\.vulnerabilityType1 | string | 
action\_result\.data\.\*\.vulnerabilityType2 | string | 
action\_result\.status | string | 
action\_result\.summary\.case\_id | string |  `arcsight case id` 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get ticket'
Get case information

Type: **investigate**  
Read only: **True**

ArcSight uses a Resource ID \(for example, <i>7Vvj0W1UBABCbNut33qjiZw==</i>\) to represent a single resource item\. Use a case's Resource ID as the <b>id</b> parameter value\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Case ID | string |  `arcsight case id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.id | string |  `arcsight case id` 
action\_result\.data\.\*\.URI | string | 
action\_result\.data\.\*\.action | string | 
action\_result\.data\.\*\.actionsTaken | string | 
action\_result\.data\.\*\.alias | string | 
action\_result\.data\.\*\.associatedImpact | string | 
action\_result\.data\.\*\.attackAgent | string | 
action\_result\.data\.\*\.attackMechanism | string | 
action\_result\.data\.\*\.attributeInitializationInProgress | boolean | 
action\_result\.data\.\*\.consequenceSeverity | string | 
action\_result\.data\.\*\.createdTime\.day | numeric | 
action\_result\.data\.\*\.createdTime\.hour | numeric | 
action\_result\.data\.\*\.createdTime\.milliSecond | numeric | 
action\_result\.data\.\*\.createdTime\.minute | numeric | 
action\_result\.data\.\*\.createdTime\.month | numeric | 
action\_result\.data\.\*\.createdTime\.second | numeric | 
action\_result\.data\.\*\.createdTime\.timezoneID | string | 
action\_result\.data\.\*\.createdTime\.year | numeric | 
action\_result\.data\.\*\.createdTimestamp | numeric | 
action\_result\.data\.\*\.creatorName | string | 
action\_result\.data\.\*\.deprecated | boolean | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.disabled | boolean | 
action\_result\.data\.\*\.displayID | numeric | 
action\_result\.data\.\*\.externalID | string | 
action\_result\.data\.\*\.frequency | string | 
action\_result\.data\.\*\.inCache | boolean | 
action\_result\.data\.\*\.inactive | boolean | 
action\_result\.data\.\*\.incidentSource1 | string | 
action\_result\.data\.\*\.initialized | boolean | 
action\_result\.data\.\*\.isAdditionalLoaded | boolean | 
action\_result\.data\.\*\.localID | numeric | 
action\_result\.data\.\*\.modificationCount | numeric | 
action\_result\.data\.\*\.modifiedTime\.day | numeric | 
action\_result\.data\.\*\.modifiedTime\.hour | numeric | 
action\_result\.data\.\*\.modifiedTime\.milliSecond | numeric | 
action\_result\.data\.\*\.modifiedTime\.minute | numeric | 
action\_result\.data\.\*\.modifiedTime\.month | numeric | 
action\_result\.data\.\*\.modifiedTime\.second | numeric | 
action\_result\.data\.\*\.modifiedTime\.timezoneID | string | 
action\_result\.data\.\*\.modifiedTime\.year | numeric | 
action\_result\.data\.\*\.modifiedTimestamp | numeric | 
action\_result\.data\.\*\.modifierName | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.numberOfOccurrences | numeric | 
action\_result\.data\.\*\.operationalImpact | string | 
action\_result\.data\.\*\.reference\.id | string |  `arcsight case id` 
action\_result\.data\.\*\.reference\.isModifiable | boolean | 
action\_result\.data\.\*\.reference\.managerID | string | 
action\_result\.data\.\*\.reference\.referenceName | string | 
action\_result\.data\.\*\.reference\.referenceString | string | 
action\_result\.data\.\*\.reference\.referenceType | numeric | 
action\_result\.data\.\*\.reference\.uri | string | 
action\_result\.data\.\*\.reportingLevel | numeric | 
action\_result\.data\.\*\.resistance | string | 
action\_result\.data\.\*\.resourceid | string |  `arcsight case id` 
action\_result\.data\.\*\.securityClassification | string | 
action\_result\.data\.\*\.securityClassificationCode | string | 
action\_result\.data\.\*\.sensitivity | string | 
action\_result\.data\.\*\.stage | string | 
action\_result\.data\.\*\.state | numeric | 
action\_result\.data\.\*\.ticketType | string | 
action\_result\.data\.\*\.type | numeric | 
action\_result\.data\.\*\.typeName | string | 
action\_result\.data\.\*\.vulnerability | string | 
action\_result\.data\.\*\.vulnerabilityType1 | string | 
action\_result\.data\.\*\.vulnerabilityType2 | string | 
action\_result\.status | string | 
action\_result\.summary\.case\_id | string |  `arcsight case id` 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'run query'
Search for a text in resources

Type: **investigate**  
Read only: **True**

This action implements the ArcSight console's search feature\. It searches for the text \(specified in the <b>query</b> parameter\) in the specified resource <b>type</b>\.<br>Multiple search strings can be separated by spaces\. Enclose the string in quotes to search for the exact string containing spaces\. For example, to search for resources containing <i>foo</i> <b>or</b> <i>bar</i>, use <b>foo bar</b>\.<br>To search for the word foo followed by bar and separated by space, use the string <b>"foo bar"</b>\.<br>ArcSight executes searches on the <i>stem</i> of each word\. For example, if the word searched is <i>going</i>, ArcSight will actually search for <i>go</i>\. The same rules apply for quoted phrases\. For example, if the <b>query</b> parameter is <b>"going description"</b>, the actual query executed will be <b>"go descript"</b>\.<br>The action's widget displays the <b>Internal Query String</b> that ArcSight ends up using\. Use this string to verify the text being searched\. Using quotes around the query string makes the search more deterministic\.<br>The Action Run dialog displays a drop\-down list of possible values for the <b>type</b> parameter\. However, playbooks allow a user to specify values other than the one listed in the Action Run dialog\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**type** |  optional  | Resource type | string | 
**query** |  required  | Query Text | string |  `arcsight search string` 
**range** |  optional  | Items range to return \(min\_offset\-max\_offset\) | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.query | string |  `arcsight search string` 
action\_result\.parameter\.range | string | 
action\_result\.parameter\.type | string | 
action\_result\.data\.\*\.elapsed | numeric | 
action\_result\.data\.\*\.hitCount | numeric | 
action\_result\.data\.\*\.rewrittenQueryString | string | 
action\_result\.data\.\*\.searchHits\.\*\.name | string | 
action\_result\.data\.\*\.searchHits\.\*\.score | numeric | 
action\_result\.data\.\*\.searchHits\.\*\.uri | string | 
action\_result\.data\.\*\.searchHits\.\*\.uuid | string |  `arcsight resource id` 
action\_result\.data\.\*\.statusString | string | 
action\_result\.status | string | 
action\_result\.summary\.total\_items | numeric | 
action\_result\.summary\.total\_items\_returned | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 