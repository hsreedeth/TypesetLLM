---
rolepilot_contract: 1
---

# Morgan Lee

Canberra, ACT · [morgan.lee@example.org](mailto:morgan.lee@example.org)

## Selection criteria

### 1. Ability to sustain a complex, multi-year data-quality program

I led a fictional multi-year data-quality program across several service teams that used the same administrative data for different purposes. At the start, the teams disagreed about which records belonged in the monthly report. I documented each interpretation, built a small set of test cases that exposed the differences, and facilitated a decision on a shared definition. I did not overwrite the historical extracts. Instead, I kept a versioned mapping so analysts could reproduce older publications and explain the change to readers. This mattered because a trend that appeared to be a sudden service change was partly the result of a revised coding rule.

The program then moved from a single clean-up effort to a repeatable control process. I wrote validation checks for missing identifiers, impossible dates, duplicate events, and records whose service code did not match the source dictionary. Exceptions were reviewed by the people closest to the service, with a clear route for unresolved cases. Analysts could see both the total and the number of excluded or pending records. Managers received a short note describing which measures were stable and which should be read with caution. Over time, the team reduced manual correction and made it easier for a new analyst to understand the process.

A major challenge was that different teams had different reporting deadlines and levels of technical capacity. I built a simple release calendar, held short review meetings before publication, and maintained plain-language definitions beside the query code. When a late source file arrived, we could decide whether to postpone, publish with a caveat, or issue a corrected report. The choice was recorded rather than hidden. This approach made the process accountable and kept the relationship between analysts and service teams constructive.

### 2. Capacity to communicate uncertainty without losing practical usefulness

I have repeatedly explained why an apparently precise measure may be uncertain. In one evaluation, service leaders asked whether a new pathway had reduced waiting time. The records covered different months, and a booking-system change had altered how cancelled appointments were counted. I showed the unadjusted series first, then a comparable series under a documented rule, and explained the remaining limitations. The adjusted series suggested an improvement, but the observational design did not establish that the pathway alone caused it.

Rather than leaving the group with a technical caveat and no next step, I proposed a short follow-up plan. We identified fields that needed consistent capture, agreed on a stable time window, and chose a small number of outcome measures that clinicians considered meaningful. The report included counts as well as rates, and it explained why small groups were aggregated to protect privacy. The final discussion was more useful because the evidence was neither overstated nor dismissed.

I would use the same method when presenting results to a mixed audience: state the question, show the measure, explain the material limits, and invite people who know the service to challenge the interpretation.


### 3. Experience making a reporting method repeatable across staff changes

A reporting method is durable only when another person can follow it and understand why choices were made. In a fictional public-health evaluation, I inherited a set of scripts with local file paths, undocumented exclusions, and charts that depended on manual edits. I first reproduced the published result, recording each difference between the scripts and the written report. I then replaced the manual steps with parameterised queries, wrote a data dictionary, and added checks for expected row counts and key fields. A colleague who had not worked on the project followed the new guide and identified two ambiguous definitions. We resolved those with the service owner before the next release.

The revised method did not assume that every future analyst would use the same tools. It specified the required inputs, definitions, checks, and outputs in plain language, with executable examples for the team's current software. We stored review notes beside the versioned code so that a decision could be traced without asking the original author. When an upstream system changed, the team could identify which measures were affected and issue a clear note to readers. This reduced the risk that a polished PDF would disguise a broken denominator.

I treat handover as a test of the method rather than an administrative step at the end. I ask the new analyst to find a known exception, explain why it is handled as it is, and reproduce a prior period before preparing a new one. That exercise reveals missing assumptions while they can still be corrected. It also creates a shared language for discussing data quality with managers and clinicians who do not need to inspect every line of code.


I also build review into normal delivery. Before publishing a new measure, I ask a second analyst to check the cohort rule and a service representative to read the label without the methods note. If either cannot explain the result as intended, I revise the measure or its presentation. For a monthly release, I keep the review small and repeatable: source version, record count, missingness, denominator, sample exceptions, and a comparison with the prior period. The resulting report is easier to trust because it records how the number was produced, not because it hides uncertainty behind a clean design.

### 4. Ability to work with service teams on a shared improvement plan

I have worked with teams that used the same data in different ways. In one project, a central group wanted a single measure of follow-up, while local services recorded several distinct kinds of contact. I met with staff who entered the records, asked them to walk through difficult cases, and mapped each local category to the proposed measure. The mapping exposed two cases that could not be combined without changing their meaning. We agreed to publish a common core measure and a short companion breakdown. The result was comparable enough for regional review while still useful to the teams delivering care.

We tested the plan before adopting it. Analysts ran the proposed rule on a small historical sample, service leads checked unexpected records, and a privacy colleague reviewed the breakdown for small groups. I documented the accepted rule, the cases it excluded, and the date from which it applied. I also wrote a plain-language description for readers who would never see the query. When the first release arrived, the team compared it with the old view and explained the difference rather than treating the new number as a direct continuation of the old series.

My contribution was to keep the discussion connected to both the data and the decision it supported. I listened to local concerns, made the trade-offs explicit, and gave people a way to test the result after publication. That process built confidence in the shared measure while preserving a record of its limits and the reasons for the choices we made.
