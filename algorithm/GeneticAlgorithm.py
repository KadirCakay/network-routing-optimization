import random
import networkx as nx
from algorithm.AlgorithmUtils import AlgorithmUtils

class GeneticAlgorithm:
    def __init__(self, graph_obj, w1, w2, w3):
        self.graph = graph_obj
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        
    def solve(self, S, D, pop_size=50, generations=100):
        G = self.graph.nx_graph
        try:
            reach_from_S = set(nx.single_source_shortest_path_length(G, S).keys())
            reach_to_D = set(nx.single_source_shortest_path_length(G, D).keys())
        except: return None

        allowed = list(reach_from_S.intersection(reach_to_D))
        allowed = [n for n in allowed if n not in (S, D)]
        if len(allowed) < 4: allowed = [n for n in G.nodes() if n not in (S, D)]
        if not allowed: return None

        def random_chromosome():
            size = random.randint(2, 6)
            return random.sample(allowed, min(size, len(allowed)))

        def safe_decode(chrom):
            for _ in range(20):
                raw = [S] + chrom + [D]
                fixed = AlgorithmUtils.fix_path(self.graph, raw)
                if fixed: return fixed
                chrom = random_chromosome()
            return None

        def fitness(path):
             d, r, b = AlgorithmUtils.calculate_metrics(self.graph, path)

             d_norm = d / 1000.0          # ms → normalize
             r_norm = r                   # -log zaten küçük
             b_norm = b                   # zaten küçük

             return self.w1*d_norm + self.w2*r_norm + self.w3*b_norm


        population = []
        cnt = 0
        while len(population) < pop_size and cnt < 200:
            c = random_chromosome()
            if safe_decode(c): population.append(c)
            cnt += 1
            
        if not population: return None

        for _ in range(generations):
            population = sorted(population, key=lambda c: fitness(safe_decode(c)))
            elites = population[:10]
            new_pop = elites.copy()
            while len(new_pop) < pop_size:
                p1, p2 = random.sample(elites, 2)
                cut = random.randint(1, min(len(p1), len(p2)) - 1) if min(len(p1), len(p2)) > 1 else 0
                child = p1[:cut] + p2[cut:]
                if random.random() < 0.4:
                    if len(child) > 2 and random.random() < 0.5:
                        child.pop(random.randint(0, len(child)-1))
                    else: child.append(random.choice(allowed))
                if safe_decode(child): new_pop.append(child)
            population = new_pop

        best = min(population, key=lambda c: fitness(safe_decode(c)))
        return safe_decode(best)