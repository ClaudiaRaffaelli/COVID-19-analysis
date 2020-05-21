import networkx as nx
import json
import math
import random


# TODO: inserire docstring per tutti i metodi
class GraphManager:
	graph = None

	def __init__(self):
		# creating a graph
		self.graph = nx.Graph()

	def add_node_to_graph(self, city_name, position_x, position_y):
		self.graph.add_node(city_name, x=position_x, y=position_y)

	def add_edges(self):
		d = 0.8
		# comparing each node in the graph with the subsequent nodes. Not checking the nodes before the current node
		# because the graph is symmetrical
		# TODO è il modo più efficiente per realizzare la cosa? Costa comunque O(n^2)
		nodes = list(self.graph.nodes(data=True))
		for i in range(len(nodes)-1):
			for j in range(i+1, len(nodes)):
				# checking if the two nodes are close enough
				if(float(nodes[i][1]['x'])-d <= float(nodes[j][1]['x']) <= float(nodes[i][1]['x']+d) and
							float(nodes[i][1]['y'])-d <= float(nodes[j][1]['y']) <= float(nodes[i][1]['y']+d)):

					#  Euclidean distance
					distance_long = (float(nodes[i][1]['x'])-float(nodes[j][1]['x'])) ** 2
					distance_lat = (float(nodes[i][1]['y'])-float(nodes[j][1]['y'])) ** 2
					distance = math.sqrt(distance_long + distance_lat)

					self.graph.add_edge(nodes[i][0], nodes[j][0], label=float(self.truncate(distance, 2)))

	def plot_graph(self, graph_name):
		print("Nodes in the graph:")
		print(list(self.graph.nodes(data=True)))

		# plotting the graph
		A = nx.nx_agraph.to_agraph(self.graph)
		A.layout('dot', args='-Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
		A.draw('./imgs/'+graph_name+'.png')

	def truncate(self, f, n):
		"""Truncates/pads a float f to n decimal places without rounding"""
		s = '%.12f' % f
		i, p, d = s.partition('.')
		return '.'.join([i, (d + '0' * n)[:n]])

	def betweenness_centrality(self):
		print("True values: ", nx.betweenness_centrality(self.graph))
		nodes = list(self.graph.nodes(data=True))
		shortest_paths = []
		for i in range(len(nodes)):
			for j in range(i + 1, len(nodes)):
				try:
					shortest_paths.append(nx.bellman_ford_path(self.graph, nodes[i][0], nodes[j][0], weight="label"))
				except:
					pass
		BC = {}
		for target_node in range(len(nodes)):
			num = 0
			den = 0
			for path in shortest_paths:
				if path[0] != nodes[target_node][0] and path[-1] != nodes[target_node][0]:
					if nodes[target_node][0] in path:
						num += 1
					den += 1
			BC[nodes[target_node][0]] = num/den
		return BC

	def bellman_ford(self, source_vertex):
		vertices = list(self.graph.nodes())

		# Initialization of the graph
		distances = dict.fromkeys(self.graph.nodes(), math.inf)
		predecessors = dict.fromkeys(self.graph.nodes(), None)

		# setting the distance from the source vertex and itself to 0
		distances[source_vertex] = 0

		# relax edges
		# TODO chiedo un parere, nell'algoritmo di wiki il while era un for ed andava da 1 a len(vertices)-1
		#  così però mi pare più corretto. A partire da un nodo infatti così dovresti poter raggiungere tutti gli
		#  altri nodi nel caso limite in cui tutti i nodi sono posti in una lunga catena, dico bene?
		#  Purtroppo a fare prove manuali si fa poco bene.
		count = len(vertices)-1
		while count > 0:
			something_has_changed = False
			for (u, v) in self.graph.edges():
				# TODO, parere anche qui. Gli archi nel grafo sono indiretti e se esiste (Chieti, L'aquila) non esiste
				#  (L'aquila, Chieti). Affinché tutto funzionasse ho dovuto considerare anche la coppia amica mancante
				#  nella lista degli archi. Non ho visto modo più carino per farlo, se ti viene in mente qualcosa dimmi
				#  pure
				if distances[u] + float(self.graph[u][v]['label']) < distances[v]:
					distances[v] = distances[u] + float(self.graph[u][v]['label'])
					predecessors[v] = u
					something_has_changed = True
				elif distances[v] + float(self.graph[v][u]['label']) < distances[u]:
					distances[u] = distances[v] + float(self.graph[v][u]['label'])
					predecessors[u] = v
					something_has_changed = True

			# early termination if running through each edge nothing has changed in the previous loop
			if something_has_changed is False:
				break
			count -= 1

		# checking for negative-weight cycles
		for (u, v) in self.graph.edges():
			# TODO nell'algoritmo di wiki c'era, anche se qui cicli con pesi negativi non dovrebbero essercene mai.
			#  inoltre come prima ho ri-scritto quel discorso per considerare anche la coppia di arco amica
			if distances[u] + float(self.graph[u][v]['label']) < distances[v]:
				raise ValueError("Graph contains a negative-weight cycle")
			elif distances[v] + float(self.graph[v][u]['label']) < distances[u]:
				raise ValueError("Graph contains a negative-weight cycle")

		return distances, predecessors

	def bellman_ford_shortest_path(self, source_vertex, target_vertex):
		"""Returns the shortest path from source to target in a weighted graph G in terms of a list of nodes """

		# inverting source vertex to target. The shortest path between the two is the same, but the reverse of the
		# list of shortest_path is not required: it is built using append (complexity O(1)) in the right ordering
		tmp = source_vertex
		source_vertex = target_vertex
		target_vertex = tmp
		distances, predecessors = self.bellman_ford(source_vertex)

		# using the predecessors of each node to build the shortest path
		shortest_path = []
		current_node = target_vertex
		shortest_path.append(target_vertex)
		while current_node != source_vertex:
			current_node = predecessors[current_node]
			# raising an exception if there is not path between the two nodes at argument
			if current_node is None:
				raise Exception("There is no path between node "+target_vertex+" and node "+source_vertex)

			shortest_path.append(current_node)
		return shortest_path


def main():
	# Parsing the JSON, the result is a Python dictionary
	with open("./dati-json/dpc-covid19-ita-province.json") as f:
		parsed_file = json.load(f)

	# Building the graph of provinces
	provinces_already_annotated = []
	P = GraphManager()
	for province_data in parsed_file:
		# extracting information from the JSON
		if province_data['sigla_provincia'] != '' and province_data['sigla_provincia'] not in provinces_already_annotated:
			provinces_already_annotated.append(province_data['sigla_provincia'])
			province = province_data['denominazione_provincia']
			position_x = province_data['long']
			position_y = province_data['lat']
			# adding each province to the graph
			P.add_node_to_graph(province, position_x, position_y)

	# Inserting the edges according to the distance between each node
	P.add_edges()
	P.plot_graph('province')

	# Building the graph of doubles
	R = GraphManager()
	# Generate 2000 pairs of double (x,y)
	for i in range(2000):
		x = random.randrange(30, 50)
		y = random.randrange(10, 20)
		R.add_node_to_graph(i, x, y)
	R.add_edges()

	print("..my values: ", P.betweenness_centrality())

	# Executing Bellman-Ford
	shortest_path = P.bellman_ford_shortest_path('Brindisi', 'Aosta')
	print(shortest_path)


if __name__ == '__main__':
	main()
