---
description: This rule is for robotframework based tasks where robot automation is required as part of the brix development. It should be used when working in any *.robot file and also considered when working within the cumulusci.yml file
alwaysApply: false
---

## File Storage Location

- .robot files must be stored within ./qbrix_local/robot or a sub-directory of ./qbrix_local/

## Robot File Setup

- Refer to code-snippets for template of robot files here .vscode/brix.code-snippets
- Ensure that the resource is referenced qx/qrobot/keywords/QRobot.resource

## Robot Libraries

- We always use the imported resources from qx/qrobot/keywords/QRobot.resource which contain multiple keywords designed for use in Salesforce user interfaces. These are built on the Browser and BuiltIn RobotFramework libraries.
- All selectors for elements use Playwright formatting
- Do not use the standard Click keyword which clicking an element, use the keyword "Wait And Click" which is designed for Salesforce UI
- When changing the URL location alawys use the "Wait For Page To Load" keyword
