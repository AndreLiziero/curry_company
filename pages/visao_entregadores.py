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

def ratings_per_traffic(df1, title = ''):
    """
    gera dataframe de avaliação média e desvio padrão dos entregadores por tipo de tráfego
    Input: DataFrame, String
    Output: DataFrame
    """
    st.markdown('##### '+title)
    df_avg_std_RpR = (df1.loc[df1['Road_traffic_density'] != 'NaN',['Road_traffic_density','Delivery_person_Ratings']]
                 .groupby('Road_traffic_density')
                 .agg({'Delivery_person_Ratings':['mean','std']}))
    df_avg_std_RpR.columns=['delivey_mean', 'delivery_std']
    df_avg_std_RpR = df_avg_std_RpR.reset_index()
    return df_avg_std_RpR

def ratings_per_weather(df1, title = ''):
    """
    gera dataframe de avaliação média e desvio padrão dos entregadores por tipo de condição climática
    Input: DataFrame, String
    Output: DataFrame
    """
    st.markdown('##### '+title)
    df_avg_std_RpW = (df1.loc[df1['Weatherconditions'] != 'conditions NaN',['Weatherconditions','Delivery_person_Ratings']]
                 .groupby('Weatherconditions')
                 .agg({'Delivery_person_Ratings':['mean','std']}))
    df_avg_std_RpW.columns=['delivey_mean', 'delivery_std']
    df_avg_std_RpW = df_avg_std_RpW.reset_index()    
    return df_avg_std_RpW

def top_deliveries(df1, list = 'top', title = ''):
    """
    gera dataframe dos top 10 entregadores mais rápidos ou mais lentos por cidade.
    Input: DataFrame, String 'top' or 'bottom', String
    Output: DataFrame
    """
    st.markdown('##### '+title)
    if list == 'top':
        asc = True
    elif list == 'bottom':
        asc = False
        
    df_aux = (df1.loc[df1['City'] != 'NaN',['Delivery_person_ID','City','Time_taken(min)']]
                .groupby(['City','Delivery_person_ID'])
                .mean()
                .sort_values(['City','Time_taken(min)'],ascending=asc)
                .reset_index())
    df_top = pd.DataFrame({})
    for city in df_aux['City'].unique():
      df_head = df_aux.loc[df_aux['City'] == city,:].head(10)
      df_top = pd.concat([df_top,df_head])
    df_top.reset_index(drop=True)
    return df_top 

#___________________Início do código para o Streamlit__________________________________

# Import
df = pd.read_csv('train.csv')

#Limpeza
df1 = clean_code(df)

#_______________________________________________________________________________________
#Visão entregadores:

st.set_page_config(layout='wide')
st.header('Marketplace - Visão Entragadores')


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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', ' ', ' '])

with tab1:
    with st.container():
        st.title('Overall Metric')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            maior_idade = df1.loc[(df1['Delivery_person_Age'] != 'NaN'),['Delivery_person_Age']].max()
            col1.metric('Entregador mais velho', maior_idade)
        with col2:
            menor_idade = df1.loc[(df1['Delivery_person_Age'] != 'NaN'),['Delivery_person_Age']].min()
            col2.metric('Entregador mais novo', menor_idade)            
        with col3:
            melhor_veiculo = df1.loc[(df1['Vehicle_condition'] != 'NaN'),['Vehicle_condition']].max()
            col3.metric('Melhor condição veículo', melhor_veiculo)
        with col4:
            pior_veiculo = df1.loc[(df1['Vehicle_condition'] != 'NaN'),['Vehicle_condition']].min()
            col4.metric('Melhor condição veículo', pior_veiculo)
                
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação por entregador')
            df1_avg_ratings_per_deliver = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                        .groupby('Delivery_person_ID')
                        .mean()
                        .sort_values('Delivery_person_Ratings',ascending=False)
                        .reset_index())
            st.dataframe(df1_avg_ratings_per_deliver, height = 490)
    
        with col2:
            with st.container():
                st.dataframe(ratings_per_traffic(df1, 'Avaliação média por trânsito'))

            with st.container():
                st.dataframe(ratings_per_weather(df1, 'Avaliação média por clima'))

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(top_deliveries(df1,'top','Entregadores mais rápidos'), hide_index=True)
        with col2:
            st.dataframe(top_deliveries(df1,'bottom','Entregadores mais lentos'), hide_index=True)


