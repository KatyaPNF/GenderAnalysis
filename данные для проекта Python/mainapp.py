#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import re
from PIL import Image
import matplotlib.pyplot as plt

# Создадим заголовок страницы
st.title("Visualization of gender distribution by profession")
st.text("Total, Managers, Professionals, Technicians and associate professionals, Clerical support workers,"
        "Service and sales workers, Skilled agricultural, forestry and fishery workers, Craft and related  workers,"
        "Plant and machine operators and assemblers, Elementary occupations, Armed forces, Not stated")
# Создадим поля для ввода профессии, года и гендера
job = st.text_input("Enter profession:")
st.text("1990, 1995, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021")
year = st.text_input("Enter year:")
st.text("Male, Female, Both sexes")
sex = st.text_input("Enter sex:")

# Скапируем написанный выше код датафрейма df,  словаря table_dict и функции table_json
if st.button("Show Data"):
    df = pd.read_excel("professions.xlsx", index_col=3, skiprows=lambda x: x in [0, 1, *range(2019, 2210)])
    df.rename(columns={'Unnamed: 0': 'professions', 'Unnamed: 1': 'sex'}, inplace=True)
    df.drop(columns='Unnamed: 2', inplace=True)
    years = list(df.columns[3:])
    dict_year = {}
    for i in range(len(years)):
        dict_year[years[i]] = i
    table_dict = {}
    prof_non = df['professions'][2]

    for i in range(len(df['professions'])):
        if df['professions'][i] not in table_dict and not (prof_non is df['professions'][i]):
            prof = df['professions'][i]
            table_dict[df['professions'][i]] = {'Female': {}, 'Male': {}, 'Both sexes': {}}

        if not (prof_non is df['sex'][i]):
            sex = df['sex'][i]
        if sex == 'Both sexes':
            if df.index[i] not in table_dict[prof]['Both sexes']:
                table_dict[prof]['Both sexes'][df.index[i]] = {}
            table_dict[prof]['Both sexes'][df.index[i]] = list(df.iloc[i][3:])

        elif sex == 'Male':
            if df.index[i] not in table_dict[prof]['Male']:
                table_dict[prof]['Male'][df.index[i]] = {}
            table_dict[prof]['Male'][df.index[i]] = list(df.iloc[i][3:])

        elif sex == 'Female':
            if df.index[i] not in table_dict[prof]['Female']:
                table_dict[prof]['Female'][df.index[i]] = {}
            table_dict[prof]['Female'][df.index[i]] = list(df.iloc[i][3:])

    dict_year = {}
    for i in range(len(years)):
        dict_year[years[i]] = i

    adm = gpd.read_file("countries.geo.json")
    adm = adm.assign(sex=np.empty(len(adm)))

    array_country = adm['name'].to_numpy()

    for country1 in table_dict['Total']['Female'].keys():
        for country2 in array_country:
            if country1 != country2:
                res1 = re.search(country1, country2)
                try:
                    res1.span()
                    adm.loc[adm['name'] == country2, 'name'] = country1
                except:
                    pass
                res2 = re.search(country2, country1)
                try:
                    res2.span()
                    adm.loc[adm['name'] == country2, 'name'] = country1
                except:
                    pass

    dict_year = {}
    for i in range(len(years)):
        dict_year[years[i]] = i

    def table_json(job, year, sex):
        table = {}
        for country in table_dict[job][sex]:
            if country not in table:
                table[country] = 0
            table[country] = table_dict[job][sex][country][dict_year[year]]

        dict_df = {'name': [], 'geometry': [], 'sex': []}
        for country in table:
            index_coutry = adm[adm['name'] == country].index[0] if adm[adm['name'] == country].shape[0] != 0 else 0
            if index_coutry and table[country] != '..':
                dict_df['name'].append(country)
                dict_df['geometry'].append(adm.iloc[index_coutry]['geometry'])
                dict_df['sex'].append(table[country])

        g = gpd.GeoDataFrame(dict_df)
        for i in range(len(adm)):
            if adm['name'][i] in dict_df['name']:
                ind = g[g['name'] == adm['name'][i]].index[0]
                adm['sex'][i] = dict_df['sex'][ind]
            else:
                adm['sex'][i] = None
        return adm
#Выведем визуальное распределение по странам для заданного гендера, профессии и года
    adm_new = table_json(job, year, sex)
    adm_new.plot(column='sex',
                       edgecolor="k",
                       missing_kwds={
                           "color": "lightgrey",
                           "edgecolor": "red",
                           "hatch": "///",
                           "label": "Missing values"},
                       figsize=(16, 6),
                       cmap='viridis',
                       legend=True)
    
    plt.xticks([])
    plt.yticks([])
    plt.axis('off')
    plt.savefig('picture.png', bbox_inches="tight")
    
    image = Image.open('picture.png') 
    st.write(f"Распределение на карте {sex}, занимающихся {job} за {year} год")
    st.image(image)

