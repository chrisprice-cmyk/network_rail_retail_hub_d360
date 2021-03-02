#!/bin/bash
#For populating a Sandbox that has been created from an SDO
./scripts/deployment/preDeploymentSteps.sh

echo
echo '**********************************'
echo '* Deploying repository source...'
echo '**********************************'
echo
#Deploy rest of source
sfdx force:source:push -f --wait 60

./scripts/deployment/postDeploymentSteps.sh
