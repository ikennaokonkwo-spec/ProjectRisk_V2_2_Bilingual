# Language and simulation state verification

This release adds language-independent session storage and background numerical jobs. The prior highlighting/irrigation/AOA-AON release is retained under `baseline/previous_corrected_release.zip`. Its detailed workbook and diagram verification is retained in `PREVIOUS_CORRECTED_VERIFICATION_REPORT.md`.

## Current checks

All **16 test scripts** in `run_tests.py` passed on Python 3.12 with `requirements-verified.txt`. See `state_full_suite.log`.

The dedicated state-retention workflow makes **32 repeated language switches**: before simulation, during main simulation, during Risk Portrait construction, during treatment simulation, after completed outputs, and while treatment controls are hidden. Each active-job check pauses inside the real numerical calculation, after a CPM calculation, while switching languages. It verifies the same Future and a single invocation of the submitted calculation. After release, calculation resumes and completes. There is no second submission or reseeding caused by a language change.

The original canonical project, activity and risk iteration frames match a synchronous simulation exactly at 100 iterations and seed 73. Every saved main-result frame, Risk Portrait summary/scenario frame and treatment-result/comparison frame remains exactly equal across subsequent language switches. Non-default iterations, seed and AOA selection survive; activity selection, ST curve state, single/multiple treatment selections and all three per-risk edits survive. The upload snapshot remains usable even when the uploader returns no object on a rerun without an explicit removal event.

Session-job tests cover stale running jobs after a workbook change, errors without replacing saved results, duplicate submission prevention, completed-result availability until commit acknowledgement, explicit upload removal, and canonical tab position/expander restoration. A completed job remains available until all state writes are acknowledged, so an intervening language rerun can repeat the commit safely.

The existing six-profile bilingual workflow passes for both general templates, both all-eight-distribution fixtures and both irrigation inputs, including simulation, Risk Portrait, single/multiple treatments, stale-comparison invalidation, language switching and AON/AOA toggles. UI tests now wait for real background jobs to complete before asserting their outputs; no synchronous production-only/test-only calculation branch was added.

## Preserved calculations and inputs

All **15** Python modules in `core/` and `data_io/`, and all **six** packaged Excel workbooks, are byte-identical to the preceding corrected release. See `STATE_PRESERVATION.json`. This retains its numerical assumptions, distributions, RNG, costs, CPM, diagnostics, exports, Excel formulas, validations, distribution-sensitive highlights and original colors. Existing numerical-equivalence and native spreadsheet QA reports remain included as prior evidence; no spreadsheet was edited in this change.

Workers execute the same existing numerical functions. Source inputs/specifications are captured once; completed baseline frames are shared read-only, avoiding an additional large result copy. A session uses one worker, and locale changes do not add numerical work. Workbook parsing is cached by content digest. No claim is made that interface response time is identical to the synchronous UI; completion polling adds up to approximately half a second under normal scheduling.

## Scope

State is retained within the same active Streamlit session. This release does not add persistence across server restart or a newly created browser session. Genuine workbook/settings/scenario changes still invalidate incompatible outputs. Workers that belong to an obsolete project may finish, but their results cannot be committed to the replacement project. See `SESSION_STATE_EN_PT_BR.md` for both languages.
