#!/bin/bash
#Assumes you've already checked out the branch
# Does a diff between current head and last push
# we're using a squash merge so this should be fine to beploy only differences between pushes
echo 'These are the deleted files:'
git --no-pager diff HEAD^ HEAD --name-only --diff-filter=D


#push the list of deleted deltas into a text file for debugging purposes
git --no-pager diff HEAD^ HEAD --name-only --diff-filter=D > deleted-files.txt

if [ -s deleted-files.txt ]; then
  echo 'Create zip file gitDeletions.zip with only deleted files'
  echo

  git archive -o gitDeletions.zip HEAD^ $(git --no-pager diff HEAD^ HEAD --name-only --diff-filter=D)

  echo 'Add sfdx-project.json to archive'
  zip -r gitDeletions.zip sfdx-project.json

  echo 'remove and recreate existing delta folders'
  echo
  rm -rf deltaDestructiveDeploySource
  mkdir deltaDestructiveDeploySource

  rm -rf deltaDestructiveDeployMeta
  mkdir deltaDestructiveDeployMeta

  echo 'Unzip the delta zip file into the deltaDestructiveDeploySource folder'
  echo
  unzip gitDeletions.zip -d deltaDestructiveDeploySource

  if [ -d "deltaDestructiveDeploySource/force-app" ]; then

    echo 'Convert source format destructive changes into MDAPI format'
    echo
    sfdx force:source:convert -r deltaDestructiveDeploySource/force-app -d deltaDestructiveDeployMeta

    echo 'Rename converted package.xml to destructiveChanges.xml'
    echo
    cp deltaDestructiveDeployMeta/package.xml deltaDestructiveDeployMeta/destructiveChanges.xml

  else
    echo 'No destructive changes, delete zip file so workflow process does not run'
    rm gitDeletions.zip
  fi
else
  echo 'There have been no deleted files since last commit'
fi
