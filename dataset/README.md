# Colunas do Dataset

**Date:** Data da medição.

**Time:** Hora da medição.

## Temperatura e Umidade

**Out Temp:** Temperatura externa medida no momento da leitura.

**THSW Temp:** "Temperature-Humidity-Sun-Wind" – índice que combina temperatura, umidade, radiação solar e vento para calcular uma temperatura aparente mais realista.

**Out Hum:** Umidade relativa do ar externa (%).

**Dew Pt. (Dew Point):** Ponto de orvalho – temperatura na qual a umidade do ar começa a condensar em forma de orvalho.

## Vento
**Wind Speed:** Velocidade instantânea do vento no momento da leitura.

**Wind Dir:** Direção do vento (graus ou pontos cardeais).

**Wind Run:** Distância total percorrida pelo vento em um determinado período (geralmente em km ou milhas).

**Hi Wind Speed:** Maior velocidade do vento registrada no período.

**Hi Wind Dir:** Direção do vento no momento da maior rajada.

**Wind Chill:** Sensação térmica provocada pelo vento – temperatura aparente considerando a perda de calor pelo corpo humano devido ao vento.

## Sensação térmica e índices

**Heat Index:** Índice de calor – temperatura aparente levando em conta temperatura e umidade elevada.

**Cool Index:** Índice de resfriamento – semelhante ao Wind Chill, mas considerando temperatura e umidade.

## Pressão Atmosférica

**Bar:** Pressão atmosférica medida pelo sensor barométrico (geralmente em hPa ou mmHg).

# Precipitação (Chuva)

**Rain:** Total de precipitação acumulada em um período (mm ou polegadas).

**Rain Rate:** Taxa de precipitação (intensidade da chuva em mm/h ou pol/h).

## Radiação Solar e Ultravioleta

**Solar Rad.:** Radiação solar instantânea medida (W/m²).

**Solar Energy:** Energia solar acumulada ao longo do tempo (geralmente em MJ/m²).

**Hi Solar Rad.:** Maior valor de radiação solar registrado no período.

**UV Index:** Índice ultravioleta – escala que mede a intensidade da radiação UV e seu potencial de dano à pele.

**UV Dose:** Quantidade acumulada de exposição à radiação UV ao longo do tempo.

**Hi UV Index:** Maior valor de índice UV registrado no período.

## Dados Internos

**In Temp:** Temperatura interna (provavelmente dentro do abrigo ou da estação).

**In Hum:** Umidade relativa interna.

**In Dew Pt.:** Ponto de orvalho interno.

**In Heat Index:** Índice de calor considerando os dados internos.

**In EMC:** Equilibrium Moisture Content – conteúdo de umidade de equilíbrio (usado para indicar a umidade de materiais orgânicos como madeira ou grãos).

**In Density:** Densidade do ar interno.

## Cálculos Agrícolas e Evapotranspiração

**Evapotranspiração:** perda de água do solo e das plantas devido à radiação solar, temperatura, umidade e vento (geralmente em mm).

**D-D (Grau-dia):** Somas térmicas usadas para calcular o crescimento de culturas agrícolas. Podem ser graus-dia de aquecimento (Heating Degree Days - HDD) ou graus-dia de resfriamento (Cooling Degree Days - CDD).

## Comunicação e Status da Estação

**ISS Recept.:** Qualidade do sinal recebido da estação de medição remota (ISS - Integrated Sensor Suite).

**Arc. Int.:** Intervalo de arquivamento dos dados, ou seja, de quanto em quanto tempo as leituras são registradas no banco de dados.

**Samp Tx:** Amostra da transmissão dos sensores para a central de dados.