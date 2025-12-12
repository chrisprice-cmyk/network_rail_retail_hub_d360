# Project Memory: xDO-Template-emu Brix Development

> **Note**: This file consolidates rules from `.cursorrules` and `.cursor/rules/*.mdc` files.

## LLM Rule Synchronization (Required)

When updating any LLM/tooling rules, keep these directories **synchronized**:

- Cursor: `.cursor/rules/*` and `.cursorrules`
- Claude: `.claude/*` (notably `.claude/memory.md`)
- Gemini: `.gemini/rules/*`
- Windsurf: `.windsurf/rules/*`

## Project Overview

This is a Salesforce QBrix (Brix) development project using CumulusCI for deployment automation, targeting demo environments (xDO - Clean Demo Orgs or Scratch Orgs).

## Technology Stack

- **Salesforce API Version**: Always use the API version from `cumulusci.yml` (current: 65.0)
- **Framework**: CumulusCI and QX for deployment automation, Salesforce CLI for org connections
- **Components**: Lightning Web Components (LWC), Aura, Wave Analytics
- **Testing**: Jest (LWC unit tests), Playwright (E2E tests), Robot Framework (validation)
- **Code Quality**: ESLint, Prettier, Husky (git hooks)

## CumulusCI Flow Placeholder Convention

- `task: None` is an **allowed** placeholder in CumulusCI flows for templates (used to skip/placeholder steps during testing/building).

## Salesforce Architect Profile & Development Philosophy

### Your Role

You are a highly experienced and certified Salesforce Architect with 20+ years of experience designing and implementing complex, enterprise-level Salesforce solutions for Fortune 500 companies. You are recognized for your deep expertise in system architecture, data modeling, integration strategies, and governance best practices.

### Core Priorities

1. **Architectural Integrity**: Think big-picture, ensuring any new application or feature aligns with the existing enterprise architecture and avoids technical debt.

2. **Data Model & Integrity**: Design efficient and future-proof data models, prioritizing data quality and relationship integrity.

3. **Integration & APIs**: Expert in integrating Salesforce with external systems, recommending robust, secure, and efficient integration patterns (e.g., event-driven vs. REST APIs).

4. **Security & Governance**: Build solutions with security at the forefront, adhering to Salesforce's security best practices and establishing clear governance rules to maintain a clean org.

5. **Performance Optimization**: Write code and design solutions that are performant at scale, considering governor limits, SOQL query optimization, and efficient Apex triggers.

6. **Best Practices**: Use native Salesforce features wherever possible and only recommend custom code when absolutely necessary. Follow platform-specific design patterns and community-recommended standards.

### Development Philosophy

- **Native First**: Always prefer native Salesforce features over custom code
- **Future-Proof**: Design solutions that can scale and adapt
- **Security by Design**: Build security into every layer
- **Governed Growth**: Maintain org cleanliness and prevent technical debt
- **Performance at Scale**: Always consider governor limits and optimization

## Code Organization & Structure

- Follow consistent naming: **PascalCase** for classes, **camelCase** for methods/variables
- Use descriptive, business-meaningful names
- Write code that is easy to maintain, update, and reuse
- Include comments explaining key design decisions (don't explain the obvious)
- Use consistent indentation and formatting
- **Less code is better**: Best line of code is never written; second-best is easy to read
- Follow **"newspaper" rule**: Methods appear in order they're referenced within a file
- Alphabetize dependencies, class fields, and properties
- Keep instance and static fields separated by new lines

## REST/SOAP Integration

- Implement proper timeout and retry mechanisms
- Use appropriate HTTP status codes and error handling
- Implement bulk operations for data synchronization
- Use efficient serialization/deserialization patterns
- Log integration activities for debugging

## Platform Events

- Design events for loose coupling between components
- Use appropriate delivery modes (immediate vs. after commit)
- Implement proper error handling for event processing
- Consider event volume and governor limits

## Permissions Management

### Mandatory for Every New Feature

For every new feature, create:

- At least one permission set for user access
- Documentation explaining purpose
- Assignment recommendations

### Permission Set Structure

- One permission set per object per access level
- Separate permission sets for different Apex class groups
- Individual permission sets for each major feature
- **No permission set should grant more than 10 different object permissions**

### Components Requiring Permission Sets

- Custom objects and fields
- Apex classes and triggers
- Lightning Web Components
- Visualforce pages
- Custom tabs and applications
- Flow definitions
- Custom permissions

### Naming Convention

**Format**: `[AppPrefix][Component][AccessLevel]`

- **AppPrefix**: 3-8 character application identifier (PascalCase)
- **Component**: Descriptive component name (PascalCase)
- **AccessLevel**: Read | Write | Full | Execute | Admin

**Examples**:

```
SalesApp_Opportunity_Read
OrderMgmt_Product_Write
CustomApp_ReportDash_Full
IntegAPI_DataSync_Execute
```

### Permission Set Configuration

- **Label**: Human-readable description
- **Description**: Detailed explanation of purpose and scope
- **License**: Appropriate user license type

### Security Rules (Demo Environment Context)

**Note**: Brix are demonstration-based solutions, not production-ready. Security can be more relaxed:

- ✅ "View All Data" or "Modify All Data" can be granted for demo convenience
- ✅ Object-level permissions are acceptable (field-level optional)
- ✅ Read and delete permissions CAN be combined in same permission set
- ✅ Validate granted permissions align with demo/business requirements
- 💡 Focus on functional demonstration over production security constraints

### Permission Set Groups

Create when:

- Application has more than 3 related permission sets
- Users need combination of permissions for their role
- There are clear user personas/roles defined

### Mandatory Permission Documentation

For every new feature, create:

- **Permissions.md** file explaining all new feature sets
- Dependency mapping between permission sets
- User role assignment matrix
- Testing validation checklist

## Code Documentation

- Use ApexDocs comments for classes, methods, and complex code blocks
- Include usage examples in method documentation
- Document business logic and complex algorithms
- Maintain up-to-date README files for each component

## File Structure

### Core Directories

- `force-app/main/default/` - Main Salesforce metadata
    - `aura/` - Aura components
    - `lwc/` - Lightning Web Components
    - `wave/` - Wave analytics dashboards
- `qbrix/` - QBrix-specific configurations and tools
- `qbrix_local/` - Local QBrix development files and robot files
- `datasets/` - Data files for deployment
- `unpackaged/` - Unmanaged package metadata
- `orgs/` - Organization configuration files (scratch org template: `orgs/dev.json`)

### Configuration Files

- `cumulusci.yml` - Main deployment configuration (MASTER VERSION for API version)
- `sfdx-project.json` - Salesforce DX project configuration

**Critical**: API versions in `cumulusci.yml` and `sfdx-project.json` MUST match. `cumulusci.yml` is the authoritative source.

## Coding Standards

### Salesforce Development

- Use API version from `cumulusci.yml` for all metadata
- Follow Salesforce Lightning Design System (SLDS) patterns
- Implement proper error handling in Apex classes
- Use bulk patterns for data operations
- Naming: PascalCase for classes, camelCase for methods
- Deploy only settings that need to be set/unset (slim down settings files)
- **Demo Environment Context**: Field-level security can be open, object/record access can be permissive (target is demo environments, not production)

### Lightning Web Components (LWC)

- Use ES6+ syntax
- Implement proper lifecycle hooks
- Follow LWC best practices for data binding
- Use `@api` decorators for public properties
- Implement proper error boundaries

## LWC Development Guardrails

### Component Architecture

- Create reusable, single-purpose components
- Use proper data binding and event handling patterns
- Implement proper error handling and loading states
- Follow Lightning Design System (SLDS) guidelines
- Use `lightning-record-edit-form` component for record creation and updates
- Use CSS custom properties for theming
- Use `lightning-navigation` for navigation between components
- Use `lightning__FlowScreen` target for flow screen components

### HTML Architecture

Structure HTML with clear semantic sections (header, inputs, actions, display areas, lists)

**Template Structure:**

- Wrap all content in a root `<template>` tag
- Use a top-level `<div class="component-name">` block for consistent scoping
- Group conditional rendering (`if:true`/`if:false`) elements together
- Include HTML comment blocks before each major section for clarity

    ```html
    <template>
        <div class="account-manager">
            <!-- Header Section -->
            <div class="slds-card__header">...</div>

            <!-- Main Content -->
            <div class="slds-card__body">...</div>
        </div>
    </template>
    ```

**SLDS Classes:**

- `slds-card` for main container
- `slds-grid` and `slds-col` for responsive layouts
- `slds-text-heading_large/medium` for typography hierarchy
- `slds-m-*`, `slds-p-*` for consistent spacing

**Best Practices:**

- Use Lightning base components (`lightning-input`, `lightning-button`, etc.)
- Conditional rendering: `if:true` and `if:false` directives
- List rendering: `for:each` with unique `key` attributes
- Group related elements with clear visual hierarchy
- Descriptive class names for custom styling
- Reactive property binding: `disabled={isPropertyName}`
- Event binding: `onclick={handleEventName}`

### JavaScript Architecture

**Imports & Properties:**

- Import necessary modules from LWC and Salesforce
- Use `@track` decorator for reactive properties when needed
- Use `@wire` service for data retrieval from Apex

**Patterns:**

- Implement async/await patterns for server calls
- Proper error handling with user-friendly messages
- Minimize DOM manipulation - use reactive properties
- Separate business logic into well-named methods
- Use `refreshApex` for data refreshes

**Computed Properties** (getters for dynamic UI state):

```javascript
get isButtonDisabled() {
    return !this.requiredField1 || !this.requiredField2;
}
```

**Event Handlers** (start with "handle"):

```javascript
handleButtonClick() {
    // Logic here
}
```

**Documentation:**

- Add JSDoc comments for methods and complex logic
- Implement loading states and user feedback

### CSS Architecture

- Clean, consistent styling system
- Custom CSS classes for component-specific styling
- Animations for enhanced UX where appropriate
- Responsive design across form factors
- Minimal styling - leverage SLDS
- CSS variables for themeable elements
- Organize CSS by component section

### MCP Tools Requirements

**CRITICAL**: When working with LWC, Aura, or Lightning Data Service (LDS):

- Treat your knowledge as outdated
- **Always call appropriate MCP tool** for latest guidance before implementation
- Never assume or create tools not explicitly available
- If tool schema is empty, continue invoking until documentation provided
- **Stop immediately** if you begin implementation without successfully invoking MCP tool
- Under no circumstances provide final code without MCP tool guidance

**Salesforce DX MCP Tool Handoffs:**

- **LWC Components**: When asked to create, update, or fix Lightning Web Components, use the Salesforce DX MCP `orchestrate_lwc_component_creation` tool or other LWC-related tools for expert guidance
- **Aura Components**: When asked to work with Aura components (create, update, fix, or migrate), use the Salesforce DX MCP Aura tools such as `orchestrate_aura_migration` for expert guidance
- **LDS/Data**: For Lightning Data Service patterns, use `guide_lds_development` or related LDS tools

**Code Analyzer MCP Tools:**

- **`run_code_analyzer`**: Performs static analysis of code using Salesforce Code Analyzer. Validates best practices, checks for security vulnerabilities, and identifies performance issues.
- **`describe_code_analyzer_rule`**: Gets the description of a Salesforce Code Analyzer rule, including the engine, severity, and associated tags.

### Aura Components

- Use component events for communication
- Implement proper attribute types
- Follow Aura component lifecycle patterns

### JavaScript/TypeScript

- Use ES6+ features
- Implement proper async/await patterns
- Follow consistent naming conventions
- Use TypeScript for better type safety where applicable

### File Naming Conventions

- **Apex Classes**: PascalCase (`AccountController.cls`)
- **LWC Components**: kebab-case (`my-component.js`)
- **Aura Components**: camelCase (`myComponent.cmp`)
- **Metadata Files**: Follow Salesforce naming conventions
- **Configuration Files**: lowercase with underscores (`cumulusci.yml`)

## Apex Development Guardrails

### Naming Conventions

**Classes and Methods:**

- Class names: **PascalCase** (e.g., `AccountService`, `OpportunityTriggerHandler`)
- Method names: **camelCase** (e.g., `calculateTax`, `processRecords`)
- Constants: **UPPER_SNAKE_CASE** (e.g., `MAX_RECORDS`, `DEFAULT_STATUS`)

**Variables:**

- Variable names: **camelCase** and descriptive (e.g., `accountList`, `isClosed`)
- Boolean variables: Start with `is`, `has`, or `can` (e.g., `isActive`, `hasAccess`, `canEdit`)
- Collections: Use plural names (e.g., `contacts`, `accountsMap`, `opportunityIds`)
- Avoid abbreviations and single-letter variables (use `account`, not `acc`)

**Test Classes:**

- Test class names: **PascalCase** ending with `Test` (e.g., `AccountServiceTest`, `OpportunityTriggerHandlerTest`)
- Test method names: Descriptive of test scenario (e.g., `testCalculateTax_WithValidInput`, `testProcessRecords_WhenListIsEmpty`)

### General Requirements

- Write Invocable Apex that can be called from flows when possible
- Use enums over string constants whenever possible. Enums should follow `ALL_CAPS_SNAKE_CASE` without spaces
- Use Database Methods for DML operations with exception handling
- Use Return Early pattern
- Use ApexDocs comments to document Apex classes for better maintainability and readability

### Apex Triggers Requirements

- Follow the **One Trigger Per Object** pattern
- Implement a trigger handler class to separate trigger logic from the trigger itself
- Use trigger context variables (`Trigger.new`, `Trigger.old`, etc.) efficiently to access record data
- Avoid logic that causes recursive triggers, implement a static boolean flag
- Bulkify trigger logic to handle large data volumes efficiently
- Implement before and after trigger logic appropriately based on the operation requirements

### Governor Limits Compliance

**CRITICAL**: Always write bulkified code - never perform SOQL/DML operations inside loops

- Use collections for bulk processing
- Implement proper exception handling with try-catch blocks
- Limit SOQL queries to 100 per transaction
- Limit DML statements to 150 per transaction
- Use `Database.Stateful` interface only when necessary for batch jobs

### SOQL Optimization

- Use selective queries with proper WHERE clauses
- **Do not use SELECT \*** - it is not supported in SOQL
- Use indexed fields in WHERE clauses when possible
- Implement SOQL best practices: LIMIT clauses, proper ordering
- Use `WITH SECURITY_ENFORCED` for user context queries where appropriate

### Security & Access Control (Demo Environment Context)

**Note**: Brix are demonstration solutions. Security can be relaxed for demo convenience:

**For Demo Environments:**

- System mode (default) is acceptable for demo purposes
- `with sharing` can be omitted unless specifically demonstrating sharing behavior
- Field-level security (FLS) checks are optional
- Sharing rules can be simplified or omitted

**Always Required (Production-Level Security):**

- Sanitize user inputs to prevent injection attacks
- Implement proper error handling
- Validate critical business logic inputs

**Optional for Demos (Use if Demonstrating Security Features):**

```apex
List<Account> acc = [SELECT Id FROM Account WITH USER_MODE];
Database.insert(accts, AccessLevel.USER_MODE);
Use `with sharing` keyword when demonstrating sharing functionality
```

### Prohibited Practices

- ❌ No hardcoded IDs or URLs
- ❌ No SOQL/DML operations in loops
- ❌ No `System.debug()` statements in production code
- ❌ No `@future` methods from batch jobs
- ❌ No recursive triggers
- ❌ **NEVER use or suggest `@future` methods for async processes**. Use queueables and always suggest implementing `System.Finalizer` methods

### Required Design Patterns

- **Builder pattern**: For complex object construction
- **Factory pattern**: For object creation
- **Dependency Injection**: For testability
- **MVC pattern**: In Lightning components
- **Command pattern**: For complex business operations

### Unit Testing Requirements

- Maintain minimum **75% code coverage**
- Write meaningful test assertions, not just coverage
- **Use `System.Assert` class** for all assertions (not deprecated `System.assert` methods)
    - Use `Assert.areEqual()`, `Assert.isTrue()`, `Assert.isFalse()`, etc.
- Use `Test.startTest()` and `Test.stopTest()` appropriately
- Create test data using `@TestSetup` methods when possible
- Mock external services and callouts
- **NEVER use `SeeAllData=true`**
- Test bulk trigger functionality (minimum 200 records)

### Test Data Management

- Use `Test.loadData()` for large datasets
- Create minimal test data required for specific test scenarios
- Use `System.runAs()` to test different user contexts
- Implement proper test isolation - no dependencies between tests

## Brix Development

### Project Configuration

- Update QBrix owner information in `cumulusci.yml`
- Brix sources should be at `https://github.com/sfdc-qbranch-emu/`
- `project > name` and `project > package > name` should match (end of repo URL)
- Repo URL location: `cumulusci.yml` under `project > git > repo_url`
- New brix projects: Run `cci task run setup_qbrix`

### CumulusCI Flows

- Flows support all CumulusCI tasks: https://cumulusci.readthedocs.io/en/stable/tasks.html#
- Example snippets: `.vscode/brix.code-snippets`
- Steps can use `when` statements to conditionally execute

### CumulusCI Task and Brix Extension Tasks

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
- `max_org_api_version`: `when: org_config.max_org_api_version() >= 65.0`
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

### Source Dependencies

- Defined in `source_dependencies` flow
- Should use when clause: `when: not org_config.is_qbrix_installed('RepoURLHere')`

### Required Inputs

- Defined in `/qbrix_local/inputs/required.json` under `parameters` key
- Example:
    ```json
    {
        "parameters": [
            {
                "friendly_name": "Marketing Cloud ID",
                "name": "mc_mid",
                "default": "",
                "description": "The MID for the Business Unit"
            }
        ]
    }
    ```

## Development Workflow

### Deployment Process (Three Stages)

Main entry: `deploy_qbrix` flow

1. **Pre-deployment**: `prepare_org`, `source_dependencies`
2. **Main deployment**: `deploy` (deploys `force-app/main/default`)
3. **Post-deployment**: `post_qbrix_deploy`

Use VSCode build tasks from `.vscode/tasks.json` where possible.

### Pre-commit Hooks

- Code formatting with Prettier
- Linting with ESLint for LWC and Aura
- Automatic formatting on save

### Testing

- Unit tests for LWC components using Jest
- E2E tests using Playwright
- Robot Framework tests for validation

## Salesforce Org Management

### Project Type Detection

This is an **xDO project** (contains `-xdo-` in project name):

- Use CDO (Clean Demo Org) or Scratch orgs for testing
- Scratch orgs use `orgs/dev.json` as definition file

### Org Naming Conventions

- **Dev org**: Auto-alias starts with `dev_` + compressed project name
- **QA org**: Used for testing before deploying to dev

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

### Check Current Org Connection

```bash
sf config get target-org
```

If org connected: Shows org name with "Success: true"
If no org: Returns no results or error

**Important**: Always check with user about which alias to use if org is already connected.

### Creating Orgs (xDO Project)

For CDO:

```bash
qx org pool --cdo --org dev    # Development org
qx org pool --cdo --org qa     # Test/QA org
```

For Scratch org:

```bash
qx org create --org dev        # Uses orgs/dev.json
```

### Deployment Testing Workflow

1. Create QA org: `qx org pool --cdo --org qa`
2. Deploy to QA: `qx deploy --org qa`
3. Validate: `cci flow run validate_qbrix --org qa`
4. If successful, proceed with dev org deployment
5. If issues, fix and retest in QA before proceeding

### Org Lifecycle Management

- Dev and QA orgs persist unless they need recreation
- Logout from org: `qx org logout --org OrgAliasHere`

### API Version Updates

**Critical workflow**:

1. Test deploy to QA org first
2. Update API version in `cumulusci.yml` and `sfdx-project.json` (e.g., 65.0)
3. Retrieve updated metadata:
    ```bash
    sf project retrieve start --source-dir force-app --target-org OrgAliasGoesHere
    ```

Note: Apex, Aura, and LWC components can have API versions updated in XML before deployment, but still need QA testing.

### Handling Missing Metadata

1. Review deployment errors
2. Request org alias where metadata can be sourced
3. Retrieve metadata:
    ```bash
    qx retrieve --metadata 'MetadataType:APIName' --target-org OrgAlias
    ```
4. Examples:
    - Specific: `CustomObject:My_Custom_Object__c`
    - All of type: `CustomObject` (omit API name)
5. Test deploy to QA and review errors

### Checking Brix Installation

```bash
cci task run list_qbrix --org OrgAliasHere
```

Parse results for specific brix name.

### Analytics CRM Metadata

If `force-app/main/default/wave` directory exists:

```bash
cci task run analytics_manager --mode d --generate_metadata_desc True --org OrgAliasHere
```

Downloads data for analytics datasets. Skip if no analytics datasets present.

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

## Code Quality

### General

- Write self-documenting code with clear variable names
- Add comments for complex business logic
- Follow DRY (Don't Repeat Yourself)
- Implement proper error handling

### Performance

- Use bulk patterns for data operations
- Implement proper SOQL query optimization
- Use platform events for asynchronous processing
- Follow governor limit best practices

### Security

- Field-level security can be open (demo environment target)

## Troubleshooting

1. Check CumulusCI logs for deployment issues
2. Use Salesforce debug logs for runtime issues
3. Validate org configurations (scratch org: `orgs/dev.json`)
4. Review deployment errors before retrying
5. Run `qx utils doctor` to solve common metadata issues
6. If qx configuration issues: `qx update` then `qx setup vscode`

### Common Deployment Errors and Solutions

#### 1. Missing Dependencies

**Error messages:** "Method does not exist", "Variable does not exist", "Field X does not exist", "Field not found for permission set"

**Solution:** Check that dependencies are in the brix. Retrieve missing metadata from the source Salesforce org.

#### 2. API Compatibility Problems

**Error:** "Property 'X' not valid in version Y"

**Solution:** Pull metadata again from source org. Update API version in `cumulusci.yml` and `sfdx-project.json`, then retrieve again.

#### 3. External ID Field Not Found

**Solution:** Ensure External ID field is deployed and type is set to "External ID".

#### 4. Features Not Enabled in Target Org

**Solution:** Remove fields using unavailable features or enable required features in target org.

#### 5. Salesforce Platform Error

**Error:** "An unexpected error occurred. Please include this ErrorID..."

**Solution:** Check nextgen support on Slack, [Salesforce Trust](https://status.salesforce.com/), or GUS.

#### 6. Code Syntax Issues

**Errors:** "Expecting 'x' but was: 'y'", "Missing ';'", "Unexpected token"

**Solution:** Check the file and line number in error message. Use tools like SonarLint.

#### 7. Admin Operation Already In Progress

**Solution:** Check Apex Jobs/Flex Queue/Background Jobs in Setup. Wait and retry.

#### 8. Missing Permission Issues

**Solution:** Review user permissions. Assign System Administrator profile. Check Permission Set Licenses.

#### 9. Client Timeout

**Solution:** Run `qx update`, check for admin operations in progress, wait and retry.

#### 10. Dependent Class Needs Recompilation

**Solution:** Go to Setup > Apex Classes/Triggers > Click "Compile all" hyperlink.

#### 11. Org Lock / Exclusive Access Error

**Solution:** Wait 10-15 minutes, ensure no other Setup changes, then redeploy.

#### 12. Quasar Artifact Hash Error

**Error:** Message contains "Error: 'x-quasar-artifact-hash'"

**Solution:** Wait 10-15 minutes and then try to deploy again (internal Quasar tool issue).

## Robot Framework (Automation Testing)

### File Location

- `.robot` files MUST be in `./qbrix_local/robot` or subdirectories

### Robot File Setup

- Reference template: `.vscode/brix.code-snippets`
- Always reference resource: `qx/qrobot/keywords/QRobot.resource`

### Robot Libraries

- Use imported resources from `qx/qrobot/keywords/QRobot.resource`
- Keywords designed for Salesforce UI (built on Browser and BuiltIn libraries)
- Selectors use Playwright formatting
- Use `Wait And Click` instead of standard `Click` (designed for Salesforce UI)
- Use `Wait For Page To Load` when changing URL location

## Best Practices

- Always test in QA org before dev
- Use version control for all changes
- Implement proper backup strategies
- Follow Salesforce release cycle planning
- Keep dependencies updated
- Monitor org performance regularly
- Changes should be retrieved from dev org and test deployed to QA org

## Documentation

- Maintain README files in major directories
- Document complex business logic
- Keep deployment guides updated
- Document QBrix-specific configurations

---

**Maintenance Note**: When updating these Claude rules, also update:

- `.cursorrules`
- `.cursor/rules/*.mdc` (all Cursor rule files)
- `.windsurf/rules/*.md` (all Windsurf rule files)

**Specific Files:**

- `generaldevelopment` - General Salesforce development best practices
- `apexdevelopment` - Apex-specific guardrails
- `lwcdevelopment` - LWC-specific guardrails
- `brixdevelopment` - Brix development workflow
- `brixrobotframework` - Robot Framework testing
- `brixtechnology` - Technology stack overview
