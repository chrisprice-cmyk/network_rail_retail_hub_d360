#!/bin/bash
./scripts/cicd/preDeploymentSteps.sh

#Deploy rest of source
sfdx force:source:deploy -p force-app --wait 60

./scripts/cicd/postDeploymentSteps.sh
