---
description: This rule should be considered when making changes to the brix project.
alwaysApply: false
---

## Communication Style

When responding to users, maintain a tone that is:

- **Friendly**: Be approachable and warm in your interactions
- **Supportive**: Encourage users and validate their efforts, especially when troubleshooting issues
- **Encouraging**: Celebrate wins (even small ones!) and motivate users through challenges
- **Light-hearted**: Sprinkle in a small amount of humor where appropriate - a well-placed quip can make debugging feel less painful 🎉

Remember: Brix development can be complex, so be the helpful colleague everyone wishes they had!

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

- Flows can have steps which support all CumulusCI tasks. Reference documentation: https://cumulusci.readthedocs.io/en/stable/tasks.html#
- Example code snippets can be found in `.vscode/brix.code-snippets`
- Steps within a flow can use when statements, defined with a `when` key and then the clause which defines if the step should run
- Up-to-date options can be found by running `cci task info orgconfig_hydrate` and reading the output

## CumulusCI Task and Brix Extension Tasks

As we are building brix on top of a template which supports CumulusCI and SalesforceDX, it means we can use the VSCode Extensions and CumulusCI tasks in addition to our own custom tasks which QX adds. Any of the CumulusCI tasks can be used as steps within your flows or as custom tasks within the `cumulusci.yml` file within your brix.

**Reference Documentation:** https://cumulusci.readthedocs.io/en/stable/tasks.html#

**Getting Task Info:** Use `cci task info task_name_here` in your terminal to get full details about any task and its available options.

### Brix Extension Tasks

In addition to CumulusCI tasks, we have custom extension tasks that extend CumulusCI and SalesforceDX functionality:

| Task Name                  | Description                                                                                                                                        |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `abort_install`            | Stop deployment with/without exception based on a when clause. Used to stop deployments when target org contains conflicting metadata or packages. |
| `analytics_fart`           | Set and update placeholders within Experience Cloud sites for Analytics Dashboards.                                                                |
| `analytics_manager`        | Download/upload dataset data for CRM Analytics, set sharing rules for Apps.                                                                        |
| `analytics_timeshift`      | Adjust dates in a CSV file to align with a new target date.                                                                                        |
| `community_publisher`      | Publish all active communities or specific communities in the target org.                                                                          |
| `display_banner`           | Display banner text in terminal to aid tracking execution progress.                                                                                |
| `display_project`          | Display current brix details in terminal at runtime.                                                                                               |
| `dustpan`                  | Remove a file or glob pattern match from the brix stack.                                                                                           |
| `experience_manager`       | Run additional setup tasks against an Experience Cloud site.                                                                                       |
| `load_sfdmu`               | Run SFDMU data loads.                                                                                                                              |
| `named_credential_import`  | Create a Named Credential in target Salesforce org from a definition.                                                                              |
| `omniscript_align`         | Repair known issues with OmniScript LWC components. Must run before LWC deployment (prepare_org flow).                                             |
| `orgconfig_hydrate`        | Add options to org_config object with information about connected Salesforce org. Used for when clauses in flow steps.                             |
| `populate_recently_viewed` | Add records to Recently Viewed list view for a given object.                                                                                       |
| `qbrix_fart`               | Find and Replace Text tool (FART) - find/replace placeholder text or inject text into files at runtime.                                            |
| `qbrix_cache_add`          | Access runtime variables, add to cache for passing values to other tasks. Can read data from org via SOQL.                                         |
| `qbrix_installer_tracking` | Log brix deployments. Data saved to QLabs org for deployment reporting and issue tracing.                                                          |
| `qbrix_upload_files`       | Upload files to Salesforce.                                                                                                                        |
| `qbrix_user_action_runner` | Run actions against the user REST API endpoint.                                                                                                    |
| `qx_wait`                  | Wait for an item to become available (SOQL result, Permission Set status, etc.).                                                                   |
| `robot_runner`             | Run robot keywords with/without parameters without creating a .robot file.                                                                         |
| `run_apex_and_wait`        | Execute Apex in target Salesforce org and wait for completion.                                                                                     |
| `run_perfect_date_wizard`  | Send request to start Perfect Date Wizard in target Salesforce org.                                                                                |
| `upsert_favourite`         | Set a favourite/bookmark within Salesforce.                                                                                                        |
| `user_manager`             | Create Users and set permissions, roles, profile images, etc.                                                                                      |

## LLM Rule Synchronization (Required)

When updating any LLM/tooling rules, keep these directories **synchronized**:

- Cursor: `.cursor/rules/*` and `.cursorrules`
- Claude: `.claude/*` (notably `.claude/memory.md`)
- Gemini: `.gemini/rules/*` (this file)
- Windsurf: `.windsurf/rules/*`

## CumulusCI Flow Placeholder Convention

- `task: None` is an **allowed** placeholder in CumulusCI flows for templates (used to skip/placeholder steps during testing/building).

### When Clause Support

When clauses are used within flows in `cumulusci.yml` to decide whether a step should **run** (when evaluates to True) or **skip** (when evaluates to False).

**Prerequisite**: `orgconfig_hydrate` must be defined in an earlier step in the **same flow** before any step that uses `when`. It’s OK to have more than one `orgconfig_hydrate` step.

**Syntax basics**

- One `when` clause per step (you can combine multiple checks in that one expression).
- Supported boolean logic: `not`, `AND`, `OR`, and parentheses.
    - Example: `(Test1() AND (Test2() OR Test3()))`
- Supported comparisons (for methods that return values): `>`, `>=`, `<`, `<=`, `==`, `!=`
- If comparing to a value containing spaces, wrap it in single quotes: `'my value with spaces'`
- Always prefer the definitive list from `cci task info orgconfig_hydrate` (method names are exact).

**Common example (deploy only if a brix isn’t already installed)**

```yaml
source_dependencies:
    steps:
        1:
            # Brix System Task - Leave in place
            task: orgconfig_hydrate
        2:
            # Deploy the requirements for Brix Registration in target org
            flow: qbrix_register_base:deploy_qbrix
            when: not org_config.is_qbrix_installed('QBrix-1-xDO-Tool-QBrixRegister')
```

**Supported when-clause methods (current at time of writing)**

- `env_present`: `when: org_config.env_present('ENV_NAME')`
- `max_org_api_version`: `when: org_config.max_org_api_version() >= 64.0`
- `is_file`: `when: org_config.is_file('path/to/file')`
- `is_customer_org`: `when: org_config.is_customer_org()`
- `is_file_glob`: `when: org_config.is_file_glob('**/*.robot')`
- `is_dir`: `when: org_config.is_dir('path/to/dir')`
- `is_qbrix_installed`:
    - `when: org_config.is_qbrix_installed('qbrix_name_here')`
    - `when: org_config.is_qbrix_installed('qbrix_name_here', nameonly=True)`
- `is_object_in_org`: `when: org_config.is_object_in_org('Account')`
- `is_org_identifier`: `when: org_config.is_org_identifier('q_key_here')`
- `is_psl_in_org`: `when: org_config.is_psl_in_org('PSL Name')`
- `is_ps_in_org`: `when: org_config.is_ps_in_org('PermissionSetApiName')`
- `is_namespace_installed`: `when: org_config.is_namespace_installed('namespace')`
- `is_package_installed`: `when: org_config.is_package_installed('Package Name')`
- `is_psl_minimal_qty_availiable_in_org`: `when: org_config.is_psl_minimal_qty_availiable_in_org('PSL Name', 5)`
- `is_data_present`: `when: org_config.is_data_present('ObjectApiNameHere', 'Name = \\'Acme\\'')`
- `is_scratch_org`: `when: org_config.is_scratch_org()`
- `is_running_headless`: `when: org_config.is_running_headless()`
- `is_running_in_github_action`: `when: org_config.is_running_in_github_action()`
- `qbrix_cache_get`: `when: org_config.qbrix_cache_get('cached_key') == 'expected_value'`
- `soql_result`: `when: org_config.soql_result('SELECT Id FROM Account', has_records=True)`
- `tooling_soql_result`: `when: org_config.tooling_soql_result('SELECT Id FROM ApexClass', has_records=True)`
- `was_brix_ordered_in_last`: `when: org_config.was_brix_ordered_in_last('brix_name_here')`

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
- **MCP Handoff**: When asked to create, update, or fix LWC components, use the Salesforce DX MCP `orchestrate_lwc_component_creation` tool or other LWC-related tools for expert guidance

### Aura Components

- Use component events for communication
- Implement proper attribute types
- Follow Aura component lifecycle patterns
- **MCP Handoff**: When asked to work with Aura components (create, update, fix, or migrate), use the Salesforce DX MCP Aura tools such as `orchestrate_aura_migration` for expert guidance

### Code Analyzer MCP Tools

For code quality analysis, use the Salesforce DX MCP Code Analyzer tools:

- **`run_code_analyzer`**: Performs static analysis of code using Salesforce Code Analyzer. Validates best practices, checks for security vulnerabilities, and identifies performance issues.
- **`describe_code_analyzer_rule`**: Gets the description of a Salesforce Code Analyzer rule, including the engine, severity, and associated tags.

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

### Assigning Permissions During Deployment

Permission Sets, Permission Set Licenses, and Permission Set Groups are assigned using CumulusCI tasks in the `post_qbrix_deploy` flow **before** any data is deployed.

**Assign Permission Sets:**

```yaml
post_qbrix_deploy:
    steps:
        1:
            task: assign_permission_sets
            options:
                api_names:
                    - MyPermissionSetAPIName_1
```

**Other Tasks:** `assign_permission_set_licenses`, `assign_permission_set_groups`

**Waiting for Permission Set Groups** (use `qx_wait` before assigning):

```yaml
post_qbrix_deploy:
    steps:
        1:
            task: qx_wait
            options:
                permission_set_group_api: MyPermissionSetGroupAPIName
        2:
            task: assign_permission_set_groups
            options:
                api_names:
                    - MyPermissionSetGroupAPIName
```

**Updating Existing Permission Sets** (use `permission_set_upsert`):

```yaml
post_qbrix_deploy:
    steps:
        1:
            task: permission_set_upsert
            options:
                permission_set_name: namespace__PermissionSetAPIName
                objects:
                    - MyCustomObject__c
                user_permissions:
                    - ActivitiesAccess
```

**Note:** Always use the full API name including namespace.

### Data Management with NextGen Data Tool

Use the **NextGen Data Tool** for data deployments in brix.

**Step 1: Configure Task in `cumulusci.yml`**

```yaml
tasks:
    deploy_nextgen_data:
        class_path: qbrix.tools.utils.qbrix_nextgen_datatool.RunDataTool
        options:
            data_keys:
                - YOUR_DATA_VERSION_ID_HERE
```

**Step 2: Create Data Flow and Deploy in `post_qbrix_deploy`**

```yaml
deploy_qbrix_data:
    steps:
        1:
            task: deploy_nextgen_data

post_qbrix_deploy:
    steps:
        1:
            flow: deploy_qbrix_data
```

**Finding Data Version IDs:** Log into NextGen Data Tool → Open data pack → Copy the unique ID.

**Troubleshooting:** "Class path not found" error → Run `cci task run update_qbrix`.

**Common Data Tool Issues:**

- **Missing field**: Check Field Level Security in Object Manager (System Admin doesn't guarantee API access)
- **No External_ID\_\_c on parent**: Field missing, FLS issue, or "External ID" checkbox not enabled. Run `qx utils doctor` to fix naming issues
- **No records**: Ensure org has records and query filters aren't excluding all data
- **Lookup not editable**: Intended behavior - re-extract via new version
- **Macros**: Supports Macros but NOT ExpressionFilter/ExpressionFilterCriteria; use user with minimal permissions

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

## Remote Containers Setup

The VS Code Remote – Containers extension (Dev Containers) integrates VS Code with Docker containers, allowing you to open any Brix project in a fully preconfigured development environment.

### Prerequisites

Install these tools in order:

1. **Docker Desktop**: [Mac](https://www.docker.com/products/docker-desktop) • [Windows](https://www.docker.com/products/docker-desktop)
2. **Visual Studio Code**: [Download](https://code.visualstudio.com/)
3. **VS Code Extensions**: Dev Containers, Docker Extension
4. **GitHub CLI (gh)**: [Download](https://cli.github.com/)
5. **GitHub Desktop** (optional): [Install](https://desktop.github.com/)

**Important**: Ensure you are connected to the Salesforce VPN (Zscaler) before proceeding.

### Docker Setup

1. Open Docker Desktop and sign in with your Salesforce account ("Continue with Google")
2. Go to Settings → Resources and adjust:
    - **CPU**: Max available
    - **Memory**: Up to 16 GB (smaller OK if limited)
    - **Swap**: Up to 1 GB
    - **Disk**: Up to 512 GB
3. Click **Apply & Restart**

### GitHub CLI Authentication

```bash
gh auth login --hostname github.com --web --scopes read:packages
```

### Docker-GitHub Authentication

Replace `{YOUR_GH_USERNAME}` with your GitHub username (ending with `_sfemu`):

```bash
echo $(gh auth token) | docker login ghcr.io -u {YOUR_GH_USERNAME} --password-stdin
```

### Pull Container Image

```bash
docker pull ghcr.io/sfdc-qbranch-emu/qbrix-base-container-quasar:latest
```

### Container Troubleshooting

**General Reset/Rebuild**: Save work, close VSCode, connect to Zscaler, update Docker Desktop, delete all containers/images/volumes, restart device, re-authenticate.

**Segmentation Fault**: Docker Desktop → Settings → General → Select "osxfs (Legacy)", uncheck "Use Virtualization Framework" → Apply & Restart.

**GitHub Push Issues**: Use VSCode Build Tasks instead of GitHub Desktop:

- Save/Push: `GITHUB: 💾 Save/Push local changes to GitHub`
- Pull: `GITHUB: 📩 Get/Pull latest version from GitHub`

**Robot Framework Errors**: Run `qx robot setup` to check, install, and update robot dependencies.

### Brix Deprecation

**Important**: Brix cannot be deleted, but they can be deprecated when no longer needed.

**Step 1**: Complete initial checks - ensure no active dependencies, recipes, or references exist

**Step 2**: Update GitHub Repository:

1. Settings → Rename with `DEPRECATED-` prefix (e.g., `DEPRECATED-Qbrix-99-MyBrix`)
2. Archive the repository from Settings page

**Step 3**: Deprecate in QLabs:

1. QLabs Org → NextGen Management app → Q Brix tab
2. Open Brix record → Select **Deprecate Brix** → Provide updated GitHub URL

### Troubleshooting

- Check CumulusCI logs for deployment issues
- Use Salesforce debug logs for runtime issues
- Validate org configurations before deployment. If using a scratch org, then `orgs/dev.json` is where this is defined
- Deployment errors should be reviewed and then changes made before test deploying again
- Often running the qx metadata doctor can solve many common issues. This is done by running `qx utils doctor`
- If the user is having issues with qx or their configuration, run the `qx update` command and then run the `qx setup vscode` command which should resolve the majority of issues with configuration

### Common Deployment Errors and Solutions

#### 1. Missing Dependencies

**Error messages like:**

- "Method does not exist or incorrect signature"
- "Variable does not exist"
- "System.NullPointerException: Attempt to de-reference a null object"
- "Field Discount_Approved\_\_c does not exist. Check spelling" (formula fields)
- "Field FOO\_\_c not found for permission set XYZ" (profiles/permission sets)
- "Field FOO\_\_c does not exist on layout Account-Account Layout" (page layouts)

**Solution:** Check that the identified dependency is stored within the brix and being deployed. If not, retrieve the missing metadata from the Salesforce org where it was created.

#### 2. API Compatibility Problems

**Error message:** "Property 'namesegment' not valid in version 57.0"

**Cause:** Metadata was retrieved on a different API version than the brix target API version in `cumulusci.yml`.

**Solution:** Pull the metadata again from a source Salesforce org, or revert to an earlier commit. Ensure metadata is first deployed to a Salesforce org, then update the API version in both `cumulusci.yml` and `sfdx-project.json`, then retrieve again.

#### 3. External ID Field Not Found

**Error:** External ID field was not found or not accessible.

**Solution:** Check that the External ID field has been deployed to the target org and that its type is set to "External ID".

#### 4. Features Not Enabled in Target Org

**Symptom:** Standard object fields being deployed don't exist in the target org.

**Solution:** These fields might use features not enabled in the target org. Remove them from the deployment or enable the required features in the target org.

#### 5. Salesforce Platform Error

**Error:** "An unexpected error occurred. Please include this ErrorID if you contact support"

**Solution:** Check with the nextgen support team on Slack, check [Salesforce Trust](https://status.salesforce.com/) for outages, or search for the error in GUS.

#### 6. Code Syntax Issues

**Error messages like:**

- "Expecting 'x' but was: 'y'"
- "Missing ';' at 'y'"
- "Unexpected token 'x'"

**Solution:** Identify the file (usually XML) from the error message with file reference and line number. Direct user to check and fix the file. Tools like SonarLint can help analyze code for bugs and vulnerabilities.

#### 7. Admin Operation Already In Progress

**Error:** "Admin operation already in progress"

**Cause:** A background process is locking admin functions.

**Solution:** Check Apex Jobs, Apex Flex Queue, or Background Jobs in Setup. Wait for the job to complete and try again.

#### 8. Missing Permission Issues

**Cause:** The deploying user lacks necessary permissions.

**Solution:** Review user permissions. Assign System Administrator profile if not already assigned. Check for required Permission Set Licenses and user checkboxes (e.g., Knowledge User, Service Cloud User).

#### 9. Client Timeout

**Solution:**

- Update SF CLI and QX if running locally: `qx update`
- Check for admin operations in progress
- Wait a few minutes and try again

#### 10. Dependent Class Needs Recompilation

**Error:** "Dependent class is invalid and needs recompilation"

**Solution:**

1. Open the stack trace in the target org
2. Go to Setup > Apex Classes or Apex Triggers
3. Click "Compile all classes/triggers" hyperlink
4. Wait for results (can take time)

#### 11. Org Lock / Exclusive Access Error

**Error:** "Error: unable to obtain exclusive access to this record"

**Cause:** Administrative lock from multiple simultaneous changes to the org.

**Solution:** Wait 10-15 minutes, ensure no other users are making Setup changes, then redeploy.

#### 12. Quasar Artifact Hash Error

**Error:** Message contains "Error: 'x-quasar-artifact-hash'"

**Cause:** An issue with our internal Quasar tool.

**Solution:** Wait 10-15 minutes and then try to deploy again.

## Local Testing and Development with Salesforce Orgs

### Org Setup and Naming Conventions

- We build in a 'dev' org, when created this will have an auto-updated alias which will start with `dev_` and then be a compressed version of the name of the project
- If the project name contains `-SDO-` an SDO is the best org to use as a dev and qa org. To create these quickly you can run the command `qx org pool --sdo --org dev` (--org dev for development org, --org qa for test/qa org)
- If the project name contains `-xdo-` a CDO or Scratch org is the best org to use as a dev and qa org. To create these quickly you can run the command `qx org pool --cdo --org dev` (--org dev for development org, --org qa for test/qa org) for a CDO (aka Clean Demo Org) or `qa org create --org dev` to create a scratch org. Remember that the scratch org will use the `orgs/dev.json` file as the scratch org definition file
- Changes should be retrieved from the dev org and test deployed to the qa org

### Scratch Org Features

The default template adds multiple features to the default "dev" scratch org definition which can be found in the `orgs/dev.json` file. There will be times where additional features need to be added to enable licenses, Permission Set Licenses (PSLs), and features within the resulting scratch org.

**Important**: Take note of features added to the scratch org definition, as TSOs (Target Salesforce Orgs) which use your brix will need those same licenses enabled in BlackTab.

**Searching for Features:**

To search for scratch org features (including non-public features), use the terminal command:

```bash
qx utils feature-search 'my search term here'
```

Replace `'my search term here'` with your search term (e.g., `accounting`). Search terms with spaces require quotes.

**Search Results Include:**

- **Features** (first column): Keywords to add to the `features` section of `orgs/dev.json`
- **Related Licenses** (third column): Must be enabled in any TSOs that might use this brix
- **Notes**: Additional features or permissions that may need to be added

**Public Scratch Org Features Reference:**
https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_scratch_orgs_def_file_config_values.htm

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
    - For xDO projects: `qx org pool --cdo --org qa`
    - For SDO projects: `qx org pool --sdo --org qa`

3. **API Version Updates:**
    - When API version updates are needed, always test deploy to a QA org first
    - Use the appropriate org type based on project naming convention
    - After successful deployment, update API version in `cumulusci.yml` and `sfdx-project.json` to the given version (e.g., 64.0)
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

## Dependencies and Packages

Package dependencies are defined in `cumulusci.yml` under the `project > dependencies` section.

### Package Dependency Syntax

```yaml
project:
    dependencies:
        # Unmanaged Package using version_id (the 04t ID from the install URL)
        - version_id: 04t2E000003VsuMQAS

        # Managed packages can use version_id (like above) or namespace + version
        - namespace: custom_namespace
          version: 1.2.3
```

### Package Dependency Guidelines

- **Unmanaged Packages**: Use `version_id` with the 18-character package version ID (starts with `04t`)
- **Managed Packages**: Can use either `version_id` OR `namespace` + `version` combination
- Use the 18-character version of the package version ID
- If adding a 15-char version ID, run `qx utils doctor` to convert it to 18-char format
- Use QBrix sources for dependent brix
- Document all external dependencies
- Include a URL comment above the `version_id` entry pointing to where package updates can be found

**Example with documentation:**

```yaml
project:
    dependencies:
        # Salesforce CPQ - https://developer.salesforce.com/docs/atlas.en-us.cpq_dev_api.meta/cpq_dev_api/
        - version_id: 04t4W000002HD2IQAW

        # Custom managed package
        - namespace: myapp
          version: 2.0.1
```
