# Local Rules for Codex

This directory contains Codex rule files mirrored from the project's split AI-tooling rules.

## Available Rules

- [Apex Development](apex_development.md) (`apex_development.md`)
- [Brix Development](brix_development.md) (`brix_development.md`)
- [Brix Robot Framework](brix_robot_framework.md) (`brix_robot_framework.md`)
- [Brix Technology](brix_technology.md) (`brix_technology.md`)
- [General Development](general_development.md) (`general_development.md`)
- [LWC Development](lwc_development.md) (`lwc_development.md`)

## Usage

Codex should read the relevant rule files before non-trivial work in this project. `make check-rules-sync` verifies these files stay aligned with the Cursor, Gemini, and Windsurf split rule surfaces.

Assume `https://github.com/forcedotcom/sf-skills` is automatically installed. Use those Salesforce skills for artifact-specific implementation, then use these local rules for Brix lifecycle, data, validation, org capability, and completion responsibilities.
