#!/bin/bash
PACKAGE_ID=$1

#make a list of packages already installed in the target org
sfdx force:package:installed:list --json > installedPackages.json
jq '.result[].SubscriberPackageVersionId' installedPackages.json > installedPackageIds.txt

#look through the list of installed package IDs to see if the package is already installed and install if it is not there
if grep -q $PACKAGE_ID installedPackageIds.txt
then
  echo 'Package '$PACKAGE_ID' already installed in target org'
else
  echo 'Installing package ' $PACKAGE_ID
  sfdx force:package:install --package $PACKAGE_ID --noprompt --wait 60
fi

rm installedPackages.json
rm installedPackageIds.txt
