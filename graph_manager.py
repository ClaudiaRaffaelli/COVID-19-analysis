import networkx as nx
import json
import math
import random


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
					# TODO non sono sicuro se la distanza bisognava calcolarla facendo la distanza euclidea tra i punti
					#  (x,y) di ogni provincia

					#  Euclidean distance
					distance_long = (float(nodes[i][1]['x']-float(nodes[j][1]['x']))) ** 2
					distance_alt = (float(nodes[i][1]['y']-float(nodes[j][1]['y']))) ** 2
					distance = math.sqrt(distance_long + distance_alt)

					# TODO l'attributo 'weight=' è stato sostituito con 'label=' perchè così veniva visualizzato sul
					#  grafo (nell'immagine province.png'
					self.graph.add_edge(nodes[i][0], nodes[j][0], label=float(self.truncate(distance, 2)))

	def plot_graph(self, graph_name):
		# TODO, una prima veloce implementazione per visualizzare il grafo. E' molto confusionaria, eventualmente da
		#  rivedere
		print("Nodes in the tree:")
		print(list(self.graph.nodes(data=True)))

		# plotting the graph
		A = nx.nx_agraph.to_agraph(self.graph)
		A.layout('dot', args='-Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
		A.draw('./imgs/'+graph_name+'.png')

	def truncate(self, f, n):
		'''Truncates/pads a float f to n decimal places without rounding'''
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

if __name__ == '__main__':
	main()
