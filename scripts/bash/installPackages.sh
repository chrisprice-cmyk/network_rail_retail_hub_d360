#!/bin/bash

#make a list of packages already installed in the target org
sfdx force:package:installed:list --json > installedPackages.json
jq '.result[].SubscriberPackageVersionId' installedPackages.json > installedPackageIds.txt

#look through the list of installed package IDs to see if the package is already installed and install if it is not there
if grep -q 04t0o000003TgdsAAC installedPackageIds.txt
then
  echo 'Package 04t0o000003TgdsAAC already installed in target org'
else
  echo 'Installing IDO Version Tracker package '
  sfdx force:package:install --package 04t0o000003TgdsAAC --wait 60
fi

rm installedPackages.json
rm installedPackageIds.txt
