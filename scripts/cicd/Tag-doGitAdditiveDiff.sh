#!/bin/bash
# Assumes you've already checked out the branch
# and fetched all the tags for the entire repo

# find the hash of the most recent tag
TAG_NAME=$(git describe --tags --abbrev=0)
TAG_HASH=$(git show-ref -s $TAG_NAME)
echo 'Using Tag: ' $TAG_NAME ' with Hash: ' $TAG_HASH
echo


echo 'These are the new and modified files: '
echo
git --no-pager diff $TAG_HASH HEAD --name-only --diff-filter=ACM

# TODO - if there are no modified files, skip over this
#https://stackoverflow.com/questions/12137431/test-if-a-command-outputs-an-empty-string
  #if [[ $(ls -A) ]]; then
  #    echo "there are files"
  #else
  #    echo "no files found"
  #fi

#push the list of deltas into a text file for debugging purposes
git --no-pager diff $TAG_HASH HEAD --name-only --diff-filter=ACM > new-modified-files.txt

echo 'Create zip file gitUpdates.zip with new and modified files'
echo
git archive -o gitUpdates.zip HEAD $(git --no-pager diff $TAG_HASH HEAD --name-only --diff-filter=ACM)

echo 'remove existing deltaDeploy folder'
echo
rm -rf deltaDeploy
mkdir deltaDeploy

echo 'Unzip the delta zip file into the deltaDeploy folder'
echo
unzip gitUpdates.zip -d deltaDeploy

# if there are no modified metadata files, delete the zip file so the workflow process does not run
  if [ $(ls -A deltaDeploy/force-app) ]; then
      echo
      echo "there ARE new/modified metadata files"
  else
      echo
      echo "the are NO new/modified metadata files found"
      rm gitUpdates.zip
      rm new-modified-files.txt
  fi
