# Distribution extension / Extensão das distribuições

This general-purpose extension adds Exponential, Lognormal and Gamma to the five existing distribution options. It also exposes Uniform consistently in the activity-duration dropdown. No case-specific assumptions, correlations, occurrence-count models or new scenario mechanisms have been added.

Esta extensão de uso geral acrescenta Exponencial, Lognormal e Gama às cinco opções existentes e disponibiliza Uniforme consistentemente no seletor de duração. Não foram acrescentadas premissas de um caso específico, correlações, contagem de ocorrências nem novos mecanismos de cenários.

## Required worksheet inputs / Entradas obrigatórias

The six parameter columns retain the order **Fixed, Minimum, Most likely, Maximum, Mean, SD**. Required cells highlight automatically when a model is chosen. Unused cells remain neutral, retain their contents and do not participate in that model's parameter calculation.

As seis colunas mantêm a ordem **Fixo, Mínimo, Mais provável, Máximo, Média, DP**. Células obrigatórias recebem destaque automático. Células não utilizadas permanecem neutras, preservam seu conteúdo e não participam do cálculo dos parâmetros daquela distribuição.

| English | Português | Populate / Preencher | Reference mean / Média de referência |
| --- | --- | --- | --- |
| Fixed | Fixa | Fixed value / Valor fixo | Fixed value / Valor fixo |
| Triangular | Triangular | Minimum, most likely, maximum / Mínimo, mais provável, máximo | (min + mode + max) / 3 |
| Beta-PERT | Beta-PERT | Minimum, most likely, maximum / Mínimo, mais provável, máximo | (min + 4 × mode + max) / 6 |
| Uniform | Uniforme | Minimum, maximum / Mínimo, máximo | (min + max) / 2 |
| Normal | Normal | Mean, SD / Média, DP | Original reference-mean rule retained / Regra original preservada |
| Exponential | Exponencial | Mean > 0 only / Somente Média > 0 | Entered arithmetic mean / Média aritmética informada |
| Lognormal | Lognormal | Arithmetic mean > 0, SD > 0 / Média aritmética > 0, DP > 0 | Entered arithmetic mean / Média aritmética informada |
| Gamma | Gama | Arithmetic mean > 0, SD > 0 / Média aritmética > 0, DP > 0 | Entered arithmetic mean / Média aritmética informada |

All required new-distribution inputs must be finite. Unrepresentable Gamma shape/scale or Lognormal spread combinations are rejected. Exponential's standard deviation equals its mean; entering a separate SD does not change that distribution. The three new distributions have nonnegative support and no finite upper limit. Minimum/maximum values left in unused cells do not truncate them.

Todas as entradas obrigatórias das novas distribuições devem ser finitas. Combinações numericamente não representáveis são rejeitadas. Na Exponencial, o desvio-padrão é igual à média; preencher DP separadamente não altera a distribuição. As três novas distribuições têm suporte não negativo e não possuem máximo finito. Valores remanescentes em Mínimo/Máximo não as truncam.

## Where to enter values / Onde informar os valores

| Purpose / Finalidade | Selector / Seletor | Parameter cells / Células de parâmetros |
| --- | --- | --- |
| Activity duration / Duração da atividade | Activities D: Duration_Model / Atividades D: Modelo_de_Duracao | E:J: Duration_* / E:J: parâmetros de duração |
| Optional intrinsic activity cost / Custo intrínseco opcional | Activities N: Cost_Model / Atividades N: Modelo_de_Custo | O:T: Cost_* / O:T: parâmetros de custo |
| Mapped risk impact / Impacto de risco mapeado | Risk_Activity_Map D: Distribution / Mapa_Risco_Atividade D: Distribuicao | E:J: Impact_* / E:J: parâmetros de impacto |

Activity-duration and optional-cost parameter cells highlight yellow. Mapped-impact parameter cells highlight green. Selectors retain their existing input formatting. The same required-cell matrix is used in both languages. The Risk Register's default-impact distribution dropdown also includes all eight options, but remains descriptive metadata; mapped impact parameters belong in the mapping sheet, as before.

Parâmetros de duração e custo opcional são destacados em amarelo; parâmetros de impactos mapeados, em verde. A mesma matriz vale nos dois idiomas. O registro de riscos oferece as oito opções na distribuição padrão do impacto, mas esse campo continua sendo metadado descritivo; os parâmetros efetivos permanecem no mapeamento.

Leave **Cost_Model blank** to retain the existing linked Fixed_Cost + Cost_Rate workflow. The new O:T columns are blank in the supplied templates. Choosing an explicit cost model uses its highlighted inputs for the duration-independent cost component, exactly as the existing adapter already allowed. This does not replace the separate time-dependent rate or direct mapped risk costs. For an explicit Fixed cost model, blank Cost_Fixed retains the legacy fallback to linked Fixed_Cost or Base_Cost. An explicit stochastic cost mean need not equal the linked fixed component; this is a user assumption, not an automatic rebudgeting operation.

Deixe **Modelo_de_Custo em branco** para manter o fluxo existente de Custo_Fixo + Taxa_de_Custo. As colunas O:T estão em branco nos modelos entregues. A escolha explícita utiliza seus parâmetros destacados para a parcela de custo independente da duração, como o adaptador já permitia. Taxas temporais e custos diretos dos riscos continuam separados. No modelo explícito Fixa, Cost_Fixed em branco mantém a regra anterior de utilizar Fixed_Cost ou Base_Cost. A média de custo estocástico é uma premissa do usuário e não implica redistribuição automática do orçamento.

## Parameter conversions / Conversões

Inputs use original units: weeks, days, monetary units, or decimal relative-impact rates as appropriate. Do not enter logarithms or Gamma shape/scale in Mean/SD cells.

As entradas usam as unidades originais: semanas, dias, unidades monetárias ou taxas decimais de impactos relativos. Não informe logaritmos nem forma/escala da Gama nas células Média/DP.

- Exponential: scale = arithmetic mean.
- Lognormal: log variance = ln(1 + (SD/mean)²); log mean = ln(mean) − log variance/2; log SD = √log variance. The implementation uses a numerically stable equivalent.
- Gamma: shape = (mean/SD)²; scale = SD²/mean.

Derived Lognormal/Gamma parameters are prepared once when the workbook is adapted to model objects and reused by the simulation. Existing sampling branches, random-number namespaces and identifiers remain unchanged.

Parâmetros derivados são preparados uma vez na conversão do arquivo para os objetos do modelo e reutilizados na simulação. Ramos de amostragem existentes, espaços de nomes aleatórios e identificadores foram preservados.

## Linked formulas and validation / Fórmulas vinculadas e validação

The expected duration for each new distribution is its entered arithmetic mean. Case_Assumptions reference-duration formulas now recognize those selections. Fixed/time cost splits continue to follow the original formulas and rounding rules. Always recalculate and save in Excel before uploading an edited workbook. The app still reads saved formula results and blocks missing/stale linked costs.

A duração esperada das novas distribuições é a média aritmética informada. As fórmulas de Premissas_do_Caso reconhecem essas escolhas. A divisão de custos fixos/temporais mantém fórmulas e arredondamentos originais. Sempre recalcule e salve no Excel antes do envio; resultados vinculados ausentes ou desatualizados continuam bloqueados.

Occurrence probability models remain **Fixed or Uniform**. The new distributions apply to magnitudes, not to whether a risk occurs. Shared occurrences, independent mapped magnitude draws, threat/opportunity signs, floors, CPM, diagnoses, Risk Portrait, treatments, exports and bilingual state retention retain their prior behavior. The Normal zero-floor and its original reference-mean rule are unchanged.

Os modelos de probabilidade de ocorrência continuam **Fixa ou Uniforme**. As novas opções descrevem magnitudes. Ocorrência compartilhada, amostras independentes dos impactos mapeados, sinais de ameaça/oportunidade, limites inferiores, CPM, diagnósticos, retrato de riscos, tratamentos, exportações e retenção de estado preservam seu comportamento. A regra de limitar amostras normais a zero e sua média de referência original também permanecem.

## Verification fixtures / Arquivos de teste

`tests/fixtures/all_distributions_en.xlsx` and `all_distributions_pt_BR.xlsx` are synthetic test fixtures exercising every option in all three parameter blocks. They are not replacements for the blank optional-cost workflow or an interpretation of a particular case. Regular input templates remain at the project root.

Os arquivos em `tests/fixtures/` são entradas sintéticas para testes de todas as opções nos três blocos. Não são adaptações de um caso específico nem substitutos dos modelos da raiz.
