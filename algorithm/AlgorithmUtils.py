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
                # Bağlantı yoksa veya kopuksa hata vermemesi için
                if not nx.has_path(G, u, v):
                    return None
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
        """
        PDF Madde 3: Metrik Hesaplamaları
        Geriye Dönüş: (Toplam Gecikme, Güvenilirlik Maliyeti, Kaynak Maliyeti)
        """
        G = graph_obj.nx_graph
        
        total_delay = 0
        reliability_cost = 0.0 # Logaritmik toplam (Minimizasyon için)
        bandwidth_cost = 0.0   # 1000/BW toplamı (Minimizasyon için)

        # 1. Kenarlar (Links) Üzerindeki Maliyetler
        for i in range(len(path_ids) - 1):
            u, v = path_ids[i], path_ids[i + 1]
            
            # Link verilerini al (Link nesnesi üzerinden de alınabilir ama graph hızlıdır)
            # Not: NetworkGraph oluştururken nx graph'a da attribute eklediğini varsayıyoruz.
            # Eğer eklemediysen graph_obj.links içinde arama yapmak gerekir.
            # Kodun önceki halinde G.edges[u,v] kullanıldığı için ona uyumlu devam ediyorum.
            if (u, v) in G.edges:
                data = G.edges[u, v]
                delay = data.get("delay", 0)
                bw = data.get("bandwidth", 100) # Varsayılan 100
                rel = data.get("reliability", 0.99)
            else:
                 # Yönlendirilmiş/Yönlendirilmemiş grafik hatası önlemi
                 continue

            # PDF 3.1: Link Delay
            total_delay += delay
            
            # PDF 3.2: -log(Link Reliability)
            reliability_cost += -math.log(rel + 1e-12)
            
            # PDF 3.3: (1 Gbps / Bandwidth_ij) -> 1000 / BW
            bandwidth_cost += (1000.0 / (bw + 1e-9))

        # 2. Düğümler (Nodes) Üzerindeki Maliyetler
        # PDF 3.1 Notu: Kaynak (S) ve Hedef (D) hariç ara düğümlerin işlem süreleri
        if len(path_ids) > 2:
            intermediate_nodes = path_ids[1:-1] # İlk ve son hariç
            for node_id in intermediate_nodes:
                node = graph_obj.get_node(node_id)
                if node:
                    total_delay += node.s_ms
                    reliability_cost += -math.log(node.reliability + 1e-12)
        
        # PDF 3.2 Notu: Kaynak ve Hedefin güvenilirliği formülde genellikle dahildir
        # ancak gecikmede hariçtir. PDF tam net değil ama güvenilirlik tüm sistemdir.
        # Güvenilirlik için uç düğümleri de ekliyoruz:
        start_node = graph_obj.get_node(path_ids[0])
        end_node = graph_obj.get_node(path_ids[-1])
        if start_node: reliability_cost += -math.log(start_node.reliability + 1e-12)
        if end_node: reliability_cost += -math.log(end_node.reliability + 1e-12)

        return total_delay, reliability_cost, bandwidth_cost

    @staticmethod
    def get_bandwidth(graph_obj, path_ids):
        if not path_ids: return "0"
        
        path_bw = []    
        for i in range(len(path_ids) - 1):
             bw = AlgorithmUtils.get_link_a_to_b(graph_obj, path_ids[i], path_ids[i + 1])
             path_bw.append(f"{bw:.1f}")
         
        return f"Path BWs: {path_bw}"

    @staticmethod
    def get_link_a_to_b(graph_obj, a_node, b_node): 
        # graph_obj.links listesi içinde arama yapar
        for link in graph_obj.links: 
            if ((link.source.id == a_node and link.target.id == b_node) or 
                (link.source.id == b_node and link.target.id == a_node)): 
                return link.bandwidth
        return 1.0 # Bulunamazsa hata vermemesi için