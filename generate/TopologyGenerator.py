import networkx as nx
import random
from model.Node import Node
from model.Link import Link
from model.NetworkGraph import NetworkGraph

class TopologyGenerator:
    def generate(self, num_nodes=250, prob=0.4):
        graph = NetworkGraph()
        
        # NetworkX kullanarak rastgele topoloji iskeleti oluştur
        G_temp = nx.erdos_renyi_graph(num_nodes, prob)

        # Node'ları Model'e aktar
        for n_id in G_temp.nodes():
            rel = random.uniform(0.90, 0.999)
            s_ms = random.uniform(0.5, 2.0)
            node = Node(n_id, reliability=rel,s_ms=s_ms)
            # Rastgele koordinat (Görselleştirme için)
            node.x = random.uniform(10, 100)
            node.y = random.uniform(10, 100)
            graph.add_node(node)

        # Link'leri Model'e aktar
        for u, v in G_temp.edges():
            src = graph.get_node(u)
            dst = graph.get_node(v)
            
            delay = random.uniform(1, 10)
            bw = random.uniform(10, 100)
            rel = random.uniform(0.90, 0.999)

            link = Link(src, dst, delay, bw, rel)
            graph.add_link(link)
            
        return graph