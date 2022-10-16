import pandas as pd
import geopandas as gpd
import folium
import re
from ast import literal_eval

#Importamos la base de datos.
df = pd.read_csv('C:/Users/urbi1/Desktop/Datos y algoritmos/Proyecto/data/poligono_de_medellin.csv', sep=";")
df

#Cargamos el poligono de medellin.
cp_union = gpd.GeoDataFrame(
    df.loc[:, [c for c in df.columns if c != "geometry"]],
    geometry=gpd.GeoSeries.from_wkt(df["geometry"]),
    crs="epsg:3005",
)
#Creamos la base del mapa con folium
m = folium.Map(location=[6.230833, -75.590553], zoom_start=12.3, tiles='CartoDB positron')
#Ploteamos el poligono de medellin
for _, r in cp_union.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'orange'})
    folium.Popup(r['importance']).add_to(geo_j)
    geo_j.add_to(m)


df = pd.read_csv('C:/Users/urbi1/Desktop/Datos y algoritmos/Proyecto/data/maparcs.csv')
df

#Cargamos la geometria del camino mas corto
mapsarcs = gpd.GeoDataFrame(
    df.loc[:, [c for c in df.columns if c != "geometry"]],
    geometry=gpd.GeoSeries.from_wkt(df["geometry"]),
    crs="epsg:3005",
)

#Modificamos los puntos de origen para sacar longitud y latitud y poder plotear las lineas y los marcadores.
coord = mapsarcs['origin']
coord.replace('[^0-9,.-]', '', regex = True, inplace = True)
coord = coord.str.split(",", expand=True)
coord2 = coord[1]+','+coord[0]
coord1 = coord2.values.tolist()

coords = [literal_eval(s) for s in coord1]

#Lineas
for i in range(len(coord)):
    my_PolyLine=folium.PolyLine(locations=coords,weight=5)
    m.add_child(my_PolyLine)
#Marcadores
for each in coords:
    folium.Marker(each).add_to(m)

folium.PolyLine(coords, color="red", weight=2.5, opacity=1).add_to(m)

m.save('index.html')
