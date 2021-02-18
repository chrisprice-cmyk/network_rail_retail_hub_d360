#!/bin/bash
echo 'Running pre-deployment CICD steps'

mkdir -p deltaDestructiveDeploySource

echo 'Deploying settings...'
./scripts/deployment/deploySettings.sh

echo 'Installing SubModules...'
./scripts/bash/installSubmodules.sh

echo 'Installing AppExchange Packages...'
./scripts/bash/installPackages.sh
