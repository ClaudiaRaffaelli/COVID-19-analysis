import networkx as nx
import json


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

					# TODO, è richieso di mettere un peso sugli archi, in particolare è scritto: "Modify P and R to
					#  weight their edges.". Non capisco se consiglia prima di fare senza peso, e nella versione
					#  definitiva aggiungerlo invece, oppure se il peso sugli archi è una cosa che dovresti essere in
					#  grado di disabilitare, o comunque avere una versione con peso e una senza. Per ora ho messo un
					#  peso/distanza a zero, da segnaposto

					# TODO calcola distanza da mettere in weight
					self.graph.add_edge(nodes[i][0], nodes[j][0], weight=0)

	def plot_graph(self, graph_name):
		# TODO, una prima veloce implementazione per visualizzare il grafo. E' molto confusionaria, eventualmente da
		#  rivedere
		print("Nodes in the tree:")
		print(list(self.graph.nodes(data=True)))

		# plotting the graph
		A = nx.nx_agraph.to_agraph(self.graph)
		A.layout('dot', args='-Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
		A.draw(graph_name+'.png')


def main():
	# Parsing the JSON, the result is a Python dictionary
	with open('../COVID-19/dati-json/dpc-covid19-ita-province.json') as f:
		parsed_file = json.load(f)

	# Building the graph of provinces
	P = GraphManager()
	for province_data in parsed_file:
		# TODO da gestire alcune province nel JSON che si chiamano "In fase di definizione/aggiornamento", la mia idea
		#  sarebbe quella di non considerarle
		# extracting information from the JSON
		province = province_data['denominazione_provincia']
		position_x = province_data['long']
		position_y = province_data['lat']
		# TODO nel JSON sono segnati per giornate diverse tutte le province italiane con relativo totale casi di COVID.
		#  Allora scorrendo nel file passiamo più volte da una stessa provincia anche se in giorni diversi. Sto
		#  sicuramente sprecando tempo con i duplicati. C'è modo di farlo più efficientemente?
		# adding each province to the graph
		P.add_node_to_graph(province, position_x, position_y)

	# Inserting the edges according to the distance between each node
	P.add_edges()
	P.plot_graph('province')

	# TODO:
	# Building the graph of doubles


if __name__ == '__main__':
	main()
