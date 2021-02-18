#!/bin/bash
#Deploy Default Pagelayout assignments
sfdx force:mdapi:deploy -d mdapiDeployments/pagelayoutAssignments --wait 20

./scripts/bash/createUsers.sh

#Apply permission sets
sfdx force:apex:execute -f scripts/apex/applyPermSets.apex --json

# Load IDO Data using Bulk API
./scripts/bash/loadProdData.sh

# Data level fixes
#Load up booking images
sfdx force:apex:execute -f scripts/apex/applyBookingImages.apex --json

#Line up NBA Icons
sfdx force:apex:execute -f scripts/apex/applyNBAIcons.apex --json

rm -rf deltaDestructiveDeploySource
