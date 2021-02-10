#!/bin/bash
echo 'Running post-deployment CICD steps...'

#Apply permission sets
#sfdx force:apex:execute -f scripts/apex/applyPermSets.apex --json

#Create Users
#./scripts/bash/createUsers.sh

# Load IDO Data using Bulk API
#./scripts/bash/loadProdData.sh
