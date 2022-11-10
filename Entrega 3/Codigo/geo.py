import pandas as pd
import geopandas as gpd
import folium
from ast import literal_eval

df = pd.read_csv('data/poligono_de_medellin.csv', sep=";")
df

#Cargamos el poligono de medellin.
cp_union = gpd.GeoDataFrame(
    df.loc[:, [c for c in df.columns if c != "geometry"]],
    geometry=gpd.GeoSeries.from_wkt(df["geometry"]),
    crs="epsg:3005",
)

m = folium.Map(location=[6.230833, -75.590553], zoom_start=12.3, tiles='CartoDB positron')

#Ploteamos el poligono de medellin
for _, r in cp_union.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'orange'})
    folium.Popup(r['importance']).add_to(geo_j)
    geo_j.add_to(m)


df_length = pd.read_csv('data/maparcs_length.csv')
df_combi = pd.read_csv('data/maparcs_combi.csv')
df_harass = pd.read_csv('data/maparcs_harass.csv')

bases = [df_length,df_combi,df_harass]
colores = ["red","yellow","blue"]

for base,color in zip(bases,colores):

    mapsarcs = gpd.GeoDataFrame(
    base.loc[:, [c for c in base.columns if c != "geometry"]],
        geometry=gpd.GeoSeries.from_wkt(base["geometry"]),
        crs="epsg:3005",
    )

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
    for each in [coords[0],coords[-1]]:
        folium.Marker(each).add_to(m)

    #Red, blue, yellow
    folium.PolyLine(coords, color=color, weight=2.5, opacity=1).add_to(m)

m.save('index_v2.html')
