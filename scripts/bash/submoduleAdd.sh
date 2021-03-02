#!/bin/bash

#exit script if any of the commands returns a non-zero exit code
set -e

subModRootDir="lib"
echo
read -p 'Git Repo URL: ' subModUrl
subModName=${subModUrl##*/}
subModPath=$subModRootDir'/'$subModName

echo
echo '********************************'
echo 'Adding '$subModName' to local path '$subModPath' from Git repo at: '$subModUrl
echo '********************************'
echo

mkdir -p $subModRootDir
echo 'Adding submodule.....'
git submodule add $subModUrl $subModPath --force
echo 'Initialising submodule.....'
git submodule init
echo 'Cloning submodule.....'
git submodule update
