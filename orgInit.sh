#!/bin/bash

#Deploy settings
sfdx force:source:deploy -p ido-tth/main/default/settings/Bot.settings-meta.xml --wait 60 --json

#Deploy rest of source
sfdx force:source:deploy -p ido-tth --wait 60 --json

#Apply permission sets
sfdx force:apex:execute -f scripts/apex/applyPermSets.apex --json

# Load IDO Data using Bulk API
#Person Account
sfdx force:data:bulk:upsert --sobjecttype Account --csvfile data/prod/PersonAccounts.csv --externalid External_ID__c --wait 30

#Account
sfdx force:data:bulk:upsert --sobjecttype Account --csvfile data/prod/tth_Account.csv --externalid External_ID__c --wait 30

#Contact
sfdx force:data:bulk:upsert --sobjecttype Contact --csvfile data/prod/tth_Contact.csv --externalid External_ID__c --wait 30

#Case
sfdx force:data:bulk:upsert --sobjecttype Case --csvfile data/prod/tth_Case.csv --externalid External_ID__c --wait 30

#Campaign
sfdx force:data:bulk:upsert --sobjecttype Campaign --csvfile data/prod/tth_Campaign.csv --externalid External_ID__c --wait 30

#Trip
sfdx force:data:bulk:upsert --sobjecttype tth_Trip__c --csvfile data/prod/tth_Trips__c.csv --externalid External_ID__c --wait 30

#Booking
sfdx force:data:bulk:upsert --sobjecttype tth_Booking__c --csvfile data/prod/tth_Bookings__c.csv --externalid External_ID__c --wait 30

#Loyalty Event
sfdx force:data:bulk:upsert --sobjecttype tth_Loyalty_Event__c --csvfile data/prod/tth_Loyalty__c.csv --externalid External_ID__c --wait 30

#Party
sfdx force:data:bulk:upsert --sobjecttype tth_Party__c --csvfile data/prod/tth_Party__c.csv --externalid External_ID__c --wait 30

#Baggage
sfdx force:data:bulk:upsert --sobjecttype tth_Baggage__c --csvfile data/prod/tth_Baggage__c.csv --externalid External_ID__c --wait 30
#Custom Activity
sfdx force:data:bulk:upsert --sobjecttype Custom_Activity__c --csvfile data/prod/tth_Custom_Activities__c.csv --externalid External_ID__c --wait 30

#REcommendation
sfdx force:data:bulk:upsert --sobjecttype Recommendation --csvfile data/prod/recommendations.csv --externalid External_ID__c --wait 30

#Suggested Booking
sfdx force:data:bulk:upsert --sobjecttype tth_Suggested_Booking__c --csvfile data/prod/tth_Suggested_Booking__c.csv --externalid External_ID__c --wait 30

#Users  - not needed for sandboxes....
sfdx force:data:bulk:upsert --sobjecttype User --csvfile data/prod/User.csv --externalid External_ID__c --wait 30

#Helen's first trip
sfdx force:data:bulk:upsert --sobjecttype Account --csvfile data/prod/HelensTrip.csv --externalid External_ID__c --wait 30


# -------------- DONE TO HERE ---------------

#Content Version - not needed for Sandboxes either...
#Needs fixing as bulk API doesn't like the way it is right now....
#sfdx force:data:bulk:upsert --sobjecttype ContentVersion --csvfile data/prod/ContentVersion.csv --externalid External_ID__c --wait 2
sfdx shane:data:file:upload -f data/prod/images/Bathroom1.jpg
sfdx shane:data:file:upload -f data/prod/images/BusinessSeat1.jpg
sfdx shane:data:file:upload -f data/prod/images/BusinessSeat2.jpg
sfdx shane:data:file:upload -f data/prod/images/BusinessSeat3.jpg
sfdx shane:data:file:upload -f data/prod/images/EconomySeat1.jpg
sfdx shane:data:file:upload -f data/prod/images/EconomySeat2.jpg
sfdx shane:data:file:upload -f data/prod/images/EconomySeat3.jpg
sfdx shane:data:file:upload -f data/prod/images/EconomySeat4.jpg
sfdx shane:data:file:upload -f data/prod/images/Gym1.jpg
sfdx shane:data:file:upload -f data/prod/images/Pool1.jpg
sfdx shane:data:file:upload -f data/prod/images/Room1.jpg
sfdx shane:data:file:upload -f data/prod/images/Room2.jpg
sfdx shane:data:file:upload -f data/prod/images/Room3.jpg


# Data level fixes
#Load up booking images
sfdx force:apex:execute -f scripts/apex/applyBookingImages.apex --json

#Line up NBA Icons
sfdx force:apex:execute -f scripts/apex/applyNBAIcons.apex --json

#Install IDO Version Tracker
sfdx force:package:install --package "04t0o000003TgdsAAC" --wait 60 --apexcompile package --securitytype AllUsers

#sfdx shane:theme:activate -n THDark --json
