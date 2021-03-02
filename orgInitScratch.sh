#!/bin/bash
#For populating a blank scratch org.  Will need to take care of loading SDO dependencies as well

#Deploy SDO Dependencies
./scripts/deployment/installSDODependencies.sh

./scripts/cicd/preDeploymentSteps.sh

echo
echo '**********************************'
echo '* Deploying repository source...'
echo '**********************************'
echo
#Deploy rest of source
sfdx force:source:push -f --wait 60

./scripts/cicd/postDeploymentSteps.sh
