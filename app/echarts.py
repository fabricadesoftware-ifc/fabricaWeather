import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts
from datetime import datetime
import json

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard Meteorológico")

# Título da aplicação
st.title("Dashboard de Dados Meteorológicos")


# Função para converter valores NaN para None (que é tratado como null em JSON)
def replace_nan(obj):
    if isinstance(obj, (list, tuple)):
        return [replace_nan(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: replace_nan(value) for key, value in obj.items()}
    elif pd.isna(obj):
        return None
    else:
        return obj


# Função para carregar e processar os dados
def load_data(file_input):
    if file_input is not None:
        # Carregar dados
        df = pd.read_csv(file_input, sep=";", na_values=["---"])

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

# Usar arquivo padrão
use_default = st.checkbox("Usar arquivo padrão", value=False)

# Define qual arquivo usar: upload ou padrão.
if use_default:
    # O arquivo padrão deve estar disponível no diretório em que o seu app está rodando
    file_to_load = "ALL.csv"
elif uploaded_file is not None:
    file_to_load = uploaded_file
else:
    file_to_load = None

# Carregar os dados
df = load_data(file_to_load)

if df is not None:
    st.success("Dados carregados com sucesso!")

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
            
            # Preparar dados para ECharts
            dates = df_filtered["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            temp_out = df_filtered["Temp Out"].tolist()
            hi_temp = df_filtered["Hi Temp"].tolist()
            low_temp = df_filtered["Low Temp"].tolist()
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Temperatura ao Longo do Tempo"},
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["Temp. Atual", "Temp. Máxima", "Temp. Mínima"]},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Temperatura (°C)"},
                "series": [
                    {"name": "Temp. Atual", "type": "line", "data": temp_out},
                    {"name": "Temp. Máxima", "type": "line", "data": hi_temp},
                    {"name": "Temp. Mínima", "type": "line", "data": low_temp},
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    if temp_range:
        with col2:
            st.subheader("Amplitude Térmica Diária")
            
            # Agrupar por dia e calcular a amplitude
            daily_temps = (
                df_filtered.groupby(df_filtered["Date"].dt.date)
                .agg({"Hi Temp": "max", "Low Temp": "min"})
                .reset_index()
            )
            daily_temps["Amplitude"] = daily_temps["Hi Temp"] - daily_temps["Low Temp"]
            
            # Preparar dados para ECharts
            dates = [str(date) for date in daily_temps["Date"].tolist()]
            amplitudes = replace_nan(daily_temps["Amplitude"].tolist())
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Amplitude Térmica Diária"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Amplitude (°C)"},
                "series": [
                    {
                        "name": "Amplitude",
                        "type": "line",
                        "areaStyle": {},
                        "data": amplitudes,
                    }
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    if temp_sensation:
        with col1:
            st.subheader("Temperatura vs. Sensação Térmica")
            
            dates = df_filtered["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            temp_out = replace_nan(df_filtered["Temp Out"].tolist())
            
            series = [{"name": "Temperatura", "type": "line", "data": temp_out}]
            legend_data = ["Temperatura"]
            
            if "Wind Chill" in df_filtered.columns:
                wind_chill = replace_nan(df_filtered["Wind Chill"].tolist())
                series.append({"name": "Sensação Térmica (Vento)", "type": "line", "data": wind_chill})
                legend_data.append("Sensação Térmica (Vento)")
                
            if "Heat Index" in df_filtered.columns:
                heat_index = replace_nan(df_filtered["Heat Index"].tolist())
                series.append({"name": "Índice de Calor", "type": "line", "data": heat_index})
                legend_data.append("Índice de Calor")
            
            options = {
                "title": {"text": "Temperatura Real vs. Sensação Térmica"},
                "tooltip": {"trigger": "axis"},
                "legend": {"data": legend_data},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Temperatura (°C)"},
                "series": series,
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")


    # Umidade e Ponto de Orvalho
    if humid_dewpoint:
        with col2:
            st.subheader("Umidade e Ponto de Orvalho")
            
            # Preparar dados para ECharts
            dates = df_filtered["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            temp_out = replace_nan(df_filtered["Temp Out"].tolist())
            dew_pt = replace_nan(df_filtered["Dew Pt."].tolist())
            out_hum = replace_nan(df_filtered["Out Hum"].tolist())
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Temperatura, Ponto de Orvalho e Umidade"},
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["Temperatura", "Ponto de Orvalho", "Umidade"]},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": [
                    {"type": "value", "name": "Temperatura (°C)", "position": "left"},
                    {"type": "value", "name": "Umidade (%)", "position": "right"}
                ],
                "series": [
                    {
                        "name": "Temperatura",
                        "type": "line",
                        "data": temp_out
                    },
                    {
                        "name": "Ponto de Orvalho",
                        "type": "line",
                        "data": dew_pt
                    },
                    {
                        "name": "Umidade",
                        "type": "line",
                        "yAxisIndex": 1,
                        "data": out_hum
                    }
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    if temp_humid_scatter:
        with col1:
            st.subheader("Relação entre Temperatura e Umidade")
            
            # Preparar dados para ECharts
            scatter_data = []
            for t, h in zip(df_filtered["Temp Out"].tolist(), df_filtered["Out Hum"].tolist()):
                if not pd.isna(t) and not pd.isna(h):
                    scatter_data.append([t, h])
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Dispersão: Temperatura vs. Umidade"},
                "tooltip": {
                    "trigger": "item", 
                    "formatter": "Temperatura: {c[0]}°C<br/>Umidade: {c[1]}%"
                },
                "xAxis": {"type": "value", "name": "Temperatura (°C)"},
                "yAxis": {"type": "value", "name": "Umidade (%)"},
                "series": [
                    {
                        "symbolSize": 5,
                        "type": "scatter",
                        "data": scatter_data,
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0,
                                "y": 0,
                                "x2": 1,
                                "y2": 0,
                                "colorStops": [
                                    {"offset": 0, "color": "blue"},
                                    {"offset": 1, "color": "red"}
                                ]
                            }
                        }
                    }
                ]
            }
            
            st_echarts(options=options, height="400px")

    # Gráficos de Vento
    if wind_speed_time:
        with col2:
            st.subheader("Velocidade do Vento ao Longo do Tempo")
            
            # Preparar dados para ECharts
            dates = df_filtered["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            wind_speed = replace_nan(df_filtered["Wind Speed"].tolist())
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Velocidade do Vento"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Velocidade (km/h)"},
                "series": [
                    {
                        "name": "Velocidade",
                        "type": "line",
                        "data": wind_speed,
                        "itemStyle": {"color": "#5470c6"}
                    }
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    if wind_gusts:
        with col1:
            st.subheader("Rajadas Máximas de Vento")
            
            # Agrupar por dia e pegar a rajada máxima
            daily_wind = (
                df_filtered.groupby(df_filtered["Date"].dt.date)
                .agg({"Hi Speed": "max"})
                .reset_index()
            )
            
            # Preparar dados para ECharts
            dates = [str(date) for date in daily_wind["Date"].tolist()]
            hi_speed = replace_nan(daily_wind["Hi Speed"].tolist())
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Rajadas Máximas Diárias"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Velocidade Máxima (km/h)"},
                "series": [
                    {
                        "name": "Rajada Máxima",
                        "type": "bar",
                        "data": hi_speed,
                        "itemStyle": {"color": "#91cc75"}
                    }
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

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
            
            # Preparar dados para gráfico de rosa dos ventos
            # Agrupar direções em bins de 10 graus
            bins = list(range(0, 361, 10))
            labels = [(bins[i] + bins[i+1])/2 for i in range(len(bins)-1)]
            
            wind_dir_binned = pd.cut(wind_directions, bins=bins, labels=labels)
            wind_speed = df_filtered["Wind Speed"]
            
            wind_data = pd.DataFrame({'direction': wind_dir_binned, 'speed': wind_speed})
            wind_counts = wind_data.groupby('direction').count().reset_index()
            
            # Configuração do gráfico ECharts para rosa dos ventos
            angles = wind_counts['direction'].tolist()
            counts = wind_counts['speed'].tolist()
            
            options = {
                "title": {"text": "Rosa dos Ventos"},
                "polar": {},
                "tooltip": {"trigger": "item"},
                "angleAxis": {
                    "type": "category",
                    "data": angles,
                    "clockwise": False,
                    "axisLine": {"show": False}
                },
                "radiusAxis": {
                    "type": "value",
                    "axisLine": {"show": False}
                },
                "series": [
                    {
                        "type": "bar",
                        "data": counts,
                        "coordinateSystem": "polar",
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0,
                                "y": 0,
                                "x2": 0,
                                "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": "#ffa500"},
                                    {"offset": 1, "color": "#ff6347"}
                                ]
                            }
                        }
                    }
                ]
            }
            
            st_echarts(options=options, height="400px")

    # Gráficos de Precipitação
    if rain_daily and "Rain" in df_filtered.columns:
        with col1:
            st.subheader("Precipitação Diária")
            
            # Agrupar por dia e somar precipitação
            daily_rain = (
                df_filtered.groupby(df_filtered["Date"].dt.date)
                .agg({"Rain": "sum"})
                .reset_index()
            )
            
            # Preparar dados para ECharts
            dates = [str(date) for date in daily_rain["Date"].tolist()]
            rain = replace_nan(daily_rain["Rain"].tolist())
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Precipitação Diária"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Precipitação (mm)"},
                "series": [
                    {
                        "name": "Precipitação",
                        "type": "bar",
                        "data": rain,
                        "itemStyle": {"color": "#5470c6"}
                    }
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    if rain_rate and "Rain Rate" in df_filtered.columns:
        with col2:
            st.subheader("Taxa de Precipitação")
            
            # Preparar dados para ECharts
            dates = df_filtered["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            rain_rate = replace_nan(df_filtered["Rain Rate"].tolist())
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Taxa de Precipitação"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Taxa (mm/h)"},
                "series": [
                    {
                        "name": "Taxa de Precipitação",
                        "type": "line",
                        "data": rain_rate,
                        "itemStyle": {"color": "#3ba272"}
                    }
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    # Gráficos de Radiação Solar e UV
    if solar_daily and "Solar Rad." in df_filtered.columns:
        with col1:
            st.subheader("Radiação Solar Diária")
            
            # Preparar dados para ECharts
            dates = df_filtered["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            solar_rad = replace_nan(df_filtered["Solar Rad."].tolist())
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Radiação Solar"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Radiação (W/m²)"},
                "series": [
                    {
                        "name": "Radiação Solar",
                        "type": "line",
                        "data": solar_rad,
                        "itemStyle": {"color": "#fac858"}
                    }
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    if uv_index and "UV Index" in df_filtered.columns:
        with col2:
            st.subheader("Índice UV Máximo Diário")
            
            # Agrupar por dia e pegar o índice UV máximo
            daily_uv = (
                df_filtered.groupby(df_filtered["Date"].dt.date)
                .agg({"UV Index": "max"})
                .reset_index()
            )
            
            # Preparar dados para ECharts
            dates = [str(date) for date in daily_uv["Date"].tolist()]
            uv = replace_nan(daily_uv["UV Index"].tolist())
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Índice UV Máximo Diário"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": {"type": "value", "name": "Índice UV"},
                "series": [
                    {
                        "name": "Índice UV",
                        "type": "bar",
                        "data": uv,
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0,
                                "y": 0,
                                "x2": 0,
                                "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": "#f1c40f"},
                                    {"offset": 1, "color": "#e74c3c"}
                                ]
                            }
                        }
                    }
                ],
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    # Análises Combinadas
    if multi_axis:
        with col1:
            st.subheader("Temperatura, Umidade e Pressão")
            
            # Preparar dados para ECharts
            dates = df_filtered["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            temp_out = replace_nan(df_filtered["Temp Out"].tolist())
            out_hum = replace_nan(df_filtered["Out Hum"].tolist())
            
            series = [
                {
                    "name": "Temperatura",
                    "type": "line",
                    "data": temp_out,
                    "yAxisIndex": 0
                },
                {
                    "name": "Umidade",
                    "type": "line",
                    "data": out_hum,
                    "yAxisIndex": 1
                }
            ]
            
            if "Bar" in df_filtered.columns:
                bar = df_filtered["Bar"].tolist()
                series.append({
                    "name": "Pressão",
                    "type": "line",
                    "data": bar,
                    "yAxisIndex": 0
                })
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Temperatura, Umidade e Pressão Atmosférica"},
                "tooltip": {"trigger": "axis"},
                "legend": {},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": [
                    {"type": "value", "name": "Temperatura (°C) / Pressão (hPa)"},
                    {"type": "value", "name": "Umidade (%)", "position": "right"}
                ],
                "series": series,
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")

    if internal_external:
        with col2:
            st.subheader("Condições Internas vs. Externas")
            
            # Preparar dados para ECharts
            dates = df_filtered["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            temp_out = replace_nan(df_filtered["Temp Out"].tolist())
            out_hum = replace_nan(df_filtered["Out Hum"].tolist())
            
            series = [
                {
                    "name": "Temp. Externa",
                    "type": "line",
                    "data": temp_out,
                    "yAxisIndex": 0
                },
                {
                    "name": "Umid. Externa",
                    "type": "line",
                    "data": out_hum,
                    "yAxisIndex": 1
                }
            ]
            
            if "In Temp" in df_filtered.columns:
                in_temp = replace_nan(df_filtered["In Temp"].tolist())
                series.append({
                    "name": "Temp. Interna",
                    "type": "line",
                    "data": in_temp,
                    "yAxisIndex": 0
                })
                
            if "In Hum" in df_filtered.columns:
                in_hum = replace_nan(df_filtered["In Hum"].tolist())
                series.append({
                    "name": "Umid. Interna",
                    "type": "line",
                    "data": in_hum,
                    "yAxisIndex": 1
                })
            
            # Configuração do gráfico ECharts
            options = {
                "title": {"text": "Comparação: Condições Internas vs. Externas"},
                "tooltip": {"trigger": "axis"},
                "legend": {},
                "xAxis": {"type": "category", "data": dates},
                "yAxis": [
                    {"type": "value", "name": "Temperatura (°C)"},
                    {"type": "value", "name": "Umidade (%)", "position": "right"}
                ],
                "series": series,
                "dataZoom": [{"type": "inside"}, {"type": "slider"}],
            }
            
            st_echarts(options=options, height="400px")
else:
    # Instruções iniciais quando nenhum arquivo é carregado
    st.info(
        "👆 Carregue um arquivo CSV de dados meteorológicos para visualizar os gráficos."
    )
    st.markdown(
        """
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
        """
    )
