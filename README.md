# Network Rail Retail Hub — Tableau Next + Data Cloud Demo

Salesforce demo project for Network Rail's Commercial Property / Retail Hub team.

**Demo date:** 15 July 2026, Waterloo  
**Owner:** Chris Price (chrisprice@salesforce.com)  
**Team:** Neil Hutchinson, Richard Steer, Ashleigh Jordan

## What this is

A Tableau Next analytics demo powered by Data Cloud (D360), showing a unified station compliance and commercial dashboard across Network Rail's 19 managed stations — with a view to scaling to ~200 under Great British Railways.

## Demo story

1. Data Cloud unifies Retail Hub Salesforce data + footfall data into a single station profile
2. Tableau Next dashboard — Statutory Compliance as lead pillar, Revenue/Commercial secondary
3. Station-level slicing by Station Type (Cat A/B/C), Geographic Region, and Risk Profile

## Repo structure

```
force-app/main/default/   Salesforce metadata (objects, fields, permission sets)
data/                     Synthetic CSV data for demo seeding
sfdx-project.json         Salesforce DX config
```

## Deploy

```bash
sf org login web --alias nr-demo
sf project deploy start --target-org nr-demo
sf data import tree --files data/Station__c.json --target-org nr-demo
```

## Key objects

| Object | Purpose |
|---|---|
| `Station__c` | Station profile — name, type (Cat A/B/C), region |
| `ComplianceCheck__c` | Inspection records — type, status, score, due date |
| `RetailUnit__c` | Commercial units — sqft, tenant, lease expiry, revenue |
| `FootfallRecord__c` | Daily/weekly footfall counts per station |
