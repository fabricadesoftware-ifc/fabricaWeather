import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard Meteorológico")

# Título da aplicação
st.title("Dashboard de Dados Meteorológicos")


# Função para carregar e processar os dados
def load_data(uploaded_file):
    if uploaded_file is not None:
        # Carregar dados
        df = pd.read_csv(uploaded_file, sep=";", na_values=["---"])

        # Converter colunas de data e hora
        try:
            # Verificar o formato da data
            if len(df["Date"].iloc[0].split("/")[0]) == 2:  # DD/MM/YY
                df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%y")
            else:  # Tentar outros formatos
                df["Date"] = pd.to_datetime(df["Date"])

            # Combinar data e hora
            if "Time" in df.columns:
                df["DateTime"] = pd.to_datetime(
                    df["Date"].dt.strftime("%Y-%m-%d") + " " + df["Time"]
                )

        except Exception as e:
            st.warning(f"Não foi possível analisar corretamente as datas: {e}")
            # Tentar uma abordagem alternativa
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            if "Time" in df.columns:
                df["DateTime"] = df["Date"]

        # Converter colunas numéricas para float
        numeric_columns = [
            "Temp Out",
            "Hi Temp",
            "Low Temp",
            "Out Hum",
            "Dew Pt.",
            "Wind Speed",
            "Wind Run",
            "Hi Speed",
            "Wind Chill",
            "Heat Index",
            "THW Index",
            "THSW Index",
            "Bar",
            "Rain",
            "Rain Rate",
            "Solar Rad.",
            "Solar Energy",
            "Hi Solar Rad.",
            "UV Index",
            "UV Dose",
            "Hi UV",
            "Heat D-D",
            "Cool D-D",
            "In Temp",
            "In Hum",
            "In Dew",
            "In Heat",
            "In EMC",
            "In Air Density",
            "ET",
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df
    return None


# Widget de upload de arquivo
uploaded_file = st.file_uploader(
    "Carregar arquivo CSV de dados meteorológicos", type=["csv"]
)

# Verificar se um arquivo foi carregado
if uploaded_file is not None:
    # Carregar os dados
    df = load_data(uploaded_file)

    if df is not None:
        # Mostrar informações básicas sobre os dados
        st.header("Visão Geral dos Dados")
        st.write(f"Período dos dados: {df['Date'].min()} a {df['Date'].max()}")
        st.write(f"Total de registros: {len(df)}")

        # Mostrar amostra dos dados
        with st.expander("Visualizar amostra dos dados"):
            st.dataframe(df.head())

        # Sidebar para selecionar gráficos
        st.sidebar.header("Selecionar Visualizações")

        # Separar os gráficos em categorias
        st.sidebar.subheader("Gráficos de Temperatura")
        temp_series = st.sidebar.checkbox("Série temporal de temperatura")
        temp_range = st.sidebar.checkbox("Amplitude térmica")
        temp_sensation = st.sidebar.checkbox("Temperatura vs. Sensação térmica")

        st.sidebar.subheader("Umidade e Ponto de Orvalho")
        humid_dewpoint = st.sidebar.checkbox("Umidade e ponto de orvalho")
        temp_humid_scatter = st.sidebar.checkbox("Dispersão temperatura vs. umidade")

        st.sidebar.subheader("Vento")
        wind_rose = st.sidebar.checkbox("Rosa dos ventos")
        wind_speed_time = st.sidebar.checkbox("Velocidade do vento ao longo do tempo")
        wind_gusts = st.sidebar.checkbox("Rajadas máximas")

        st.sidebar.subheader("Precipitação")
        rain_daily = st.sidebar.checkbox("Precipitação diária")
        rain_rate = st.sidebar.checkbox("Taxa de precipitação")

        st.sidebar.subheader("Radiação Solar e UV")
        solar_daily = st.sidebar.checkbox("Radiação solar diária")
        uv_index = st.sidebar.checkbox("Índice UV máximo diário")

        st.sidebar.subheader("Análises Combinadas")
        multi_axis = st.sidebar.checkbox("Temperatura, umidade e pressão")
        internal_external = st.sidebar.checkbox("Condições internas vs. externas")

        # Adicionar filtro de data
        if "Date" in df.columns:
            st.sidebar.subheader("Filtrar por Data")
            min_date = df["Date"].min().date()
            max_date = df["Date"].max().date()

            start_date = st.sidebar.date_input(
                "Data inicial", min_date, min_value=min_date, max_value=max_date
            )
            end_date = st.sidebar.date_input(
                "Data final", max_date, min_value=min_date, max_value=max_date
            )

            # Aplicar filtro de data
            df_filtered = df[
                (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
            ]
        else:
            df_filtered = df

        # Layout de colunas para organizar os gráficos
        col1, col2 = st.columns(2)

        # Gráficos de Temperatura
        if temp_series:
            with col1:
                st.subheader("Série Temporal de Temperatura")
                fig = px.line(
                    df_filtered,
                    x="DateTime",
                    y=["Temp Out", "Hi Temp", "Low Temp"],
                    title="Temperatura ao Longo do Tempo",
                    labels={"value": "Temperatura (°C)", "DateTime": "Data/Hora"},
                )
                st.plotly_chart(fig, use_container_width=True)

        if temp_range:
            with col2:
                st.subheader("Amplitude Térmica Diária")
                # Agrupar por dia e calcular a amplitude
                daily_temps = (
                    df_filtered.groupby(df_filtered["Date"].dt.date)
                    .agg({"Hi Temp": "max", "Low Temp": "min"})
                    .reset_index()
                )
                daily_temps["Amplitude"] = (
                    daily_temps["Hi Temp"] - daily_temps["Low Temp"]
                )

                fig = px.area(
                    daily_temps,
                    x="Date",
                    y="Amplitude",
                    title="Amplitude Térmica Diária",
                    labels={"Amplitude": "Amplitude (°C)", "Date": "Data"},
                )
                st.plotly_chart(fig, use_container_width=True)

        if temp_sensation:
            with col1:
                st.subheader("Temperatura vs. Sensação Térmica")

                # Verificar quais colunas existem nos dados
                y_cols = ["Temp Out"]
                if "Wind Chill" in df_filtered.columns:
                    y_cols.append("Wind Chill")
                if "Heat Index" in df_filtered.columns:
                    y_cols.append("Heat Index")

                fig = px.line(
                    df_filtered,
                    x="DateTime",
                    y=y_cols,
                    title="Temperatura Real vs. Sensação Térmica",
                    labels={"value": "Temperatura (°C)", "DateTime": "Data/Hora"},
                )
                st.plotly_chart(fig, use_container_width=True)

        # Umidade e Ponto de Orvalho
        if humid_dewpoint:
            with col2:
                st.subheader("Umidade e Ponto de Orvalho")
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                fig.add_trace(
                    go.Scatter(
                        x=df_filtered["DateTime"],
                        y=df_filtered["Temp Out"],
                        name="Temperatura",
                    ),
                    secondary_y=False,
                )

                fig.add_trace(
                    go.Scatter(
                        x=df_filtered["DateTime"],
                        y=df_filtered["Dew Pt."],
                        name="Ponto de Orvalho",
                    ),
                    secondary_y=False,
                )

                fig.add_trace(
                    go.Scatter(
                        x=df_filtered["DateTime"],
                        y=df_filtered["Out Hum"],
                        name="Umidade",
                    ),
                    secondary_y=True,
                )

                fig.update_layout(
                    title_text="Temperatura, Ponto de Orvalho e Umidade",
                    xaxis_title="Data/Hora",
                )

                fig.update_yaxes(title_text="Temperatura (°C)", secondary_y=False)
                fig.update_yaxes(title_text="Umidade (%)", secondary_y=True)

                st.plotly_chart(fig, use_container_width=True)

        if temp_humid_scatter:
            with col1:
                st.subheader("Relação entre Temperatura e Umidade")
                fig = px.scatter(
                    df_filtered,
                    x="Temp Out",
                    y="Out Hum",
                    color="Temp Out",
                    title="Dispersão: Temperatura vs. Umidade",
                    labels={"Temp Out": "Temperatura (°C)", "Out Hum": "Umidade (%)"},
                )
                st.plotly_chart(fig, use_container_width=True)

        # Gráficos de Vento
        if wind_speed_time:
            with col2:
                st.subheader("Velocidade do Vento ao Longo do Tempo")
                fig = px.line(
                    df_filtered,
                    x="DateTime",
                    y="Wind Speed",
                    title="Velocidade do Vento",
                    labels={"Wind Speed": "Velocidade (km/h)", "DateTime": "Data/Hora"},
                )
                st.plotly_chart(fig, use_container_width=True)

        if wind_gusts:
            with col1:
                st.subheader("Rajadas Máximas de Vento")
                daily_wind = (
                    df_filtered.groupby(df_filtered["Date"].dt.date)
                    .agg({"Hi Speed": "max"})
                    .reset_index()
                )

                fig = px.bar(
                    daily_wind,
                    x="Date",
                    y="Hi Speed",
                    title="Rajadas Máximas Diárias",
                    labels={"Hi Speed": "Velocidade Máxima (km/h)", "Date": "Data"},
                )
                st.plotly_chart(fig, use_container_width=True)

        if wind_rose and "Wind Dir" in df_filtered.columns:
            with col2:
                st.subheader("Rosa dos Ventos")

                # Converter direção do vento de texto para números, se necessário
                if df_filtered["Wind Dir"].dtype == "object":
                    # Mapeamento de direções cardinais para ângulos
                    direction_map = {
                        "N": 0,
                        "NNE": 22.5,
                        "NE": 45,
                        "ENE": 67.5,
                        "E": 90,
                        "ESE": 112.5,
                        "SE": 135,
                        "SSE": 157.5,
                        "S": 180,
                        "SSW": 202.5,
                        "SW": 225,
                        "WSW": 247.5,
                        "W": 270,
                        "WNW": 292.5,
                        "NW": 315,
                        "NNW": 337.5,
                    }

                    # Tentar converter, mantendo NaN onde não é possível
                    wind_dir_numeric = pd.to_numeric(
                        df_filtered["Wind Dir"], errors="coerce"
                    )

                    # Substituir valores não numéricos usando o mapeamento
                    mask = wind_dir_numeric.isna()
                    directions_to_map = df_filtered.loc[mask, "Wind Dir"]

                    for direction, angle in direction_map.items():
                        directions_to_map = directions_to_map.replace(direction, angle)

                    wind_dir_numeric.loc[mask] = pd.to_numeric(
                        directions_to_map, errors="coerce"
                    )
                    wind_directions = wind_dir_numeric
                else:
                    wind_directions = df_filtered["Wind Dir"]

                # Criar figura polar para rosa dos ventos
                fig = px.scatter_polar(
                    df_filtered,
                    r="Wind Speed",
                    theta=wind_directions,
                    color="Wind Speed",
                    title="Rosa dos Ventos",
                )
                fig.update_layout(
                    polar=dict(radialaxis=dict(showticklabels=True, ticks=""))
                )

                st.plotly_chart(fig, use_container_width=True)

        # Gráficos de Precipitação
        if rain_daily and "Rain" in df_filtered.columns:
            with col1:
                st.subheader("Precipitação Diária")
                daily_rain = (
                    df_filtered.groupby(df_filtered["Date"].dt.date)
                    .agg({"Rain": "sum"})
                    .reset_index()
                )

                fig = px.bar(
                    daily_rain,
                    x="Date",
                    y="Rain",
                    title="Precipitação Diária",
                    labels={"Rain": "Precipitação (mm)", "Date": "Data"},
                )
                st.plotly_chart(fig, use_container_width=True)

        if rain_rate and "Rain Rate" in df_filtered.columns:
            with col2:
                st.subheader("Taxa de Precipitação")
                fig = px.line(
                    df_filtered,
                    x="DateTime",
                    y="Rain Rate",
                    title="Taxa de Precipitação",
                    labels={"Rain Rate": "Taxa (mm/h)", "DateTime": "Data/Hora"},
                )
                st.plotly_chart(fig, use_container_width=True)

        # Gráficos de Radiação Solar e UV
        if solar_daily and "Solar Rad." in df_filtered.columns:
            with col1:
                st.subheader("Radiação Solar Diária")
                fig = px.line(
                    df_filtered,
                    x="DateTime",
                    y="Solar Rad.",
                    title="Radiação Solar",
                    labels={"Solar Rad.": "Radiação (W/m²)", "DateTime": "Data/Hora"},
                )
                st.plotly_chart(fig, use_container_width=True)

        if uv_index and "UV Index" in df_filtered.columns:
            with col2:
                st.subheader("Índice UV Máximo Diário")
                daily_uv = (
                    df_filtered.groupby(df_filtered["Date"].dt.date)
                    .agg({"UV Index": "max"})
                    .reset_index()
                )

                fig = px.bar(
                    daily_uv,
                    x="Date",
                    y="UV Index",
                    title="Índice UV Máximo Diário",
                    labels={"UV Index": "Índice UV", "Date": "Data"},
                )
                st.plotly_chart(fig, use_container_width=True)

        # Análises Combinadas
        if multi_axis:
            with col1:
                st.subheader("Temperatura, Umidade e Pressão")
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                fig.add_trace(
                    go.Scatter(
                        x=df_filtered["DateTime"],
                        y=df_filtered["Temp Out"],
                        name="Temperatura",
                    ),
                    secondary_y=False,
                )

                fig.add_trace(
                    go.Scatter(
                        x=df_filtered["DateTime"],
                        y=df_filtered["Out Hum"],
                        name="Umidade",
                    ),
                    secondary_y=True,
                )

                if "Bar" in df_filtered.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df_filtered["DateTime"],
                            y=df_filtered["Bar"],
                            name="Pressão",
                            line=dict(dash="dash"),
                        ),
                        secondary_y=False,
                    )

                fig.update_layout(
                    title_text="Temperatura, Umidade e Pressão Atmosférica",
                    xaxis_title="Data/Hora",
                )

                fig.update_yaxes(
                    title_text="Temperatura (°C) / Pressão (hPa)", secondary_y=False
                )
                fig.update_yaxes(title_text="Umidade (%)", secondary_y=True)

                st.plotly_chart(fig, use_container_width=True)

        if internal_external:
            with col2:
                st.subheader("Condições Internas vs. Externas")
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                fig.add_trace(
                    go.Scatter(
                        x=df_filtered["DateTime"],
                        y=df_filtered["Temp Out"],
                        name="Temp. Externa",
                    ),
                    secondary_y=False,
                )

                if "In Temp" in df_filtered.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df_filtered["DateTime"],
                            y=df_filtered["In Temp"],
                            name="Temp. Interna",
                        ),
                        secondary_y=False,
                    )

                fig.add_trace(
                    go.Scatter(
                        x=df_filtered["DateTime"],
                        y=df_filtered["Out Hum"],
                        name="Umid. Externa",
                        line=dict(dash="dot"),
                    ),
                    secondary_y=True,
                )

                if "In Hum" in df_filtered.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df_filtered["DateTime"],
                            y=df_filtered["In Hum"],
                            name="Umid. Interna",
                            line=dict(dash="dot"),
                        ),
                        secondary_y=True,
                    )

                fig.update_layout(
                    title_text="Comparação: Condições Internas vs. Externas",
                    xaxis_title="Data/Hora",
                )

                fig.update_yaxes(title_text="Temperatura (°C)", secondary_y=False)
                fig.update_yaxes(title_text="Umidade (%)", secondary_y=True)

                st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(
            "Não foi possível processar os dados. Verifique o formato do arquivo CSV."
        )
else:
    # Instruções iniciais quando nenhum arquivo é carregado
    st.info(
        "👆 Carregue um arquivo CSV de dados meteorológicos para visualizar os gráficos."
    )

    st.markdown("""
    ### Informações sobre o formato do arquivo
    O aplicativo espera um arquivo CSV com as seguintes características:
    - Separado por ponto e vírgula (;)
    - Campos nulos representados por "---"
    - Deve conter as colunas fundamentais de uma estação meteorológica (Data, Hora, Temperatura, etc.)
    
    ### Gráficos disponíveis
    Após carregar o arquivo, você poderá selecionar diferentes visualizações no menu lateral:
    - Gráficos de temperatura
    - Análises de umidade e ponto de orvalho
    - Visualizações de vento
    - Análises de precipitação
    - Dados de radiação solar e UV
    - Comparações de condições internas e externas
    """)
