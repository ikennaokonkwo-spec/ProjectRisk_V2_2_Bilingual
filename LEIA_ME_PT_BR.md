# Troca de idioma com preservação do estado

Esta edição mantém o estado da sessão antes, durante e depois dos cálculos. Trocas repetidas de idioma preservam dados, configurações, resultados e edições de tratamento temporariamente ocultas. Consulte [SESSION_STATE_EN_PT_BR.md](SESSION_STATE_EN_PT_BR.md). Os arquivos Excel e os módulos `core/` e `data_io/` não foram alterados nesta edição.

Atualização: esta edição acrescenta Exponencial, Lognormal e Gama, disponibiliza Uniforme e expõe parâmetros opcionais de custo. Consulte DISTRIBUTION_GUIDE_EN_PT_BR.md e verification/VERIFICATION_REPORT.md. A descrição de preservação byte a byte da edição anterior é histórica; os arquivos estendidos são identificados no relatório atual.

# Análise de Riscos de Projetos V2.2 — inglês e português

O aplicativo mantém o mecanismo computacional da versão recebida. A adaptação acrescenta interface, apresentação, mensagens, modelo de entrada e saídas em inglês e português do Brasil. A escolha de idioma não converte moedas, unidades, probabilidades nem parâmetros.

## Instalação e execução

Use Python 3.12 para reproduzir o ambiente verificado. Extraia o ZIP, abra a pasta `ProjectRisk_State_Persistent` no VS Code e abra **Terminal → Novo Terminal**. Execute:

```bash
python -m venv .venv
```

No Windows, ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as versões verificadas e execute:

```bash
python -m pip install -r requirements-verified.txt
python -m streamlit run app2_2.py
```

Abra o endereço local exibido pelo Streamlit, normalmente `http://localhost:8501`. O arquivo `app2_2.py` é uma aplicação Streamlit; não deve ser executado como um programa comum pelo botão de execução de Python. Os scripts de inicialização e as configurações originais do VS Code também estão incluídos. O arquivo `requirements.txt` oferece faixas de versões compatíveis; `requirements-verified.txt` registra as versões usadas nos testes entregues.

## Idioma e entrada de dados

Selecione **Português (Brasil)** em **Language / Idioma**, na barra lateral. Baixe o modelo pelo aplicativo ou abra `project_risk_template_v2_2_pt_BR.xlsx`. O modelo inglês original também está incluído e continua sendo aceito. É possível enviar o modelo inglês na interface portuguesa e vice-versa.

A troca de idioma apresenta os mesmos resultados já calculados. Não é necessário executar novamente a simulação, reconstruir o retrato de riscos ou repetir o tratamento apenas para mudar o idioma. As seleções e os parâmetros de tratamento são preservados. Mudanças reais de parâmetros continuam invalidando comparações desatualizadas, como na versão original.

As células numéricas do Excel devem conter números reais. Na rara necessidade de números armazenados como texto, use a convenção do modelo: `1.234,56` em português e `1,234.56` em inglês. Formatos incompatíveis são rejeitados em vez de convertidos por tentativa. Probabilidades e impactos relativos continuam usando frações decimais: `0,30` representa 30%. Listas de predecessoras mantêm IDs como `A01,A02`; o leitor também aceita ponto e vírgula nesse campo.

Preserve IDs de atividades e riscos, bem como a ordem das linhas. Não crie duas planilhas equivalentes, uma em cada idioma, no mesmo arquivo. Cabeçalhos equivalentes duplicados também são rejeitados. Cabeçalhos podem estar nas primeiras 50 linhas, conforme o mecanismo original de detecção.

Os textos do caso demonstrativo têm traduções incluídas. Textos novos escritos pelo usuário permanecem no idioma em que foram digitados, sem tradução automática de nomes, responsáveis ou justificativas próprias. Os menus nativos do Excel, do navegador, do sistema operacional e alguns controles do Streamlit dependem das configurações desses programas.

## Fluxo de análise

1. Preencha Projeto, Atividades, Registro_de_Riscos e Mapa_Risco_Atividade. Planilhas de relações, tratamentos, categorias e premissas mantêm seus papéis originais.
2. Em Atividades, selecione a associação de custo. Edite orçamento e parcela temporal em Premissas_do_Caso. Edite os parâmetros de duração nas atividades. Recalcule e salve no Excel antes do envio; o aplicativo lê os resultados salvos das fórmulas.
3. Envie o arquivo. Erros bloqueiam a análise; avisos preservam a possibilidade de continuar. A validação concilia custos salvos com orçamento, parcela temporal, distribuição de duração e associação atuais.
4. Examine a rede, o CPM de referência, as atividades e os caminhos críticos. As durações de referência são valores esperados das distribuições.
5. Defina número de iterações e semente e execute a simulação. A semente controla a reprodutibilidade, com o mesmo comportamento do original.
6. Examine métricas, distribuições acumuladas, histogramas, cronograma ajustado, intervalos P10/P50/P90, importância dos riscos, criticalidade, crucialidade e frequência dos caminhos críticos.
7. Construa o retrato completo de riscos. A tabela mantém todos os cenários cumulativos; o gráfico destaca os quatro riscos mais importantes e oferece a curva ST de todos os riscos ativos.
8. Selecione um ou vários riscos, ajuste a probabilidade após tratamento e os multiplicadores independentes de duração e custo direto e execute a comparação. As propostas da planilha inicializam os controles, mas não são aplicadas automaticamente a todos os riscos.
9. Baixe o registro de riscos e o pacote completo de resultados.

## Custos e limites preservados

O custo final da atividade é o máximo entre zero e: custo fixo + taxa de custo × duração final da própria atividade + custos diretos dos riscos mapeados. A associação Apenas fixo usa taxa zero e mantém o orçamento original como custo fixo. Fixo + tempo calcula a taxa a partir do orçamento, da parcela temporal e da duração de referência, com os mesmos arredondamentos originais.

Custos diretos explícitos de riscos continuam aplicáveis a atividades com preço fixo quando mapeados. Não contabilize duas vezes uma despesa temporal também como custo direto. O modelo não acrescenta custos gerais por duração total do projeto, tempo ocioso entre atividades ou custos de implementação das respostas.

O caso mantém 30 atividades, 24 riscos e 256 linhas de mapeamento. Os seis pacotes ilustrativos de preço fixo são A15, A22, A23, A24, A29 e A30. Orçamentos originais somam 1.057.000 unidades monetárias, frente à meta original de 900.000; essa diferença foi preservada. A meta de duração permanece 150 unidades de tempo. Novas taxas, avaliações e eficácias da versão original continuam identificadas como ilustrativas. Todas as aceitações residuais permanecem Pendentes.

## Exportação

O ZIP mantém os CSVs originais na raiz, com os mesmos nomes, valores e estrutura de V2.2. A subpasta `pt_BR/` acrescenta cópias com cabeçalhos e valores controlados em português, codificação UTF-8 com BOM, ponto e vírgula como separador e vírgula decimal. Em inglês, a subpasta é `en/`. O glossário `field_glossary_en_pt_BR.csv` relaciona os campos internos e suas traduções.

Para integração com código existente, use os CSVs originais da raiz. Para leitura em Excel em português, use as cópias em `pt_BR/`. Os dados numéricos completos são exportados; o arredondamento da apresentação na interface não altera os dados computacionais.

## Verificação

```bash
python run_tests.py
python verify_preservation.py --iterations 5000 --seed 42
```

O primeiro comando executa os testes originais e os testes bilíngues. O segundo extrai o pacote original preservado, executa os mecanismos em processos separados e compara a versão original com os modelos inglês e português. Consulte o relatório entregue em `verification/VERIFICATION_REPORT.md`. Nenhuma suíte demonstra ausência absoluta de defeitos; o relatório delimita exatamente o que foi verificado.

Consulte `NOTAS_DE_IMPLEMENTACAO_PT_BR.md` para as definições analíticas e `GUIA_DE_CAMPOS_EN_PT_BR.csv` para os nomes dos campos. Os documentos técnicos originais e o ZIP original estão preservados para auditoria.
