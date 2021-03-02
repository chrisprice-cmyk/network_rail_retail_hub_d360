#!/bin/bash
#Assumes you've already checked out the branch
# and fetched all the tags for the entire repo

# find the hash of the most recent tag
TAG_NAME=$(git describe --tags --abbrev=0)
TAG_HASH=$(git show-ref -s $TAG_NAME)
echo 'Using Tag: ' $TAG_NAME ' with Hash: ' $TAG_HASH
echo

# branch being merged into is passed in a parameter 1
BASE_BRANCH='origin/'$1
echo 'Merging into Base branch: '$BASE_BRANCH' '
echo


echo 'These are the deleted files:'
git --no-pager diff $TAG_HASH HEAD --name-only --diff-filter=D

# TODO - if there are no deleted files, skip over the rest
#https://stackoverflow.com/questions/12137431/test-if-a-command-outputs-an-empty-string
  #if [[ $(ls -A) ]]; then
  #    echo "there are files"
  #else
  #    echo "no files found"
  #fi

#push the list of deleted deltas into a text file for debugging purposes
git --no-pager diff $TAG_HASH HEAD --name-only --diff-filter=D > deleted-files.txt

if [ -s deleted-files.txt ]; then
  echo 'Create zip file gitDeletions.zip with only deleted files'
  echo
  git archive -o gitDeletions.zip $BASE_BRANCH $(git --no-pager diff $TAG_HASH HEAD --name-only --diff-filter=D)

#  echo 'Add sfdx-project.json to archive'
#  zip -r gitDeletions.zip sfdx-project.json

  echo 'remove and recreate existing delta folders'
  echo
  rm -rf deltaDestructiveDeploySource
  mkdir -p deltaDestructiveDeploySource

  rm -rf deltaDestructiveDeployMeta
  mkdir -p deltaDestructiveDeployMeta

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
    echo 'No destructive metadata changes, delete zip file so workflow process does not run'
    rm gitDeletions.zip
  fi
else
  echo "There were no deleted files between the last tag and now"
fi
