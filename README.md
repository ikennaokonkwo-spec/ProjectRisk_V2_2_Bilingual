# State-preserving language switching

English/Portuguese switching now preserves the active session before, during and after simulation, Risk Portrait and treatment calculations. Hidden treatment edits, upload data, simulation settings, diagram choices and completed outputs are retained. See [SESSION_STATE_EN_PT_BR.md](SESSION_STATE_EN_PT_BR.md) for behavior and session boundaries.

All workbook files and all `core/` and `data_io/` Python modules remain byte-identical to the preceding corrected release. The original colors, distribution highlights, general templates and separate irrigation inputs remain included.

# Corrected highlighting, irrigation inputs and AOA/AON display

This release repairs the Excel conditional-formatting XML and overlapping optional-cost column definitions. It reuses the original workbook's differential styles and colour identification. Automatic recalculation is explicit. All eight distribution choices remain available.

Two additional, validated case inputs are included:

- `examples/irrigation_case_en.xlsx`
- `examples/irrigation_case_pt_BR.xlsx`

They contain 15 activities, 8 risks and 16 mappings, including the three source interpretations explicitly confirmed by the user. The general templates remain separate and retain their construction demonstration data. See `examples/IRRIGATION_README_EN_PT_BR.md` for source provenance, decisions and scope. Source correlations are documented but not simulated; no cost estimates were invented.

The app now offers **Network diagram: AON / AOA**. AON remains the default. AOA is a display-only conversion; zero-duration dummy links preserve joins without adding simulated activities or costs. See `NETWORK_DISPLAY_EN_PT_BR.md`.

A correção restaura os estilos e as cores originais e regulariza a estrutura XML e as colunas opcionais de custo. Os dois exemplos de irrigação são adicionais aos modelos gerais. AON permanece como opção inicial; AOA altera somente a representação. Consulte os guias bilíngues e o relatório atual.

The verification report includes the old-defect regression, exact original-style comparisons, independent LibreOffice highlighting checks, source transcription checks and analysis-state preservation when switching diagrams. It supersedes the earlier release's preview-only formatting assurances.

---

# Project Risk Analysis V2.2 — bilingual distribution extension

English and Brazilian Portuguese support, with eight distribution options: Fixed, Triangular, Beta-PERT, Uniform, Normal, Exponential, Lognormal and Gamma. The existing network, simulation, diagnostics, Risk Portrait, treatments, costs and exports retain their original behavior for existing inputs.

## Run

From this folder, preferably with the verified Python 3.12 environment:

```bash
python -m pip install -r requirements-verified.txt
python -m streamlit run app2_2.py
```

For Streamlit hosting, the main file is **app2_2.py**. The original Windows/shell launch scripts and VS Code settings remain included. Running the file directly with Python does not start a Streamlit session.

Select **Language / Idioma** in the sidebar. Download or upload either root-level Excel template. Either workbook language works with either interface language. Switching language preserves computed results and treatment controls.

## Input distributions

Required cells highlight according to the selection:

| Distribution | Required fields |
| --- | --- |
| Fixed | Fixed value |
| Triangular, Beta-PERT | Minimum, most likely, maximum |
| Uniform | Minimum, maximum |
| Normal | Mean, standard deviation |
| Exponential | Arithmetic mean > 0 |
| Lognormal, Gamma | Arithmetic mean > 0, standard deviation > 0 |

Duration parameters occupy Activities E:J. Optional intrinsic cost parameters occupy O:T, selected in N. Risk-impact parameters occupy Risk_Activity_Map E:J. All previous columns retain their positions. **Leave Cost_Model blank to preserve the linked fixed/time cost workflow**; the supplied templates do so. Original probabilities retain Fixed/Uniform support.

Recalculate and save edited workbooks in Excel before uploading. Existing validation still blocks missing or stale formula results. No correlations, event-count mechanisms or case-specific assumptions were added.

Read **DISTRIBUTION_GUIDE_EN_PT_BR.md** for parameter meanings, conversions, highlighted cells, scope and cost handling. **LEIA_ME_PT_BR.md** provides Portuguese launch and workflow guidance.

## Verification and preserved baseline

```bash
python run_tests.py
python verify_preservation.py --iterations 5000 --seed 42
python benchmark_preservation.py
```

The verification report records exact legacy numerical comparisons, new-distribution tests, workbook checks, Streamlit workflows and measured performance. Sampling, expected values, validation, parameter adaptation, dropdowns, formulas and highlighting were extended together. Unextended calculation modules remain unchanged. No new runtime dependency was added.

The original package remains in `baseline/ProjectRisk_V2_2_original.zip`; the previous bilingual package is also retained there. Existing legacy workbooks remain accepted. The two current root-level templates have intentionally been extended; they are no longer byte-identical to their predecessors. Original modeling notes are retained as historical references with notices pointing to the current extension guide.

Canonical CSVs remain at the root of result ZIPs. Localized copies and a field glossary remain included. New user-authored free text is preserved. Excel, browser/OS dialogs and framework-owned controls may use their own language settings. Desktop Excel and a real browser session have not been exercised in the verification environment; this limitation is recorded in the report.
