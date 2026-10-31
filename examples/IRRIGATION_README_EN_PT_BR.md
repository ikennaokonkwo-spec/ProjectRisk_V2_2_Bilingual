# Irrigation case input / Entrada do caso de irrigação

The two Excel files contain the same numerical case and predecessor network, with English or Portuguese labels and descriptions. They are additional inputs; the general-purpose templates remain in the project root.

Os dois arquivos Excel contêm o mesmo caso numérico e a mesma rede de precedências, com textos em inglês ou português. São entradas adicionais; os modelos gerais permanecem na raiz.

Source: `irrigation_source.docx`, copied unchanged from the supplied “estudo de caso Irrigação (1).docx”. Stage 2 contains **15 activities, 8 risks and 16 mappings**. The time unit is weeks. Identifiers **2.1 and 2.10 are distinct text IDs**; do not convert IDs into decimal numbers.

Fonte: documento original preservado em `irrigation_source.docx`. A segunda etapa contém **15 atividades, 8 riscos e 16 mapeamentos**. A unidade é semana. **2.1 e 2.10 são IDs textuais distintos**; não converter identificadores em números decimais.

## Explicit decisions confirmed by the user / Decisões confirmadas

| Source ambiguity | Confirmed input interpretation |
| --- | --- |
| R8 names Material Review but prints 2.15 | Map R8 to **2.4 Material Review**, plus 2.12 Project Documentation |
| R1, R2, R5, R6 and R8 supply three points but no distribution name | **Triangular**, with the supplied minimum, most likely and maximum |
| R3 supplies mean 1.5 and SD 1 but no distribution name | **Normal**, using the existing zero-floor policy |

| Ambiguidade da fonte | Interpretação confirmada |
| --- | --- |
| R8 nomeia Revisão dos Materiais, mas imprime 2.15 | Mapear para **2.4 Revisão dos Materiais**, além de 2.12 Documentação |
| R1, R2, R5, R6 e R8 informam três pontos sem nomear distribuição | **Triangular**, com mínimo, mais provável e máximo fornecidos |
| R3 informa média 1,5 e DP 1 sem nomear distribuição | **Normal**, mantendo o limite inferior zero existente |

All supplied activity parameters, risk probabilities and affected activity pairs were transcribed. Four exponential activities use means 1, 1, 2 and 1 weeks for 2.3, 2.8, 2.11 and 2.14. Exponential risk impacts are R4 mean **2 weeks** and R7 mean **3 weeks**. A risk occurrence is shared across its two mappings; mapped magnitudes are sampled independently, as in the existing general model.

Os parâmetros das atividades, probabilidades e pares de atividades afetadas foram transcritos. As quatro atividades exponenciais usam médias 1, 1, 2 e 1 semanas em 2.3, 2.8, 2.11 e 2.14. Impactos exponenciais: R4, média **2 semanas**; R7, média **3 semanas**. A ocorrência é compartilhada entre os dois mapeamentos; suas magnitudes são independentes, conforme o modelo geral existente.

## Scope retained / Escopo mantido

The source gives four activity correlations: (2.3,2.6)=0.7; (2.2,2.5)=0.6; (2.7,2.8)=0.5; (2.9,2.13)=0.7. They are preserved as source notes in Case_Summary/Resumo_do_Caso. **They are not simulated.** No correlation functionality or four-scenario mechanism was added. The supplied model supports the case's uncorrelated schedule/risk analysis; the files do not claim to reproduce every requested Crystal Ball scenario.

A fonte informa quatro correlações de atividades, preservadas como notas em Resumo_do_Caso. **Não são simuladas.** Não foram acrescentadas correlações nem mecanismo de quatro cenários. Os arquivos permitem a análise de prazo/riscos sem correlações, dentro do escopo atual; não afirmam reproduzir todos os cenários solicitados no Crystal Ball.

No cost estimates, contractual cost associations, targets, qualitative ratings, owners or treatment effectiveness were supplied. Cost inputs are set to zero solely to disable cost calculations; zero outputs are not cost estimates. The technical Fixed only setting in this schedule-only input is not a claim about contracts. Targets and unsupplied management/treatment fields are blank. The 5,000 iterations and seed 42 are inherited simulation controls, not facts asserted by the case document.

Não foram informados custos, associações contratuais, metas, avaliações qualitativas, responsáveis nem eficácias de tratamento. Zeros apenas desativam custos; não são estimativas. A opção técnica Apenas fixo não afirma condições contratuais. Metas e campos de gestão/tratamento não fornecidos permanecem em branco. As 5.000 iterações e semente 42 são controles herdados, não dados atribuídos ao documento.

The reference CPM duration is **26.5 weeks**, calculated from the model's expected activity durations. This is a computed reference value, not a duration promised by the case. AON and AOA displays use the same precedence logic; selecting AOA does not add dummy activities to the simulation.

O CPM de referência resulta em **26,5 semanas**, calculado a partir das durações esperadas. É um resultado de referência, não prazo prometido pela fonte. AON e AOA representam as mesmas precedências; escolher AOA não acrescenta atividades fictícias à simulação.

Use the original colour key: green inputs, neutral grey optional/calculated fields, yellow required duration/cost parameters, and green required mapped-impact parameters. Recalculate and save in Excel after edits, before upload. The app also displays the input notes so the confirmed interpretations and unapplied correlations are visible.

Use a identificação original de cores: entradas verdes, opcionais/calculados cinza, parâmetros obrigatórios de duração/custo amarelos e impactos mapeados obrigatórios verdes. Recalcule e salve após editar, antes de enviar. O aplicativo também apresenta as notas de entrada.
