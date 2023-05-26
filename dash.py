from typing import Tuple
import streamlit as st
import pandas as pd
#import pydeck as pdk
import seaborn as sns
from matplotlib import pyplot as plt
import datetime as date
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

import os

sns.set_theme()

DIAS = [
    'Segunda-feira',
    'Terça-feira',
    'Quarta-feira',
    'Quinta-Feira',
    'Sexta-feira',
    'Sábado',
    'Domingo'
]

st.set_page_config(page_title="TrendTopics ", layout="wide")


norm=1000000
ndias = 10


pd.options.display.float_format = '{:,.2f}'.format





st.title("Análise de TrendTopics do Twitter")  
st.write("[Como se comporta o TrendTopics do Twitter ? (1) — Contextualização](https://robertosavio.medium.com/como-se-comporta-o-trendtopics-do-twitter-1-contextualiza%C3%A7%C3%A3o-9d7c6b8ca395)")
st.write("[Como se comporta o TrendTopics do Twitter ? (2) — Código, tratamento e visão geral dos dados](https://robertosavio.medium.com/como-se-comporta-o-trendtopics-do-twitter-2-c%C3%B3digo-tratamento-e-vis%C3%A3o-geral-dos-dados-47b128f4ddb2)")
st.write("[Como se comporta o TrendTopics do Twitter ? (3) — Criação do dashboard e exploração dos dados](https://robertosavio.medium.com/como-se-comporta-o-trendtopics-do-twitter-3-cria%C3%A7%C3%A3o-do-dashboard-e-explora%C3%A7%C3%A3o-dos-dados-edf34c389bc6)")



df = pd.DataFrame()

dir_list= os.listdir('.')
for i in range(len(dir_list)):
    filename = dir_list[i]
    if filename.endswith('.csv'):
        dfapp = pd.read_csv(filename, decimal=',', sep=';')
        df = df.concat(dfapp, ignore_index=True)
        

df.reset_index(drop=True, inplace=True)

#df['dma'] = pd.to_datetime(df['dma'])
df['dma'] = df.apply(lambda row: date.datetime.strptime(row.dma,'%Y-%m-%d'), axis=1)
df['dma'] = df.apply(lambda row: row.dma.date() , axis=1)

diaMes = df.groupby(by=['dma'], as_index=False).qtd.agg('sum')

#dados agrupados por dia e hora
diaHora = df.groupby(by=['nDiaSemana','diaSemana','hora'], as_index=False).qtd.agg('mean')
diaHora = diaHora.sort_values(by=['nDiaSemana','hora'])
diahoratabela = diaHora[['nDiaSemana','hora','qtd']].pivot(index='hora', columns='nDiaSemana', values='qtd')

#dados agrupados por dia
diaQTD = diaHora.groupby(by=['nDiaSemana'], as_index=False).qtd.agg('mean')
diaQTD['diaSemana'] = diaQTD.apply(lambda row: DIAS[int(row.nDiaSemana)], axis=1)

#quantidade por hora
horaQTD = diaHora.groupby(by=['hora'], as_index=False).qtd.agg('mean')


st.sidebar.markdown("#### Escolha uma data para filtrar os trendtopics")

datasSelecionadas = st.sidebar.date_input("Datas", min_value=diaMes.dma.min(), max_value=diaMes.dma.max(), value=[])

hora = st.sidebar.slider(value=(0,23), label="Hora", min_value=0, max_value=23)
qHora = ' (hora >= @hora[0]) & (hora <= @hora[1]) '

if datasSelecionadas != () :       
    if(len(datasSelecionadas) == 1):
        datasSelecionadas= datasSelecionadas + datasSelecionadas   

    
    ds = pd.to_datetime(datasSelecionadas)

    #filtro por dia     
    qData = ' (dma >= @ds[0]) & (dma <= @ds[1]) '

    #filtro por hastag       
    #----------------------
    #acrescenta item inicial na lista    
    qHash = '& (1 == 1) & ' 
    #default = {0:[' - ']} #nenhuma hashtag
    #default = pd.DataFrame(data=default)
    #hashtags dos dias filtrados
    #hashtags = pd.concat([df.query(qData + qHash + qHora)['hashtag'],default], ignore_index=True)
    hashtags = df.query(qData + qHash + qHora)['hashtag']
    hashSelecionada = st.sidebar.multiselect('Hashtags', hashtags.sort_values().unique() )    
    
    if (len(hashSelecionada) != 0):
        qHash = '& (hashtag == @hashSelecionada) & '
    else:
        qHash = '& (1 == 1) &' 
    #----------------------
    
    

    #dias selecionados
    #usando query pra ser dinâmico
    diaMesFiltrado = df.query(qData + qHash + qHora).groupby(by=['dma'], as_index=False).qtd.agg('sum') 

    ttFiltrado = df.query(qData + qHash + qHora)

    maioresHashs = ttFiltrado.groupby(by=['hashtag'], as_index=False).qtd.agg('sum')

    containerFiltrado = st.expander("Dados filtrados", expanded=True)

    c1, c2, c3 = containerFiltrado.columns([2,3,4])

    c1.markdown("### Tweets no dia")
    c1.write(diaMesFiltrado.sort_values(by='qtd', ascending=False).set_index('dma').style.format({'qtd': '{:,.2f}'}))
    
    c2.markdown("### Maiores hashtags no período")
    c2.write(maioresHashs.sort_values(by='qtd', ascending=False).set_index('hashtag').style.format({'qtd': '{:,.2f}'}))

    c3.markdown("### TrendTopics (100 maiores hastags em um hora)")
    c3.write(ttFiltrado[['dma','hora','hashtag','qtd']].sort_values(by='qtd', ascending=False).head(100).reset_index().style.format({'qtd': '{:,.2f}'}))    


    containerFiltrado.markdown("### Soma das ocorrências das hashtags por dia")
        
    figpx2 = go.Figure()
    figpx2.add_trace(go.Scatter(x=diaMesFiltrado['dma'], y=diaMesFiltrado['qtd'], name='Qtd', line=dict(color='#888888', width=2)))
    figpx2.add_trace(go.Scatter(x=diaMesFiltrado['dma'], y=diaMesFiltrado.qtd.rolling(ndias).mean(), name='Média Móvel',  line=dict(color='firebrick', width=5)))
    figpx2.update_layout(height=350, autosize=True, margin=dict(b=10, l=10, r=10, t=10) )

    containerFiltrado.plotly_chart(figpx2, use_container_width=True)


   
    
#layout dados completos
completo = st.expander("Histórico completo", expanded=True )

#tit1 = completo.columns(2)
#tit1[0].write('Soma de observações das hashtags por dia')

completo.markdown('### Soma de ocorrência das hashtags por dia')


colComp1, colComp2 = completo.columns([1,4])
colComp1.write(' ') # pra alinhar gráfico com tabela
colComp1.write(diaMes.sort_values(by='qtd', ascending=False).head(100).set_index('dma').style.format({'qtd': '{:,.2f}'}))

diaMes['mm'] = diaMes.rolling(ndias).mean()

figpx = go.Figure()
figpx.add_trace(go.Scatter(x=diaMes['dma'], y=diaMes['qtd'], name='Qtd', line=dict(color='#888888', width=2)))
figpx.add_trace(go.Scatter(x=diaMes['dma'], y=diaMes['mm'], name='Média Móvel',  line=dict(color='firebrick', width=5)))
figpx.update_layout(height=350, autosize=True, margin=dict(b=10, l=10, r=10, t=10) )

colComp2.plotly_chart(figpx, use_container_width=True)

#gráfico de quantidade média por dia
completo.markdown('### Média de ocorrência por dia da semana e por hora do dia')

colComp21, colComp22 = completo.columns([1,1])
fig1, ax = plt.subplots(figsize=(10, 5))
plt.bar(diaQTD.diaSemana,diaQTD.qtd)
colComp21.pyplot(fig1)

#gráfico de quantidade por hora
fig2, ax = plt.subplots(figsize=(10, 5))
plt.bar(horaQTD.hora,horaQTD.qtd)
colComp22.pyplot(fig2)

#gráfico de linhas pra cada dia da semana por hora
completo.markdown('### Média das ocorrências por hora do dia em cada dia da semana')

# fig3, ax = plt.subplots(figsize=(15, 7))
# sns.lineplot(data=diaHora, x=diaHora.hora,  y=diaHora.qtd, hue=diaHora.diaSemana ,ci=None, legend="full")
figdiaS = px.line(diaHora,x='hora', y='qtd', color='diaSemana')
figdiaS.update_layout( margin=dict(b=10, l=10, r=10, t=10) )

completo.plotly_chart(figdiaS, use_container_width=True)


#gráfico heatmap
fig, ax = plt.subplots(figsize=(15, 10))
sns.heatmap(diahoratabela, cmap='YlGnBu', annot=True, fmt=".2f", vmin=diaHora.qtd.min(), vmax=diaHora.qtd.max(), linewidths=0.5, linecolor='white', cbar=False)
plt.xticks(np.arange(7) + .5, labels=DIAS)
ax.xaxis.tick_top()
completo.pyplot(fig)

