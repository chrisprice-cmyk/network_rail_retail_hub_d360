---
trigger: model_decision
description: This rule should be considered when making changes to the brix project.
globs:
---

## File Structure Conventions

### Core Directories

- `force-app/main/default/` - Main Salesforce metadata
  - `aura/` - Aura components
  - `lwc/` - Lightning Web Components
  - `wave/` - Wave analytics dashboards
- `qbrix/` - QBrix-specific configurations and tools
- `qbrix_local/` - Local QBrix development files and robot files
- `datasets/` - Data files for deployment
- `unpackaged/` - Unmanaged package metadata
- `orgs/` - Organization configuration files. The main scratch org template is `orgs/dev.json` which is used for both dev and qa scratch orgs.

### Configuration Files

- `cumulusci.yml` - Main deployment configuration (master version for API version)
- `sfdx-project.json` - Salesforce DX project configuration

**Note**: API versions between `cumulusci.yml` and `sfdx-project.json` must be the same. The `cumulusci.yml` is the master version.

### Project Configuration

- Update QBrix owner information in `cumulusci.yml`
- Set proper QBrix description and documentation URLs
- Configure dependencies and sources as needed
- Brix sources should be located in GitHub at a location under https://github.com/sfdc-qbranch-emu/
- `source_dependencies` flow is the main location where sources are actually deployed. They should default have the when clause `when: not org_config.is_qbrix_installed('RepoURLHere')`
- The repo URL for the brix can be found in the `cumulusci.yml` file under `project > git > repo_url`
- `project > name` and `project > package > name` should be the same. They should be the end of the repo URL for the brix
- New brix projects need to have the setup task run: `cci task run setup_qbrix`

## Coding Standards

### Brix Development

- Flows can have steps which support all CumulusCI tasks. Reference documentation: https://cumulusci.readthedocs.io/en/latest/cumulusci_tasks.html
- Example code snippets can be found in `.vscode/brix.code-snippets`
- Steps within a flow can use when statements, defined with a `when` key and then the clause which defines if the step should run
- Up-to-date options can be found by running `cci task info orgconfig_hydrate` and reading the output

### When Clause Support

When clauses are only supported if the task called `orgconfig_hydrate` has been defined within an earlier step within the same flow.

**Available Options** (Note: You can add NOT in front of any of these and use joining words like AND or OR):

- `max_org_api_version`: Returns current Salesforce Target Org API Version
  - Example: `where: org_config.max_org_api_version >= 58.0`
- `is_qbrix_installed`: Returns True if the target org has the demo brix installed
  - Example: `where: org_config.is_qbrix_installed('DemoBrixNameHere')`
- `is_object_in_org`: Returns True if the sObject API name is present within the target org
  - Example: `where: org_config.is_object_in_org('ObjectAPINameHere')`
- `is_psl_in_org`: Returns True if the provided PSL is present in the target org
  - Example: `where: org_config.is_psl_in_org('PSLAPINameHere')`
- `is_ps_in_org`: Returns True if the provided Permission Set is present within the target Org
  - Example: `where: org_config.is_ps_in_org('PermissionSetApiNameHere')`
- `is_namespace_installed`: Returns True if the provided namespace is present within the target org
  - Example: `where: org_config.is_namespace_installed('NamespaceHere')`
- `is_package_installed`: Returns True if the provided package is present within the target org
  - Example: `where: org_config.is_package_installed('PackageNameHere')`
- `is_psl_minimal_qty_available_in_org`: Returns True if the provided required amount of licenses is available within the target org for a given PSL
  - Example: `where: org_config.is_psl_minimal_qty_available_in_org('PSLNameHere', AmountRequiredHere)`
- `is_data_present`: Returns True if the provided data is present within the target org
  - Example: `where: org_config.is_data_present('sObjectApiNameHere', 'Filter Here')`
- `is_scratch_org`: Returns True if target org is a scratch org
  - Example: `where: org_config.is_scratch_org`

### Required Inputs

Brix can support input parameters which we call required inputs. These are defined within `/qbrix_local/inputs/required.json`, within the parameters key.

**Example Parameter:**

```json
{
  "parameters": [
    {
      "friendly_name": "Marketing Cloud ID",
      "name": "mc_mid",
      "default": "",
      "description": "The MID for the Business Unit which we want to deploy to"
    }
  ]
}
```

### Salesforce Development

- Use API version defined in `cumulusci.yml` file for all metadata
- Follow Salesforce Lightning Design System (SLDS) patterns
- Implement proper error handling in Apex classes
- Use bulk patterns for data operations
- Follow naming conventions: PascalCase for classes, camelCase for methods
- Only deploy settings which need to be set or unset in the org. Settings files can contain multiple other settings but ideally you would slim these down to just the ones which are needed for the solution within the brix.

### Lightning Web Components (LWC)

- Use ES6+ syntax
- Implement proper lifecycle hooks
- Follow LWC best practices for data binding
- Use @api decorators for public properties
- Implement proper error boundaries

### Aura Components

- Use component events for communication
- Implement proper attribute types
- Follow Aura component lifecycle patterns

### JavaScript/TypeScript

- Use ES6+ features
- Implement proper async/await patterns
- Follow consistent naming conventions
- Use TypeScript for better type safety where applicable

## Development Workflow

### Pre-commit Hooks

- Code formatting with Prettier
- Linting with ESLint for LWC and Aura
- Automatic formatting on save

### Testing

- Unit tests for LWC components using Jest
- E2E tests using Playwright
- Robot Framework tests for validation

### Deployment

- Use CumulusCI flows for deployment
- Follow the three-stage deployment process:
  1. Pre-deployment (`prepare_org`, `source_dependencies`)
  2. Main deployment (`deploy_qbrix` - deploys `force-app/main/default`)
  3. Post-deployment (`post_qbrix_deploy`)
- Main entry point for deployment to org is `deploy_qbrix` flow, which runs `prepare_org`, `source_dependencies`, `deploy` (task) and then `post_qbrix_deploy` in that order
- Use VSCode build tasks where possible. Tasks are found in `.vscode/tasks.json`

### General

- Write self-documenting code with clear variable names
- Add comments for complex business logic
- Follow DRY (Don't Repeat Yourself) principles
- Implement proper error handling
- Always update API version via deployment to a Salesforce org, then update the API version in the `cumulusci.yml` and `sfdx-project.json`, then retrieve the project. Apex, Aura and LWC components can have API versions updated within the XML source files before deployment and don't need to follow the same process, however they still need to be test deployed to a qa org

### Performance

- Use bulk patterns for data operations
- Implement proper SOQL query optimization
- Use platform events for asynchronous processing
- Follow governor limit best practices

### Troubleshooting

- Check CumulusCI logs for deployment issues
- Use Salesforce debug logs for runtime issues
- Validate org configurations before deployment. If using a scratch org, then `orgs/dev.json` is where this is defined
- Deployment errors should be reviewed and then changes made before test deploying again
- Often running the qx metadata doctor can solve many common issues. This is done by running `qx utils doctor`
- If the user is having issues with qx or their configuration, run the `qx update` command and then run the `qx setup vscode` command which should resolve the majority of issues with configuration

## Local Testing and Development with Salesforce Orgs

### Org Setup and Naming Conventions

- We build in a 'dev' org, when created this will have an auto-updated alias which will start with `dev_` and then be a compressed version of the name of the project
- If the project name contains `-SDO-` an SDO is the best org to use as a dev and qa org. To create these quickly you can run the command `qa org pool --sdo --org dev` (--org dev for development org, --org qa for test/qa org)
- If the project name contains `-xdo-` a CDO or Scratch org is the best org to use as a dev and qa org. To create these quickly you can run the command `qa org pool --cdo --org dev` (--org dev for development org, --org qa for test/qa org) for a CDO (aka Clean Demo Org) or `qa org create --org dev` to create a scratch org. Remember that the scratch org will use the `orgs/dev.json` file as the scratch org definition file
- Changes should be retrieved from the dev org and test deployed to the qa org

### Org Connections

**To check if a project has a target org connected, run:** `sf config get target-org`

- If an org is connected, you'll see output with the org name and "Success: true"
- If no org is connected, the command will return no results or an error
- **Note**: If an org is already connected, check with the end user about which alias you should use for the task or command you want to run

**If no Salesforce org is currently connected and deployment testing is needed:**

1. **Determine Org Type Based on Project Name:**

   - If project name contains `-xdo-`: Use CDO (Clean Demo Org) for testing
   - If project name contains `-sdo-`: Use SDO (Salesforce Demo Org) for testing
   - For other org types where `-xdo-` and `-sdo-` are not present in the project name (found in the `cumulusci.yml` file under `project > name`), request an alias from the user for the org you are creating (i.e. dev or qa) and then run `qx org pool --org AliasHere` with the alias provided. Read the returned table of results which are the different org types they can create and request which one they want, the list should be generated from the 2nd column of the results table

2. **Create QA Org for Testing:**

   - For xDO projects: `qa org pool --cdo --org qa`
   - For SDO projects: `qa org pool --sdo --org qa`

3. **API Version Updates:**

   - When API version updates are needed, always test deploy to a QA org first
   - Use the appropriate org type based on project naming convention
   - After successful deployment, update API version in `cumulusci.yml` and `sfdx-project.json` to the given version (e.g., 63.0)
   - Retrieve the updated project metadata by running: `sf project retrieve start --source-dir force-app --target-org OrgAliasGoesHere` (replace `OrgAliasGoesHere` with the org alias in use, or remove `--target-org` if none provided to use the project default org)

4. **Deployment Testing Workflow:**

   - Create QA org using appropriate command based on project type
   - Deploy to QA org for testing: `qx deploy --org qa`
   - Validate deployment: `cci flow run validate_qbrix --org qa`
   - If successful, proceed with dev org deployment
   - If issues found, fix and retest in QA org before proceeding

5. **Org Lifecycle Management:**

   - Dev and QA orgs can be created and used for the duration unless they need to be recreated
   - To remove or logout of an org, use: `qx org logout --org OrgAliasHere`
   - Replace `OrgAliasHere` with the alias of the Salesforce org

6. **Handling Missing Metadata:**

   - When running test deployments, review errors (if any) and make updates to the files
   - If certain metadata is missing, request the alias of the org where the missing source metadata could be sourced from
   - If given, retrieve the metadata using: `qx retrieve --metadata 'MetadataTypeHere:MetadataAPINameHere' --target-org OrgAliasHere`
   - Replace `MetadataTypeHere:MetadataAPINameHere` with the Salesforce metadata API naming conventions (metadata type then `:` then the API name)
   - The API name can be omitted if you want to retrieve everything of a specific type
   - Example for specific metadata: `CustomObject:My_Custom_Object__c`
   - Once retrieved, test deploy to a QA org and review any deployment errors again

7. **Checking Brix Installation:**

   - To check if a brix (aka qbrix) is installed in a target Salesforce org, run: `cci task run list_qbrix --org OrgAliasHere`
   - Add the org alias at the end of the command
   - Parse the results to look for the specific brix name

8. **Analytics CRM Metadata:**
   - If working with Analytics CRM metadata, defined by the `force-app/main/default/wave` directory being present, then run the command `cci task run analytics_manager --mode d --generate_metadata_desc True --org OrgAliasHere` with the org alias at the end, to download the data associated with any analytics datasets which have been retrieved
   - If no analytics datasets are present, then this can be omitted
