*** Settings ***
Resource          cumulusci/robotframework/SalesforcePlaywright.robot
Library           qbrix/robot/QbrixSharedKeywords.py
Library           qbrix/robot/QbrixEinsteinKeywords.py
Library           qbrix/robot/QbrixFieldServiceKeywords.py
Library           qbrix/robot/QbrixMarketingKeywords.py
Library           qbrix/robot/QbrixNetZeroKeywords.py
Library           qbrix/robot/QbrixSalesCloudKeywords.py
Library           qbrix/robot/QbrixSchedulerKeywords.py
Library           qbrix/robot/QbrixSurveysKeywords.py
Library           qbrix/robot/QbrixVraKeywords.py
Library           qbrix/robot/QbrixServiceKeywords.py
Library           qbrix/robot/QbrixToolingKeywords.py
Library           qbrix/robot/QbrixValidationKeywords.py
Suite Setup       Run keywords
...               Set browser timeout    900 seconds
...               AND    Open test browser    wait=false
...               AND    Go To Lightning Setup Home
Suite Teardown    Close browser

*** Test Cases ***
Validate Qbrix
   Validate Minimal Rowcount  Organization  1  continueonfail=True  datatag=Simple Query validation of the Organization Object
   #Validate With Testim  Validate_Hello_Login