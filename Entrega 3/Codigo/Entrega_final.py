#Version final del algoritmo Dijkstra, (Cambios: Se cambió el archivo CSV al original siguiendo las observaciones, Se crea un archivo de requirements.txt para instalar
# los requisitos del entorno, Nota: geopandas tiene un medio de instalación diferente, quizas es geopandas el que presenta problemas al importar las librerias, Tambien se quitaron
# la mayoria de comentarios explicando el codigo)
import math
import sys
import pandas as pd
import time



data = pd.read_csv('data/calles_de_medellin_con_acoso.csv', sep = ';')

data['harassmentRisk'].fillna(data['harassmentRisk'].mean(),inplace=True)

data50 = data.loc[:68749]

data_arcs = data50


#Extraccion de todos los nodos unicos para poder crear el grafo
tst = pd.concat([data_arcs['origin'],data_arcs['destination']],ignore_index=True)
vertices = len(tst.unique())

#Medida de distancia y riesgo.
def log_trans(x):
    return math.log(x,5)


y = data_arcs['length'].max()
def percent_trans(x,y = y):
    return x/y

def sig_trans(x):
    return 1/(1+pow(0.000165*x/(1-0.000165*x),-3))

def haras_1(x):
    return x+1

def normal(x):
    return x

data_arcs['peso'] = data_arcs['length'].apply(log_trans)

data_arcs['peso'] = data_arcs['peso']*data_arcs['harassmentRisk']
data_arcs['peso']
 

class Graph(object):
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)
        
    def construct_graph(self, nodes, init_graph):

        graph = {}
        for node in nodes:
            graph[node] = {}
        graph.update(init_graph)                  
        return graph
    
    def get_nodes(self):
        return self.nodes
    
    def get_outgoing_edges(self, node):
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections
    
    def value(self, node1, node2):
        return self.graph[node1][node2][0]

def dijkstra_algorithm(graph, start_node):
    unvisited_nodes = list(graph.get_nodes())
 
    shortest_path = {}
 
    previous_nodes = {}
 
    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0
    
    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node
                
        neighbors = graph.get_outgoing_edges(current_min_node)
        for neighbor in neighbors:
            tentative_value = shortest_path[current_min_node] + graph.value(current_min_node, neighbor)
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                previous_nodes[neighbor] = current_min_node
 
        unvisited_nodes.remove(current_min_node)
    
    return previous_nodes, shortest_path

def print_result(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node
    
    while node != start_node:
        path.append(node)
        node = previous_nodes[node]
 
    path.append(start_node)
    
    print("Mejor camino encontrado, costo: {} .".format(shortest_path[target_node]))
    print(" -> ".join(reversed(path)))


def map_arcs(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node
    
    while node != start_node:
        path.append(node)
        node = previous_nodes[node]
 
    path.append(start_node)
    
    df_maparcs = pd.DataFrame(data = [], columns = ["","name","origin","destination","length","oneway","harrasmentRisk","geometry","peso"])

    for i in range(0,len(path)-1):
        addi = data_arcs[(data_arcs["origin"] == path[i+1]) & (data_arcs["destination"] == path[i])]
        df_maparcs = pd.concat([df_maparcs,addi], ignore_index=True)

#Cambiar el nombre del archivo que guarda para los 3 algoritmos
    df_maparcs.to_csv('data/maparcs_combi.csv')
    return df_maparcs

def mostrarinfo(df):
    print("Valores para los tres costos del algoritmo")
    print(df['length'].sum())
    print(df['harassmentRisk'].sum())
    print(df['peso'].sum())
    print("\n")

nodes = tst.unique()
nodes = [str(x) for x in nodes]
 
init_graph = {}
for node in nodes:
    init_graph[node] = {}

for origin,destination,peso in zip(data_arcs["origin"], data_arcs["destination"],data_arcs['peso']):
    init_graph[str(origin)][str(destination)] = [peso]
graph = Graph(nodes, init_graph)


#Eafit-Nacional
#(-75.5801229, 6.1956618) - (-75.5796302, 6.2604275)

#caarrera 90 - palmas
#(-75.6098595, 6.2524028) - (-75.5678887, 6.2343491)


#Runtime
start = time.time()

previous_nodes, shortest_path = dijkstra_algorithm(graph=graph, start_node="(-75.6098595, 6.2524028)")

end = time.time()
print(end-start)

print_result(previous_nodes, shortest_path, start_node="(-75.6098595, 6.2524028)", target_node="(-75.5678887, 6.2343491)")

df_maparcs = map_arcs(previous_nodes, shortest_path, start_node="(-75.6098595, 6.2524028)", target_node="(-75.5678887, 6.2343491)")

mostrarinfo(df_maparcs)

