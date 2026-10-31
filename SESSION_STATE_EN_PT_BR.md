# Language switching and session state / Idioma e estado da sessão

Use the pinned Streamlit 1.66.1 dependency; its keyed widgets and stateful tabs/panels are required.

Choose English or Português (Brasil) at any stage, as often as needed. Within the current app session, the language selector changes presentation while retaining:

- Uploaded workbook bytes and canonical input data.
- Iterations, random seed and AON/AOA selection.
- Completed simulation samples, diagnostics and Risk Portrait scenarios.
- Selected activity and the ST curve checkbox.
- Single/multiple treatment mode, selected risks, probabilities and impact multipliers, including edits to temporarily hidden risks.
- Completed treatment comparison, until its actual input assumptions change.
- Active tab and expanded/collapsed panels.

Simulation, Risk Portrait and treatment calculations run in a session-owned background executor. A language refresh leaves the same calculation running with the same captured inputs and random seed; it does not submit another calculation. Completion is polled every half second. Results are committed only to the matching project/settings/scenario. Workers do not access translated widgets or Streamlit session state. The numerical functions are unchanged.

The uploaded workbook snapshot also survives a UI rerun where the uploader is temporarily absent. Explicitly removing the upload or uploading different content clears the previous project's calculations and controls. Changing numerical settings requires a matching simulation, and changing treatment assumptions invalidates the old comparison. Failed calculations report an error without replacing previously completed results.

This is in-memory state for the **same active Streamlit session**. It does not add recovery after a server restart, a new browser session or a browser reload that creates a new session. User-written workbook text, units, currency and numerical parameters are not translated or converted by the language selector.

## Português (Brasil)

Selecione English ou Português (Brasil) em qualquer etapa, quantas vezes precisar. Na mesma sessão ativa, a troca de idioma mantém o arquivo carregado, os dados internos, as iterações, a semente, a escolha AON/AOA, as amostras calculadas, os diagnósticos, os cenários do retrato de riscos, a atividade selecionada e a opção da curva ST.

Também mantém o modo de tratamento, os riscos selecionados, as probabilidades e os multiplicadores, inclusive quando os campos ficam temporariamente ocultos. A comparação permanece válida enquanto suas premissas não forem alteradas. A aba selecionada e os painéis abertos/fechados são preservados.

Os cálculos de simulação, retrato de riscos e tratamento continuam em segundo plano quando o idioma muda. A mesma tarefa utiliza os mesmos dados capturados e a mesma semente; a troca de idioma não inicia outra tarefa. A conclusão é verificada a cada meio segundo. Os resultados são associados ao projeto, às configurações e ao cenário correspondentes. As funções numéricas não foram alteradas.

Remover explicitamente o arquivo ou carregar conteúdo diferente limpa os cálculos e os controles do projeto anterior. Alterar as configurações numéricas exige uma simulação correspondente; alterar as premissas de tratamento invalida a comparação anterior. Uma falha não substitui resultados já concluídos.

A preservação ocorre em memória, na **mesma sessão ativa do Streamlit**. Não inclui recuperação após reinício do servidor, nova sessão do navegador ou recarregamento que crie uma nova sessão. A troca de idioma não altera textos livres, unidades, moeda nem parâmetros numéricos do arquivo.
