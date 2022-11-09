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
Suite Setup       Run keywords
...               Set browser timeout    900 seconds
...               AND    Open test browser    wait=false
...               AND    Go To Lightning Setup Home
Suite Teardown    Close browser

*** Test Cases ***
#
# **NOTES**
#
# Each test should be added to an existing test case or a new test case. These can then be referenced by a task in the cumulusci.yml file.
#
# All Tests have been organised into different products or shared if they are non specific or cross multiple products. Please add new tests to the relevant sections below.
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# SHARED TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------
Check and Enable Contacts to Multiple Accounts
    Enable Contacts to Multiple Accounts

Set Org Wide Email Address
    Set Org Wide Email
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# EINSTEIN TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Run Automation to check and Enable Einstein TCRM
    Enable Einstein Analytics CRM

Run Automation to Check and Enable Einstein Insights
    Go To Campaign Insights Setup Page
    Set Lightning Toggle    on
    Go To Opportunity Insights Setup Page
    Set Lightning Toggle    on
    Go To Account Insights Setup Page
    Set Lightning Toggle    on
    Go To Key Account Insights Setup Page
    Set Lightning Toggle    on

Run Automation to check and enable Campaign Insights
    Go To Campaign Insights Setup Page
    Set Lightning Toggle    on

Check and Enable Prediction Builder
    Enable Einstein Prediction Builder

Check and Enable Einstein Forecasting
    Enable Einstein Forecasting

Check and Enable Oppty Scoring
    Go To Oppty Scoring Setup page

Check and Enable Lead Scoring
    Go To Lead Scoring Setup page

Check and Enable Automated Data Capture
    Enable Automated Data Capture

Check and Enable Call Coaching ECI
    Enable Call Coaching ECI
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# FIELD SERVICE TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Check and Enable Field Service
    Enable Field Service

Check Enable and Update Field Service Permission Sets
    Enable All Field Service Permission Sets

Check and Disable Field Service Integration
    Disable Field Service Integration

Check and Disable Field Service Status Transitions
    Disable Field Service Status Transitions

Create Rider Chat Button
    Create A Chat Button And Automated Invitations    SFS - Rider Bot    SDO_SFS_Rider_Bot

Create Tracker Chat Button
    Create A Chat Button And Automated Invitations    SFS - Tracker Bot    SDO_SFS_Tracker_Bot

Add Case Wrap Up Model
    Enable Einstein Classification
    Add Case Wrap Up Model

Add Case Classification Model
    Enable Einstein Classification
    Create Case Classification Model
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# MARKETING TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Check and Setup Pardot Connected App
    Enable Pardot App

Check and Enable Pardot
    Enable Pardot Setting

Check and Create Pardot Email Template
    Create Pardot Template
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# SALES CLOUD TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Run Automation to Enable Sales Engagement
    Enable Sales Engagement

Run Automation to Check and Enable Forecasts
    Enable Forecasts

Set Guest API Access for Standard Channel Menu
    Set Guest on Channel Menu    SDO_Standard_Channel_Menu

Check and Update Forecast Hiararchy Settings
    Update Forecast Hierarchy Settings

Check and Enable Opportunity Splits
    Enable Opportunity Splits
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# SERVICE CLOUD TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Check and Enable Incident Management
    Enable Incident Management

Check and Enable Case Swarming
    Enable Case Swarming

Create Service Chat Buttons
    Create A Chat Button And Automated Invitations    *Standard Chat Button    SDO_Service_Chat
    Create A Chat Button And Automated Invitations    Service - Sunny Bot    SDO_Service_Sunny_Bot
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# Q BRANCH TOOLING TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Run Automation to check that Q Passport is configured
    Enable Q Passport

Check and Enable Q Tooling
    Enable Q Passport
    Enable Demo Boost
    Enable Demo Wizard
    Enable Data Tool
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# Marketing CLOUD TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Check and Enable Territory Management
    Enable Territory Management
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# Net Zero Cloud TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Check and Enable Net Zero Cloud
    Enable Net Zero
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# VRA TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Check and Create VRA Service Channel
    Create VRA Service Channel
#
# -----------------------------------------------------------------------------------------------------------------------------------------
# Chat Button
# -----------------------------------------------------------------------------------------------------------------------------------------

Chat Buttons and Automated Invitations
    Create Chat Button and Automated Invitations
# -----------------------------------------------------------------------------------------------------------------------------------------
# SCHEDULER TESTS
# -----------------------------------------------------------------------------------------------------------------------------------------

Check and Enable Scheduler Setting
    Enable Scheduler

Check and Create Appointment Assignment Polcies
    Create Appointment Assignment Policies
# -----------------------------------------------------------------------------------------------------------------------------------------
# Survey Setup
# -----------------------------------------------------------------------------------------------------------------------------------------

Set Survey Default Community
    Set Survey Default Community    SDO - Consumer
# -----------------------------------------------------------------------------------------------------------------------------------------
# Service Presence Statuses to Profile
# -----------------------------------------------------------------------------------------------------------------------------------------

Add Service Presence Statuses to Profile
    Add Service Presence Statuses to Profile    System Administrator    All - Available
    Add Service Presence Statuses to Profile    System Administrator    Busy
    Add Service Presence Statuses to Profile    System Administrator    Busy - Break
    Add Service Presence Statuses to Profile    System Administrator    Busy - Lunch
    Add Service Presence Statuses to Profile    System Administrator    Busy - Training
    Add Service Presence Statuses to Profile    System Administrator    Cases - Available
    Add Service Presence Statuses to Profile    System Administrator    Chat - Available
    Add Service Presence Statuses to Profile    System Administrator    Messaging - Available
    Add Service Presence Statuses to Profile    System Administrator    Phone - Available
# -----------------------------------------------------------------------------------------------------------------------------------------
# Validation Counts
# -----------------------------------------------------------------------------------------------------------------------------------------

Validate Data Rows Exist
    Validate Minimal Rowcount    Account 1
    Validate Minimal Rowcount    Account 1    Name!=''
    Validate Maximum Rowcount    Account 300 Name!=''
    Validate Range Rowcount    Account 1    300    Name!=''
    Validate Minimal Rowcount    Contact 1
    Validate Minimal Rowcount    Contact 1    Name!=''
    Validate Exact Rowcount    Product2    52
# -----------------------------------------------------------------------------------------------------------------------------------------
# Chat Agent Configurations
# -----------------------------------------------------------------------------------------------------------------------------------------

Add Profile to Chat Agent Configuration
    Add Profile To Chat Configuration    Chat Representatives    System Administrator
    Add Profile To Chat Configuration    Chat Representatives    SDO-Service
