echo
echo '***************************'
echo 'Loading Production data...'
echo '***************************'
echo

echo '***************************'
echo 'Installing Person Account data...'
echo '***************************'
echo
sfdx force:data:bulk:upsert --sobjecttype Account --csvfile data/prod/PersonAccounts.csv --externalid External_ID__c --wait 2
