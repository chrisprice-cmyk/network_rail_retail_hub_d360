#!/bin/bash
IMAGE_NAME=$1
FILE_PATH=$2


sfdx force:data:soql:query -q "select ID from ContentVersion where title = '$IMAGE_NAME'" > ImageQuery.txt
if grep -q "no results" ImageQuery.txt
then
  echo 'uploading '$IMAGE_NAME' image'
  sfdx shane:data:file:upload -f $FILE_PATH
fi
rm ImageQuery.txt
