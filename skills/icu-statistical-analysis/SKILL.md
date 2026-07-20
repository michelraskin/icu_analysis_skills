---
name: icu-statistical-analysis
description: Design and review statistical analyses of longitudinal ICU/EHR data, including predictive model evaluation, p-values, confidence intervals, feature selection, repeated measurements, and subgroup analyses. Use whenever an ICU analysis reports inferential statistics or evaluates a learned model; enforce patient/stay-grouped cross-validation, leakage-safe preprocessing, cluster-aware uncertainty, multiplicity control, and reproducible fold metadata.
---

# ICU statistical analysis

Use all eligible observations without pretending that repeated bins or cross-validation folds are
new independent patients. Define the estimand, index time, outcome horizon, analysis unit, and
clustering unit before fitting.

## Cross-validation standard

- Use grouped cross-validation for every learned-model evaluation and every p-value analysis that
  includes model fitting, tuning, screening, or selection. Keep all rows from a patient in one
  fold; use `stay_id` only when patients cannot recur across stays, otherwise group by patient.
- Prefer 5-fold `StratifiedGroupKFold` for binary/classification outcomes and `GroupKFold` for
  continuous outcomes. Reduce the fold count when events or groups are sparse. Use temporal or
  external validation when deployment requires it.
- Put imputation, scaling, encoding, feature selection, dimensionality reduction, and tuning inside
  each training fold. Use nested grouped CV when hyperparameters or features are selected.
- Generate exactly one out-of-fold prediction or score per eligible observation. Verify that every
  group appears in one test fold, no group crosses train/test, and no row is counted more than once
  in pooled out-of-fold results.
- Prefer pooled grouped OOF evaluation over a fixed internal holdout so every eligible patient is
  tested once. Retain a separate holdout only when it is external, temporal, or explicitly required
  for confirmatory evaluation.
- Report rows, unique patients, unique stays, events, fold-level counts, seed, splitter, grouping
  key, and fold assignments. Persist these with model parameters.

## Valid p-values and confidence intervals

- Do not claim that CV increases the independent sample size. CV uses the available sample more
  efficiently; the effective independent sample size is bounded by independent patients/groups.
- For model-performance comparisons, compute paired differences from out-of-fold predictions and
  derive uncertainty by resampling or permuting whole patients/groups. Never run an unpaired test
  on duplicated predictions from repeated folds.
- For coefficients or treatment effects after data-adaptive nuisance fitting, use grouped
  cross-fitting with an estimator that supports valid orthogonal/influence-function inference
  (for example double/debiased machine learning or targeted learning). Do not attach ordinary
  regression p-values to a variable set chosen on the same data.
- For prespecified longitudinal regressions, use GEE, mixed-effects models, patient-clustered robust
  standard errors, or a patient-level cluster bootstrap as appropriate. Cross-validation does not
  replace correlation-aware inference.
- If fold-specific effects are reported, show their heterogeneity. Do not combine overlapping-fold
  p-values as if independent. Use a justified cross-fitted estimator or group bootstrap for the
  final inferential result.
- Correct families of exploratory tests with Benjamini-Hochberg FDR by default; identify
  prespecified primary tests separately. Report effect sizes and confidence intervals with p-values.

## Longitudinal ICU safeguards

- Split before creating any statistic learned across rows. Compute rolling features using only
  information available at the index time and fit population-level transforms on training folds.
- Treat bins within a stay and multiple stays within a patient as correlated. Use the highest
  repeated-measure grouping level available.
- Preserve censoring, competing-risk, missingness, and eligibility definitions across folds.
- Keep a final untouched external/temporal test set when confirmatory performance is required; use
  grouped CV only within development data.

## Acceptance checks

Require code or assertions demonstrating:

1. no patient/group overlap across train and test in every fold;
2. one out-of-fold result per eligible observation or one predeclared unit-level aggregation;
3. all adaptive preprocessing and tuning occur within training folds;
4. p-value uncertainty is clustered at the patient/group level;
5. fold definitions, seeds, sample counts, methods, and multiplicity corrections are saved;
6. narrative language distinguishes prediction, association, and causal effects.

Fail review when row-wise random CV is used for repeated ICU measurements, fold results are stacked
to inflate `N`, or ordinary p-values follow same-sample feature selection.
