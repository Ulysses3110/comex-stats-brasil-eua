import streamlit as st
import pandas as pd
import openpyxl as xls


# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Comércio Bilateral Brasil x EUA",
    page_icon="📊",
    layout="wide",
)
# --- Carregamento dos dados ---
df = pd.read_excel("df_comex.xlsx")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Fluxo
fluxo_disponiveis = sorted(df['Fluxo'].unique())
fluxo_selecionados = st.sidebar.multiselect("Fluxo", fluxo_disponiveis, default=fluxo_disponiveis)

# Filtro de Ano
ano_disponiveis = sorted(df['Ano'].unique())
ano_selecionados = st.sidebar.multiselect("Ano", ano_disponiveis, default=ano_disponiveis)

# Filtro por CGCE
cgce_disponiveis = sorted(df['Descrição CGCE Nível 1'].unique())
cgce_selecionados = st.sidebar.multiselect("Descrição CGCE Nível 1", cgce_disponiveis, default=cgce_disponiveis)

# Filtro por ISIC
isic_disponiveis = sorted(df['Descrição ISIC Seção'].unique())
isic_selecionados = st.sidebar.multiselect("Descrição ISIC Seção", isic_disponiveis, default=isic_disponiveis)

# Filtro por CUCI
cuci_disponiveis = sorted(df['Descrição CUCI Seção'].unique())
cuci_selecionados = st.sidebar.multiselect("Descrição CUCI Seção", cuci_disponiveis, default=cuci_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['Fluxo'].isin(fluxo_selecionados)) &
    (df['Ano'].isin(ano_selecionados)) &
    (df['Descrição CGCE Nível 1'].isin(cgce_selecionados)) &
    (df['Descrição ISIC Seção'].isin(isic_selecionados)) &
    (df['Descrição CUCI Seção'].isin(cuci_selecionados))
]
# --- Conteúdo Principal ---
st.title("Comércio Bilateral Brasil x EUA")
st.markdown("Explore os fluxos comerciais entre Brasil e EUA nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Comércio Bilateral (Valores em USD)")

if not df_filtrado.empty:
    valor_total = df_filtrado['Valor US$ FOB'].sum()
    valor_maximo = df_filtrado['Valor US$ FOB'].max()
    total_registros = df_filtrado.shape[0]
else:
    valor_total, valor_maximo, total_registros = 0, 0, 0

col1, col2, col3 = st.columns(3)
col1.metric("valor total", f"${valor_total:,.0f}")
col2.metric("valor maximo", f"${valor_maximo:,.0f}")
col3.metric("total registros", f"{total_registros:,}")

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

import plotly.express as px

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_ncm = df_filtrado.groupby('Descrição NCM')['Valor US$ FOB'].sum().nlargest(20).sort_values(ascending=True).reset_index()
        grafico_ncm = px.bar(
            top_ncm,
            x='Valor US$ FOB',
            y='Descrição NCM',
            orientation='h',
            title="Top 20 NCM por valor total",
            labels={'Valor US$ FOB': 'Valor anual (USD)', 'Descrição NCM': ''}
        )
        grafico_ncm.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_ncm, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de ncm.")

with col_graf2:
    if not df_filtrado.empty:
        top_cgce = df_filtrado.groupby('Descrição CGCE Nível 1')['Valor US$ FOB'].sum().nlargest(5).sort_values(ascending=True).reset_index()
        grafico_cgce = px.bar(
            top_cgce,
            x='Valor US$ FOB',
            y='Descrição CGCE Nível 1',
            orientation='h',
            title="Top 5 CGCE",
            labels={'Valor US$ FOB': 'Valor anual (USD)', 'Descrição CGCE Nível 1': ''}
        )
        grafico_cgce.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cgce, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cgce.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        top_cuci = df_filtrado.groupby('Descrição CUCI Seção')['Valor US$ FOB'].sum().nlargest(5).sort_values(ascending=True).reset_index()
        grafico_cuci = px.bar(
            top_cuci,
            x='Valor US$ FOB',
            y='Descrição CUCI Seção',
            orientation='h',
            title="Top 5 CUCI por valor total",
            labels={'Valor US$ FOB': 'Valor anual (USD)', 'Descrição CUCI Seção': ''}
        )
        grafico_cuci.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cuci, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cuci.")

with col_graf4:
    if not df_filtrado.empty:
        isic_contagem = df_filtrado['Descrição ISIC Seção'].value_counts().reset_index()
        isic_contagem.columns = ['Descrição ISIC Seção', 'Valor US$ FOB']
        grafico_remoto = px.pie(
            isic_contagem,
            names='Descrição ISIC Seção',
            values='Valor US$ FOB',
            title='Share ISIC',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos ISIC.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)

