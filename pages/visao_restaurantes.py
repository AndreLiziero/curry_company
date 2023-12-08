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

def avg_std_festival(df1, festival, calc):
    """
    gera a média ou desvio padrão das entregas durante ou fora do Festival.
    Input: DataFrame, String 'Yes' or 'No', String 'avg_time' or 'std_time'
    Output: Float
    """
    df_aux = (df1.loc[:,['Festival','Time_taken(min)','distance']]
                .groupby('Festival')
                .agg({'Time_taken(min)':['mean','std'],'distance':['mean','std']}))
    df_aux.columns = ['avg_time','std_time','avg_distance','std_distance']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, calc],3)
    return df_aux

def avg_time_delivery(df1,title = ''):
    """
    gera gráfico de barras com intervalo de desvio padrão do tempo médio de entregas por cidade.
    Input: DataFrame, String
    Output: gráfico barras
    """
    st.markdown('##### '+title)
    df_aux = (df1.loc[df1['City'] != 'NaN',['City','Time_taken(min)']]
                  .groupby('City')
                  .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name= 'Control',
                          x= df_aux['City'],
                          y= df_aux['avg_time'],
                          error_y= dict(type='data', 
                                        array=df_aux['std_time'])))
    fig.update_layout(barmode='group')    
    return fig

def avg_distance_delivery(df1, title = ''):
    """
    gera gráfico de pizza da distância média das entregas por cidade.
    Input: DataFrame, String
    Output: gráfico de pizza
    """
    st.markdown('##### '+title)
    df_aux = (df1.loc[df1['City'] != 'NaN',['City','Time_taken(min)','distance']]
                  .groupby('City')
                  .agg({'Time_taken(min)':['mean','std'],'distance':['mean','std']}))
    df_aux.columns = ['avg_time','std_time','avg_distance','std_distance']
    avg_distance = df_aux.loc[:,'avg_distance'].reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],
                                 values=avg_distance['avg_distance'],
                                 pull=[0.02,0.02,0.02])],
                    layout = {'width': 630})
    fig.update_layout(legend=dict(orientation='v',
                                  y=1,
                                  x=0.9),
                     margin = dict(t=10, l=10, r=100, b=10))    
    return fig

def avg_time_city_traffic(df1, title = ''):
    """
    gera gráfico de explosão solar do tempo médio das entregas por cidade e tipo de tráfego, colorido de acordo com valor do desvio padrão.
    Input: DataFrame, String
    Output: gráfico de explosão solar
    """
    st.markdown('##### '+title)
    df_aux = (df1.loc[(df1['City'] != 'NaN')&(df1['Road_traffic_density'] != 'NaN'),['City','Road_traffic_density','Time_taken(min)','distance']]
              .groupby(['City','Road_traffic_density'])
              .agg({'Time_taken(min)':['mean','std'],'distance':['mean','std']}))
    df_aux.columns = ['avg_time','std_time','avg_distance','std_distance']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux,
                      path=['City','Road_traffic_density'],
                      values='avg_time',
                      color='std_time',
                      color_continuous_scale='bluered',
                      color_continuous_midpoint=np.average(df_aux['std_time']))                
    fig.update_layout(legend = dict(orientation='v',
                                    y=0.99,
                                    x=0),
                      margin = dict(t=0, l=0, r=10, b=0)) 
    return fig

def df_avg_std_city_order(df1, title = ''):
    """
    gera tabela do tempo/distância médio e desvio padrão das entregas por cidade e tipo de pedido.
    Input: DataFrame, String
    Output: DataFrame.
    """
    st.markdown('##### '+title)
    df_aux = df1.loc[df1['City'] != 'NaN',['City','Type_of_order','Time_taken(min)','distance']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std'],'distance':['mean','std']})
    df_aux.columns = ['avg_time','std_time','avg_distance','std_distance']
    df_aux = df_aux.reset_index()
    return df_aux

#___________________Início do código para o Streamlit__________________________________

# Import
df = pd.read_csv('train.csv')

#Limpeza
df1 = clean_code(df)

#_______________________________________________________________________________________
#Visão restaurantes:

st.set_page_config(layout='wide')
st.header('Marketplace - Visão Restaurantes')

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
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1: 
            qnt_deliver = df1.loc[:,'Delivery_person_ID'].nunique()
            col1.metric('Quantidade de Entregadores', qnt_deliver)
        with col2:
            avg_dist = np.round(df1['distance'].mean(),3)
            col2.metric('Distância média de entregas', avg_dist)
        with col3:
            col3.metric('Tempo médio de entrega durante o Festival',avg_std_festival(df1,'Yes','avg_time'))
        with col4:
            col4.metric('Desvio padrão de entrega durante o Festival',avg_std_festival(df1,'Yes','std_time'))
        with col5:
            col5.metric('Tempo médio de entrega fora do Festival',avg_std_festival(df1,'No','avg_time'))        
        with col6:
            col6.metric('Desvio padrão de entrega fora do Festival',avg_std_festival(df1,'No','std_time'))
    
    with st.container():
        left,middle,right = st.columns([1,7,1])
        with middle:
            st.plotly_chart(avg_time_delivery(df1,'Tempo Médio por Cidade'), use_container_widht=True)
            
    with st.container():
        col1,col2 = st.columns(2, gap='large')        
        with col1:
            st.plotly_chart(avg_distance_delivery(df1,'Distância Média por Cidade'), use_container_widht=True)
        with col2:
            st.plotly_chart(avg_time_city_traffic(df1, 'Tempo Médio por Cidade e Tráfego'), use_container_widht=True)

    with st.container():
        left,middle,right = st.columns([1,1,1])
        with middle:
            st.dataframe(df_avg_std_city_order(df1))
        
