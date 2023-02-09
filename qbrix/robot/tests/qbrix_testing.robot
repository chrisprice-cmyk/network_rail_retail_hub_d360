*** Settings ***
Resource            qbrix/robot/QRobot.robot

Suite Setup         Run keyword    Open Q Browser    record_video=False
Suite Teardown      QRobot.Close Browser


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
    #download_cms_content    Professional Site
    download_cms_content    Product Listing Content
    download_cms_content    Community Cloud Resources
    download_cms_content    Corporate Blog
    download_cms_content    Shared Marketing Content
    download_cms_content    Partner Central
    download_cms_content    B2B Commerce Content
    download_cms_content    Consumer Community
