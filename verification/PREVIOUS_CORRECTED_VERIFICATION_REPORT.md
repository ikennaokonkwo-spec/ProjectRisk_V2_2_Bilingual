# Corrected input and network-display verification

Verified 31 October 2026. This release repairs native workbook compatibility, adds separate English/Portuguese irrigation case inputs, and offers an AON/AOA display choice. The general-purpose model and its calculation assumptions remain unchanged from the preceding distribution release.

## What the earlier verification missed

The preceding release's new conditional-style records contained children in `fill, font` order. SpreadsheetML CT_Dxf specifies `font, numFmt, fill, alignment, border, protection, extLst` order, with optional children. A tolerant preview importer accepted those records, so a rendered preview and a conditional-rule count did not establish Excel compatibility. A new regression test explicitly rejects the previously delivered file.

The optional cost-column definitions also overlapped an original N:XFD default-column range. Those column intervals have been normalized into ordered, non-overlapping ranges. Native Excel table column labels are now synchronized with the actual worksheet headers, including Portuguese headers and the original Base_Cost/Fixed_Cost label mismatch. Table identities and ranges, input values, formulas, named ranges and unrelated styles/controls are retained. No structured-reference formulas were present that required migration.

The current files reuse the **67 original differential-style records verbatim in structure and values**, rather than constructing replacement colours. Required duration/cost parameters use the original yellow; mapped-impact parameters use the original green; neutral grey and other original fill definitions are retained. All differential-style references are in range, column definitions do not overlap, table headers agree with their native table definitions, and automatic recalculation/full calculation on load is explicit.

References: [Microsoft DifferentialFormat documentation](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.differentialformat) and SpreadsheetML CT_Dxf child-order requirements. The checks target the identified defects; they are not presented as full validation of every Open XML feature.

## Independent native highlighting checks

LibreOfficeDev 26.8.0.0.alpha0 opened disposable test copies and evaluated actual conditional formatting during headless PDF export. The tests selected every supported distribution across duration, optional intrinsic cost and mapped impact parameters in both languages.

**48 selection profiles and 288 parameter-cell backgrounds were sampled from the resulting PDFs. All passed**, including 96 required highlights and 192 neutral unused cells. Original yellow RGB (255,242,204), green (198,239,206) and neutral grey (242,242,242) matched within a two-channel-unit rendering tolerance. These were actual native-application calculations, not colours painted onto screenshot examples. Existing populated unused cells stayed present and neutral.

See `NATIVE_HIGHLIGHT_QA.json`, `native_highlight_qa.log` and `highlighting_native_examples.png`.

## Irrigation transcription and explicit user decisions

The two additional files in `examples/` contain **15 activities, 8 risks and 16 mappings**, in weeks. All activity distributions and supplied parameters, predecessor sets, risk probabilities and affected activity pairs were checked against the supplied document and the explicit decisions confirmed in this conversation:

- R8 follows the named Material Review activity **2.4**, not the inconsistent printed reference 2.15; the model's risk statement and mapping both reflect the correction.
- R1/R2/R5/R6/R8 use **Triangular**, with the supplied three points.
- R3 uses **Normal**, mean 1.5 weeks and SD 1 week, retaining the model's existing zero-floor rule.

All four exponential activities and both exponential risk impacts are populated. R7 has mean impact 3 weeks and occurrence probability 30%; R4 has mean impact 2 weeks and probability 40%. Activity identifiers **2.1 and 2.10 remain separate text identifiers** throughout native files, the reader, simulation and diagrams.

No costs, contractual assumptions, targets, qualitative ratings, owners or treatment-effectiveness estimates were invented. Zero cost inputs disable the cost component and are explicitly described as placeholders, not estimates. Unsupplied management/treatment fields and targets are blank. Iterations 5,000 and seed 42 are inherited model controls, not claimed case facts.

The four source activity correlations are recorded in Case_Summary/Resumo_do_Caso but are **not simulated**. No correlation layer or four-scenario mechanism was added. These are inputs for the supported uncorrelated schedule/risk analysis, not a claim to reproduce every requested Crystal Ball scenario. Shared occurrence and independently sampled mapped magnitudes remain the existing model procedure. Source provenance, corrections and limits appear in both workbook notes and the general input-notes display.

Both case files pass validation without issues. Their complete project/activity/risk iteration frames match exactly at **1,000 iterations, seed 42**. Reference CPM duration is **26.5 weeks** in both languages. This is a calculated reference value, not a source-promised target.

## Native case opening/save check

Both delivered case files were opened and saved to disposable XLSX copies by LibreOffice. The reopened copies pass the same validation and retain all model objects, including names, text identifiers and parameters. Complete simulation frames before/after native open/save match exactly at **100 iterations, seed 42**. See `NATIVE_CASE_ROUNDTRIP.json` and `native_case_roundtrip.log`.

## AON/AOA equivalence and state retention

AON remains the default and calls the existing diagram function. AOA is implemented in the separate `presentation/` package. Events are circles; actual activities are solid arrows; necessary zero-duration dummy links are dashed. Red denotes critical activities/links; labels preserve ID, duration, timing fields and slack. Dummy links do not become input activities, costs, samples or export rows.

The converter is tested on **30 varied acyclic networks**, including zero-duration activities, forks, joins and multiple roots/terminals. Tests compare every activity pair for missing or additional precedence and compare project duration, ES, EF, LS, LF, slack and critical flags with the original CPM. No minimum-dummy-count claim is made. Irrigation AOA and AON reference duration both equal 26.5 weeks. Input objects are unchanged by rendering, SVG identifiers are escaped, and decimal-looking identifiers remain unchanged in Portuguese displays.

The Streamlit workflow covers **six profiles**: both regular templates, both all-eight-distribution fixtures and both irrigation files. Each profile covers upload/validation, simulation, complete Risk Portrait, single/multiple treatments, both language directions and AOA/AON switching. Simulation frames, portrait summaries and treatment comparisons remain exactly unchanged when changing representation. Stale treatment comparisons still invalidate when treatment inputs change.

## Computational preservation

Every Python module in `core/` and `data_io/` is byte-identical to the preceding distribution release. There are no new simulation, risk, cost, treatment or export calculations. The additions are presentation, input metadata/translations and corrected workbooks. See `CALCULATION_PRESERVATION.json`.

The legacy comparison with original V2.2 was repeated with **5,000 iterations and seed 42** for the main original/English/Portuguese runs; complete project, activity and risk iteration frames match exactly. Complete Risk Portrait scenarios and single/multiple treatments also match in separate **100-iteration** comparisons. New distribution and previous bilingual tests remain included. See `NUMERICAL_EQUIVALENCE.json` and `exact_equivalence.log`.

The complete suite contains **14 test scripts** and passes. The seven additional correction/case/network tests are also rerun after the final native metadata and source-statement corrections. The legacy test changes from the previous release are limited to its already-intended extra formatting/validation counts; no computational assertion was removed to hide a failure.

## Environment and limits

Python 3.12; the pinned direct dependencies remain in `requirements-verified.txt`. No new application runtime dependency was added. LibreOffice and PDF colour sampling were verification-only tools, not application requirements. AOA has only display conversion overhead; the simulation implementation is unchanged. The earlier simulation-only performance record is retained as historical evidence and is not claimed as a fresh measurement of the new diagram UI.

Microsoft Excel's interactive desktop UI and an actual browser session were not exercised. Native workbook behaviour was independently checked with LibreOffice; Streamlit behaviour used AppTest. The record therefore establishes the specified tests and fixes, not a universal absence of defects on every Office/browser/version combination. Recalculate and save edited workbooks in Excel before uploading; saved-result validation remains active.

## Resumo em português

A correção substitui os registros condicionais inválidos pelos estilos originais, elimina sobreposição de definições de colunas e alinha cabeçalhos de tabelas nativas aos cabeçalhos visíveis. Foram conferidos **288 fundos de células em 48 combinações** por exportação PDF real do LibreOffice, preservando amarelo, verde e cinza originais.

Os dois arquivos de irrigação contêm **15 atividades, 8 riscos e 16 mapeamentos**. As três decisões do usuário estão registradas: R8 para 2.4; impactos de três pontos triangulares em R1/R2/R5/R6/R8; R3 normal. IDs 2.1 e 2.10 permanecem distintos. Custos e eficácias não foram inventados. Correlações da fonte são notas, não entradas simuladas.

Os resultados inglês/português coincidem exatamente com 1.000 iterações; os arquivos também preservam objetos e resultados após abertura/salvamento nativos. AON permanece inicial; AOA apenas muda a representação. Precedências e todos os campos CPM coincidem em 30 redes variadas. O fluxo completo foi verificado em seis perfis, incluindo troca de idioma e de diagrama sem perda de resultados. Os **14 scripts passam**, e todos os módulos computacionais de core/data_io permanecem idênticos à edição anterior. A comparação legada com 5.000 iterações continua exata.

Excel de desktop interativo e navegador real não foram exercitados; o relatório diferencia essa limitação dos testes efetivamente executados com LibreOffice e AppTest.

## Repeat

```bash
python -m pip install -r requirements-verified.txt
python run_tests.py
python verify_preservation.py --iterations 5000 --seed 42
```

See `examples/IRRIGATION_README_EN_PT_BR.md`, `NETWORK_DISPLAY_EN_PT_BR.md` and `SOURCE_HASHES.json`.
