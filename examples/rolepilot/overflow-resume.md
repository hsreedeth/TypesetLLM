---
rolepilot_contract: 1
target_role: Principal Health Informatics Analyst
---

# Alexandra-Maryana Chen-Williams-Singh

Greater Western Sydney, NSW · [alexandra.maryana.chen.williams.singh@example.org](mailto:alexandra.maryana.chen.williams.singh@example.org) · [https://portfolio.example.org/alexandra-maryana-chen-williams-singh/health-data-governance-and-reproducible-analysis](https://portfolio.example.org/alexandra-maryana-chen-williams-singh/health-data-governance-and-reproducible-analysis)

## Experience

### Principal Health Informatics Analyst · Western Regional Community Health and Integrated Care Partnership · January 2015–October 2026

- Designed and maintained a longitudinal reporting pipeline covering referrals, appointments, care plans, and outcomes across metropolitan and regional services. The work included mapping inconsistent historical codes, documenting every change to cohort definitions, and presenting limitations to clinicians before any figures were used in planning.
- Built automated checks for incomplete dates, duplicate records, unexpected currency values such as $1,250 and £900, and names containing accents such as José and Zoë. Exceptions remained visible for review instead of disappearing from published totals.
- Led a long, cross-functional consultation with service managers, nurses, allied-health staff, privacy officers, and analysts. The group reviewed draft measures, tested edge cases, and agreed on plain-language descriptions that could travel with the report when it was forwarded beyond the original audience.
- Prepared technical notes and training materials explaining the query logic, access controls, and release process. A new analyst could reproduce the monthly report from the approved source without relying on undocumented manual steps.

## Additional work

In a regional access review, I compared referral volumes and wait times across service types while accounting for changed clinic boundaries and a new booking system. I retained the original records, joined them through documented keys, and checked whether missing values were concentrated in particular services. The first view suggested a large disparity, but a denominator change explained part of it. I presented both the unadjusted and comparable series so decision-makers could see the effect of the correction. I also met with representatives from smaller communities to understand whether aggregation obscured meaningful differences. The final report explained where evidence was strong, where uncertainty remained, and which questions required fresh data. It was designed to support a careful service conversation, not to make a clinical determination. The written method described each filter, transformation, and suppression rule so the analysis could be repeated when new months arrived.


### Data Standards Lead · Regional Health Analytics Consortium · 2010–2015

- Coordinated a shared dictionary for ten services that had developed different meanings for the same encounter status. The work required careful review of old reports, meetings with data stewards, and tests that showed how revised codes affected each published measure.
- Built reproducible quality summaries that highlighted missing values and date conflicts by source, month, and service. Rather than assigning blame, the summaries made it easier for each team to correct upstream capture and verify the change in the next extract.
- Wrote a handover guide explaining the release calendar, roles, review points, and escalation path for unresolved anomalies. This helped the consortium sustain the reporting process when staff changed.

## Education and methods

**Master of Health Informatics**, Fictional State University, 2010. **Bachelor of Science (Statistics)**, Fictional Coastal University, 2007. Methods include cohort construction, audit trails, SQL, Python, R, and privacy-aware visualisation.


## Selected projects

### Community referral pathway review

I prepared a comparative analysis of referrals and follow-up appointments after a new pathway was introduced. The source data changed during the review period, so I recorded which measures could be compared directly and which needed a revised mapping. I used record-level checks to understand unexpected values, discussed the interpretation with clinicians, and reported both absolute numbers and rates. The final paper separated observed associations from causal claims and proposed a small set of fields to capture more consistently in the next cycle.

### Accessible reporting and handover

I redesigned a monthly report so readers could find definitions and caveats beside the figures they qualified. I replaced shorthand labels with plain language, retained links to technical notes, and asked service managers to test draft charts against questions they actually received from staff. For handover, I wrote a reproducible method covering source versions, validation checks, aggregation rules, and publication steps. A colleague reproduced a prior release from the guide and raised two ambiguities that we resolved before the next cycle.

### Regional data release process

I coordinated a quarterly release used by teams in five regions. Each region supplied data on a different schedule, so I published a cut-off date, checked late records against the previous extract, and marked measures that would be revised in the next release. A short review meeting let service leads identify coding changes before the figures became public. I kept the published dataset, query version, and decision log together. When a reader later questioned a sharp change in one measure, the team could reproduce the figure and show that a new intake code had moved records between categories. We corrected the comparison and described the change in ordinary language.

## Professional practice

I routinely review code and documentation with another analyst, check output against source totals, and record limitations where readers will see them. I use accessible colours and labels, avoid small-cell disclosures, and keep a clear distinction between operational monitoring and clinical decision-making. These habits make the work easier to challenge and improve when new evidence arrives.

I also plan for continuity. A release is not complete until another person can find the source, understand the cohort, rerun the checks, and explain any exceptions. I keep a concise handover note with the current owner, next review date, open data-quality questions, and links to approved methods. This has helped teams continue reporting through staff changes without treating a previous PDF as the only record of how a result was made.
