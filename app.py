import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configurações Iniciais ---
st.set_page_config(
    page_title="ODS 3 - Saúde e Bem-Estar no Brasil",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Definição dos Indicadores ---
INDICADORES_PARA_GRAFICO = [
    'Mortalidade Infantil (por 1000 NV)',
    'Incidência de AIDS (por 100 mil hab)',
    'Taxa de Suicídio (por 100 mil hab)',
    'Cobertura Pré-Natal (7+ consultas)'
]

INDICADORES_PARA_CORRELACAO = {
    'Mortalidade Infantil (por 1000 NV)': 'Mortalidade Infantil',
    'Incidência de AIDS (por 100 mil hab)': 'Incidência de AIDS',
    'Taxa de Suicídio (por 100 mil hab)': 'Taxa de Suicídio',
    'Cobertura Pré-Natal (7+ consultas)': 'Cobertura Pré-Natal'
}

# --- Carregamento dos Dados ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/ods_saude_brasil_limpo.csv', sep=';')
        
        # Conversão de Tipos e Filtro
        df['Ano'] = df['Ano'].astype(int)
        df['Valor'] = df['Valor'].astype(float)
        df = df[df['Ano'] <= 2025].copy() 

        return df
    except FileNotFoundError:
        st.error("Erro: O arquivo de dados 'data/ods_saude_brasil_limpo.csv' não foi encontrado. Verifique o caminho.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# --- Sidebar para Filtros ---
st.sidebar.header("Filtros de Análise")

indicador_selecionado = st.sidebar.selectbox(
    "Selecione o Indicador Principal:",
    options=INDICADORES_PARA_GRAFICO
)

list_ufs = sorted(df['Nome_UF'].unique().tolist())
list_ufs.insert(0, "BRASIL (Média Nacional)")
uf_selecionada = st.sidebar.selectbox(
    "Selecione a UF para Análise Histórica:",
    options=list_ufs
)

max_year = df['Ano'].max()
ano_selecionado = st.sidebar.slider(
    "Ano para Análise Regional/Correlação:",
    min_value=df['Ano'].min(),
    max_value=max_year,
    value=max_year,
    step=1
)

# --- Título Principal ---
st.title("Dashboard ODS 3: Saúde e Bem-Estar no Brasil 🇧🇷")
st.markdown(f"Análise dos indicadores de **{INDICADORES_PARA_CORRELACAO.get(indicador_selecionado, indicador_selecionado)}** por Unidade Federativa (2018-{max_year})")

# --- Função de Cálculo e Formatação de Variação ---
def calcular_e_formatar_variacao(data_serie):
    if len(data_serie) < 2:
        return "N/A", "off" 
    
    data_serie = data_serie.sort_values()
    valor_inicial = data_serie.iloc[0] 
    valor_final = data_serie.iloc[-1]  

    if valor_inicial == 0:
        return "N/A", "off"

    variacao_percentual = ((valor_final - valor_inicial) / valor_inicial) * 100

    # Lógica para definir a cor do delta (inverso para indicadores negativos)
    if 'Mortalidade' in indicador_selecionado or 'Incidência' in indicador_selecionado or 'Suicídio' in indicador_selecionado:
        cor = "inverse" if variacao_percentual > 0 else "normal"
    elif 'Cobertura' in indicador_selecionado:
        cor = "normal" if variacao_percentual > 0 else "inverse"
    else:
        cor = "off"

    return f"{variacao_percentual:.2f} %", cor

# --- Pré-processamento para Métricas e Histórico ---
if uf_selecionada == "BRASIL (Média Nacional)":
    df_metrica = df[df['Ano'] == max_year].groupby('Indicador')['Valor'].mean().reset_index()
    df_historico_indicador = df.groupby(['Ano', 'Indicador'])['Valor'].mean().reset_index()
    df_historico_indicador = df_historico_indicador[df_historico_indicador['Indicador'] == indicador_selecionado]
    titulo_metrica = "Média Nacional"
else:
    df_metrica = df[(df['Nome_UF'] == uf_selecionada) & (df['Ano'] == max_year)]
    df_historico_indicador = df[(df['Nome_UF'] == uf_selecionada) & (df['Indicador'] == indicador_selecionado)]
    titulo_metrica = uf_selecionada

# --- LAYOUT PRINCIPAL (Colunas de Métricas) ---
valor_atual_principal = df_metrica[df_metrica['Indicador'] == indicador_selecionado]['Valor'].iloc[0] if not df_metrica[df_metrica['Indicador'] == indicador_selecionado].empty else 0
variacao, cor_variacao = calcular_e_formatar_variacao(df_historico_indicador.sort_values(by='Ano')['Valor'])
df_media_nacional = df[df['Ano'] == max_year].groupby('Indicador')['Valor'].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label=f"Valor Mais Recente ({max_year}) em {titulo_metrica}",
        value=f"{valor_atual_principal:.2f}",
        delta=f"Variação ({df['Ano'].min()}-{max_year}): {variacao}",
        delta_color=cor_variacao
    )

indicadores_ref = [ind for ind in INDICADORES_PARA_GRAFICO if ind != indicador_selecionado]

for i, ind_ref in enumerate(indicadores_ref):
    valor_atual_ref = df_metrica[df_metrica['Indicador'] == ind_ref]['Valor'].iloc[0] if not df_metrica[df_metrica['Indicador'] == ind_ref].empty else 0
    media_nacional_ref = df_media_nacional.get(ind_ref, 0)
    
    if media_nacional_ref != 0:
        diferenca_percentual = ((valor_atual_ref - media_nacional_ref) / media_nacional_ref) * 100
        delta_str = f"{diferenca_percentual:.2f} %"
    else:
        delta_str = "N/A"

    if 'Mortalidade' in ind_ref or 'Incidência' in ind_ref or 'Suicídio' in ind_ref:
        cor_ref = "inverse" if valor_atual_ref > media_nacional_ref else "normal"
    elif 'Cobertura' in ind_ref:
        cor_ref = "normal" if valor_atual_ref > media_nacional_ref else "inverse"
    else:
        cor_ref = "off"

    with [col2, col3, col4][i]:
        st.metric(
            label=f"Ref: {INDICADORES_PARA_CORRELACAO[ind_ref]} ({max_year})",
            value=f"{valor_atual_ref:.2f}",
            delta=f"Vs. Média Nacional: {delta_str}",
            delta_color=cor_ref
        )


# =========================================================================
# --- LAYOUT COM ABAS (st.tabs) ---
# =========================================================================

tab_evolucao, tab_regional, tab_correlacao = st.tabs(["📊 Evolução Histórica", "🗺️ Distribuição Regional", "🔗 Correlação"])

# -----------------------------------------------------------
# TAB 1: EVOLUÇÃO HISTÓRICA
# -----------------------------------------------------------
with tab_evolucao:
    st.subheader(f"Evolução Histórica do Indicador em {titulo_metrica}")
    
    fig_evolucao = px.line(
        df_historico_indicador,
        x='Ano',
        y='Valor',
        markers=True,
        title=f'Série Histórica de {INDICADORES_PARA_CORRELACAO.get(indicador_selecionado, indicador_selecionado)} ({df["Ano"].min()}-{max_year})',
        template='plotly_dark'
    )
    fig_evolucao.update_traces(line=dict(color='yellow', width=3))
    
    fig_evolucao.update_xaxes(
        dtick=1, 
        tickformat='d', 
        categoryorder='category ascending' 
    )
    st.plotly_chart(fig_evolucao, use_container_width=True)


# -----------------------------------------------------------
# TAB 2: DISTRIBUIÇÃO REGIONAL
# -----------------------------------------------------------
with tab_regional:
    st.subheader(f"Distribuição Regional do Indicador (Ano: {ano_selecionado})")
    
    df_filtrado_ano_indicador = df[(df['Ano'] == ano_selecionado) & (df['Indicador'] == indicador_selecionado)]
    df_regional = df_filtrado_ano_indicador.groupby(['Regiao', 'Nome_UF'])['Valor'].mean().reset_index()

    fig_regional = px.bar(
        df_regional,
        x='Valor',
        y='Nome_UF',
        color='Regiao',
        orientation='h',
        title=f'Distribuição por UF em {ano_selecionado}',
        template='plotly_dark',
        height=600,
        labels={'Valor': indicador_selecionado, 'Nome_UF': 'Unidade Federativa'}
    )
    fig_regional.update_layout(yaxis={'categoryorder':'total ascending'})
    
    st.plotly_chart(fig_regional, use_container_width=True)


# -----------------------------------------------------------
# TAB 3: CORRELAÇÃO DE INDICADORES
# -----------------------------------------------------------
with tab_correlacao:
    st.subheader(f"Análise de Correlação entre Indicadores (Ano: {ano_selecionado})")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        indicador_corr_x = st.selectbox(
            "Selecione o Indicador A (Eixo X):",
            options=INDICADORES_PARA_GRAFICO,
            index=0 
        )

    with col_y:
        opcoes_y = [ind for ind in INDICADORES_PARA_GRAFICO if ind != indicador_corr_x]
        try:
            default_index = opcoes_y.index('Cobertura Pré-Natal (7+ consultas)')
        except ValueError:
            default_index = 0

        indicador_corr_y = st.selectbox(
            "Selecione o Indicador B (Eixo Y):",
            options=opcoes_y,
            index=default_index
        )
        
    df_corr_base = df[df['Ano'] == ano_selecionado].pivot(
        index='Nome_UF', 
        columns='Indicador', 
        values='Valor'
    ).reset_index()
    
    try:
        correlacao = df_corr_base[indicador_corr_x].corr(df_corr_base[indicador_corr_y])
        correlacao_str = f"{correlacao:.2f}"
    except Exception:
        correlacao_str = "N/A"

    st.info(f"O Coeficiente de Correlação de Pearson (r) entre **{INDICADORES_PARA_CORRELACAO[indicador_corr_x]}** e **{INDICADORES_PARA_CORRELACAO[indicador_corr_y]}** é: **{correlacao_str}**")
    
    fig_corr = px.scatter(
        df_corr_base,
        x=indicador_corr_x,
        y=indicador_corr_y,
        hover_name='Nome_UF',
        title=f'Correlação entre {INDICADORES_PARA_CORRELACAO[indicador_corr_x]} e {INDICADORES_PARA_CORRELACAO[indicador_corr_y]}',
        template='plotly_dark'
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# --- Rodapé com Expander para Documentação ---
st.markdown("---")

with st.expander("📚 Documentação dos Indicadores ODS 3 Selecionados"):
    st.markdown(
        """
        * **Mortalidade Infantil:** Número de óbitos de menores de 1 ano por 1.000 nascidos vivos (Meta 3.2).
        * **Incidência de AIDS:** Casos novos de AIDS por 100 mil habitantes (Meta 3.3 - Combate a Doenças Transmissíveis).
        * **Taxa de Suicídio:** Óbitos por suicídio por 100 mil habitantes (Meta 3.4 - Saúde Mental e Bem-Estar Psicológico).
        * **Cobertura Pré-Natal:** Percentual de nascidos vivos cujas mães realizaram 7 ou mais consultas de pré-natal (Meta 3.7/3.8 - Acesso a Serviços de Saúde e Promoção da Saúde).
        """
    )