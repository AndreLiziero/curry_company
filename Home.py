# Para que a integração das páginas funcione, é necessário criar uma pasta com o nome 'pages' no mesmo diretório que este arquivo.

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
)

#image = Image.open(r"C:\Users\andreliziero\Documents\repos\ftc\logo.png")
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes

    ### Ask for Help
    - @andreliziero
    """)