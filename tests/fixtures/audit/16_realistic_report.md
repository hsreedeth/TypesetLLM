---
title: "Synthetic cohort analysis"
author: "Example Analytics Team"
---

# Five-year mortality analysis

Synthetic data for software testing only. We analysed **12,480** participants, with **847** events over **58,231.5** person-years. The adjusted hazard ratio was **1.43 (95% CI 1.21–1.68)**. A β-blocker dose of 5 μg/mL is included only as a typography sentinel.

## Model

$$
h(t\mid x)=h_0(t)\exp(\beta_1x_1+\beta_2x_2)
$$

## Results

| Phenotype | N | Events | HR | 95% CI |
|---|---:|---:|---:|---|
| Cardiometabolic | 6240 | 381 | 1.00 | Reference |
| Ischaemic/cerebrovascular | 3744 | 312 | 1.43 | 1.21–1.68 |
| Respiratory | 2496 | 154 | 1.17 | 0.97–1.41 |

## Reproducible analysis

```r
fit <- coxph(Surv(time, event) ~ phenotype + age + bmi, data = cohort)
summary(fit)
```

## Limitations

These are synthetic estimates.[^note] No inference about patients is intended.

[^note]: Test data created specifically for TypesetLLM evaluation.

END_REPORT_927