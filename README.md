# Q Branch | Industries - IDO Template

This is the master template that all new IDO masters should start from.  It contains a number of best practice and reusable scripts that will help in getting you up to speed with Migrating your IDO master onto an [Automated Build process](https://docs.google.com/presentation/d/1HPtzrf2yQBJeM_iCkfRWizuT-wqlTivY0WbLCl_3SzE/edit?usp=sharing).

# Branching Strategy

   1. Use a master / release / feature branch pipeline model
   2. Follow a prescribed branch naming and tagging convention (described below)
   3. Ensure the appropriate Github Actions and related scripts are contained within your repository

## Branch naming and tagging convention
  1. master/main always works and represents your currently released and live IDO - never commit directly to master/main
  2. Releases: go into a release/"meaningful-branch-name" e.g. release/winter22r1
  3. As soon as you've created a new release branch and before you've commited anything to it, please create a tag such as <branchName-0.01>
  4. Features: go into a feature/"meaningful-branch-name" e.g. feature/hvsUpdates or feature/payeeUseCase or feature/C360SalesPlay
  5. Once you're done work on your feature, create a pull request to merge into a particular release branch.  This will validate and deploy to your TEST org.
  6. Once all work for a release is completed and merged into the appropriate release branch, create a pull request to merge into master/main .  This will validate and merge into your MASTER/PROD org.

## Other repo setup steps for automated validation/deployments
   1. GitHub secrets
      - Test Org Authorisation 
        - sfdx force:org:display --verbose -u <Test Alias>
        - get Sfdx Auth Url
        - put in GitHub Secret: TEST_AUTH_SECRET
      - Prod Org Authorisation 
        - sfdx force:org:display --verbose -u <Prod Alias>
        - get Sfdx Auth Url
        - put in GitHub Secret: PROD_AUTH_SECRET  



# SUGGESTED CONTENT FOR THE README
The following are examples of what should be contained within the README file.  

TL:DR: have all the up to date steps that anyone who would need to perform an SDO Rebase process and get your IDO master up and running on a freshly cut SDO.

The bulk of the SDO Rebase process should be taken care of within the [orgInit.sh](orgInit.sh) file, anything above and beyond what the script takes care of should be documented here (or at the very least provide a link to the most up to date manual SDO Rebase steps)


# EXAMPLE CONTENT

## TH IDO Master Org Setup Steps
* Spin up a new SDO - https://org62.lightning.force.com/lightning/r/Demo_Org__c/a1T300000008OOcEAM/view
* Install other Key Packages
  * [IDO Record Data Marker](https://industry-deployer.herokuapp.com/byoo?template=https://github.com/sfdc-qbranch/IDO-RecordDataMarker)
  * [Getting to know the IDO](https://industry-deployer.herokuapp.com/byoo?template=https://github.com/sfdc-qbranch/IDO-GTK)
* Install via Industry Deployer - https://industry-deployer.herokuapp.com/byoo?template=https://github.com/sfdc-qbranch/IDO-TravelHospitality
* Post Installation Manual Steps:

  * Default Page Layout Assignments
    * Contact
    * Person Account
  * Chatbot Setup
    * Embedded Service Deployment
    * Apply bot to a channel
  * Communities
    * Branding - Logo: #76BDB9
    * Branding - Text: #484B58
    * Login Image:
    * Login Logo:
     * ![Login Logo](data/prod/images/vipcommunity/CommunityLoginLogo.png)
    * Header Image:
    * Header Logo
     * ![Header Logo](data/prod/images/vipcommunity/CommunitiesLogo.png)
  * Update Industry Version Tracker values
  * Add Getting to Know your IDO tab to the Q Branch app

# Manual deployment - Environment setup
The industry deployer takes care of deploying all this via a heroku server with no local setup, however if you wish to install it manually on your local machine, the following items need to be installed/configured:

* SalesforceDX CLI - https://developer.salesforce.com/docs/atlas.en-us.sfdx_setup.meta/sfdx_setup/sfdx_setup_install_cli.htm
* Heroku CLI - https://devcenter.heroku.com/articles/heroku-cli
* SFDX Plug-ins
   * Shane McLaughlan SFDX plugins - https://github.com/mshanemc/shane-sfdx-plugins (command line install: sfdx plugins:install shane-sfdx-plugins)
* In terminal, connect to your target org via SFDX CLI
* In terminal run ./orgInit.sh
