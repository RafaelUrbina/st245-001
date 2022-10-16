import pandas as pd

#Importamos la base de datos.
data = pd.read_csv('data/calles_de_medellin_con_acoso.csv', sep = ';')
data

#Exploremos si existen Nans en la base.

#Existen 23559 Nans en nombre
data['name'].isnull().sum()

#0 Nans
data['origin'].isnull().sum()

#0 Nans
data['destination'].isnull().sum()

#0 Nans
data['length'].isnull().sum()

#0 Nans
data['oneway'].isnull().sum()

#Existen 16091 Nans en harassmentRisk
data['harassmentRisk'].isnull().sum()

#0 Nans
data['geometry'].isnull().sum()


######################################################
#Reemplazo de Nans en harassmentRisk por el promedio.#
######################################################

data['harassmentRisk'].fillna(data['harassmentRisk'].mean(),inplace=True)

##############################################################################
#Valores unicos en origin y destination para determinar el numero de vertices#
##############################################################################

len(data['origin'].unique())
len(data['destination'].unique())


##########################################################################################################
#Creamos cada valor de nodo en enteros por simplicidad, luego se genera el cambio a cordenadas nuevamente#
##########################################################################################################


frames = [data['origin'],data['destination']]

mrg = pd.concat(frames)

cat = pd.Categorical(mrg, categories=mrg.unique())
nds, uniques = pd.factorize(cat)

orgn_nodes = nds[0:len(nds)//2]
dest_nodes = nds[len(nds)//2:]

data.insert(1,"Orgn_node",orgn_nodes,True)
data.insert(3,"Dest_node",dest_nodes,True)

data[data['Dest_node']==27670]

data.head(50)


#############################################################################
#Sacamos una base temporal solo con las variables relevantes para la  prueba#
#############################################################################

data_test = pd.concat([data['Orgn_node'],data['Dest_node'],data['length'],data['oneway'],data['harassmentRisk']],axis=1,join='inner')

data_test

data_test.to_csv('data/data_test.csv')
#############################################################################################
data_clean = data

data_clean

data_clean.to_csv('data/data_clean.csv')
