#!/bin/bash
echo
echo '**********************************'
echo 'Post-deployment data fixes...'
echo '**********************************'
echo

#Load up booking images
#sfdx force:apex:execute -f scripts/apex/applyBookingImages.apex --json

#Line up NBA Icons
#sfdx force:apex:execute -f scripts/apex/applyNBAIcons.apex --json
