#!/bin/bash
IMAGE_NAME=$1
FILE_PATH=$2

echo
echo 'Checking if ContentVerion with name '$IMAGE_NAME' exists...'
sfdx force:data:soql:query -q "select ID from ContentVersion where title = '$IMAGE_NAME'" --json > ImageQuery.json
jq '.result.records[].Id' ImageQuery.json > ImageQuery.txt

if [ -s ImageQuery.txt ];
then
  echo 'ContentVersion with name '$IMAGE_NAME' already exists, not uploading it again.'
else
  echo 'uploading '$IMAGE_NAME' as a ContentVersion metadata type...'
  sfdx shane:data:file:upload -f $FILE_PATH
fi
rm ImageQuery.json
rm ImageQuery.txt
