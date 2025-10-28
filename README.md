## ⚙️ Explicação Técnica: Dashboard ODS 3 — Saúde e Bem-Estar no Brasil

Este dashboard é uma aplicação de análise de dados poderosa, integralmente desenvolvida em Python, utilizando o framework **Streamlit** para a interface interativa e a biblioteca **Plotly** para a geração de gráficos dinâmicos e de alta qualidade.

---

## 🎯 Objetivo e Metodologia

O projeto visa transformar dados brutos do sistema público de saúde em *insights* acionáveis para monitorar o **Objetivo de Desenvolvimento Sustentável (ODS) 3: Saúde e Bem-Estar** no Brasil.

* **Metodologia:** Utiliza a arquitetura moderna de Data Science (Python e bibliotecas de visualização) para entregar uma ferramenta de BI (Business Intelligence) com foco em desempenho e clareza analítica.
* **Foco Analítico:** Prioriza a visualização da evolução histórica, o ranking regional e a correlação entre indicadores para embasamento de políticas públicas.

---

### **Desenvolvedor e Fontes**

| Detalhe | Informação |
| :--- | :--- |
| **Desenvolvido por:** | **Claudiano Pinto de Oliveira Junior** |
| **Curso/Área:** | **Ciência da Computação** |
| **Instituição:** | **CEUB** |
| **Disciplina:** | **Programação para Web** |
| **Base de Dados:** | DATASUS (Departamento de Informática do Sistema Único de Saúde) |
| **Licença:** | Direitos Reservados a Claudiano Pinto de Oliveira Junior. |

---

### 1. Estrutura e Desempenho

* **Cache de Dados (`@st.cache_data`):** Garante a alta performance e a agilidade do dashboard. O arquivo CSV é lido e processado apenas uma vez, otimizando o desempenho e tornando todas as interações subsequentes (filtros e trocas de aba) instantâneas.
* **Carregamento e Limpeza (`load_data()`):** A função é responsável por ler o arquivo `ods_saude_brasil_limpo.csv` com separador **ponto e vírgula (`;`)**. As colunas `Ano` e `Valor` são tipadas rigorosamente para `int` e `float`. **Crucialmente, a base de dados é limitada ao ano de 2025** para manter o foco na análise temporal recente (`df = df[df['Ano'] <= 2025].copy()`).

### 2. Interface de Usuário (Streamlit)

* **Configuração e Layout:** O dashboard utiliza o layout `wide` e organiza a navegação em três **Abas (`st.tabs`)**, substituindo a antiga rolagem por uma estrutura modular, o que otimiza o fluxo de navegação do usuário.
* **Barra Lateral (Filtros):** Permite a filtragem dinâmica da análise por:
    * **Indicador de Saúde:** Define o foco principal da visualização.
    * **UF/Região:** Permite alternar entre uma UF específica e a Média Nacional.
    * **Ano de Referência:** Controla o *snapshot* temporal para as análises Regional e de Correlação.
* **Design Consistente:** O uso do `template='plotly_dark'` em todos os gráficos garante uma estética moderna e coesa.

### 3. Análise de Métricas (KPIs)

A seção de métricas (KPIs) no topo do dashboard fornece um resumo executivo imediato em quatro cartões (`st.metric`):

* **KPI Principal:** Exibe o valor mais recente do indicador selecionado e sua **variação percentual** calculada entre o primeiro e o último ano disponível.
* **Lógica de Cores (Inteligência de Negócio):** A função `calcular_e_formatar_variacao` implementa uma lógica essencial: indicadores de **redução** (Mortalidade, AIDS, Suicídio) têm a cor do delta **invertida** (`delta_color='inverse'`) para que o **verde** signifique **melhora** (redução do valor) e o vermelho signifique piora.
* **KPIs de Referência:** Os três KPIs restantes comparam o desempenho da UF (ou Média Nacional) com a Média Nacional para os outros indicadores, fornecendo contexto imediato.

### 4. Visualização e Fluxo Analítico (Plotly)

O dashboard é dividido em três áreas analíticas principais, com visualizações Plotly dinâmicas:

| Seção | Objetivo Analítico | Tipo de Gráfico/Elemento | Destaque Técnico |
| :--- | :--- | :--- | :--- |
| **📊 Evolução Histórica** | Tendência do indicador ao longo do tempo. | Gráfico de Linha | Detalhe por ano (`dtick=1`) e traço em `yellow` para contraste no tema escuro. |
| **🗺️ Distribuição Regional** | Comparação de desempenho entre as UFs para identificar outliers e padrões. | Gráfico de Barras (Ranking) | Utiliza `color='Regiao'` e `yaxis={'categoryorder':'total ascending'}` para ordenar as UFs pelo valor, criando um ranking de fácil leitura. |
| **🔗 Correlação** | Relação estatística entre dois indicadores para inferir causas e efeitos. | Gráfico de Dispersão (`Scatter Plot`) e `st.info` | Cálculo e exibição do **Coeficiente de Correlação de Pearson (r)**, uma métrica-chave em análise de dados. |
