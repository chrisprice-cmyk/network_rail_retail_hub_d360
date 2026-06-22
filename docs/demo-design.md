# Network Rail Retail Hub — Demo Design

**Customer:** Network Rail — Commercial Property / Retail Hub  
**Demo date:** 15 July 2026, Waterloo (2 hours)  
**Salesforce AE:** Ashleigh Jordan  
**SE lead (analytics):** Chris Price  

---

## What we are building

A Tableau Next embedded analytics demo that shows Network Rail's Retail Hub team what a unified station intelligence platform looks like — built on Data Cloud (D360) and surfaced through Tableau Next dashboards inside Salesforce.

The core idea: NR already has Retail Hub on Salesforce and Data Cloud licensed. Today their compliance and commercial data lives in spreadsheets and disconnected systems. This demo shows what it looks like when that data is unified into a single station profile in Data Cloud, and explored through interactive dashboards that cover the two pillars that matter most to Vince and Kieran.

---

## The two pillars

### Pillar 1 — Statutory Compliance (lead story)

This is NR's most pressing operational need. Statutory compliance failures carry regulatory and reputational risk. The dashboard answers:

- Which stations are compliant, at risk, or overdue right now?
- Where are the outstanding actions piling up?
- Which check types (EICR, Fire Risk, Sprinklers, COSHH, Cleaning) are the weakest across the estate?
- How does compliance correlate with station type (Cat A / B / C) and region?

Key metrics:
- Overall Station Compliance Score (%)
- EICR Validity Rate
- Fire Risk Assessment status and days to next due
- Fire Alarm & Sprinkler Testing compliance rate
- COSHH Risk Assessment completion rate
- Cleaning Standard pass rate
- Outstanding actions count

### Pillar 2 — Revenue & Commercial (supporting story)

Shows the commercial health of the retail estate alongside compliance — making the case that a single platform can serve both the risk and revenue sides of the Retail Hub remit.

Key metrics:
- Retail unit vacancy rate (%)
- Revenue per square foot
- Footfall trends by station
- Lease expiry pipeline
- Footfall-to-revenue conversion rate

---

## How it is built

### Layer 1 — Salesforce CRM objects (source of truth)

Four custom objects hold the synthetic demo data:

| Object | What it stores |
|---|---|
| `Station__c` | Station profile — name, type (Cat A/B/C), region, overall compliance score, risk profile |
| `ComplianceCheck__c` | Individual inspection records — check type, status, score, dates, outstanding actions |
| `RetailUnit__c` | Commercial units per station — tenant, size, rent, lease expiry, vacancy status |
| `FootfallRecord__c` | Weekly footfall counts per station |

12 stations are loaded covering all NR regions, with deliberate variation in compliance scores and risk profiles to make the dashboard story clear — a clean high-performer like London Waterloo sitting alongside a Critical-rated station like Birmingham New Street.

### Layer 2 — Data Cloud (D360)

Data Cloud ingests the four CRM objects as **Salesforce CRM Connector data streams** and maps them to Data Model Objects (DMOs):

- `Station__c` → `Station` DMO (unified station profile)
- `ComplianceCheck__c` → `Compliance Check` DMO
- `RetailUnit__c` → `Retail Unit` DMO
- `FootfallRecord__c` → `Footfall Record` DMO

The Station DMO acts as the anchor — the others relate back to it via the `Station__c` external ID field. This gives Data Cloud a single unified station record that rolls up compliance, commercial, and footfall signals.

No identity resolution or CDP unification is needed for this demo — the relationships are already clean through the CRM objects. Data Cloud's role here is as the semantic analytics layer that Tableau Next queries.

### Layer 3 — Tableau Next dashboards

Two dashboards embedded in the NR Retail Hub Lightning app:

**Compliance Dashboard**
- Station compliance heatmap (score by station, colour-coded by risk profile)
- Outstanding actions leaderboard (worst stations first)
- Check type breakdown — which check types are failing across the estate
- Filter bar: Station Type / Region / Risk Profile
- Alert list: stations with Overdue or Fail checks requiring immediate action

**Commercial Dashboard**
- Vacancy rate by station and region
- Footfall trend (weekly, last 8 weeks)
- Revenue per sq ft ranking
- Lease expiry timeline (next 12 months)
- Footfall vs revenue scatter (conversion efficiency)

Both dashboards connect to Data Cloud via Tableau Next's native D360 connector — no intermediate extract or CRMA dataset needed.

### Layer 4 — Station record page (to build)

Each Station record page will surface a condensed view of the same metrics from layers 2 and 3, scoped to that individual station. The intent is that a user can navigate from the estate-level dashboard down to a single station record and see the same KPIs in context — no rebuilding vizzes from scratch, just reusing the same Tableau Next published views filtered to the station in context.

**Right column — three embedded Tableau Next vizzes:**
- **Compliance score gauge** — reused from the Compliance Dashboard, filtered to this station. Shows overall score, risk profile colour, and trend vs last quarter.
- **Footfall trend sparkline** — reused from the Commercial Dashboard. Last 8 weeks of weekly footfall for this station only.
- **Retail vacancy snapshot** — reused from the Commercial Dashboard. Unit count, vacancy rate, and next lease expiry for this station.

**Left column — standard record detail plus:**
- Related list: Compliance Checks (most recent first)
- Related list: Retail Units

**Action: Raise Compliance Alert (to build)**

A "Raise Compliance Alert" button on the Station record page (and triggerable from the dashboard). When a user spots an insight in Tableau Next — a station whose compliance score has dropped, an overdue check, a vacancy spike — they click the action, which opens a guided screen flow:

1. **Alert details** — pick alert type (Fire Risk / EICR / Sprinkler / Cleaning / COSHH / Revenue / Vacancy / Other), set priority (Critical / High / Medium), describe the insight in free text.
2. **Confirm** — review before submitting.
3. **Submit** — creates a follow-up Task linked to the Station record, assigned to the current user, with subject "Compliance Alert — [type] at [station name]".

This closes the "insight to action" loop in the demo: you see a problem in the dashboard, you don't just look at it — you raise it, own it, and track it.

**Demo narrative for this moment:**
> "Here's Birmingham New Street. You've already seen it at the bottom of the estate compliance ranking in the dashboard — three failing checks, 18 outstanding actions. Now I'm on the station record. I can see the same compliance score and footfall trend I had in the dashboard, scoped to just this station. And I can see the related checks that are failing. From here I hit 'Raise Compliance Alert' — this is the moment where the insight becomes an action. I pick the check type, set it to Critical, describe what I'm seeing, and submit. That creates a task on this record, assigned to me, so it lives in Salesforce alongside everything else. The dashboard told me there was a problem. The record page told me the detail. The action made sure someone owns it."

---

## Demo flow (Waterloo, 15 July)

1. **Open the app** — land on the Compliance Dashboard. Vince and Kieran see the estate at a glance.
2. **Filter to London stations** — show the regional view, call out the two stations with Critical risk.
3. **Drill into Birmingham New Street** — three failing/overdue checks, 18 outstanding actions. This is the "burning platform" moment.
4. **Navigate to the station record** — click through from the dashboard to the Birmingham New Street record page. The same compliance score and footfall trend appear in the right column, scoped to this station. The related compliance checks confirm the failures.
5. **Raise a Compliance Alert** — hit the action button, walk through the flow: pick EICR as the type, set Critical priority, describe the overdue test. Submit. Show the Task created on the record. "The dashboard found it. The record confirmed it. The action owns it."
6. **Flip to Commercial Dashboard** — show vacancy rate sitting at 15% across the estate, footfall-to-revenue gap at underperforming stations.
7. **The ask** — "This is one unified view of your estate — compliance, commercial, and footfall, all in one place, with action built in. Today it runs on synthetic data; in a real deployment it connects directly to your Salesforce Retail Hub and footfall feeds. The next step is a scoping conversation with Kieran's team."

---

## What is not in scope

- **Agentforce** (policy search, retailer onboarding, web-to-case) — owned by Richard Steer, separate track
- **PSS module** — removed from NR shelfware; compliance tracking uses custom objects only
- **Real NR data** — demo runs on synthetic data until NR sandbox access is confirmed
- **GBR ~200 station rollout** — framed as the vision, not built in this demo

---

## Repo structure

```
network_rail_retail_hub_d360/
├── force-app/main/default/
│   ├── applications/        # NR Retail Hub Lightning app
│   ├── objects/             # Station__c, ComplianceCheck__c, RetailUnit__c, FootfallRecord__c
│   ├── tabs/                # Custom tabs for each object
│   ├── permissionsets/      # NR_Retail_Hub_Demo
│   ├── profiles/            # Admin profile (app + tab visibility)
│   ├── flexipages/          # Station__c record page (to build)
│   ├── flows/               # Raise_Compliance_Alert screen flow (to build)
│   └── quickActions/        # Station__c.Raise_Compliance_Alert (to build)
├── data/
│   ├── Station__c.json      # 12 stations (sf data import tree)
│   ├── ComplianceCheck__c.csv  # 20 records (sf data import bulk)
│   ├── RetailUnit__c.csv       # 20 records (sf data import bulk)
│   └── FootfallRecord__c.csv   # 20 records (sf data import bulk)
└── docs/
    └── demo-design.md       # This file
```

## Deploy commands

```bash
# Deploy all metadata
sf project deploy start --source-dir force-app --target-org nr-demo

# Load stations first (JSON tree — no external ID dependency)
sf data import tree --files data/Station__c.json --target-org nr-demo

# Load child objects (CSV bulk — uses Station__r.ExternalId__c relationship)
sf data import bulk --sobject ComplianceCheck__c --file data/ComplianceCheck__c.csv --target-org nr-demo --wait 10
sf data import bulk --sobject RetailUnit__c --file data/RetailUnit__c.csv --target-org nr-demo --wait 10
sf data import bulk --sobject FootfallRecord__c --file data/FootfallRecord__c.csv --target-org nr-demo --wait 10
```
