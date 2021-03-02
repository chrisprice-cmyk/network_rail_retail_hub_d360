#!/bin/bash
./scripts/deployment/preDeploymentSteps.sh

echo
echo '**********************************'
echo '* Deploying repository source...'
echo '**********************************'
echo
#Deploy rest of source
sfdx force:source:deploy -p force-app --wait 60

./scripts/deployment/postDeploymentSteps.sh
