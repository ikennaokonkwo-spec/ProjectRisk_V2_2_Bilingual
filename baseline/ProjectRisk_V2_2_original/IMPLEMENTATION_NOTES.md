# Project Risk Analysis V2.2

Run `python -m pip install -r requirements.txt`, then `python -m streamlit run app2_2.py` from this folder. The launch scripts now reference this entry point. Run `python run_tests.py` for calculation, integration and Streamlit workflow checks.

## Cost model

Activity final cost is max(0, fixed cost + cost rate × final activity duration + direct risk cost). Each activity's own duration drives its time costs; idle time between activities and whole-project overhead rates are not included. All rates use the Project sheet's Time_Unit, and all costs use Currency.

The populated V2.2 classroom case splits each original activity budget between a fixed component and an illustrative time-dependent portion. At the expected reference duration the original budget is preserved within rounding tolerance. The case document does not specify these shares, ratings or treatment effectiveness; all are explicitly illustrative. Case_Assumptions calculates the split through live formulas. Legacy Base_Cost workbooks remain readable. Legacy intrinsic cost distributions also remain supported; their sampled duration-independent cost replaces the fixed component.

Relative direct cost impacts use the baseline cost including baseline duration-related costs. Absolute direct cost impacts are additional financial consequences. Do not map the same time-based expense again as a direct cost. Activity exports show fixed, time-dependent and direct cost components; a zero floor may prevent their unadjusted sum from equalling the final cost when an opportunity exceeds all expenses.

## Register and response planning

The register preserves existing risks, categories and responses. New optional fields support separate schedule/cost impact assessments, rationale, response owner/date, residual probability/impacts and acceptance. Active=false keeps a risk documented but excludes its occurrence from the main simulation and treatment selector; its probability may be blank. Core identification/type/scope fields remain required.

Category definitions are editable working conventions, not an external classification standard. Initial impact ratings are 1 very low, 2 low, 3 moderate, 4 high and 5 very high. Define concrete project-specific consequences in Assessment_Rationale. Probability × impact is an ordinal screening aid, separately for cost and schedule. Missing ratings produce missing scores, not zero. No automatic acceptance threshold is imposed. Threats and opportunities should be interpreted in their respective directions.

Response_Action now accepts descriptive text. Original strategy-only values are preserved and trigger non-blocking warnings. Acceptance remains a human decision; incomplete documentation is flagged. Register CSV exports include simulation findings but do not overwrite the input workbook.

## Treatment scenarios

Risk_Treatments is optional. It accepts one row per active risk: Treated_Probability, Duration_Impact_Multiplier, Cost_Impact_Multiplier and Assumption_Rationale. Blank probability retains the input value; blank multipliers mean 1. These values initialise app controls. Select risks and explicitly run the comparison; the app does not treat every populated row automatically. The exported treatment assumptions record the controls actually used.

Duration and direct-cost multipliers are independent. Changes to duration automatically change rate-based costs. Changes to the controls clear an obsolete comparison. Residual register fields are documentation and never silently replace simulation assumptions.

## Diagnostics and Risk Portrait

Risk importance retains the original Pearson occurrence/project-outcome correlations. Activity cruciality retains Spearman activity-duration/project-duration correlation. Negative associations remain visible; absolute risk associations determine ranking. Constant-variable associations display zero for compatibility, and must not be read as evidence that a deterministic risk has no effect. Realized risk cost impacts are direct mapped costs; duration-related changes are separately available at activity level.

Every portrait curve represents total project duration under a specified risk subset. S0 has activity uncertainty only. The focused chart retains the top-four cumulative scenarios and offers ST (all active risks), on by default. Hiding ST can improve curve separation. The full scenario table remains available. ST reuses the existing complete simulation; intermediate scenarios are still simulated with common random numbers. Large complete portraits can still take time.

Risk-to-risk propagation, within-activity risk timing, new uncertainty typologies and more sophisticated probability models remain deferred. Risk_Relationships is inactive. Existing Uniform probability support is retained for compatibility, not expanded.

## Verification

The suite includes deterministic cost accounting, independent treatment dimensions, opportunity cost floors, shared risk occurrences, inactive risks, legacy workbook compatibility, invalid rates, portrait-result reuse, existing core/treatment/integration tests, and a Streamlit upload–simulate–portrait–treat workflow with stale-comparison invalidation. Workbook layouts were visually inspected through rendered previews. The desktop Excel interface has not been exercised.

## Populated construction example

All 30 activities have live linked cost calculations; 24 have illustrative time rates and six demonstrate fixed-price packages. All 24 risks have initial schedule/cost ratings, concrete responses, response owners, relative deadlines and post-response assumptions. Risk_Treatments contains proposals for all 24 risks. Opportunity proposals increase benefit likelihood or magnitude. Only selected risks are treated by the app. Treatment implementation costs are not priced.

The source uses generic time and monetary units, so the workbook does too. No actual calendar dates are invented. Original targets remain 150 time units and 900,000 monetary units; the original reference activity cost sum is 1,057,000, already above that cost target. This pre-existing target/budget mismatch is preserved for classroom discussion.

All residual acceptance fields remain Pending. Original lifecycle statuses and Active flags are preserved. Case_Assumptions is now live and linked to Activities. Edit Original_Base_Cost and Time_Dependent_Share there, and select Cost_Association in Activities. Reference durations update from activity duration inputs.

## Live cost formulas and fixed-price packages

Activities has a Cost_Association dropdown. Fixed only sets cost rate to zero and the full original budget becomes fixed cost. Fixed + time uses ROUND(original budget × time share / reference duration, 2). Fixed cost is ROUND(original budget − rate × reference duration, 2). Case_Assumptions contains these formulas and Activities links to the results. Reference duration is calculated from the selected duration distribution. Zero time share is also valid for a mixed association and yields zero rate.

A15, A22, A23, A24, A29 and A30 are illustrative fixed-price packages/fees; this is a modelling example, not a claim about actual contracts. Explicit direct risk costs still apply if mapped. For a price contract that transfers those costs, adjust the direct cost mappings to reflect who bears the exposure. Rate costs do not include general project overheads or idle time.

Green cost assumption cells and the association selector are editable. Grey cost fields are calculated. Recalculate and save in Excel before uploading changes, since the Python reader uses saved formula results. Missing saved linked costs and nonzero rates for Fixed only are blocked by validation. Formula tests used the bundled spreadsheet calculation engine; desktop Excel has not been exercised.

## Unified V2.2 application integration

The model adapter carries Cost_Association into each activity. The simulation enforces zero duration rate for Fixed only even when called directly. Direct mapped risk costs remain independent. An activity-cost table shows each association, reference duration, fixed component, rate, time cost and reference total before simulation. The result export includes activity_cost_inputs.csv.

The reader loads Case_Assumptions, and validation matches it by Activity_ID rather than row order. Saved formula outputs are reconciled against the current original budget, time share, duration distribution and cost association. Missing, duplicate or stale live cost inputs are blocked with a recalculation message. A legacy workbook without the live-assumption sheet remains supported.

## Reformatted workbook compatibility

The supplied reformatted workbook moves most table headers from row 3 to row 2. The reader now detects each sheet's header independently. The attached workbook passes validation with 30 activities and 24 risks, and its 210 cost formulas retain saved values. The workbook bytes are preserved exactly. Regression checks cover headers in rows 1, 2, 3 and 6, mixed layouts across sheets, whitespace, and descriptive missing-header errors.

Risk Portrait display update: ST legend reads only Total Project Risk. Full risk membership remains in the scenario table/export. Legend fits within the plotting area and tight layout is applied.
