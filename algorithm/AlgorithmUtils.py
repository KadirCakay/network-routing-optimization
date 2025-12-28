import networkx as nx
import math

class AlgorithmUtils:
    
    @staticmethod
    def fix_path(graph_obj, node_id_list):
        """Node ID listesini alır, araları Shortest Path ile doldurur."""
        G = graph_obj.nx_graph
        final_path = []
        for i in range(len(node_id_list) - 1):
            u, v = node_id_list[i], node_id_list[i + 1]
            try:
                # NetworkX altyapısını kullanıyoruz
                p = nx.shortest_path(G, u, v, weight="delay")
            except nx.NetworkXNoPath:
                return None
            
            if i == 0:
                final_path.extend(p)
            else:
                final_path.extend(p[1:])
        return final_path

    @staticmethod
    def calculate_metrics(graph_obj, path_ids):
        G = graph_obj.nx_graph
        total_delay = 0
        total_bandwidth = []
        #total_reliability = []
        #path_reliability = 1.0
        reliability_cost = 0.0

        for i in range(len(path_ids) - 1):
            u, v = path_ids[i], path_ids[i + 1]
            data = G.edges[u, v]
            
            total_delay += data["delay"]
            total_bandwidth.append(data["bandwidth"])
            #path_reliability *= data["reliability"]
            reliability_cost += -math.log(data["reliability"] + 1e-12)

            #total_reliability.append(data["reliability"])
        for node_id in path_ids:
         node = graph_obj.get_node(node_id)
         if node:
            total_delay += node.s_ms
            #path_reliability *= node.reliability
            reliability_cost += -math.log(node.reliability + 1e-12)
        

        delay_score = total_delay
        # reliability_cost = 1 - min(total_reliability) if total_reliability else 1 
        #underflow riski reliability_cost = -math.log(path_reliability + 1e-12)
        #reliability_cost = 1 - path_reliability
        bandwidth_cost = 1 / (min(total_bandwidth)+1) if total_bandwidth else 1

        return delay_score, reliability_cost, bandwidth_cost

    @staticmethod
    def get_bandwidth(graph_obj, path_ids):
      
        if not path_ids: return 0
        
        source_id = str(path_ids[0]).strip()
        target_id = str(path_ids[-1]).strip()
        
        required_bw = 0
        key = source_id + target_id
        if key in graph_obj.demands:
            required_bw = graph_obj.demands[key]
           
        path_bw=[]    
        for i in range(len(path_ids) - 1):
         bw = AlgorithmUtils.get_link_a_to_b(graph_obj,path_ids[i],path_ids[i + 1])
         path_bw.append(bw)
         
         
        return f"Required BW: {required_bw}\nPath Bandwidths: {path_bw}"

    
    def get_link_a_to_b(graph_obj,a_node,b_node): 
        for link in graph_obj.links: 
            if ( (link.source.id == a_node and link.target.id == b_node) or 
                (link.source.id == b_node and link.target.id == a_node) ): 
             return link.bandwidth