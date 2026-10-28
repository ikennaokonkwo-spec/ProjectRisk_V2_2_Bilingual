# Notas de implementação — V2.2 bilíngue

## Arquitetura e preservação

Todos os arquivos Python em `core/`, o adaptador `data_io/model_adapter.py`, o exportador canônico `data_io/export_results.py` e o modelo inglês permanecem idênticos aos recebidos. A interface chama funções de apresentação e tradução sem alterar os objetos usados na simulação. O leitor reconhece os dois idiomas e normaliza nomes de planilhas, cabeçalhos e valores controlados antes da validação original.

Os catálogos em `localization/` são locais e não utilizam serviços de tradução, rede ou modelos de IA durante a execução. A linguagem é selecionada por sessão; o aplicativo não modifica a configuração global de locale do processo. A tradução não altera IDs, ordem das linhas, índices de mapeamento nem espaços de nomes dos geradores aleatórios. Esses elementos participam da amostragem determinística e foram preservados.

A tradução atua sobre cópias de apresentação. Números permanecem numéricos durante a leitura, a validação e a análise. A formatação com vírgula decimal pertence à exibição e às cópias localizadas dos CSVs. Os arquivos canônicos do ZIP de resultados mantêm os bytes produzidos pelo exportador original.

O modelo português preserva as 12 planilhas, todos os 32 componentes OOXML, intervalos, fórmulas, resultados salvos, validações, formatações condicionais, referências nomeadas e painéis congelados. Os textos, comparações de valores de listas e referências aos nomes traduzidos das planilhas foram adaptados conjuntamente. A apresentação de células traduzidas recebeu quebra de linha e altura suficiente para leitura. Números, fórmulas matemáticas e parâmetros originais não foram substituídos por resultados estáticos.

## Modelo de custos original

O custo final da atividade é `max(0, custo fixo + taxa de custo × duração final da atividade + custo direto do risco)`. A duração da própria atividade determina seu custo temporal. Não se incluem tempo ocioso entre atividades nem taxas de despesas gerais por duração total do projeto. Todas as taxas usam a unidade temporal de Projeto e todos os custos usam sua moeda.

O caso ilustrativo divide cada orçamento original em uma parcela fixa e uma parcela dependente do tempo. Na duração esperada de referência, o orçamento é preservado dentro da tolerância original de arredondamento. Parcelas temporais, avaliações e eficácias de tratamento continuam ilustrativas. Premissas_do_Caso calcula a divisão por fórmulas vinculadas. Pastas antigas com Base_Cost continuam aceitas; distribuições intrínsecas de custo também permanecem disponíveis e seu custo amostrado independente da duração substitui a parcela fixa.

Impactos relativos de custo direto usam o custo de base incluindo os custos da duração de base. Impactos absolutos são consequências financeiras adicionais. Não mapeie novamente como custo direto uma despesa temporal já incluída na taxa. As saídas das atividades discriminam custos fixos, temporais e diretos. O limite inferior zero pode impedir que a soma não ajustada desses componentes coincida com o custo final quando uma oportunidade excede todas as despesas.

## Registro e respostas

O registro mantém riscos, categorias e respostas existentes. Campos opcionais permitem avaliações separadas de impacto em prazo/custo, justificativas, responsável/prazo da resposta, probabilidade e impactos residuais e aceitação. Ativo=falso documenta o risco, mas exclui sua ocorrência da simulação principal e do seletor de tratamento. Sua probabilidade pode ficar em branco. Identificação, tipo e abrangência continuam exigidos conforme a versão original.

Categorias são convenções de trabalho editáveis, não uma classificação externa. A escala é 1 muito baixo, 2 baixo, 3 moderado, 4 alto e 5 muito alto. Justifique consequências específicas do projeto. Probabilidade × impacto é uma triagem ordinal separada para prazo e custo; não é um valor monetário esperado. Avaliações ausentes produzem pontuações ausentes, não zero. Nenhum limite automático de aceitação é imposto. Interprete ameaças e oportunidades em suas respectivas direções.

Acao_de_Resposta aceita texto descritivo. Um valor que contenha apenas uma estratégia conhecida é preservado e gera o aviso original, também quando escrito em português. Aceitação continua uma decisão humana; documentação incompleta é sinalizada. As exportações acrescentam achados da simulação, sem sobrescrever o arquivo de entrada.

## Tratamento

Tratamentos_dos_Riscos é opcional e aceita uma linha por risco ativo, com probabilidade tratada, multiplicador de impacto na duração, multiplicador de impacto no custo direto e justificativa. Probabilidade em branco mantém a original; multiplicadores em branco significam 1. As linhas inicializam os controles. Somente riscos explicitamente selecionados são tratados ao executar a comparação. As premissas exportadas registram os controles efetivamente usados.

Os dois multiplicadores são independentes. Mudanças de duração alteram automaticamente os custos baseados em taxas. Alterar controles elimina uma comparação obsoleta. Campos residuais do registro são documentação e nunca substituem silenciosamente premissas da simulação. Trocar apenas o idioma preserva resultados e parâmetros.

## Diagnósticos e retrato de riscos

A importância dos riscos mantém correlações de Pearson entre ocorrência e resultado do projeto. A crucialidade mantém correlação de Spearman entre duração da atividade e duração do projeto. Associações negativas são apresentadas; valores absolutos determinam a ordenação dos riscos. Associações indefinidas por variáveis constantes aparecem como zero por compatibilidade; isso não demonstra ausência de efeito de um risco determinístico. Impactos realizados de custo dos riscos representam custos diretos mapeados; alterações temporais aparecem nas atividades.

Criticalidade é a proporção de iterações em que uma atividade é crítica. A frequência dos caminhos considera quantas vezes cada caminho completo se torna crítico. O CPM de referência usa valores esperados das distribuições; não equivale à criticalidade probabilística.

Cada curva do retrato representa a duração total do projeto para um subconjunto de riscos. S0 contém apenas incerteza das atividades. O gráfico destaca os quatro primeiros cenários cumulativos e oferece ST, de todos os riscos ativos, inicialmente visível. Ocultar ST pode melhorar a separação visual. A tabela completa permanece disponível. ST reutiliza a simulação principal; os cenários intermediários usam números aleatórios comuns. Retratos completos grandes podem demorar.

Propagação entre riscos, instante de ocorrência dentro das atividades, novas tipologias de incerteza e modelos de probabilidade mais sofisticados permanecem fora da versão. Relacoes_entre_Riscos está inativa. O suporte existente à probabilidade Uniforme foi mantido, sem expansão.

## Caso de construção e fórmulas vinculadas

As 30 atividades têm cálculos de custo vinculados: 24 com taxas temporais ilustrativas e seis com preço fixo. Os 24 riscos mantêm avaliações iniciais de prazo/custo, respostas concretas, responsáveis, prazos relativos e premissas após resposta. Há propostas para os 24 riscos na planilha de tratamentos. Oportunidades podem receber probabilidades ou magnitudes maiores para ampliar benefícios. Custos de implementação dos tratamentos não são precificados.

A fonte usa unidades genéricas de tempo e moeda. Não se criaram datas reais. As metas originais de 150 unidades de tempo e 900.000 unidades monetárias permanecem; o orçamento de referência original soma 1.057.000, já superior à meta. Aceitações residuais permanecem Pendentes. Situações do ciclo de vida e indicadores de atividade originais são preservados; a situação Encerrado não exclui automaticamente um risco se Ativo continuar verdadeiro.

Apenas fixo impõe taxa zero e orçamento integral como custo fixo. Fixo + tempo usa `ROUND(orçamento original × parcela temporal / duração de referência, 2)`. O custo fixo usa `ROUND(orçamento original − taxa × duração de referência, 2)`. A duração de referência decorre da distribuição selecionada. Uma parcela temporal zero também é válida na associação mista e produz taxa zero. Uma parcela temporal positiva exige duração de referência positiva.

A15, A22, A23, A24, A29 e A30 são exemplos ilustrativos de pacotes/taxas fixos, sem afirmação sobre contratos reais. Custos diretos explícitos continuam aplicáveis se mapeados. Ajuste os mapeamentos conforme a alocação contratual da exposição.

Células verdes de premissas e o seletor de associação são editáveis; células cinzas de custo são calculadas. Recalcule e salve no Excel antes do envio. Custos vinculados sem resultados salvos, taxas não zero em Apenas fixo e resultados desatualizados são bloqueados pela validação. Premissas_do_Caso é conciliada por ID da atividade, não pela posição da linha. Entradas ausentes, duplicadas ou incompatíveis são bloqueadas. Uma pasta antiga sem essa planilha continua suportada.

O leitor detecta o cabeçalho de cada planilha independentemente nas primeiras 50 linhas, preservando suporte a cabeçalhos em linhas 1, 2, 3, 6 e outros arranjos aceitos. Espaços em cabeçalhos são tratados; duplicidades e ambiguidades geram erros. Nomes portugueses equivalentes são convertidos para os campos originais antes desses testes.

## Glossário e leitura

| Termo | Significado |
| --- | --- |
| CPM | Método do caminho crítico |
| ES / IC | Início mais cedo |
| EF / TC | Término mais cedo |
| LS / IT | Início mais tarde |
| LF / TT | Término mais tarde |
| Slack / Folga | Folga total da atividade |
| Criticality / Criticalidade | Fração de iterações em que a atividade é crítica |
| Cruciality / Crucialidade | Correlação de Spearman entre duração da atividade e do projeto |
| CDF | Função de distribuição acumulada |
| Risk Portrait / Retrato de riscos | Cenários cumulativos de exposição aos riscos |
| MEP | Instalações mecânicas, elétricas e hidrossanitárias |
| HSE / SSMA | Saúde, segurança e meio ambiente |

## Limites da verificação

Os testes computacionais, de integração, de interface Streamlit e de equivalência foram executados no ambiente registrado no relatório. O arquivo português foi recalculado com o mecanismo de planilhas disponível, e os 180 resultados numéricos de fórmulas coincidiram com os originais. Os 30 resultados textuais vinculados de associação foram traduzidos de forma consistente.

A interface do Excel de desktop, o navegador real do usuário, leitores de tela, dispositivos móveis, versões antigas de dependências e projetos arbitrários não foram testados. Diálogos nativos podem permanecer no idioma desses programas. Estas limitações não foram ocultadas nem substituídas por uma promessa de ausência absoluta de erros.
