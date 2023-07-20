# Mini-Projeto 1 - Dashboard Interativo com Streamlit, Folium e Plotly Para Monitoramento de Casos de Covid-19 em Tempo Real

# Execute no terminal: streamlit run Mini-Projeto1.py

# Imports
import json
import folium
import requests
import mimetypes
import http.client
import pandas as pd
import streamlit as st
import plotly
import plotly.express as px
from streamlit_folium import folium_static
from folium.plugins import HeatMap
from pandas.io.json import json_normalize
import warnings
warnings.filterwarnings("ignore", category = FutureWarning)

# Função Main
def main():

    # Título da área principal
    st.markdown("<h1 style='text-align: center; color: #fa634d;'><strong><u>Real-Time Covid-19 Dashboard</u></strong></h1>", unsafe_allow_html = True)
    
    # Título do menu lateral
    st.sidebar.markdown("<h1 style='text-align: center; color: #baccee;'><strong><u>Monitoramento de Casos de Covid-19</u></strong></h1>", unsafe_allow_html = True)

    # Sub-títulos da área principal
    st.markdown("O Dashboard Utiliza Dados Reais da Johns Hopkins CSSE.", unsafe_allow_html = True)
    st.markdown("Os Dados São Atualizados Diariamente.", unsafe_allow_html = True)

    # Conexão aos dados em tempo real via API
    # https://coronavirus.jhu.edu/map.html
    # https://covid19api.com/
    conn = http.client.HTTPSConnection("api.covid19api.com")
    payload = ''
    headers = {}
    conn.request("GET","/summary",payload,headers)
    res = conn.getresponse()
    data  = res.read().decode('UTF-8')
    covid = json.loads(data)

    # Gera o dataframe
    df = pd.DataFrame(covid['Countries'])

    # Remove as colunas que não usaremos
    covid1 = df.drop(columns = ['CountryCode', 'Slug', 'Date', 'Premium'], axis = 1)
    
    # Realiza os cálculos
    covid1['ActiveCases'] = covid1['TotalConfirmed'] - covid1['TotalRecovered']
    covid1['ActiveCases'] = covid1['ActiveCases'] - covid1['TotalDeaths']

    # Dataframe com agrupamentos
    dfn = covid1.drop(['NewConfirmed', 'NewDeaths', 'NewRecovered'], axis = 1)
    dfn = dfn.groupby('Country')['TotalConfirmed','TotalDeaths','TotalRecovered','ActiveCases'].sum().sort_values(by = 'TotalConfirmed', ascending = False)
    dfn.style.background_gradient(cmap = 'Oranges')
    dfc = covid1.groupby('Country')['TotalConfirmed', 'TotalDeaths', 'TotalRecovered', 'ActiveCases'].max().sort_values(by = 'TotalConfirmed', ascending = False).reset_index()

    # Mapa 1
    m1 = folium.Map(tiles = 'Stamen Terrain', min_zoom = 1.5)
    url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'
    folium.Choropleth(geo_data = country_shapes,
        min_zoom = 2,
        name = 'Covid-19',
        data = covid1,
        columns = ['Country','TotalConfirmed'],
        key_on = 'feature.properties.name',
        fill_color = 'YlOrRd',
        nan_fill_color = 'white',
        legend_name = 'Total de Casos Confirmados',).add_to(m1)

    # Mapa 2
    m2 = folium.Map(tiles = 'Stamen Terrain', min_zoom = 1.5)
    url='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'
    folium.Choropleth(geo_data = country_shapes,
        min_zoom = 2,
        name = 'Covid-19',
        data = covid1,
        columns = ['Country','TotalRecovered'],
        key_on = 'feature.properties.name', 
        fill_color = 'PuBu',
        nan_fill_color = 'white',
        legend_name = 'Total de Casos Recuperados',).add_to(m2)

    # Mapa 3
    m3 = folium.Map(tiles = 'Stamen Terrain', min_zoom = 1.5)
    url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'
    folium.Choropleth(geo_data = country_shapes,
        min_zoom = 2,
        name = 'Covid-19',
        data = covid1,
        columns = ['Country','ActiveCases'],
        key_on = 'feature.properties.name',
        fill_color = 'YlGnBu',
        nan_fill_color = 'white',
        legend_name = 'Total de Casos Ativos',).add_to(m3)

    # Coordenadas dos países
    coordinates = pd.read_csv('dados/country-coordinates-world.csv')
    covid_final = pd.merge(covid1, coordinates, on = 'Country')

    # Mostra o dataframe agrupado na tela
    dfn
    
    # Obtém os totais consolidados
    confirmed_tot = int(dfc['TotalConfirmed'].sum())
    deaths_tot = int(dfc['TotalDeaths'].sum())
    recovered_tot = int(dfc['TotalRecovered'].sum())
    active_tot = int(dfc['ActiveCases'].sum())

    # Imprime os totais na área principal
    st.write('Total de Casos Confirmados no Mundo - ', confirmed_tot)
    st.write('Total de Mortes no Mundo - ', deaths_tot)
    st.write('Total de Pessoas Recuperadas no Mundo - ', recovered_tot)
    st.write('Total de Casos Ativos no Mundo - ', active_tot)

    # Menu lateral - Mapas
    st.sidebar.subheader('Análise Através de Mapa')

    # Caixa de seleção
    select = st.sidebar.selectbox('Escolha o Tipo de Mapa',['Casos Confirmados', 'Casos Recuperados', 'Casos Ativos', 'Mortes'], key = '1')

    # Condicional para mostrar o mapa 
    if not st.sidebar.checkbox("Ocultar Mapa", False):

        if select == "Casos Confirmados":
           folium_static(m1)

        elif select == "Casos Recuperados":
           folium_static(m2)

        elif select == "Casos Ativos":
           folium_static(m3)

        else:
           m4 = folium.Map(tiles = 'StamenToner', min_zoom = 1.5)
           deaths = covid_final['TotalDeaths'].astype(float)
           lat = covid_final['latitude'].astype(float)
           long = covid_final['longitude'].astype(float)
           m4.add_child(HeatMap(zip(lat, long, deaths), radius = 0))
           folium_static(m4)

    # Menu lateral - Gráfico de Barras
    st.sidebar.subheader('Análise com Gráfico de Barras')

    select = st.sidebar.selectbox('Escolha o Gráfico de Barras',
        ['Casos Confirmados','Casos Recuperados','Casos Ativos','Mortes'],
        key = '2')

    if not st.sidebar.checkbox("Ocultar Gráfico de Barras", False):

        if select == "Casos Confirmados":

           fig = px.bar(dfc.head(10), y = 'TotalConfirmed', x = 'Country', color = 'Country', height = 400)
           fig.update_layout(title = 'Comparação do Total de Casos Confirmados dos 10 Países Mais Afetados Neste Momento',
            xaxis_title = 'Country',
            yaxis_title = 'Total de Casos Confirmados',
            template = "ggplot2")
           st.plotly_chart(fig)

        elif select == "Casos Recuperados":

           fig = px.bar(dfc.head(10), y = 'TotalRecovered', x = 'Country', color = 'Country', height=400)
           fig.update_layout(title='Comparação do Total de Casos Recuperados dos 10 Países Mais Afetados Neste Momento',
            xaxis_title = 'Country',
            yaxis_title = 'Total de Casos Recuperados',
            template = "seaborn")
           st.plotly_chart(fig)

        elif select == "Casos Ativos":

           fig = px.bar(dfc.head(10), y = 'ActiveCases', x = 'Country', color = 'Country', height = 400)
           fig.update_layout(title = 'Comparação de Casos Ativos dos 10 Países Mais Afetados Neste Momento',
            xaxis_title = 'Country',
            yaxis_title = 'Total de Casos Ativos',
            template = "plotly")
           st.plotly_chart(fig)

        else:
            
          fig = px.bar(dfc.head(10), y = 'TotalDeaths', x = 'Country', color = 'Country', height = 400)
          fig.update_layout(title='Comparação do Total de Mortes dos 10 Países Mais Afetados Neste Momento',
            xaxis_title = 'Country',
            yaxis_title = 'Total de Mortes', 
            template = "plotly_dark")
          st.plotly_chart(fig)


    # Menu lateral - Gráfico 3D
    st.sidebar.subheader('Análise com Gráfico 3D')

    if not st.sidebar.checkbox("Ocultar Gráfico 3D", True):

        fig = px.scatter_3d(dfc.head(10), x = 'TotalConfirmed', y = 'TotalDeaths', z = 'TotalRecovered', color = 'Country')
        fig.update_layout(title = 'Gráfico 3D do Total de Casos, Total de Mortes e Total de Recuperados dos 20 Principais Países Afetados Neste Momento')
        st.plotly_chart(fig)

    if st.sidebar.checkbox("Mostrar Dados Brutos", False):
        st.subheader("Dados do Covid 19")
        st.write(covid1)

if __name__ == '__main__':
    main()

    st.markdown("Obrigado Por Usar Este Real-Time Dashboard!")
