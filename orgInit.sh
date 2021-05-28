#!/bin/bash
# DO NOT EDIT THIS UNLESS YOU REALLY KNOW WHAT YOU ARE DOING
# CHANGES HERE WILL IMPACT THE AUTOMATED CI/CD PROCESS
# AN EXPLANATION OF HOW THE SCRIPTS WORK CAN BE FOUND HERE: https://salesforce.quip.com/IiB7AoUkpgi8

./scripts/deployment/preDeploymentSteps.sh --skipSubmodules

echo
echo '**********************************'
echo '* Deploying repository source...'
echo '**********************************'
echo
#Deploy rest of source
sfdx force:source:push -f --wait 60

./scripts/deployment/postDeploymentSteps.sh
