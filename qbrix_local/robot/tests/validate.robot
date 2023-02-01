*** Settings ***
Resource            qbrix/robot/QRobot.robot

Suite Setup         Run keywords
...                     Open Q Browser
Suite Teardown      QRobot.Close Browser


*** Test Cases ***
Validate Qbrix
    Validate Minimal Rowcount
    ...    Organization
    ...    1
    ...    continueonfail=True
    ...    datatag=Simple Query validation of the Organization Object
    #Validate With Testim    Validate_Hello_Login
