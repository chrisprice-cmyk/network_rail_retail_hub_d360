#!/bin/bash
echo
echo '**********************************'
echo '* Running pre-deployment steps...'
echo '**********************************'
echo

mkdir -p deltaDestructiveDeploySource

./scripts/deployment/preDeploymentPermissionSets.sh

./scripts/deployment/deploySettings.sh

./scripts/bash/installSubmodules.sh

./scripts/bash/installPackages.sh

./scripts/bash/uploadImages.sh

./scripts/bash/createPreDeploymentUsers.sh
