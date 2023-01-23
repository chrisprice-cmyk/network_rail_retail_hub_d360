*** Settings ***
Resource          cumulusci/robotframework/SalesforcePlaywright.robot
Library           qbrix/robot/QbrixSharedKeywords.py
Library           qbrix/robot/QbrixEinsteinKeywords.py
Library           qbrix/robot/QbrixServiceKeywords.py
Library           qbrix/robot/QbrixToolingKeywords.py

Suite Setup         Run keywords
...                     Open test browser    wait=false
...                     AND    Set browser timeout    900 seconds
...                     AND    Go To Lightning Setup Home
Suite Teardown      Close browser

*** Test Cases ***
#
# **TESTING NOTES**
#
# This is a test only robot file. Replace the keywords under Run Automation to test the task(s) you want to test.
#
# It is best to test them directly from terminal by running cci task run robot --org OrgAliasHere --suites qbrix/robot/tests/qbrix_testing.robot
#
# The above will allow you to see what the robot is doing and also generate a log of what is happening. See the output.xml file afterwards to help diagnose issues.
#
# Note: The default timeout for this is 900 seconds but if you have a long running process, ensure you change the value above next to "Set browser timeout" to something more suitable for the overall timeout for everything you are running.
#
Run Automation
    enable_data_tool

