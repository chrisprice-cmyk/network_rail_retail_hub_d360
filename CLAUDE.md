# CLAUDE.md

@./AGENTS.md

## Claude-specific notes

- Metadata goes in `force-app/main/default/`
- Synthetic data files go in `data/` as CSV or JSON tree format for `sf data import tree`
- Deploy with `sf project deploy start`, not CumulusCI — this is a lightweight demo project
- `sfdx-project.json` sourceApiVersion is the single source of truth for API version
