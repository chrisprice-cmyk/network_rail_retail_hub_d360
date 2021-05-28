echo
echo '***************************'
echo 'Loading Production data...'
echo '***************************'
echo

echo '***************************'
echo 'Installing Account data...'
echo '***************************'
echo
#sfdx force:data:bulk:upsert --sobjecttype Account --csvfile data/prod/ido_Account.csv --externalid External_ID__c --wait 2
