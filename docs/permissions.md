# Permissions Setup

This file tracks all manual permission and visibility configuration required in the target org. These steps cannot be version-controlled via metadata (profiles are gitignored) and must be applied manually after each fresh deploy.

---

## Permission set

**Name:** `NR_Retail_Hub_Demo`  
**How to assign:**
```bash
sf org assign permset --name NR_Retail_Hub_Demo --target-org nr-demo
```
Or in Setup → Permission Sets → NR Retail Hub Demo → Manage Assignments.

**What it grants:**
- Create / Read / Edit / Delete / View All / Modify All on: `Station__c`, `ComplianceCheck__c`, `RetailUnit__c`, `FootfallRecord__c`
- Field-level read + edit on optional fields: `ExternalId__c`, `RiskProfile__c`, `OverallComplianceScore__c`, `ManagedSince__c`, compliance check score/dates/actions, retail unit tenant/size/rent/lease

Note: required fields (picklists, lookups) are excluded — Salesforce does not allow FLS overrides on required fields via permission sets.

---

## App Launcher visibility

The `NR_Retail_Hub` Lightning app is not visible in the App Launcher until the running user's profile has `applicationVisibilities` set for it.

**How to set (Setup UI):**
1. Setup → Apps → App Manager → find **NR Retail Hub** → Edit
2. Under **User Profiles**, move **System Administrator** (or the relevant profile) to Selected
3. Save

**Tab visibility** must also be set so the four tabs appear in the app nav:

1. Setup → Users → Profiles → System Administrator → Edit
2. Under **Custom Tab Settings**, set all four tabs to **Default On**:
   - Station
   - Compliance Check
   - Retail Unit
   - Footfall Record
3. Save

---

## Checklist for a fresh org deploy

| Step | Command / Location | Done |
|---|---|---|
| Deploy metadata | `sf project deploy start --source-dir force-app --target-org <alias>` | |
| Import stations | `sf data import tree --files data/Station__c.json --target-org <alias>` | |
| Import compliance checks | `sf data import bulk --sobject ComplianceCheck__c --file data/ComplianceCheck__c.csv --target-org <alias> --wait 10` | |
| Import retail units | `sf data import bulk --sobject RetailUnit__c --file data/RetailUnit__c.csv --target-org <alias> --wait 10` | |
| Import footfall records | `sf data import bulk --sobject FootfallRecord__c --file data/FootfallRecord__c.csv --target-org <alias> --wait 10` | |
| Assign permission set | `sf org assign permset --name NR_Retail_Hub_Demo --target-org <alias>` | |
| Set app visibility on profile | Setup → App Manager → NR Retail Hub → Edit → add profile | |
| Set tab visibility on profile | Setup → Profiles → [profile] → Custom Tab Settings → set all 4 to Default On | |
