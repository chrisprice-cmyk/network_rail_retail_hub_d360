#!/bin/bash
SUITE_NAME=$1

# the following sets the context as provided by cumulus core task cumulusci.tasks.command.SalesforceCommand
sfdx config:set instanceUrl=$SF_INSTANCE_URL
LOGIN_URL=$SF_INSTANCE_URL'/secur/frontdoor.jsp?sid='$SF_ACCESS_TOKEN

echo '********* Running TESTIM script: '$SCRIPT_NAME
echo '********* Base URL: '$LOGIN_URL

testim --token "$TESTIM_KEY" --project "$TESTIM_PROJECT" --grid "Testim-Grid" --suite "$SUITE_NAME" --base-url $LOGIN_URL
