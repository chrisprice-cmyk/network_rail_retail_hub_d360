#!/bin/bash
echo
echo '**********************************'
echo '* Running pre-deployment steps...'
echo '**********************************'
echo

mkdir -p deltaDestructiveDeploySource

./scripts/deployment/preDeploymentPermissionSets.sh $@

./scripts/deployment/deploySettings.sh $@

./scripts/bash/installPackages.sh $@

if [[ " $@ " =~ " --skipSubmodules " ]]; then
   echo "skipping installation of subModules"
 else
   ./scripts/bash/installSubmodules.sh $@
fi

./scripts/bash/uploadImages.sh $@

./scripts/bash/createPreDeploymentUsers.sh $@

./scripts/bash/createCommunities.sh $@
