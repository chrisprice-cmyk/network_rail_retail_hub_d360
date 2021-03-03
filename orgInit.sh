#!/bin/bash
./scripts/deployment/preDeploymentSteps.sh --skipSubmodules

echo
echo '**********************************'
echo '* Deploying repository source...'
echo '**********************************'
echo
#Deploy rest of source
sfdx force:source:push -f --wait 60

./scripts/deployment/postDeploymentSteps.sh
