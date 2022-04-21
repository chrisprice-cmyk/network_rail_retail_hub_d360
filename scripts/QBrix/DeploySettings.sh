#!/bin/bash

if [ -d "force-app/main/default/settings" ] 
then
    echo "Deploying Settings to $SF_INSTANCE_URL"
    sfdx config:set instanceUrl=$SF_INSTANCE_URL
    sfdx force:source:deploy -p force-app/main/default/settings --targetusername $SF_ACCESS_TOKEN
    sfdx config:unset instanceUrl
else
    echo "No Settings Found. Skipping."
fi
exit 0
