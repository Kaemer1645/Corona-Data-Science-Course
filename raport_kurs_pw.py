# -*- coding: utf-8 -*-
"""RAPORT_KURS_PW.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Qm5PixKCjC5lY0y1ivzgS-VINulhedC0

IMPORT LIBRARIES
"""

#instalacja brakujących bibliotek
!pip install geopandas

pip install mapclassify

# -*- coding: utf-8 -*-
#import bibliotek
import requests
import bs4
import re
import pprint
import os
import zipfile
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import mapclassify

#pobranie obiektu response ze strony covid19poland
URL="https://covid19poland.bss.design/"
requests.get(URL)

requests.get(URL, {}).text

"""Stworzenie obiektu beautifulSoup"""

#stworzenie obiektu bs4.BeautifulSoup
web_page = bs4.BeautifulSoup(requests.get(URL, {}).text, "lxml")

#wybranie daty aktualizacji bazy
#przeszukanie = web_page.find(name="span", attrs={"class": "text-nowrap grey date"})
#data=przeszukanie.get_text()
#data
przeszukanie = web_page.find('span', class_ = 'text-nowrap grey total').get_text()
data=przeszukanie
data

web_page

web_page.head

web_page.head.title

web_page.head.title.text

web_page.body

#dane jakie zawiera strona dla id w elemencie span
zmienna=web_page.find_all(lambda e: e.name == 'span' and e.attrs.get('id'))
zmienna

#pominiecie lini z tekstem "text-nowrap"
zmienna0=web_page.find_all(name="span", attrs={"class": "text-nowrap"})
lista_red=[]
for x in zmienna0:
  x.decompose()

#odczytanie danych ze strony napisanej w HTML
lista=[]
tag=['None']
for y in zmienna:
  lista.append(y)
lista_red=[]
lista_green=[]
lista_purple=[]
lista2=[]
for x in lista:
  y=str(x)
  lista2.append(y)
for line in lista2:
  for img in re.findall('<span class="red".*', line):
    lista_red.append(img)
  for img in re.findall('<span class="green".*',line):
    lista_green.append(img)
  for img in re.findall('<span class="purple".*',line):
    lista_purple.append(img)

lista_red2=[]
lista_green2=[]
lista_purple2=[]
for x,y,z in zip(lista_red,lista_green,lista_purple):
  if x != None:
    lista_red2.append(x)
  if y != None:
    lista_green2.append(y)
  if z != None:  
    lista_purple2.append(z)

nazwy_woj=[]
zainfekowani=[]
wyzdrowienia=[]
zgony=[]
for line in lista_red2:
  for img in re.findall('"\w+_', line):
    a=img.replace("\"","").replace("_","")
    nazwy_woj.append(a)
  for img in re.findall('>\d+', line):
    a=img.replace(">","")
    zainfekowani.append(a)
for line in lista_green2:
  for img in re.findall('>\d+', line):
    a=img.replace(">","")
    wyzdrowienia.append(a)
for line in lista_purple2:
  for img in re.findall('>\d+', line):
    a=img.replace(">","")
    zgony.append(a)
print(nazwy_woj[0],zainfekowani[0],wyzdrowienia[0],zgony[0])

"""Pobranie ShapeFile wojewodztw"""

#pobranie pliku ze strony
!wget --no-check-certificate \
     https://www.gis-support.pl/downloads/Wojewodztwa.zip \
    -O /tmp/Wojewodztwa.zip


local_zip = '/tmp/Wojewodztwa.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/tmp')
zip_ref.close()

#lokalna sciezka do pliku zip z geometrią
baseDir='/tmp/Wojewodztwa.zip'
dirname=os.path.dirname(baseDir)

#odczytanie pliku Esri ShapeFile
try:
  wojewodztwa_shape = gpd.read_file(os.path.join(dirname,'Województwa.shp'))
except ValueError as err:
  print(err)

#układ współrzędnych pliku ShapeFile
wojewodztwa_shape.crs

#stworzenie kodu teryt, który posłużył do późniejszego połączenia z plikiem z geometrią
kod_teryt=[]
for x in range(2,34,2):
  kod_teryt.append('%02d' % (x,))

#stworzenie ramki danych w libie Pandasa
df = pd.DataFrame({
    'wojewodztwa': nazwy_woj,
    'zarazenia': zainfekowani,
    'wyzdrowienia':wyzdrowienia,
    'zgony':zgony ,
    'kod_teryt':kod_teryt,
})
df

#połączenie danych z plikiem zawierającym geometrie 
wojewodztwa = wojewodztwa_shape.merge(df, left_on='JPT_KOD_JE', right_on='kod_teryt', how='left')
wojewodztwa

"""Wizualizacja danych na mapie Polski"""

wojewodztwa['zarazenia'] = wojewodztwa['zarazenia'].astype(float)
wojewodztwa['coords'] = wojewodztwa['geometry'].apply(lambda x: x.representative_point().coords[:])
wojewodztwa['coords'] = [coords[0] for coords in wojewodztwa['coords']]
fig, ax = plt.subplots(figsize=(12,10))
'''wojewodztwa.assign(zarazenia=hr60_q10.yb).plot(column='zarazenia', categorical=True,cmap='OrRd', linewidth=0.1, ax=ax, \
                              edgecolor='white', legend=True)'''
wojewodztwa.plot(ax=ax, column='zarazenia', cmap='Reds', legend=True, scheme='quantiles', k=5)
for idx, row in wojewodztwa.iterrows():
    plt.annotate(s=row['wojewodztwa'], xy=row['coords'],
                 horizontalalignment='center')
ax.set_title('Przypadki zakażenia Koronawirusem w Polsce na dzień'+' '+str(data), fontdict={'fontsize': 20}, loc='left')
ax.get_legend().set_bbox_to_anchor((.2, .3))
ax.set_axis_off()

wojewodztwa['wyzdrowienia'] = wojewodztwa['wyzdrowienia'].astype(float)
wojewodztwa['coords'] = wojewodztwa['geometry'].apply(lambda x: x.representative_point().coords[:])
wojewodztwa['coords'] = [coords[0] for coords in wojewodztwa['coords']]
fig, ax = plt.subplots(figsize=(12,10))
wojewodztwa.plot(ax=ax, column='wyzdrowienia', cmap='Greens', legend=True, scheme='quantiles', k=5)
for idx, row in wojewodztwa.iterrows():
    plt.annotate(s=row['wojewodztwa'], xy=row['coords'],
                 horizontalalignment='center')
ax.set_title('Przypadki wyzdrowienia z Koronawirusa w Polsce na dzień'+' '+str(data), fontdict={'fontsize': 20}, loc='left')
ax.get_legend().set_bbox_to_anchor((.2, .3))
ax.set_axis_off()

wojewodztwa['zgony'] = wojewodztwa['zgony'].astype(float)
wojewodztwa['coords'] = wojewodztwa['geometry'].apply(lambda x: x.representative_point().coords[:])
wojewodztwa['coords'] = [coords[0] for coords in wojewodztwa['coords']]
fig, ax = plt.subplots(figsize=(12,10))
wojewodztwa.plot(ax=ax, column='zgony', cmap='Purples',categorical=True, legend=True)
for idx, row in wojewodztwa.iterrows():
    plt.annotate(s=row['wojewodztwa'], xy=row['coords'],
                 horizontalalignment='center')
ax.set_title('Przypadki zgonów z powodu Koronawirusa w Polsce na dzień'+' '+str(data), fontdict={'fontsize': 20}, loc='left')
ax.get_legend().set_bbox_to_anchor((.2, .3))
ax.set_axis_off()

"""Suma wszystkich przypadków w Polsce"""

przy_zaraz=df["zarazenia"].astype(int).sum()
przy_zaraz

przyp_wyzdro=df["wyzdrowienia"].astype(int).sum()
przyp_wyzdro

przyp_zgon=df["zgony"].astype(int).sum()
przyp_zgon

#konwersja kolumn ze string'a na numeryczne w celu pozniejszego ich posortowania
cols=['zarazenia','wyzdrowienia','zgony']
a=df[cols].apply(pd.to_numeric)
a['wojewodztwa']=nazwy_woj
a

"""Wizualizacja danych na wykresach"""

c=a[['wojewodztwa','zarazenia']].sort_values(by=['zarazenia'], ascending=True)
fig, ax = plt.subplots(figsize=(12,10))
plt.plot(c['wojewodztwa'],c['zarazenia'],color='red', marker='o',label="Zarazenia")
plt.grid(color='k', linestyle='-', linewidth=0.1)
plt.xticks( fontsize=16)
plt.yticks( fontsize=16)
ax.set_title('Przypadki zakażenia Koronawirusem w Polsce na dzień'+' '+str(data),fontsize=15)
plt.xlabel('Województwa',fontsize=16)
plt.ylabel('Ilość',fontsize=16)
plt.legend()
fig.autofmt_xdate()

c=a[['wojewodztwa','wyzdrowienia']].sort_values(by=['wyzdrowienia'], ascending=True)
fig, ax = plt.subplots(figsize=(12,10))
plt.plot(c['wojewodztwa'],c['wyzdrowienia'],color='green', marker='o',label='Wyzdrowienia')
plt.grid(color='k', linestyle='-', linewidth=0.1)
plt.xticks( fontsize=16)
plt.yticks( fontsize=16)
ax.set_title('Przypadki wyzdrowienia z Koronawirusa w Polsce na dzień'+' '+str(data),fontsize=15)
plt.xlabel('Województwa',fontsize=16)
plt.ylabel('Ilość',fontsize=16)
plt.legend()
fig.autofmt_xdate()

c=a[['wojewodztwa','zgony']].sort_values(by=['zgony'], ascending=True)
fig, ax = plt.subplots(figsize=(12,10))
plt.plot(c['wojewodztwa'],c['zgony'], color='black',marker='x',label='Zgony')
plt.grid(color='k', linestyle='-', linewidth=0.1)
plt.xticks( fontsize=16)
plt.yticks( fontsize=16)
ax.set_title('Przypadki zgonów z powodu Koronawirusa w Polsce na dzień'+' '+str(data),fontsize=15)
plt.xlabel('Województwa',fontsize=16)
plt.ylabel('Ilość',fontsize=16)
plt.legend()
fig.autofmt_xdate()