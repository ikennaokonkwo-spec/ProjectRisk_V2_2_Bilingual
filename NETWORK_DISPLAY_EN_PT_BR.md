# AON and AOA display / Exibição AON e AOA

In **Project Network Analysis**, choose **Network diagram**:

- **AON — Activities on nodes** retains the original diagram and remains the default.
- **AOA — Activities on arrows** shows events as circles, actual activities as solid arrows, and required zero-duration dummy links as dashed arrows.

Em **Análise da rede do projeto**, escolha **Diagrama de rede**:

- **AON — Atividades nos nós** mantém o diagrama original e é a opção inicial.
- **AOA — Atividades nas setas** apresenta eventos em círculos, atividades em setas contínuas e ligações fictícias de duração zero em setas tracejadas.

Red marks critical activities/links. Activity panels retain ID, reference duration, ES/EF, LS/LF and slack. Event circles show tE and tL: earliest and latest event times. Diagram text is black on light backgrounds, and the diagram supports scrolling.

Vermelho identifica atividades/ligações críticas. Os rótulos mantêm ID, duração de referência, início/término mais cedo e mais tarde e folga. Nos eventos, tE/tL são os tempos mais cedo/mais tarde. O texto é preto sobre fundo claro e o diagrama permite rolagem.

## What changes / O que muda

Only the representation changes. The original CPM, Monte Carlo simulation, risk occurrence/impact procedure, cost calculations, diagnoses, Risk Portrait, treatment comparisons and exports keep the same inputs and computational procedures. Changing the diagram does not invalidate or recompute simulation results. Language changes preserve the diagram choice and analysis state through stable widget keys.

Muda somente a representação. CPM, simulação, riscos, custos, diagnósticos, retrato de riscos, tratamentos e exportações mantêm entradas e procedimentos. Trocar o diagrama não invalida resultados da simulação. As chaves estáveis dos controles preservam o estado ao trocar o idioma.

The converter gives every real activity its own completion event. A single predecessor can share its completion event with the successor's start; several predecessors feed a join through zero-duration dummy arrows. Equal predecessor sets share the same join. Multiple terminal activities receive a common finish event. This construction preserves the exact precedence closure and does not assert a minimum number of dummy links.

Cada atividade recebe seu evento de conclusão. Uma predecessora pode compartilhar esse evento com o início da sucessora; várias predecessoras se unem por ligações fictícias de duração zero. Conjuntos iguais compartilham a junção. Várias atividades terminais se ligam a um término comum. A construção preserva todas as precedências, sem afirmar número mínimo de ligações fictícias.

Dummy links belong only to the display graph. They do not appear as additional input activities, samples, costs or rows in the analysis exports. Their purpose is to preserve the supplied joins without introducing extra precedences. Activity correlations and risk-to-risk propagation remain outside the current model.

Ligações fictícias existem somente no grafo de exibição. Não acrescentam atividades, amostras, custos nem linhas às exportações. Preservam junções sem criar precedências extras. Correlações e propagação entre riscos permanecem fora do modelo atual.

The converter is tested against the original CPM for all timing fields, criticality flags and project duration on 30 varied acyclic networks, including zero durations, forks, joins and disconnected components. It also checks every activity pair for missing or additional precedence relationships. The irrigation reference network yields the same **26.5-week** duration in both representations.

A conversão foi comparada ao CPM original em 30 redes acíclicas variadas, com durações zero, ramificações, junções e componentes desconectados. Todos os pares foram verificados para detectar precedências ausentes ou adicionais. O caso de irrigação resulta nas mesmas **26,5 semanas** de referência nos dois formatos.
