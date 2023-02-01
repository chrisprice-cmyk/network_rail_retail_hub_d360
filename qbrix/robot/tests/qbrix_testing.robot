*** Settings ***
Resource            qbrix/robot/QRobot.robot

Suite Setup         Run keywords
...                     Open Q Browser
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
    create_mobile_app_extension
    ...    label=Customer Signature
    ...    type=Flow
    ...    name=Customer Signature
    ...    launch_value=SDO_SFS_SendForCustomerSignature
    ...    object_scope=WorkOrder
    ...    pageReload=True
    create_mobile_app_extension
    ...    label=Complete Work
    ...    type=Flow
    ...    name=CompleteWork
    ...    launch_value=SDO_FSL_Image_Capture_Flow_SDO
    ...    object_scope=WorkOrder
    ...    pageReload=False
    create_mobile_app_extension
    ...    label=Create Quote
    ...    type=iOS
    ...    name=Create Quote
    ...    launch_value=salesforce1://sObject/{!$CPQ_Quote__c}/view
    ...    object_scope=WorkOrder
    ...    pageReload=False
    create_mobile_app_extension
    ...    label=Visual Remote Assistant (iOS)
    ...    type=iOS
    ...    name=Visual Remote Assistant
    ...    launch_value=https://<your SF myDomain>.lightning.force.com/lightning/r/WorkOrder/{!Id}/view
    ...    object_scope=WorkOrder
    ...    pageReload=False
    create_mobile_app_extension
    ...    label=Visual Remote Assistant (Android)
    ...    type=Android
    ...    name=Visual Remote Assistant
    ...    launch_value=https://<your SF myDomain>.lightning.force.com/lightning/n/tspa__Visual_Remote_Assistant_Mobile_Dashboard?c__recordId={!Id}
    ...    object_scope=WorkOrder
    ...    pageReload=False
    create_mobile_app_extension
    ...    label=Create Quote (Android)
    ...    type=Android
    ...    name=Customer Signature
    ...    launch_value=salesforce1://sObject/{!CPQ_Quote__c}/view
    ...    object_scope=WorkOrder
    ...    pageReload=False
    create_mobile_app_extension
    ...    label=En Route
    ...    type=Flow
    ...    name=EnRoute
    ...    launch_value=SDO_FSL_Appointment_Assistant_Simulate_Tech_Location
    ...    object_scope=ServiceAppointment
    ...    pageReload=False
    create_mobile_app_extension
    ...    label=Create Return Order
    ...    type=Flow
    ...    name=CreateReturnOrder
    ...    launch_value=SDO_FSL_RMA_Flow
    ...    object_scope=WorkOrder
    ...    pageReload=False
