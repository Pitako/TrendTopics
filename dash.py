import streamlit as st
import pandas as pd
#import pydeck as pdk
import seaborn as sns
from matplotlib import pyplot as plt
import datetime as date
import numpy as np


DIAS = [
    'Segunda-feira',
    'Terça-feira',
    'Quarta-feira',
    'Quinta-Feira',
    'Sexta-feira',
    'Sábado',
    'Domingo'
]


pd.options.display.float_format = '{:,.2f}'.format

st.set_page_config(page_title="TrendTopics ", layout="wide")



st.title("Análise de TrendTopics do Twitter")  

df = pd.read_csv('trendsTratados.csv', decimal=',', sep=';')
 
#df['dma'] = pd.to_datetime(df['dma'])
df['dma'] = df.apply(lambda row: date.datetime.strptime(row.dma,'%Y-%m-%d'), axis=1)
df['dma'] = df.apply(lambda row: row.dma.date() , axis=1)

diaMes = df.groupby(by=['dma'], as_index=False).qtd.agg('sum')

#gráfico com todos os dias
f1, ax = plt.subplots(figsize=(15, 4))
sns.lineplot(x=diaMes.dma, y=diaMes.qtd, ci=None, ax=ax, markers='o' )

#dados agrupados por dia e hora
diaHora = df.groupby(by=['nDiaSemana','diaSemana','hora'], as_index=False).qtd.agg('mean')
diaHora = diaHora.sort_values(by=['nDiaSemana','hora'])
diahoratabela = diaHora[['nDiaSemana','hora','qtd']].pivot(index='hora', columns='nDiaSemana', values='qtd')

#dados agrupados por dia
diaQTD = diaHora.groupby(by=['nDiaSemana'], as_index=False).qtd.agg('mean')
diaQTD['diaSemana'] = diaQTD.apply(lambda row: DIAS[int(row.nDiaSemana)], axis=1)

#quantidade por hora
horaQTD = diaHora.groupby(by=['hora'], as_index=False).qtd.agg('mean')




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

    containerFiltrado = st.beta_expander("Dados filtrados", expanded=True)

    c1, c2, c3 = containerFiltrado.beta_columns([2,3,4])

    c1.markdown("### Dias selecionados")
    c1.write(diaMesFiltrado.style.format({'qtd': '{:,.2f}'}))
    
    c2.markdown("### Maiores hashtags")
    c2.write(maioresHashs.sort_values(by='qtd', ascending=False).style.format({'qtd': '{:,.2f}'}))

    c3.markdown("### TrendTopics")
    c3.write(ttFiltrado[['dma','hora','hashtag','qtd']].sort_values(by=['dma','hora']).style.format({'qtd': '{:,.2f}'}))


    containerFiltrado.markdown("### Soma das ocorrências das hashtags por dia")
    f, ax = plt.subplots(figsize=(15, 5))
    sns.lineplot(x=diaMesFiltrado.dma, y=diaMesFiltrado.qtd, ci=None, ax=ax, markers='o')

    containerFiltrado.pyplot(f)

    
    
#layout dados completos
completo = st.beta_expander("Histórico completo", expanded=True )

#tit1 = completo.beta_columns(2)
#tit1[0].write('Soma de observações das hashtags por dia')

completo.markdown('### Soma de ocorrência das hashtags por dia')


colComp1, colComp2 = completo.beta_columns([1,4])
colComp1.write(' ') # pra alinhar gráfico com tabela
colComp1.write(diaMes.style.format({'qtd': '{:,.2f}'}))
colComp2.pyplot(f1)

#gráfico de quantidade média por dia
completo.markdown('### Média de ocorrência por dia da semana e por hora do dia')

colComp21, colComp22 = completo.beta_columns([1,1])
fig1, ax = plt.subplots(figsize=(10, 5))
plt.bar(diaQTD.diaSemana,diaQTD.qtd)
colComp21.pyplot(fig1)

#gráfico de quantidade por hora
fig2, ax = plt.subplots(figsize=(10, 5))
plt.bar(horaQTD.hora,horaQTD.qtd)
colComp22.pyplot(fig2)

#gráfico de linhas pra cada dia da semana por hora
completo.markdown('### Média das ocorrências por hora do dia em cada dia da semana')

fig3, ax = plt.subplots(figsize=(15, 7))
sns.lineplot(data=diaHora, x=diaHora.hora,  y=diaHora.qtd, hue=diaHora.diaSemana ,ci=None, legend="full")
completo.pyplot(fig3)


#gráfico heatmap
fig, ax = plt.subplots(figsize=(15, 10))
sns.heatmap(diahoratabela, cmap='YlGnBu', annot=True, fmt=".2f", vmin=diaHora.qtd.min(), vmax=diaHora.qtd.max(), linewidths=0.5, linecolor='white', cbar=False)
plt.xticks(np.arange(7) + .5, labels=DIAS)
ax.xaxis.tick_top()
completo.pyplot(fig)

