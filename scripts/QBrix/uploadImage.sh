#!/bin/bash
IMAGE_NAME=$1
FILE_PATH=$2

# the following sets the context as provided by cumulus core task cumulusci.tasks.command.SalesforceCommand
sfdx config:set instanceUrl=$SF_INSTANCE_URL

echo
echo 'Checking if ContentVerion with name '$IMAGE_NAME' exists...'
sfdx force:data:soql:query -q "select ID from ContentVersion where title = '$IMAGE_NAME'" --targetusername $SF_ACCESS_TOKEN --json > ImageQuery.json
jq '.result.records[].Id' ImageQuery.json > ImageQuery.txt

if [ -s ImageQuery.txt ];
then
  echo 'ContentVersion with name '$IMAGE_NAME' already exists, not uploading it again.'
else
  echo 'uploading '$IMAGE_NAME' as a ContentVersion metadata type...'
  sfdx shane:data:file:upload -f $FILE_PATH --targetusername $SF_ACCESS_TOKEN
fi
rm ImageQuery.json
rm ImageQuery.txt
