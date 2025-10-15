# ⚙️ Explicação Técnica: Dashboard ODS 3

Este dashboard foi desenvolvido em Python, utilizando o framework **Streamlit** para a interface interativa e a biblioteca **Plotly** para a geração de gráficos dinâmicos.

## O que o código faz

O objetivo principal do código (`app.py`) é transformar dados brutos de saúde (ODS 3) contidos no arquivo CSV em visualizações interativas e métricas de desempenho (KPIs).

### 1. Estrutura e Desempenho

* **Cache de Dados (`@st.cache_data`):** Garante a alta performance. Os dados do CSV são lidos e processados apenas uma vez, na primeira execução, tornando as interações subsequentes (filtros e trocas de indicador) instantâneas.
* **Carregamento de Dados:** Utiliza a função `load_data()` para ler o arquivo `ods_saude_brasil_limpo.csv`, especificando o separador **ponto e vírgula (`;`)** e garantindo que as colunas 'Ano' e 'Valor' estejam nos tipos corretos (`int` e `float`).

### 2. Interface de Usuário (Streamlit)

* **Sidebar de Configurações:** A barra lateral permite filtrar dinamicamente os dados por:
    * **Indicador de Saúde:** Seleção única do ODS 3.
    * **Região e UF:** Seleção múltipla para focar em áreas geográficas específicas.
* **Elementos Visuais:** O uso de **emojis** (definidos no dicionário `INDICATOR_ICONS`) torna a interface mais amigável, aparecendo no título principal e no seletor de indicadores.

### 3. Análise e Visualização (Plotly)

O dashboard é dividido em três seções analíticas principais, todas dinâmicas e baseadas nos filtros da sidebar:

| Seção | Função | Tipo de Gráfico/Elemento |
| :--- | :--- | :--- |
| **Resumo (KPIs)** | Exibe o desempenho geral do indicador selecionado, calculando a **média** para o primeiro ano, o último ano e a **variação percentual** entre eles. | `st.metric` (Cards) |
| **Evolução Histórica** | Mostra a tendência do indicador ao longo do tempo (2019 a 2021) para cada UF selecionada. | `plotly.express` (Linhas) |
| **Análise Regional** | Compara a média do indicador entre as Regiões para o **último ano disponível** nos dados, facilitando a identificação de disparidades regionais. | `plotly.express` (Barras) |

O uso do `template="plotly_dark"` garante uma estética moderna e consistente com o tema escuro do Streamlit.