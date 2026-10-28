# Verification report / Relatório de verificação

Verified on 28 October 2026. This is a bilingual extension of the supplied V2.2 package, not a replacement computational model.

Verificado em 28 de outubro de 2026. Esta é uma extensão bilíngue do pacote V2.2 recebido, sem substituição do modelo computacional.

## Preserved baseline / Base preservada

The untouched uploaded archive is included at `baseline/ProjectRisk_V2_2_original.zip`. Every Python file in `core/`, the model adapter, the original canonical CSV exporter and the English workbook are byte-identical to that baseline. The ten original test scripts are also retained without edits. Their baseline run passed before implementation.

O arquivo original intacto está incluído em `baseline/ProjectRisk_V2_2_original.zip`. Todos os arquivos Python de `core/`, o adaptador do modelo, o exportador canônico original e o modelo Excel em inglês são idênticos em bytes à base recebida. Os dez scripts de teste originais também foram mantidos sem alterações. Sua execução na base original passou antes da implementação.

## Exact numerical comparison / Comparação numérica exata

`python verify_preservation.py --iterations 5000 --seed 42` executed three separate Python processes: original V2.2 with its workbook, bilingual application with the English workbook, and bilingual application with the Portuguese workbook.

The three runs used the populated case: 30 activities, 24 risks and 256 mapping rows. Each main run produced 5,000 project rows, 150,000 activity rows and 120,000 risk rows. Every cell of those canonical iteration frames matched exactly, including IDs, random realizations, durations, cost components, CPM timing, criticality flags and complete critical-path strings. Equality was exact rather than a tolerance-based numerical comparison.

The comparison also covered reference CPM, project summary statistics, risk ranking, activity diagnostics, schedule quantiles, path frequencies, and numerical/controlled fields of cost and register summaries. Narrative names and descriptions intentionally translated for the Portuguese workbook were excluded from equality checks; they remain available in the untouched English workbook and original archive.

All complete cumulative Risk Portrait scenarios were additionally compared at 100 iterations with seed 42, including every scenario's project, activity and risk iteration frame and the summary table. Single-risk and multiple-risk treatments were compared at 100 iterations. Those counts are deliberately stated separately: full portraits and treatment scenarios were not verified at 5,000 iterations in this report.

Result: PASS. See `NUMERICAL_EQUIVALENCE.json` and `exact_equivalence.log`.

O comando executou três processos Python separados: V2.2 original com seu modelo, aplicação bilíngue com o modelo inglês e aplicação bilíngue com o modelo português. Cada execução principal produziu 5.000 linhas de projeto, 150.000 de atividades e 120.000 de riscos. Todas as células desses resultados canônicos coincidiram exatamente. Também foram comparados CPM, estatísticas, ordenação dos riscos, diagnósticos, quantis do cronograma, frequências dos caminhos e campos numéricos/controlados dos resumos. Nomes e descrições traduzidos foram excluídos das comparações numéricas e permanecem preservados na base original.

Todos os cenários cumulativos do retrato de riscos e os tratamentos de um e vários riscos foram comparados separadamente com 100 iterações e semente 42. Esses cenários completos não foram verificados com 5.000 iterações neste relatório. Resultado: PASSOU.

## Workbook checks / Verificações da pasta de trabalho

- All 12 worksheets and all 32 original OOXML archive parts retained, in their original order.
- All 210 original cost-related formulas retained as formulas: 180 numeric saved results match after recalculation; 30 formula-returned association labels use the translated controlled vocabulary.
- Numeric inputs and logical values retained with their original types and values.
- Merged ranges, freeze panes, data validation counts and conditional-formatting counts checked against the original.
- Formula references, comparison literals, dropdown lists and named-range references translated together.
- Existing cached numeric results preserved exactly in the delivered file; missing/stale results remain blocked by original validation.
- All 12 translated sheets rendered for visual review. Translated text cells wrap and rows expand where needed. The English workbook remains unchanged.

Foram preservadas 12 planilhas, 32 componentes OOXML e 210 fórmulas vinculadas de custo. Os 180 resultados numéricos coincidiram após recálculo; os 30 resultados textuais de associação foram traduzidos consistentemente. Entradas numéricas, tipos lógicos, mesclagens, painéis congelados, validações e formatações condicionais foram comparados com a base. Todas as planilhas traduzidas foram renderizadas para revisão visual. A pasta inglesa permanece intacta.

## Bilingual checks / Verificações bilíngues

The original ten test scripts and two new test scripts pass. The new boundary suite contains ten tests covering normalized model equality, controlled vocabularies, inactive Portuguese booleans, headers and collisions, locale numbers, validation translation, non-mutating display, canonical/localized exports, native workbook preservation and exact seeded language equivalence.

The new Streamlit workflow script runs the complete flow using each workbook language: upload, validation, 100-iteration simulation, complete portrait, single-risk treatment, switching languages in both directions, stale-treatment invalidation and multiple-risk treatment. Canonical simulation frames, portrait summaries, comparisons and treatment parameters remain exactly unchanged when switching language. Tests cover all four combinations of input language and interface language through those switches.

Additional checks ensure that an ID such as `Threat` remains `Threat`, and a newly authored risk name `Threat` is not silently renamed by a generic word translation. Known demonstration narratives have explicit translations; new user-authored text is preserved.

Both versions validate without issues for the supplied case. Original result ZIP members match the canonical exporter's bytes; additional localized copies have explicit delimiters, decimal conventions and UTF-8 BOM. Localized CSV round trips preserve tested numerical values.

Os dez scripts originais e dois scripts novos passam. A suíte bilíngue verifica limites de leitura/apresentação, igualdade dos modelos, vocabulários controlados, indicadores de atividade em português, colisões de cabeçalhos/planilhas, números localizados, mensagens, exportação e preservação da pasta. O teste Streamlit percorre o fluxo completo com os dois modelos, alterna idiomas nos dois sentidos e confirma a preservação exata dos resultados e das premissas. Também verifica tratamento de vários riscos e invalidação de resultados obsoletos. IDs e textos livres próprios não são renomeados por tradução genérica.

## Environment / Ambiente

Python 3.12. Tested direct dependencies:

| Dependency | Version |
| --- | --- |
| Streamlit | 1.66.1 |
| pandas | 2.2.3 |
| NumPy | 2.3.5 |
| NetworkX | 3.7 |
| Matplotlib | 3.10.8 |
| openpyxl | 3.1.5 |

Use `requirements-verified.txt` to reproduce these versions. The original dependency ranges are retained except that Streamlit's minimum is raised to 1.55 for keyed-widget behavior; the tested pinned environment is the reference for this report. No translation service or new computational dependency is required at runtime.

Use `requirements-verified.txt` para reproduzir essas versões. O ambiente fixado é a referência deste relatório. A dependência mínima do Streamlit foi elevada para 1.55 por causa do comportamento dos widgets com chaves estáveis. Não há serviço externo de tradução nem nova dependência computacional na execução.

## Scope and remaining limits / Escopo e limites

These tests establish preservation for the supplied case and the enumerated regression fixtures. They do not prove an absence of defects for every possible workbook, browser, operating system or dependency version.

The desktop Excel interface and a real browser session were not exercised. Workbook calculation was checked with the available spreadsheet engine; Streamlit workflows were checked with its AppTest framework. Browser-native/OS dialogs and framework-owned controls can use their own language settings. The application translates its own interface and known demonstration narratives, and deliberately preserves new user-authored text. It does not provide automatic translation of an arbitrary project's free text.

After editing either workbook in Excel, recalculate and save before uploading, as required in the original V2.2 workflow. The reader consumes saved formula results and does not become an Excel recalculation engine.

The original modeling limits remain unchanged: no risk-to-risk propagation, no within-activity timing of risks, no whole-project overhead/idle-time charging, no treatment implementation costs and no automatic residual acceptance or treatment optimization. Original target/budget mismatch, illustrative rates/ratings/effectiveness and Pending acceptance decisions are preserved.

Streamlit emits an inherited deprecation notice about `use_container_width` in this environment. It does not cause a test failure. Existing layout calls were retained; a future framework upgrade may require a presentation-only migration.

Os testes demonstram preservação para o caso recebido e os cenários enumerados, sem provar ausência absoluta de defeitos. Excel de desktop e navegador real não foram exercitados. Controles nativos e alguns controles do framework podem seguir o idioma desses programas. Textos livres novos não recebem tradução automática. É necessário recalcular e salvar no Excel após alterações. Todos os limites analíticos originais permanecem, incluindo ausência de propagação entre riscos, custos de implementação dos tratamentos, aceitação automática e otimização. O aviso herdado de descontinuação de `use_container_width` não causou falhas, mas pode exigir migração de apresentação em uma futura atualização do Streamlit.

## Repeat / Repetir

```bash
python -m pip install -r requirements-verified.txt
python run_tests.py
python verify_preservation.py --iterations 5000 --seed 42
```

`SOURCE_HASHES.json` records the delivered source and workbook hashes. `NUMERICAL_EQUIVALENCE.json` records original core hashes and the comparison scope. Logs are supplied alongside this report.
