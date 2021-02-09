#!/bin/bash

#Apply permission sets
sfdx force:apex:execute -f scripts/apex/applyPermSets.apex --json

./scripts/bash/createUsers.sh

# Load IDO Data using Bulk API
./scripts/bash/loadProdData.sh
