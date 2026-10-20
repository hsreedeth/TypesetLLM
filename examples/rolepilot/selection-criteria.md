---
rolepilot_contract: 1
target_role: Senior Health Data Analyst
target_employer: North Coast Health Network
---

# Avery Chen

Sydney, NSW · [avery.chen@example.org](mailto:avery.chen@example.org) · [+61 400 123 456](tel:+61400123456)

## Selection criteria

### 1. Demonstrated experience analysing complex health data and communicating findings

At Harbour Health Network, I was responsible for a monthly service report spanning 18 community clinics and three outreach teams. The source systems recorded referrals, appointments, and outcomes differently, so a single chart could be misleading unless the underlying cohort and timing rules were explicit. I met with clinical leads to agree on the questions they needed answered, wrote definitions for each measure, and built a SQL pipeline with Python checks that recorded missing or inconsistent values. I retained exceptions for review rather than silently dropping them.

The initial report showed an apparent rise in missed appointments. Before presenting it, I checked whether a booking-system change had altered the denominator. It had. I recalculated the series on a comparable basis and explained both views to the service managers. They could then focus on the clinics where the pattern remained after adjustment. The team used the report to plan targeted follow-up while keeping the uncertainty visible. This experience reinforced my practice of checking measurement changes before drawing conclusions from trends.

For a regional telehealth evaluation, I compared operational extracts across six services and documented the analysis plan before examining outcomes. I reported counts, rates, and confidence intervals together, and I explained why the observational design could not establish causality. Clinical leads used the findings to identify where additional follow-up appointments might be useful. My written summary included the limitations, so it could be read independently of my presentation.

### 2. Ability to improve data quality, reproducibility, and privacy-aware delivery

At Southern Community Care, I inherited a registry of approximately 85,000 records used for weekly reporting. Priority fields were incomplete, identifiers were inconsistent, and manual spreadsheet steps made it hard to trace changes. I mapped each source field, wrote validation checks in SQL and Python, and produced a report of exceptions for the service owners to resolve. I kept source values available and made every transformation visible in a versioned notebook.

Over the following reporting cycles, completeness of priority fields improved from 88% to 97%. The extract became repeatable without depending on one analyst's notes. I also worked with privacy and security colleagues to move the workflow from emailed spreadsheets to approved dashboards with role-based access. We tested that users could see only the level of detail needed for their work. Where small groups could risk re-identification, the published view used appropriate aggregation and withheld the detailed breakdown.

At Harbour Health Network, I applied the same principles to a new patient-flow dashboard. I wrote definitions before implementation, asked another analyst to review the query, and included checks for duplicate referrals, missing dates, and changes to service codes. We resolved 1,200 historical exceptions and documented those still open. This approach gave managers a more dependable trend and gave analysts a clear route to investigate surprising results.

### 3. Strong collaboration with clinical and non-technical stakeholders

I start a reporting project by asking what decision the information needs to support. For the community-clinic dashboard, nurses wanted to know which referrals required action, while managers needed a consistent monthly comparison. I ran short workshops with both groups, tested draft views against real examples, and changed labels that were technically accurate but easily misunderstood. The final report used counts alongside rates and placed caveats next to the charts they qualified.

When a metric showed a sharp change after a coding update, I met with the service owner and analyst responsible for the extract before reporting it. We traced the change to a new service code, corrected the mapping, and recorded the change in the data dictionary. I then explained the revised series and its limits in plain language. The discussion kept the team focused on the actual service pattern rather than a reporting artefact.

I have also coached four analysts in peer review and accessible communication. We used short review checklists for cohort definitions, missing data, and chart labels, and we practised explaining results without overstating them. My aim is to make technical work easy to question and improve. That has helped clinical colleagues trust the analysis while remaining alert to uncertainty and exceptions.


### 4. Capacity to manage delivery while maintaining clear documentation

For the monthly community-clinic report, I coordinated a predictable release process across data owners, analysts, and service managers. Before each cycle, I confirmed source availability and checked whether definitions or coding practices had changed. The analyst responsible for the extract ran automated checks, and a second analyst reviewed the query and a sample of exceptions. I recorded material differences from the previous month so that readers could distinguish a service change from a reporting change.

When a new booking-system release altered the way cancelled appointments were recorded, we did not rush a revised trend into the dashboard. I worked with the system owner to understand the change, tested the mapping on examples supplied by clinic staff, and published a short methods note beside the corrected series. The note explained the old and new definitions and which comparisons remained reliable. Managers could then use the report for planning while understanding why some historic figures had been revised.

I keep documentation close to the work. The data dictionary names each source field and transformation; release notes explain changes in measures; and the dashboard itself links to the definitions people need when they see a surprising result. This structure has supported handover between analysts and made it easier for clinical colleagues to raise useful questions.

### 5. Commitment to ethical and accessible use of health information

I treat privacy and accessibility as design requirements rather than final checks. In the appointment-access project, I reviewed proposed breakdowns with information-governance colleagues to identify where a small group might be recognisable. We used aggregation for the published view and limited detailed records to people with a clear service need and approved access. I documented the trade-off so that readers understood why some requested detail was not available.

I also tested the language and visual structure of reports with people who would use them. A chart labelled with a technical service code was accurate to the database but unhelpful to a clinical manager; a revised plain-language label, paired with the code in the methods note, served both audiences. I used counts beside rates and avoided colour as the only way to distinguish categories. The aim was to help people make responsible decisions from the information, including knowing when the data did not support a conclusion.
