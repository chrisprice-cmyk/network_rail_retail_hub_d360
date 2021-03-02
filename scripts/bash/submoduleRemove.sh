#!/bin/bash

#exit script if any of the commands returns a non-zero exit code
set -e

subModRootDir="lib"
echo
read -p 'Git Module Name: ' subModName

subModPath=$subModRootDir'/'$subModName

git submodule deinit -f $subModPath
git rm -f $subModPath
rm -rf .git/modules/$subModPath
