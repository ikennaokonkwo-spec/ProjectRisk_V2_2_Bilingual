# English / Português (Brasil)

This bilingual extension preserves the V2.2 computational engine. Select **Language / Idioma** in the sidebar. Either workbook language can be uploaded in either interface language. Switching languages preserves the simulation, Risk Portrait and treatment results.

Esta extensão bilíngue preserva o mecanismo computacional V2.2. Selecione **Language / Idioma** na barra lateral. As duas versões da pasta de trabalho podem ser usadas em qualquer idioma da interface. A troca de idioma preserva a simulação, o retrato de riscos e os resultados de tratamento. Consulte **LEIA_ME_PT_BR.md** e **NOTAS_DE_IMPLEMENTACAO_PT_BR.md**.

## Start / Iniciar

Use Python 3.12 for the verified environment. From this folder:

```bash
python -m pip install -r requirements-verified.txt
python -m streamlit run app2_2.py
```

- `project_risk_template_v2_2.xlsx`: original English workbook, byte-identical to the upload.
- `project_risk_template_v2_2_pt_BR.xlsx`: Portuguese workbook, with equivalent inputs, formulas, validations and saved results.
- `python run_tests.py`: original and bilingual tests.
- `python verify_preservation.py --iterations 5000 --seed 42`: repeat the numerical comparison with the original archived engine.
- `verification/VERIFICATION_REPORT.md`: evidence, scope, environment and remaining limits.
- `baseline/ProjectRisk_V2_2_original.zip`: untouched original package for audit and recovery.

Original canonical CSVs remain at the root of each result ZIP. Additional selected-language CSVs are in `en/` or `pt_BR/`. Portuguese copies use UTF-8 BOM, semicolon delimiters and decimal commas; the numeric values remain unchanged. Project currency is never converted by selecting a language.

The application translates its own labels and known demonstration-case text. New user-authored free text is preserved as entered. Excel, the operating system, browser dialogs and framework-owned controls may use their own language settings. Recalculate and save edited workbooks in Excel before uploading, exactly as required in V2.2. Desktop Excel has not been exercised in the verification environment.

The original V2.2 README follows unchanged.

---

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
