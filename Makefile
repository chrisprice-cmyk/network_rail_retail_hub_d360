.PHONY: help precommit lockfiles check-lockfiles-clean \
	npm-lock npm-ci npm-lint npm-test \
	check-tools check-rules-sync

SHELL := /bin/sh

help:
	@printf "%s\n" "Targets:" \
	"  make precommit              Run repo pre-commit checks (lockfiles + tooling checks + optional lint/tests)" \
	"  make lockfiles              Regenerate lockfiles (currently: npm package-lock.json if package.json exists)" \
	"  make check-lockfiles-clean  Fail if regenerated lockfiles are not staged (prevents committing without lockfile updates)" \
	"  make check-tools            Verify required CLI tools are installed (sf, cci, qx)" \
	"  make check-rules-sync       Verify LLM rule surfaces exist (Cursor/Claude/Gemini/Windsurf)" \
	"" \
	"Node/npm (only runs if package.json exists):" \
	"  make npm-lock               Update package-lock.json (does not install node_modules)" \
	"  make npm-ci                 Install node_modules from lock (CI-safe) " \
	"  make npm-lint               Run npm script 'lint' if present" \
	"  make npm-test               Run npm script 'test' if present"

precommit: lockfiles check-lockfiles-clean check-tools check-rules-sync npm-lint npm-test
	@printf "%s\n" "Precommit checks completed."

lockfiles: npm-lock
	@true

check-lockfiles-clean:
	@# Fail if lockfiles changed but are not staged.
	@# - Allowed: staged changes (XY like 'M ' or 'A ')
	@# - NOT allowed: unstaged changes or untracked (worktree status char != ' ')
	@if [ -f package-lock.json ]; then \
		status="$$(git status --porcelain -- package-lock.json)"; \
		if [ -n "$$status" ]; then \
			echo "$$status" | awk '{ if (substr($$0,2,1) != " ") exit 2 }'; \
			rc="$$?"; \
			if [ "$$rc" -ne 0 ]; then \
				printf "%s\n" "ERROR: package-lock.json changed but is not staged." \
					"Run: git add package-lock.json"; \
				exit "$$rc"; \
			fi; \
		fi; \
	fi

check-tools:
	@missing=""; \
	for cmd in sf cci qx; do \
		if ! command -v $$cmd >/dev/null 2>&1; then \
			missing="$$missing $$cmd"; \
		fi; \
	done; \
	if [ -n "$$missing" ]; then \
		printf "%s\n" "ERROR: Missing required CLI tool(s):$$missing" \
			"Install them (or use the devcontainer) before committing."; \
		exit 2; \
	fi

check-rules-sync:
	@# Ensure the expected project-level rule surfaces exist.
	@for p in .cursorrules .cursor/rules .claude/memory.md .gemini/rules .windsurf/rules; do \
		if [ ! -e "$$p" ]; then \
			printf "%s\n" "ERROR: Expected rules path missing: $$p"; \
			exit 2; \
		fi; \
	done
	@# Ensure the repo-specific synchronization section exists where expected (keeps humans honest).
	@for f in .cursorrules .cursor/rules/brixdevelopment.mdc .claude/memory.md .gemini/rules/brix_development.md .windsurf/rules/brixdevelopment.md; do \
		if ! grep -q "LLM Rule Synchronization (Required)" "$$f"; then \
			printf "%s\n" "ERROR: Missing 'LLM Rule Synchronization (Required)' section in $$f"; \
			exit 2; \
		fi; \
	done
	@# Ensure hardcoded API-version guidance matches the project config.
	@api_version="$$(sed -n 's/^[[:space:]]*api_version:[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}[[:space:]]*$$/\1/p' cumulusci.yml | head -n 1)"; \
	source_api_version="$$(sed -n 's/.*"sourceApiVersion":[[:space:]]*"\([^"]*\)".*/\1/p' sfdx-project.json | head -n 1)"; \
	if [ -z "$$api_version" ] || [ -z "$$source_api_version" ]; then \
		printf "%s\n" "ERROR: Unable to read API versions from cumulusci.yml and sfdx-project.json"; \
		exit 2; \
	fi; \
	if [ "$$api_version" != "$$source_api_version" ]; then \
		printf "%s\n" "ERROR: API version mismatch: cumulusci.yml=$$api_version sfdx-project.json=$$source_api_version"; \
		exit 2; \
	fi; \
	for f in .cursorrules .claude/memory.md .cursor/rules/brixdevelopment.mdc .cursor/rules/brixtechnology.mdc .gemini/rules/brix_development.md .gemini/rules/brix_technology.md .windsurf/rules/brixdevelopment.md .windsurf/rules/brixtechnology.md; do \
		if ! grep -q "$$api_version" "$$f"; then \
			printf "%s\n" "ERROR: Expected API version $$api_version in $$f"; \
			exit 2; \
		fi; \
	done
	@# Ensure mirrored split rules have identical content after stripping tool metadata.
	@normalize_rule() { awk 'NR==1 && $$0=="---"{fm=1; next} fm && $$0=="---"{fm=0; next} !fm{print}' "$$1" | sed '/./,$$!d'; }; \
	for mapping in \
		apexdevelopment:apexdevelopment:apex_development \
		brixdevelopment:brixdevelopment:brix_development \
		brixrobotframework:brixrobotframework:brix_robot_framework \
		brixtechnology:brixtechnology:brix_technology \
		generaldevelopment:generaldevelopment:general_development \
		lwcdevelopment:lwcdevelopment:lwc_development; do \
		cursor="$${mapping%%:*}"; \
		rest="$${mapping#*:}"; \
		windsurf="$${rest%%:*}"; \
		gemini="$${rest#*:}"; \
		tmp_cursor="$$(mktemp)"; \
		tmp_other="$$(mktemp)"; \
		normalize_rule ".cursor/rules/$$cursor.mdc" > "$$tmp_cursor"; \
		normalize_rule ".windsurf/rules/$$windsurf.md" > "$$tmp_other"; \
		if ! diff -q "$$tmp_cursor" "$$tmp_other" >/dev/null; then \
			printf "%s\n" "ERROR: Rule drift between .cursor/rules/$$cursor.mdc and .windsurf/rules/$$windsurf.md"; \
			rm -f "$$tmp_cursor" "$$tmp_other"; \
			exit 2; \
		fi; \
		normalize_rule ".gemini/rules/$$gemini.md" > "$$tmp_other"; \
		if ! diff -q "$$tmp_cursor" "$$tmp_other" >/dev/null; then \
			printf "%s\n" "ERROR: Rule drift between .cursor/rules/$$cursor.mdc and .gemini/rules/$$gemini.md"; \
			rm -f "$$tmp_cursor" "$$tmp_other"; \
			exit 2; \
		fi; \
		rm -f "$$tmp_cursor" "$$tmp_other"; \
	done

# -----------------------
# Node/npm (optional)
# -----------------------

NPM ?= npm

npm-lock:
	@if [ -f package.json ]; then \
		$(NPM) install --package-lock-only --no-audit --no-fund || \
		(printf "%s\n" "Retrying with --legacy-peer-deps due to peer dependency conflict..." && \
		$(NPM) install --package-lock-only --no-audit --no-fund --legacy-peer-deps); \
	else \
		printf "%s\n" "Skipping npm lockfile generation (no package.json found at repo root)."; \
	fi

npm-ci:
	@if [ -f package.json ]; then \
		$(NPM) ci --no-audit --no-fund || \
		(printf "%s\n" "Retrying with --legacy-peer-deps due to peer dependency conflict..." && \
		$(NPM) ci --no-audit --no-fund --legacy-peer-deps); \
	else \
		printf "%s\n" "Skipping npm ci (no package.json found at repo root)."; \
	fi

npm-lint:
	@if [ -f package.json ]; then \
		script="$$( $(NPM) pkg get scripts.lint 2>/dev/null || echo null )"; \
		if [ "$$script" != "null" ] && [ "$$script" != "\"\"" ]; then \
			$(NPM) run -s lint; \
		else \
			printf "%s\n" "Skipping npm lint (no scripts.lint found)."; \
		fi; \
	else \
		printf "%s\n" "Skipping npm lint (no package.json found at repo root)."; \
	fi

npm-test:
	@if [ -f package.json ]; then \
		script="$$( $(NPM) pkg get scripts.test 2>/dev/null || echo null )"; \
		if [ "$$script" != "null" ] && [ "$$script" != "\"\"" ]; then \
			$(NPM) run -s test; \
		else \
			printf "%s\n" "Skipping npm test (no scripts.test found)."; \
		fi; \
	else \
		printf "%s\n" "Skipping npm test (no package.json found at repo root)."; \
	fi
