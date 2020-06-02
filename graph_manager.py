import networkx as nx
import json
import math
import random
import time
from collections import deque


class GraphManager:
	"""
	This is a class used to create, manage, draw and process some properties of graphs and, in particular, of its nodes
	like: shortest path and betweenness of each node
	"""
	graph = None

	def __init__(self):
		""" The constructor for GraphManager class. It initializes a NetworkX Graph object """
		# creating a graph
		self.graph = nx.Graph()

	def add_node_to_graph(self, city_name, position_x, position_y):
		"""
		Utility for add_edges method

		Parameters
		-----------
		city_name: string
			city's name which identifies the node
		position_x: float
			it's an attribute of the node which represents the longitude of the city
		position_y: float
			it's an attribute of the node which represents the latitude of the city

		"""
		self.graph.add_node(city_name, x=position_x, y=position_y)

	def add_edges(self):
		"""
		Utility that adds edges to the graph. Two nodes a and b are connected by an edge if the following holds:
		if x,y is the position of a, then b is in position z,w with z in [x-d,x+d] and w in [y-d, y+d], with d=0.8.
		"""

		d = 0.8
		# Creating a dictionary with key the node name and value
		nodes = {key: value for (key, value) in self.graph.nodes(data=True)}
		
		# Sorting the dictionary by value 'x'
		nodes_sorted_by_x = [(k, nodes[k]) for k in sorted(nodes, key=lambda x: nodes[x]['x'], reverse=False)]
		i = 0
		j = 1
		# Iterating over the list of nodes ordered by x
		while i < len(nodes_sorted_by_x) - 1:
			# if the nodes indexed by i and j are close enough relatively to x and y, then we add an edge. For the x
			# coordinate there's no need to check if the node i is smaller then the node j, since it is obvious from the
			# ordering
			if float(nodes_sorted_by_x[j][1]['x']) <= float(nodes_sorted_by_x[i][1]['x']) + d:
				if float(nodes_sorted_by_x[i][1]['y']) - d <= float(nodes_sorted_by_x[j][1]['y']) <= float(nodes_sorted_by_x[i][1]['y']) + d:

					#  Euclidean distance
					distance_long = (float(nodes_sorted_by_x[i][1]['x']) - float(nodes_sorted_by_x[j][1]['x'])) ** 2
					distance_lat = (float(nodes_sorted_by_x[i][1]['y']) - float(nodes_sorted_by_x[j][1]['y'])) ** 2
					distance = math.sqrt(distance_long + distance_lat)

					self.graph.add_edge(nodes_sorted_by_x[i][0], nodes_sorted_by_x[j][0],
										label=float(self.truncate(distance, 6)))

				# if the nodes indexed by i and j were close only relatively to x, since the list is not ordered by
				# the y values we just increment j in order to compare the node i with the next one. Otherwise, after
				# the adding of the edge we still increment j to continue the comparison
				j += 1
				# if j goes out of range there are no more nodes to compare the node indexed by i to
				if j >= len(nodes_sorted_by_x):
					i += 1
					j = i + 1
			# if the node indexed by i and the node indexed by j are not close enough relatively to x, then there is no
			# point in checking the node i with the next one (j+1).
			else:
				i += 1
				j = i + 1

	def plot_graph(self, graph_name):
		"""
		Utility function used to draw the graph and save it as a .png file

		Parameters
		----------
		graph_name: string
			string used as the name of the .png file which will be stored in the imgs subdirectory

		"""
		# print("Nodes in the graph:")
		# print(list(self.graph.nodes(data=True)))

		# plotting the graph
		graph_to_be_plotted = nx.nx_agraph.to_agraph(self.graph)
		graph_to_be_plotted.layout('dot', args='-Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
		graph_to_be_plotted.draw('./imgs/' + graph_name + '.png')

	def truncate(self, f, n):
		"""
		Truncates/pads a float f to n decimal places without rounding

		Parameters
		----------
		f: float
			float to be truncated
		n: int
			decimal places required for truncating

		Returns
		-------
		_: float
			a truncated number
		"""
		s = '%.12f' % f
		i, p, d = s.partition('.')
		return '.'.join([i, (d + '0' * n)[:n]])

	def betweenness_centrality(self, SPFA=True):
		"""
		Finds the betweenness value for each node in the graph

		Returns
		-------
		BC: dictionary
			a dictionary that has the names of the nodes as keys and each node contains its value of betweenness
		SPFA : Boolean
			if True uses the optimized version bellman_ford_SPFA to find all the shortest path in the graph

		Notes
		-----
		We assume there is only one shortest path between two nodes

		"""
		nodes = list(self.graph.nodes(data=True))
		shortest_paths = []  # Store all the shortest path between each pair of nodes in the graph
		for i in range(len(nodes)):
			try:  # there may not be a path between two nodes
				paths_lists = self.bellman_ford_shortest_path(nodes[i][0], SPFA=SPFA)
				for p in paths_lists:
					shortest_paths.append(p)
			except:
				pass

		# Store the Betweenness Centrality for each node. For now, we suppose there is only 1 shortest path
		# between 2 nodes
		BC = {}
		for target_node in range(len(nodes)):
			sum_ous = 0
			for path in shortest_paths:
				if path[0] != nodes[target_node][0] and path[-1] != nodes[target_node][0] and nodes[target_node][
					0] in path:
					sum_ous += 1
			BC[nodes[target_node][0]] = (sum_ous) / ((len(nodes) - 1) * (len(nodes) - 2))
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
		distances, predecessors: dictionaries
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
		distances, predecessors: dictionaries
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

	def bellman_ford_shortest_path(self, source_vertex, SPFA=True):
		"""Finds all the shortest paths from source vertex to all the nodes in a weighted graph G in terms of a list of
		lists of nodes. Uses bellman_ford method or the optimized version bellman_ford_SPFA.

		Parameters
		----------
		source_vertex : node label
			Starting node for the path
		SPFA : Boolean
			if True uses the optimized version bellman_ford_SPFA

		Returns
		-------
		all__shortest_path: list of list
			list of list of nodes indicating the shortest path from source_vertex to all the other vertex in the graph
		Raises
		------
		ValueError
			If there is no path between the starting node and target node

		Notes
		-----
			Each shortest path returned is provided in the reverse order, that is, source_vertex is the last element
			of the list.
		"""

		if SPFA:
			distances, predecessors = self.bellman_ford_SPFA(source_vertex)
		else:
			distances, predecessors = self.bellman_ford(source_vertex)

		all__shortest_paths = []
		nodes = list(self.graph.nodes(data=True))
		for target_vertex in nodes:
			target_vertex = target_vertex[0]
			if predecessors[target_vertex] == math.inf:
				continue
			# using the predecessors of each node to build the shortest path
			shortest_path = []
			current_node = target_vertex
			shortest_path.append(target_vertex)
			while current_node != source_vertex:
				current_node = predecessors[current_node]
				# exit from the loop if there is not path between the two nodes considered
				if current_node is None:
					break

				shortest_path.append(current_node)
			if len(shortest_path) != 1:
				all__shortest_paths.append(shortest_path)
		return all__shortest_paths


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
	start_time = time.time()
	P.add_edges()
	end_time = time.time()
	print("Time required for adding edges to P: " + str(end_time - start_time))
	P.plot_graph('province')

	# Building the graph of doubles
	R = GraphManager()
	# Generate 2000 pairs of double (x,y)
	for i in range(2000):
		x = random.randrange(30, 50)
		y = random.randrange(10, 20)
		R.add_node_to_graph(str(i), x, y)

	start_time = time.time()
	R.add_edges()
	end_time = time.time()
	print("Time required for adding edges to R: " + str(end_time - start_time))

	# Executing Bellman-Ford

	start_time = time.time()
	path = P.bellman_ford_shortest_path('Firenze', SPFA=False)
	end_time = time.time()
	print("Time to execute Bellman-Ford without SPFA on P: " + str(end_time - start_time))
	print(path)

	start_time = time.time()
	path = P.bellman_ford_shortest_path('Firenze', SPFA=True)
	end_time = time.time()
	print("Time to execute Bellman-Ford with SPFA on P: " + str(end_time - start_time))
	print(path)

	# Betweenness
	start = time.time()
	print("Betweenness values for P: ", P.betweenness_centrality(SPFA=True))
	end = time.time()
	print("Time to execute Betweenness on P:", end - start)


if __name__ == '__main__':
	main()
