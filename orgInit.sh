#!/bin/bash

#Deploy settings
#sfdx force:source:deploy -p force-app/main/default/settings/Bot.settings-meta.xml --wait 60 --json

#Deploy rest of source
sfdx force:source:deploy -p force-app --wait 60 --json

#Apply permission sets
#sfdx force:apex:execute -f scripts/apex/applyPermSets.apex --json

# Load IDO Data using Bulk API
#./scripts/bash/loadProdData.sh

#Work around for ContentVersion upload as the Bulk API in sfdx cannot do it
#sfdx force:data:bulk:upsert --sobjecttype ContentVersion --csvfile data/prod/ContentVersion.csv --externalid External_ID__c --wait 2
#./scripts/bash/uploadImages.sh

# Data level fixes
#Line up NBA Icons
#sfdx force:apex:execute -f scripts/apex/applyNBAIcons.apex --json

#Install Packages
#./scripts/bash/installPackages.sh
