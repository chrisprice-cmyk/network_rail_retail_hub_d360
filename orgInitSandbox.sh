#!/bin/bash

#Deploy settings
./scripts/deployment/deploySettings.sh

sfdx force:source:push --wait 60 -f

./scripts/cicd/postDeploymentSteps.sh
