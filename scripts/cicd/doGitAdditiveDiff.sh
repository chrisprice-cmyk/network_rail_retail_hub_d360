#!/bin/bash
# Assumes you've already checked out the branch
# Does a diff between current head and last push
# we're using a squash merge so this should be fine to deploy only differences between pushes
echo 'Input parameters: '$@

FROM_REF=$1
TO_REF=$2

echo 'From reference SHA: '$FROM_REF' '
echo 'To reference SHA: '$TO_REF' '

echo 'These are the new and modified files: '
echo
git --no-pager diff $FROM_REF $TO_REF --name-only --diff-filter=ACM

#push the list of deltas into a text file for debugging purposes
git --no-pager diff $FROM_REF $TO_REF --name-only --diff-filter=ACM > new-modified-files.txt

echo
echo 'Create zip file gitUpdates.zip with new and modified files'
echo
git archive -o gitUpdates.zip $TO_REF $(git --no-pager diff $FROM_REF $TO_REF --name-only --diff-filter=ACM)

echo
echo 'remove existing deltaDeploy folder'
echo
rm -rf deltaDeploy
mkdir deltaDeploy

echo 'Unzip the delta zip file into the deltaDeploy folder'
echo
unzip gitUpdates.zip -d deltaDeploy

# TODO - if there are no modified files, skip over this
#https://stackoverflow.com/questions/12137431/test-if-a-command-outputs-an-empty-string
  if [ $(ls -A deltaDeploy/force-app) ]; then
      echo
      echo "there ARE new/modified metadata files"
  else
      echo
      echo "the are NO new/modified metadata files found"
      rm gitUpdates.zip
      rm new-modified-files.txt
  fi

  echo
