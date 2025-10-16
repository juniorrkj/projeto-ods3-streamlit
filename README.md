## ⚙️ Explicação Técnica: Dashboard ODS 3 — Saúde e Bem-Estar no Brasil

Este dashboard foi integralmente desenvolvido em Python, utilizando o framework **Streamlit** para a interface interativa e a biblioteca **Plotly** para a geração de gráficos dinâmicos e de alta qualidade.

### 1. Estrutura e Desempenho

* **Cache de Dados (`@st.cache_data`):** Garante a alta performance e a agilidade do dashboard. O arquivo CSV é lido e processado apenas uma vez, otimizando o desempenho e tornando todas as interações subsequentes (filtros e trocas de aba) instantâneas.
* **Carregamento e Limpeza (`load_data()`):** A função é responsável por ler o arquivo `ods_saude_brasil_limpo.csv` com separador **ponto e vírgula (`;`)**. As colunas `Ano` e `Valor` são tipadas rigorosamente para `int` e `float`. **Crucialmente, a base de dados é limitada ao ano de 2025** para manter o foco na análise temporal recente (`df = df[df['Ano'] <= 2025].copy()`).

### 2. Interface de Usuário (Streamlit)

* **Configuração e Layout:** O dashboard utiliza o layout `wide` e organiza a navegação em três **Abas (`st.tabs`)**, substituindo a antiga rolagem por uma estrutura modular.
* **Barra Lateral (Filtros):** Permite a filtragem dinâmica da análise por:
    * **Indicador de Saúde:** Define o foco principal da visualização.
    * **UF/Região:** Permite alternar entre uma UF específica e a Média Nacional.
    * **Ano de Referência:** Controla o *snapshot* temporal para as análises Regional e de Correlação.
* **Design Consistente:** O uso do `template='plotly_dark'` em todos os gráficos garante uma estética moderna e coesa.

### 3. Análise de Métricas (KPIs)

A seção de métricas (KPIs) no topo do dashboard fornece um resumo executivo imediato em quatro cartões (`st.metric`):

* **KPI Principal:** Exibe o valor mais recente do indicador selecionado e sua **variação percentual** calculada entre o primeiro e o último ano disponível.
* **Lógica de Cores:** A função `calcular_e_formatar_variacao` implementa uma lógica essencial: indicadores de **redução** (Mortalidade, AIDS, Suicídio) têm a cor do delta **invertida** (`delta_color='inverse'`) para que o verde (normal) signifique *melhora* (redução do valor).
* **KPIs de Referência:** Os três KPIs restantes comparam o desempenho da UF (ou Média Nacional) com a Média Nacional para os outros indicadores, fornecendo contexto imediato.

### 4. Visualização e Fluxo Analítico (Plotly)

O dashboard é dividido em três áreas analíticas principais, com visualizações Plotly dinâmicas:

| Seção | Objetivo Analítico | Tipo de Gráfico/Elemento | Destaque Técnico |
| :--- | :--- | :--- | :--- |
| **📊 Evolução Histórica** | Tendência do indicador ao longo do tempo. | Gráfico de Linha | Detalhe por ano (`dtick=1`) e traço em `yellow` para contraste. |
| **🗺️ Distribuição Regional** | Comparação de desempenho entre as UFs. | Gráfico de Barras (Ranking) | Utiliza `color='Regiao'` e `yaxis={'categoryorder':'total ascending'}` para ordenar as UFs pelo valor, criando um ranking claro. |
| **🔗 Correlação** | Relação estatística entre dois indicadores. | Gráfico de Dispersão (`Scatter Plot`) e `st.info` | Cálculo e exibição do **Coeficiente de Correlação de Pearson (r)** entre as variáveis selecionadas. |