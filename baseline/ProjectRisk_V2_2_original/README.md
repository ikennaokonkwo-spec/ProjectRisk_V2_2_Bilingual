# Project Risk Analysis V2.2

This unified package contains the Streamlit application, populated residential construction workbook, supporting modules, tests and implementation notes.

## Run

From this folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app2_2.py
```

Upload `project_risk_template_v2_2.xlsx`. Run `python run_tests.py` for automated checks. Windows and shell launch scripts are also supplied.

## Cost inputs

Select Cost_Association in Activities. Fixed only uses the full original budget as fixed cost and zero time rate. Fixed + time calculates a rate from the original budget, time-dependent share and reference duration. Edit budget/share in Case_Assumptions; reference durations and linked activity costs use live Excel formulas. Recalculate and save in Excel before uploading. The app checks the saved outputs against the current assumptions and blocks inconsistencies.

The app displays an activity-cost summary and exports it as activity_cost_inputs.csv. The simulator also enforces fixed-only behaviour for direct programmatic calls. Separate direct risk costs remain applicable if mapped. Review the contractual allocation before removing them.

## Other features

The package includes network/CPM analysis, four activity duration options with parameter highlighting, shared risk occurrence across mapped activities, risk and activity diagnostics, a broader risk register with response/residual assessment fields, cumulative Risk Portrait with optional all-risks ST curve, independent duration/direct-cost treatment controls, and before/after comparisons. ST reuses the main result. Risk-to-risk propagation remains inactive.

The workbook provides 30 activities, 24 risks, six illustrative fixed-price activities, and proposed treatment assumptions for all 24 risks. New rates, ratings and treatment effectiveness are illustrative classroom inputs, not measured case estimates. All residual acceptance decisions remain Pending. Only risks selected in the app are treated. Treatment implementation costs are excluded.

Original reference activity budgets sum to 1,057,000 monetary units; the original 900,000 cost target is retained for discussion. General project overheads and idle-time charging are outside the activity-rate model. See IMPLEMENTATION_NOTES.md for details.

## Header detection fix

The workbook reader locates each table header by column names within the first 50 rows, rather than assuming Excel row 3. It accepts row-2 headers, the original row-3 layout, and different title/blank-row layouts on individual sheets. Header whitespace is trimmed; missing, duplicate or ambiguous headers produce a worksheet-specific message. Fonts do not affect parsing. This package includes the user's reformatted workbook unchanged.
