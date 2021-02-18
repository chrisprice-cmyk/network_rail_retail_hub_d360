#!/bin/bash
sfdx force:source:deploy -p lib/IDO-Inclusiveness/force-app --wait 60

sfdx force:source:deploy -p lib/IDO-version-tracker/ido-version --wait 60
