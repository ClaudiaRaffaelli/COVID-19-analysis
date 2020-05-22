import networkx as nx
import json
import math
import random
import time
from collections import deque


# TODO: controlla i docstring per tutti i metodi
class GraphManager:
	"""
	This is a class used to create, manage, draw and process some properties of graphs and, in particular, of its nodes
	like: shortest path and betweenness of each node
	"""
	graph = None

	def __init__(self):
		""" The constructor for GraphManager class. It initialize a networkx Graph object """
		# creating a graph
		self.graph = nx.Graph()

	def add_node_to_graph(self, city_name, position_x, position_y):
		"""
		Utility for add_edges method

		Paramenters
		-----------
		city_name (string):
			city's name which identify the node
		position_x (float):
			it's an attribute of the node which rappresent the longitude of the city
		position_y (float):
			it's an attribute of the node which rappresent the altitude of the city

		"""
		self.graph.add_node(city_name, x=position_x, y=position_y)

	def add_edges(self):
		"""
		Each node corresponds to a city and two cities a and b are connected by an edge if the following holds:
		if x,y is the position of a, then b is in position z,w with z in [x-d,x+d] and w in [y-d, y+d], with d=0.8.

		"""

		d = 0.8
		# comparing each node in the graph with the subsequent nodes. Not checking the nodes before the current node
		# because the graph is symmetrical
		# TODO è il modo più efficiente per realizzare la cosa? Costa comunque O(n^2)
		nodes = list(self.graph.nodes(data=True))
		for i in range(len(nodes) - 1):
			for j in range(i + 1, len(nodes)):
				# checking if the two nodes are close enough
				if (float(nodes[i][1]['x']) - d <= float(nodes[j][1]['x']) <= float(nodes[i][1]['x'] + d) and
						float(nodes[i][1]['y']) - d <= float(nodes[j][1]['y']) <= float(nodes[i][1]['y'] + d)):
					#  Euclidean distance
					distance_long = (float(nodes[i][1]['x']) - float(nodes[j][1]['x'])) ** 2
					distance_lat = (float(nodes[i][1]['y']) - float(nodes[j][1]['y'])) ** 2
					distance = math.sqrt(distance_long + distance_lat)

					self.graph.add_edge(nodes[i][0], nodes[j][0], label=float(self.truncate(distance, 6)))

	def plot_graph(self, graph_name):
		"""
		Utility function used to draw the graph and save it as a .png file

		Parameters
		----------
		graph_name (string):
			string used as the name of the .png file which will be stored in the imgs/
			subdirectory

		"""
		print("Nodes in the graph:")
		print(list(self.graph.nodes(data=True)))

		# plotting the graph
		A = nx.nx_agraph.to_agraph(self.graph)
		A.layout('dot', args='-Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
		A.draw('./imgs/' + graph_name + '.png')

	def truncate(self, f, n):
		"""Truncates/pads a float f to n decimal places without rounding"""
		s = '%.12f' % f
		i, p, d = s.partition('.')
		return '.'.join([i, (d + '0' * n)[:n]])

	def betweenness_centrality(self):
		"""
		Finds the betweenness value for each node in the graph

		Returns
		-------
		BC (dictionary):
			dictionary that has the names of the nodes as keys and each node contains its value of betweenness

		Notes
		-----
		We assume there is only one shortest path between two nodes

		"""
		# TODO Migliorare eventualmente i valori ottenuti con questa funzione rispetto a quelli calcolati
		#  con nx.betweenness_centrality()
		print("True values: ", nx.betweenness_centrality(self.graph, normalized=True, endpoints=False))
		nodes = list(self.graph.nodes(data=True))
		shortest_paths = []  # Store all the shortest path between each pair of nodes in the graph
		for i in range(len(nodes)):
			for j in range(i + 1, len(nodes)):
				try:  # there may not be a path between two nodes
					shortest_paths.append(self.bellman_ford_shortest_path(nodes[i][0], nodes[j][0]))
				except:
					pass

		# Store the Betweenness Centrality for each node. For now, we suppose there is only 1 shortest path
		# between 2 nodes
		BC = {}
		for target_node in range(len(nodes)):
			num = 0
			den = 0
			for path in shortest_paths:
				if path[0] != nodes[target_node][0] and path[-1] != nodes[target_node][0]:
					if nodes[target_node][0] in path:
						num += 1
					den += 1
			BC[nodes[target_node][0]] = num / den
		return BC

	def bellman_ford(self, source_vertex):
		"""Finds the shortest path from source vertex to all the others in the graph.

		Utility for bellman_ford_shortest_path method.

		Parameters
		----------
		source_vertex : node label
			Starting node for the path

		Returns
		-------
		distances, predecessors:
			pair of dictionaries. distances takes as key a node_name, and as value the distance,
			in terms of weight from source node to the current node_name. predecessors has as key a node_name, and as value
			the predecessor node in the shortest path from source node to the current node_name

		Raises
		------
		ValueError
			If the graph contains a negative-weight cycle

		Notes
		-----
		Distances are calculated as sums of weighted edges traversed.
		"""

		vertices = list(self.graph.nodes())

		# Initialization of the graph
		distances = dict.fromkeys(self.graph.nodes(), math.inf)
		predecessors = dict.fromkeys(self.graph.nodes(), None)

		# setting the distance from the source vertex and itself to 0
		distances[source_vertex] = 0

		# relax edges
		count = len(vertices) - 1
		while count > 0:
			something_has_changed = False
			for (u, v) in self.graph.edges():
				# because the Bellman Ford algorithm works with digraphs we have to consider both the symmetric edges
				# in the form (u, v) and (v, u)
				if distances[u] + float(self.graph[u][v]['label']) < distances[v]:
					distances[v] = distances[u] + float(self.graph[u][v]['label'])
					predecessors[v] = u
					something_has_changed = True
				if distances[v] + float(self.graph[v][u]['label']) < distances[u]:
					distances[u] = distances[v] + float(self.graph[v][u]['label'])
					predecessors[u] = v
					something_has_changed = True

			# early termination if running through each edge nothing has changed in the previous loop
			if something_has_changed is False:
				break
			count -= 1

		'''
		# checking for negative-weight cycles. In fact because we are working with an undirected graph, if an edge
		# has a negative weight associated with it, it will count as a negative-weight cycle.
		for (u, v) in self.graph.edges():
			# as before, considering both the symmetric edges in the form (u, v) and (v, u)
			if distances[u] + float(self.graph[u][v]['label']) < distances[v]:
				raise ValueError("Graph contains a negative-weight cycle")
			if distances[v] + float(self.graph[v][u]['label']) < distances[u]:
				raise ValueError("Graph contains a negative-weight cycle")
		'''
		return distances, predecessors

	def bellman_ford_SPFA(self, source_vertex):
		"""Finds the shortest path from source vertex to all the others in the graph implementing the optimized version
		of Bellman Ford algorithm: Shortest Path First Algorithm (SPFA).

		Utility for bellman_ford_shortest_path method.

		Parameters
		----------
		source_vertex : node label
			Starting node for the path

		Returns
		-------
		distances, predecessors:
			pair of dictionaries. distances takes as key a node_name, and as value the distance,
			in terms of weight from source node to the current node_name. predecessors has as key a node_name, and as value
			the predecessor node in the shortest path from source node to the current node_name

		Notes
		-----
		Distances are calculated as sums of weighted edges traversed.
		"""
		# Initialization of the graph
		distances = dict.fromkeys(self.graph.nodes(), math.inf)
		already_in_queue = dict.fromkeys(self.graph.nodes(), False)
		predecessors = dict.fromkeys(self.graph.nodes(), math.inf)

		# setting the distance from the source vertex and itself to 0
		distances[source_vertex] = 0
		q = deque()
		q.append(source_vertex)
		already_in_queue[source_vertex] = True

		while len(q) > 0:
			u = q.popleft()

			for (u, v) in self.graph.edges(u):
				if distances[u] + float(self.graph[u][v]['label']) < distances[v]:
					distances[v] = distances[u] + float(self.graph[u][v]['label'])
					if not already_in_queue[v]:
						q.append(v)
						already_in_queue[v] = True
					predecessors[v] = u

				if distances[v] + float(self.graph[v][u]['label']) < distances[u]:
					distances[u] = distances[v] + float(self.graph[v][u]['label'])
					if not already_in_queue[u]:
						q.append(u)
						already_in_queue[u] = True
					predecessors[u] = v

		return distances, predecessors

	def bellman_ford_shortest_path(self, source_vertex, target_vertex):
		"""Finds the shortest path from source to target in a weighted graph G in terms of a list of nodes.
		Uses bellman_ford method or the optimized version bellman_ford_SPFA.

		Parameters
		----------
		source_vertex : node label
			Starting node for the path
		target_vertex: node label
			Ending node for the path

		Returns
		-------
		shortest_path:
			list of nodes indicating the shortest path from source_vertex to target_vertex
		Raises
		------
		ValueError
			If there is no path between the starting node and target node
		"""

		# inverting source vertex to target. The shortest path between the two is the same, but the reverse of the
		# list of shortest_path is not required: it is built using append (complexity O(1)) in the right ordering
		tmp = source_vertex
		source_vertex = target_vertex
		target_vertex = tmp
		distances, predecessors = self.bellman_ford_SPFA(source_vertex)

		# using the predecessors of each node to build the shortest path
		shortest_path = []
		current_node = target_vertex
		shortest_path.append(target_vertex)
		while current_node != source_vertex:
			current_node = predecessors[current_node]
			# raising an exception if there is not path between the two nodes at argument
			if current_node is None:
				raise ValueError("There is no path between node " + target_vertex + " and node " + source_vertex)

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
		if province_data['sigla_provincia'] != '' and province_data[
			'sigla_provincia'] not in provinces_already_annotated:
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

	# Executing Bellman-Ford
	'''
	start_time = time.time()
	path = P.bellman_ford_shortest_path('Enna', 'Catanzaro')
	end_time = time.time()
	print("tempo mio: " + str(end_time - start_time))
	start_time = time.time()
	path_vero = nx.bellman_ford_path(P.graph, 'Enna', 'Catanzaro', weight="label")
	end_time = time.time()
	print("tempo networkx: " + str(end_time - start_time))
	print(path)
	print(path_vero)
	'''

	#print("..my values: ", P.betweenness_centrality())

if __name__ == '__main__':
	main()
