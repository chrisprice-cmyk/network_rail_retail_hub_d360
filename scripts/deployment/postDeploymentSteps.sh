#!/bin/bash
echo
echo '**********************************'
echo '* Running post-deployment steps...'
echo '**********************************'
echo

./scripts/bash/postDeploymentMDAPI.sh $@

#Deploy Default Pagelayout assignments
./scripts/deployment/deployPagelayoutAssignments.sh $@

#Apply permission sets
./scripts/deployment/postDeploymentPermissionSets.sh $@

#Create any required Users
./scripts/bash/createUsers.sh $@

# Load IDO Data using Bulk API
./scripts/bash/loadProdData.sh $@

#Load Analytics Datasets
./scripts/deployment/loadAnalyticsDatasets.sh $@

# Data level fixes
./scripts/deployment/runDataFixes.sh $@

rm -rf deltaDestructiveDeploySource
