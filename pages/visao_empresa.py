#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime as dt, date, time

#Bibliotecas necessárias
import pandas as pd
import streamlit as st
import numpy as np
import folium
from streamlit_folium import folium_static
from PIL import Image

#========================================
#Funções
#========================================
def clean_code(df1):
    """funcao criada para realizar a limpeza dos dados do arquivo train.csv
       Limpezas realizadas:
       #1. removendo espaços no final dos dados.
       #2. convertendo a coluna Delivery_person_Age de str para int
       #3. convertendo a coluna Delivery_person_Ratings de str para float
       #4. convertendo a coluna Order_Date de str para datetime
       #5. convertendo a coluna multiple_deliveries de str para int
       #6. Definindo apenas números para a coluna Time_taken(min)
       #7. Criando a coluna 'distance' com base na latitude e longitude do restaurante e entrega
       #8. Criando a coluna 'week_of_year'
    
       Input: Dataframe
       Output: Dataframe
    """
    
    #1. removendo espaços no final dos dados.
    df1 = df1.reset_index(drop = True)
    df1.loc[:, 'Delivery_person_Age'] = df1.loc[:, 'Delivery_person_Age'].str.strip()
    df1.loc[:, 'multiple_deliveries'] = df1.loc[:, 'multiple_deliveries'].str.strip()
    df1.loc[:, 'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    
    #2. convertendo a coluna Age de str para int
    df1.loc[df1['Delivery_person_Age'] != 'NaN',['Delivery_person_Age']] = df1.loc[df1['Delivery_person_Age'] != 'NaN',['Delivery_person_Age']].astype( int )
    
    #3. convertendo a coluna Ratings de str para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    #4. convertendo a coluna order_date de str para datetime
    df1['Order_Date']=pd.to_datetime(df1['Order_Date'],format='%d-%m-%Y')
    
    #5. convertendo a coluna multiple_delivery de str para int
    df1.loc[df1['multiple_deliveries'] != 'NaN',['multiple_deliveries']] = df1.loc[df1['multiple_deliveries'] != 'NaN',['multiple_deliveries']].astype( int )
    
    #6. Definindo apenas números para a coluna Time_taken(min)
    df1 = df1.reset_index(drop = True)
    # for i in range(len(df1)):
    #   df1.loc[i, 'Time_taken(min)'] = re.findall(r'\d+', df1.loc[i, 'Time_taken(min)'])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] =df1['Time_taken(min)'].astype(int)
    
    #7. Criando a coluna 'distance'
    df1['Delivery_location_latitude'] = df1['Delivery_location_latitude'].abs()
    df1['Delivery_location_longitude'] = df1['Delivery_location_longitude'].abs()
    df1['Restaurant_latitude'] = df1['Restaurant_latitude'].abs()
    df1['Restaurant_longitude'] = df1['Restaurant_longitude'].abs()
    dist = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
    df1['distance'] = df1.loc[:, dist].apply(lambda x: haversine((x['Delivery_location_latitude'],x['Delivery_location_longitude']),(x['Restaurant_latitude'],x['Restaurant_longitude'])),axis=1)

    #8. Criando a coluna 'week_of_year'
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U').astype(int)

    return df1

def order_by_date(df1, fig_title = ''):
    """
    gera gráfico de barras dos pedidos por dia
    Input: DataFrame, String
    Output: gráfico de barras
    """
    st.markdown('##### '+fig_title)
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig 

def order_by_traffic(df1, fig_title = ''):
    """
    gera gráfico de pizza dos pedidos por tipo de tráfego
    Input: DataFrame, String
    Output: gráfico de pizza
    """
    st.markdown('##### '+fig_title)
    dfaux = df1.loc[df1['Road_traffic_density'] != 'NaN',['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    dfaux['entregas_perc'] = dfaux['ID'] / dfaux['ID'].sum()
    fig = px.pie(dfaux, values= 'ID', names='Road_traffic_density')
    return fig

def order_by_traffic_city(df1, fig_title = ''):
    """
    gera gráfico de bolhas dos pedidos por tipo de tráfego e cidade
    Input: DataFrame, String
    Output: gráfico de bolhas
    """
    st.markdown('##### '+fig_title)
    dfaux = (df1.loc[(df1['City'] != 'NaN')&(df1['Road_traffic_density'] != 'NaN'),['ID','City','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .count()
                .reset_index())
    fig = px.scatter(dfaux, x= 'City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week(df1, fig_title = ''):
    """
    gera gráfico de linha dos pedidos por semana
    Input: DataFrame, String
    Output: gráfico de linha
    """
    st.markdown('##### '+fig_title)
    df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')
    return fig

def order_by_week_deliver(df1, fig_title = ''):
    """
    gera gráfico de linha da média de entregas semanais por entregador
    Input: DataFrame, String
    Output: gráfico de linha
    """
    st.markdown('##### '+fig_title)
    df_pedidos = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_entregadores = df1.loc[:, ['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    dfaux = pd.merge(df_pedidos,df_entregadores,how='inner')
    dfaux['order_by_deliver'] = dfaux['ID'] / dfaux['Delivery_person_ID']
    fig = px.line(dfaux,x='week_of_year',y='order_by_deliver')
    return fig

def country_map(df1,fig_title = ''):
    """
    gera mapa da Localização central de cada cidade por tipo de tráfego
    Input: DataFrame, String
    Output: mapa
    """
    st.markdown('##### '+fig_title)
    df_aux = df1.loc[(df1['City'] != 'NaN')&(df1['Road_traffic_density'] != 'NaN'),['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                    popup=location_info[['City','Road_traffic_density']]).add_to(map)
    folium_static(map, width=512*1.5, height=300*1.5)    

#___________________Início do código para o Streamlit__________________________________

# Import
df = pd.read_csv('train.csv')

#Limpeza
df1 = clean_code(df)

#_______________________________________________________________________________________
#Visão empresa:

st.set_page_config(layout='wide')
st.header('Marketplace - Visão Empresa')


#========================================
#Sidebar no Streamlit
#========================================

#image = Image.open(r"C:\Users\andreliziero\Documents\repos\ftc\logo.png")
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

df_min = (df1.loc[df1['Order_Date'] != 'NaN', ['Order_Date']].sort_values('Order_Date', ascending= True).iloc[0,0])
df_max = (df1.loc[df1['Order_Date'] != 'NaN', ['Order_Date']].sort_values('Order_Date', ascending= False).iloc[0,0])
df_traffic = (df1.loc[df1['Road_traffic_density'] != 'NaN', 'Road_traffic_density'].unique())

date_slider = st.sidebar.slider(
    'Até qual dia?',
    min_value = (df_min),
    max_value = (df_max),
    value = (dt(int(dt.strftime(df_max,'%Y')),int(dt.strftime(df_max,'%m')),int(dt.strftime(df_max,'%d')))),
    format = 'DD/MM/YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Defina as condições de trânsito',
    df_traffic,
    default = df_traffic
)

st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Comunidade DS')

df1 = df1.loc[(df1['Order_Date'] <= date_slider) & (df1['Road_traffic_density'].isin(traffic_options)),:]


#========================================
#Layout no Streamlit
#========================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        fig = order_by_date(df1, fig_title='Totais de Entregas Diárias')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = order_by_traffic(df1,'Pedidos por tipo de tráfego')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = order_by_traffic_city(df1,'Pedidos por tipo de tráfego e Cidade')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header('Estatísticas Semanais')
    with st.container():
        fig = order_by_week(df1, 'Pedidos por semana')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        fig = order_by_week_deliver(df1, 'Pedidos semanais por entregador')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    country_map(df1)



