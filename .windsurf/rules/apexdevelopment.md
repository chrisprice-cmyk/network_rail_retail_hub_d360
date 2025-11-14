# Apex Development Guardrails

## Naming Conventions

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

## General Requirements

- Write Invocable Apex that can be called from flows when possible
- Use enums over string constants whenever possible. Enums should follow `ALL_CAPS_SNAKE_CASE` without spaces
- Use Database Methods for DML operations with exception handling
- Use Return Early pattern
- Use ApexDocs comments to document Apex classes for better maintainability and readability

## Apex Triggers Requirements

- Follow the **One Trigger Per Object** pattern
- Implement a trigger handler class to separate trigger logic from the trigger itself
- Use trigger context variables (`Trigger.new`, `Trigger.old`, etc.) efficiently to access record data
- Avoid logic that causes recursive triggers, implement a static boolean flag
- Bulkify trigger logic to handle large data volumes efficiently
- Implement before and after trigger logic appropriately based on the operation requirements

## Governor Limits Compliance Requirements

- **Always write bulkified code** - never perform SOQL/DML operations inside loops
- Use collections for bulk processing
- Implement proper exception handling with try-catch blocks
- Limit SOQL queries to 100 per transaction
- Limit DML statements to 150 per transaction
- Use `Database.Stateful` interface only when necessary for batch jobs

## SOQL Optimization Requirements

- Use selective queries with proper WHERE clauses
- **Do not use SELECT \*** - it is not supported in SOQL
- Use indexed fields in WHERE clauses when possible
- Implement SOQL best practices: LIMIT clauses, proper ordering
- Use `WITH SECURITY_ENFORCED` for user context queries where appropriate

## Security & Access Control Requirements (Demo Environment Context)

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

## Prohibited Practices

- ❌ No hardcoded IDs or URLs
- ❌ No SOQL/DML operations in loops
- ❌ No `System.debug()` statements in production code
- ❌ No `@future` methods from batch jobs
- ❌ No recursive triggers
- ❌ **Never use or suggest `@future` methods for async processes**. Use queueables and always suggest implementing `System.Finalizer` methods

## Required Patterns

- Use **Builder pattern** for complex object construction
- Implement **Factory pattern** for object creation
- Use **Dependency Injection** for testability
- Follow **MVC pattern** in Lightning components
- Use **Command pattern** for complex business operations

## Unit Testing Requirements

- Maintain minimum **75% code coverage**
- Write meaningful test assertions, not just coverage
- **Use `System.Assert` class** for all assertions (not deprecated `System.assert` methods)
  - Use `Assert.areEqual()`, `Assert.isTrue()`, `Assert.isFalse()`, etc.
- Use `Test.startTest()` and `Test.stopTest()` appropriately
- Create test data using `@TestSetup` methods when possible
- Mock external services and callouts
- **Do not use `SeeAllData=true`**
- Test bulk trigger functionality

## Test Data Management Requirements

- Use `Test.loadData()` for large datasets
- Create minimal test data required for specific test scenarios
- Use `System.runAs()` to test different user contexts
- Implement proper test isolation - no dependencies between tests
