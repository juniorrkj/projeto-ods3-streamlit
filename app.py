# app.py - CÓDIGO FINAL COM ANÁLISE DE CORRELAÇÃO

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="📊 ODS 3: Indicadores de Saúde e Bem-Estar no Brasil",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = os.path.join("data", "ods_saude_brasil_limpo.csv")


# --- 2. CARREGAMENTO E CACHE DE DADOS ---
@st.cache_data
def load_data():
    """Carrega o DataFrame e garante a tipagem correta."""
    try:
        df = pd.read_csv(DATA_PATH, sep=';')
        df['Ano'] = df['Ano'].astype(int)
        df['Valor'] = df['Valor'].astype(float)
        return df
    
    except Exception as e:
        st.error(f"Erro de carregamento. Detalhe: {e}")
        return pd.DataFrame()

df_full = load_data()


# --- 3. DICIONÁRIO PARA AJUDA VISUAL (EMOJIS) ---
INDICATOR_ICONS = {
    'Mortalidade Infantil (por 1000 NV)': '👶',
    'Casos de Tuberculose (por 100 mil hab)': '🦠',
    'Razão de Mortalidade Materna (por 100 mil NV)': '🤰',
    'Taxa de Suicídio (por 100 mil hab)': '🧠',
    'Cobertura de Pré-Natal (em %)': '🏥'
}
 

# --- 4. CONSTRUÇÃO DO DASHBOARD ---

if not df_full.empty:
    
    # 4.1. BARRA LATERAL (FILTROS)
    st.sidebar.title("🛠️ Configurações de Análise")

    indicadores_unicos = df_full['Indicador'].unique()

    def format_indicador_option(indicador):
        icon = INDICATOR_ICONS.get(indicador, '📈')
        return f"{icon} {indicador}"

    # Filtro 1: Indicador Principal
    indicador_selecionado_formatado = st.sidebar.selectbox(
        "1. Selecione o Indicador Principal:",
        options=[format_indicador_option(i) for i in indicadores_unicos]
    )
    indicador_principal = indicador_selecionado_formatado.split(' ', 1)[-1]
    
    # Filtro 2: Indicador Secundário (PARA CORRELAÇÃO)
    indicador_secundario_options = [i for i in indicadores_unicos if i != indicador_principal]
    indicador_secundario_formatado = st.sidebar.selectbox(
        "2. Selecione o Indicador para Correlação:",
        options=[format_indicador_option(i) for i in indicador_secundario_options]
    )
    indicador_secundario = indicador_secundario_formatado.split(' ', 1)[-1]

    # Filtro 3: Região
    regioes_unicas = sorted(df_full['Regiao'].unique())
    regioes_selecionadas = st.sidebar.multiselect(
        "3. Selecione a(s) Região(ões):",
        options=regioes_unicas,
        default=regioes_unicas
    )

    # Filtro 4: UF
    ufs_disponiveis = sorted(df_full[df_full['Regiao'].isin(regioes_selecionadas)]['Nome_UF'].unique())
    ufs_selecionadas = st.sidebar.multiselect(
        "4. Selecione as Unidades Federativas (UF):",
        options=ufs_disponiveis,
        default=ufs_disponiveis
    )

    # Aplica os filtros para o indicador principal (para os gráficos 1, 2 e KPIs)
    df_principal_filtrado = df_full[
        (df_full['Indicador'] == indicador_principal) & 
        (df_full['Nome_UF'].isin(ufs_selecionadas))
    ]

    # --- 5. TÍTULO E INTRODUÇÃO ---
    st.markdown(f"## {INDICATOR_ICONS.get(indicador_principal, '📈')} ODS 3: {indicador_principal}")
    st.markdown("##### *Objetivo de Desenvolvimento Sustentável 3: Saúde e Bem-Estar*")
    st.markdown("---")

    # --- 6. VISUALIZAÇÃO DE DADOS ---
    if not df_principal_filtrado.empty:
        
        unidade_principal = indicador_principal.split('(')[-1].replace(')', '').strip() if '(' in indicador_principal else 'Valor'
        unidade_secundaria = indicador_secundario.split('(')[-1].replace(')', '').strip() if '(' in indicador_secundario else 'Valor'

        # Agrupa os dados para métricas de resumo
        df_resumo = df_principal_filtrado.groupby('Ano')['Valor'].mean().reset_index()
        
        # --- 6.1. CARDS DE MÉTRICAS (KPIs do Indicador Principal) ---
        st.subheader("Resumo do Indicador Principal")
        col1, col2, col3 = st.columns(3)
        
        ultimo_ano = df_resumo['Ano'].max()
        primeiro_ano = df_resumo['Ano'].min()
        
        media_ultimo_ano = df_resumo[df_resumo['Ano'] == ultimo_ano]['Valor'].iloc[0]
        media_primeiro_ano = df_resumo[df_resumo['Ano'] == primeiro_ano]['Valor'].iloc[0]
        
        variacao = ((media_ultimo_ano - media_primeiro_ano) / media_primeiro_ano) * 100
        delta_label = f"{variacao:.2f}%"
        
        col1.metric(
            label=f"Média Geral ({ultimo_ano})",
            value=f"{media_ultimo_ano:.2f} {unidade_principal}"
        )
        col2.metric(
            label=f"Média Geral ({primeiro_ano})",
            value=f"{media_primeiro_ano:.2f} {unidade_principal}"
        )
        col3.metric(
            label="Variação Total",
            value=f"{media_ultimo_ano - media_primeiro_ano:.2f} {unidade_principal}",
            delta=delta_label
        )
        
        st.markdown("---")
        
        # --- 6.2. GRÁFICO DE LINHA (SÉRIE HISTÓRICA POR UF) ---
        st.subheader("Evolução Histórica por Unidade Federativa")
        
        fig_uf = px.line(
            df_principal_filtrado,
            x='Ano',
            y='Valor',
            color='Nome_UF',
            markers=True,
            title=f'Série Histórica de {indicador_principal}',
            labels={
                "Valor": f"Valor ({unidade_principal})",
                "Ano": "Ano",
                "Nome_UF": "UF"
            },
            template="plotly_dark"
        )
        
        fig_uf.update_layout(hovermode="x unified")
        st.plotly_chart(fig_uf, use_container_width=True)


        # --- 6.3. ANÁLISE DE CORRELAÇÃO (GRÁFICO NOVO) ---
        st.markdown("## 🔎 Análise de Correlação entre Indicadores")

        # 1. Pivotar o DataFrame para ter os dois indicadores em colunas
        df_corr = df_full[
            df_full['Indicador'].isin([indicador_principal, indicador_secundario]) &
            df_full['Nome_UF'].isin(ufs_selecionadas)
        ]
        
        # Cria a tabela de comparação (Ano, UF, Valor_Principal, Valor_Secundario)
        df_pivot = df_corr.pivot_table(
            index=['Nome_UF', 'Ano', 'Regiao'],
            columns='Indicador',
            values='Valor'
        ).reset_index()

        # 2. Calcular o Coeficiente de Correlação de Pearson (em todos os pontos de dados)
        correlacao = df_pivot[indicador_principal].corr(df_pivot[indicador_secundario])

        # 3. Exibir o Coeficiente de Correlação
        st.metric(
            label=f"Coeficiente de Correlação de Pearson (r) entre {indicador_principal} e {indicador_secundario}",
            value=f"{correlacao:.3f}",
            delta=f"Relação {'Positiva Forte' if correlacao > 0.7 else ('Positiva' if correlacao > 0.3 else ('Negativa Forte' if correlacao < -0.7 else ('Negativa' if correlacao < -0.3 else 'Fraca/Nula')))}"
        )
        
        st.caption("Quanto mais próximo de 1, mais forte é a relação positiva (ambos sobem). Quanto mais próximo de -1, mais forte é a relação negativa (um sobe, o outro desce).")


        # 4. Gráfico de Dispersão (Scatter Plot)
        fig_corr = px.scatter(
            df_pivot,
            x=indicador_principal,
            y=indicador_secundario,
            color='Regiao',
            hover_data=['Nome_UF', 'Ano'],
            title=f'Correlação: {indicador_principal} vs. {indicador_secundario}',
            labels={
                indicador_principal: f'X: {indicador_principal} ({unidade_principal})',
                indicador_secundario: f'Y: {indicador_secundario} ({unidade_secundaria})'
            },
            template="plotly_dark"
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("---")

        # --- 6.4. Tabela de Dados (Expansível) ---
        with st.expander("Visualizar Tabela de Dados Completos do Indicador Principal"):
            st.dataframe(df_principal_filtrado, use_container_width=True)

    else:
        st.info("Selecione um indicador e pelo menos uma UF para visualizar os dados.")