# -------------------------------------------------------------------------------------------------------------------------------#
#
#   Description:    Validate the Qbrix installation in target environment. Note this is designed to be run with a Salesforce Org
#
# -------------------------------------------------------------------------------------------------------------------------------#

*** Settings ***
Resource            qx/qrobot/keywords/QRobot.resource
Suite Setup         QRobot.Open Q Browser
Suite Teardown      QRobot.Close Q Browser
Documentation       Validate the Qbrix installation

*** Test Cases ***
Validate Qbrix

    # Basic Validation Test Example to ensure org connection is working
    Validate Minimal Rowcount
    ...    Organization
    ...    1
    ...    continueonfail=True
    ...    datatag=Simple Query validation of the Organization Object
