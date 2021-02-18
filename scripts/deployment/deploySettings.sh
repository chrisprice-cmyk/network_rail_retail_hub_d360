#!/bin/bash

sfdx force:source:deploy -p force-app/main/default/settings/Bot.settings-meta.xml --wait 60
sfdx force:source:deploy -p force-app/main/default/settings/AccountInsights.settings-meta.xml --wait 60
sfdx force:source:deploy -p force-app/main/default/settings/ExperienceBundle.settings-meta.xml --wait 60
sfdx force:source:deploy -p force-app/main/default/settings/Industries.settings-meta.xml --wait 60
sfdx force:source:deploy -p force-app/main/default/settings/OpportunityInsights.settings-meta.xml --wait 60
sfdx force:source:deploy -p force-app/main/default/settings/OpportunityScore.settings-meta.xml --wait 60
sfdx force:source:deploy -p force-app/main/default/settings/OrderManagement.settings-meta.xml --wait 60
sfdx force:source:deploy -p force-app/main/default/settings/PardotEinstein.settings-meta.xml --wait 60
sfdx force:source:deploy -p force-app/main/default/settings/SourceTracking.settings-meta.xml --wait 60
