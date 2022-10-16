#Version final del algoritmo Dijkstra, no hay cambios por hacer.

import math
import sys
import pandas as pd

data = pd.read_csv('data/data_clean.csv')
#data.drop(columns=['name','geometry'],inplace=True)
data50 = data.loc[:68749]
#[0:68749]

#Condicion para agregar los arcos que son doble via.(Esta condicion ocasiona que el algoritmo pueda coger la regional en contra via, sin ella la ruta tiene mas sentido. se deja ya que en clase nos dijeron que oneway =  true era doble via.)
cond = data50[data50["oneway"] == True]
temp = cond["destination"]
temp1 = cond["origin"]
cond['origin'] = temp
cond['destination'] = temp1

data_arcs = pd.concat([data50,cond], ignore_index=True)

#Extraccion de todos los nodos unicos para poder crear el grafo
tst = pd.concat([data_arcs['origin'],data_arcs['destination']],ignore_index=True)
vertices = len(tst.unique())

#Totalidad de vertices, no se usa, se usa el de arriba  que tiene en cuenta la contidad de datos tomada en data50(En este momento data50 contiene todos los  datos.)
vertices_full = 27671

#Medida de distancia y riesgo. (Ademas de estas se puede tomar solo la distancia o solo el riesgo.)
def log_trans(x):
    return math.log(x,5)

y = data_arcs['length'].max()
def percent_trans(x,y = y):
    #data_arcs['peso']=data_arcs['length'].div(data_arcs['length'].max())
    return x/y

def sig_trans(x):
    return 1/(1+pow(0.000165*x/(1-0.000165*x),-3))

def normal(x):
    return x

#Aplicamos la transformacion de la distancia.
data_arcs['peso'] = data_arcs['length'].apply(percent_trans)

#Juntamos distancia transformada con el riesgo.
data_arcs['peso'] = data_arcs['peso']+data_arcs['harassmentRisk']
data_arcs['peso']
 
#####################################################################################

class Graph(object):
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)
        
    def construct_graph(self, nodes, init_graph):

        #Alternativa para construir el grafo si fuera no direccionado.
        graph = {}
        for node in nodes:
            graph[node] = {}
        graph.update(init_graph)                  
        return graph
    
    def get_nodes(self):
        #Nodos del grafo
        return self.nodes
    
    def get_outgoing_edges(self, node):
        #Nodos vecinos
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections
    
    def value(self, node1, node2):
        #Retorna el peso entre los arcos
        return self.graph[node1][node2][0]

def dijkstra_algorithm(graph, start_node):
    unvisited_nodes = list(graph.get_nodes())
 
    # Se guarda el costo de cada nodo a medida que se va visitando se actualiza hasta la meta   
    shortest_path = {}
 
    # Se guarda el camino mas corto hasta el nodo actual.
    previous_nodes = {}
 
    # Max value entrega un valor muy grande simulando el infinito para los nodos aun no visitados.
    # Se podria poner un valor muy grande y ya, ej: 9999999  
    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    # El nodo inicial siempre tiene un costo de cero  
    shortest_path[start_node] = 0
    
    # El algoritmo se ejecuta hasta visitar todos los nodos.
    while unvisited_nodes:
        # Encuentra el nodo con el menor score
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node
                
        # devuelve los vecinos  del nodo actual y actualiza sus distancias respectivas
        neighbors = graph.get_outgoing_edges(current_min_node)
        for neighbor in neighbors:
            tentative_value = shortest_path[current_min_node] + graph.value(current_min_node, neighbor)
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                # Mejor camino al nodo actual
                previous_nodes[neighbor] = current_min_node
 
        # Despues de visitar los vecinos marcamos el nodo como visitado
        unvisited_nodes.remove(current_min_node)
    
    return previous_nodes, shortest_path

#Funcion que immprime el resultado por consola mostrando la ruta, no es tan necesario debido a que ya se esta exportando el camino para plotearlo en geopandas
def print_result(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node
    
    while node != start_node:
        path.append(node)
        node = previous_nodes[node]
 
    # Nodo inicial
    path.append(start_node)
    
    print("Mejor camino encontrado, costo: {}.".format(shortest_path[target_node]))
    print(" -> ".join(reversed(path)))


#Funcion para almacenar el camino selecionado, el csv contiene los nodos que se van a graficar con geopandas.
def map_arcs(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node
    
    while node != start_node:
        path.append(node)
        node = previous_nodes[node]
 
    # Nodo inicial
    path.append(start_node)
    
    df_maparcs = pd.DataFrame(data = [], columns = ["origin","destination","length","oneway","harrasmentRisk"])

    #Loop que toma los nodos guardados en path y los organiza en el csv para exportarlo.
    for i in range(0,len(path)-1):
        addi = data_arcs[(data_arcs["origin"] == path[i+1]) & (data_arcs["destination"] == path[i])]
        df_maparcs = pd.concat([df_maparcs,addi], ignore_index=True)

    df_maparcs.to_csv('data/maparcs.csv')

#Lista de nodos creada a partir de los nodos unicos en origen y destino. estos se usan para crear los nodos posibles de la lista de adyacencia.
nodes = tst.unique()
nodes = [str(x) for x in nodes]
 
#Diccionario vacio para inicializar el grafo.
init_graph = {}
#Loop para crear el grafo inicial, este toma la lista de nodos y recorre sobre cada uno de ellos.
for node in nodes:
    init_graph[node] = {}

#Loop para asignar el origen, destino y peso de cada nodo del grafo, (crea la lista de adyacencia.)
for origin,destination,peso,oneway in zip(data_arcs["origin"], data_arcs["destination"],data_arcs['length'],data_arcs['oneway']):
    init_graph[str(origin)][str(destination)] = [peso,oneway]
graph = Graph(nodes, init_graph)

#Shortest path es un diccionario el camino mas corto a cualquier nodo desde el nodo inicial,
#Previous nodes es un diccionario con cada arco que lleva desde el destino hasta el inicio
previous_nodes, shortest_path = dijkstra_algorithm(graph=graph, start_node="(-75.5801229, 6.1956618)")

#Funcion que printea el resultado.
print_result(previous_nodes, shortest_path, start_node="(-75.5801229, 6.1956618)", target_node="(-75.5796302, 6.2604275)")
#Se crea el csv para graficar los caminos en otro codigo.
map_arcs(previous_nodes, shortest_path, start_node="(-75.5801229, 6.1956618)", target_node="(-75.5796302, 6.2604275)")


