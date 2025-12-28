import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time

# --- Modülleri İçe Aktar ---
from generate.ReadData import ReadData
from generate.TopologyGenerator import TopologyGenerator
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from algorithm.AlgorithmUtils import AlgorithmUtils

# Global değişken
network_graph = None

def load_graph():
    global network_graph
    try:
        source_type = graph_source_var.get()
        if source_type == "Random":
            gen = TopologyGenerator()
            network_graph = gen.generate(num_nodes=250)
            msg = "Rastgele Topology Oluşturuldu."
        else:
            reader = ReadData()
            network_graph = reader.read()
            msg = "CSV Verileri Yüklendi."
            
        # Ekrana çiz
        draw_graph()
        log_message(f"{msg}\nNode Sayısı: {len(network_graph.nodes)}\nLink Sayısı: {len(network_graph.links)}")
        
    except Exception as e:
        messagebox.showerror("Hata", str(e))

def draw_graph(path=None):
    if network_graph is None: return
    
    plt.clf() # Eski çizimi temizle
    G = network_graph.nx_graph
    # Büyük graflarda tutarlılık için seed sabitliyoruz
    pos = nx.spring_layout(G, seed=42)
    
    # 1. Tüm düğümleri varsayılan renkte (açık mavi) çiz
    nx.draw(G, pos, node_size=20, node_color='lightblue', with_labels=False)
    
    if path:
        # Yol bulunduysa işlemleri yap:
        
        # 2. Yol üzerindeki KENARLARI (Linkleri) Kırmızı çizgi yap
        nx.draw_networkx_edges(G, pos, 
                               edgelist=list(zip(path, path[1:])), 
                               edge_color="red", width=2)
        
        # 3. Ara düğümleri (Başlangıç ve Bitiş HARİÇ) Kırmızı nokta yap
        if len(path) > 2:
            intermediate_nodes = path[1:-1]
            nx.draw_networkx_nodes(G, pos, nodelist=intermediate_nodes, 
                                   node_color="red", node_size=30)
            
        # 4. BAŞLANGIÇ NODU (path[0]) -> YEŞİL
        nx.draw_networkx_nodes(G, pos, nodelist=[path[0]], 
                               node_color="green", node_size=80) # Biraz daha büyük (80)
        
        # 5. HEDEF NODU (path[-1]) -> KIRMIZI
        nx.draw_networkx_nodes(G, pos, nodelist=[path[-1]], 
                               node_color="red", node_size=80)   # Biraz daha büyük (80)
        
    canvas.draw()

def log_message(msg):
    result_text.config(state="normal")
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, msg)
    result_text.config(state="disabled")

def calculate():
    if network_graph is None:
        messagebox.showwarning("Uyarı", "Önce Grafiği Yükleyin!")
        return
        
    try:
        S = int(entry_s.get())
        D = int(entry_d.get())
        w1 = float(entry_w1.get())
        w2 = float(entry_w2.get())
        w3 = float(entry_w3.get())
        algo_name = algo_var.get()
        
        # Algoritma Seçimi ve Çalıştırma
        start_time = time.time()
        path = None
        
        if algo_name == "GA":
            solver = GeneticAlgorithm(network_graph, w1, w2, w3)
            path = solver.solve(S, D)
        elif algo_name == "Dijkstra":
            # Dijkstra sınıfını çağır
            solver = DijkstraAlgorithm(network_graph, w1, w2, w3)
            path = solver.solve(S, D)
            
        duration = (time.time() - start_time) * 1000
        
        if not path:
            log_message("Yol Bulunamadı.")
            return

        # Sonuç Hesaplama
        d, r_cost, b_cost = AlgorithmUtils.calculate_metrics(network_graph, path)
        total_cost = w1*d + w2*r_cost + w3*b_cost
        
        # Helper sınıfında metod ismi get_max_bandwidth idi, burayı düzelttim
        max_bw = AlgorithmUtils.get_bandwidth(network_graph, path)
        real_rel = 1.0 - r_cost
        
        sb = f">>> SONUÇ ({algo_name}) <<<\n"
        sb += f"Kaynak: {S} -> Hedef: {D}\n"
        sb += f"Adım: {len(path)-1}\n"
        sb += f"Adımlar: {path}\n"
        sb += f"Süre: {duration:.2f} ms\n"
        sb += f"Gecikme: {d:.4f}\n"
        sb += f"Güvenilirlik: {real_rel:.6f}\n"
        sb += f"Maliyet: {total_cost:.4f}\n"
        sb += f"Bandwidth: {max_bw}{' (Belirtilmemiş)' if max_bw == 0 else ''}\n"
        
        log_message(sb)
        draw_graph(path)

    except Exception as e:
        log_message(f"Hata: {e}")
        print(e)

# --- GUI BAŞLANGIÇ ---
window = tk.Tk()
window.title("BSM307 - Mimari Yapı")
window.geometry("1200x750")

main_frame = tk.Frame(window)
main_frame.pack(fill="both", expand=True)

# Sol Panel
left = tk.Frame(main_frame, width=350, bg="#f0f0f0")
left.pack(side="left", fill="y", padx=10, pady=10)
left.pack_propagate(False)

# Sağ Panel
right = tk.Frame(main_frame, bg="white")
right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Kontroller
tk.Label(left, text="Kaynak:", bg="#f0f0f0", font=("Arial", 11, "bold")).pack(anchor="w")
graph_source_var = tk.StringVar(value="Random")
tk.Radiobutton(left, text="Random", variable=graph_source_var, value="Random", bg="#f0f0f0").pack(anchor="w")
tk.Radiobutton(left, text="CSV", variable=graph_source_var, value="CSV", bg="#f0f0f0").pack(anchor="w")
tk.Button(left, text="Yükle / Oluştur", command=load_graph, bg="green", fg="white").pack(fill="x", pady=5)

tk.Label(left, text="Kaynak Node ID (S):", bg="#f0f0f0").pack(anchor="w", pady=(10,0))
entry_s = tk.Entry(left)
entry_s.pack(fill="x", pady=(0, 5))

tk.Label(left, text="Hedef Node ID (D):", bg="#f0f0f0").pack(anchor="w")
entry_d = tk.Entry(left)
entry_d.pack(fill="x", pady=(0, 5))

tk.Label(left, text="Algoritma:", bg="#f0f0f0").pack(anchor="w", pady=(5,0))
algo_var = tk.StringVar()
# Dijkstra seçeneğini combobox'a ekledim
combo = ttk.Combobox(left, textvariable=algo_var, values=["GA","Dijkstra"])
combo.current(0)
combo.pack(fill="x")

tk.Label(left, text="Ağırlıklar (Delay, Rel, BW):", bg="#f0f0f0").pack(anchor="w", pady=(10,0))
entry_w1 = tk.Entry(left); entry_w1.insert(0,"0.5"); entry_w1.pack(fill="x")
entry_w2 = tk.Entry(left); entry_w2.insert(0,"0.3"); entry_w2.pack(fill="x")
entry_w3 = tk.Entry(left); entry_w3.insert(0,"0.2"); entry_w3.pack(fill="x")

tk.Button(left, text="HESAPLA", command=calculate, bg="blue", fg="white", font=("Arial", 12, "bold")).pack(fill="x", pady=20)

result_text = tk.Text(left, height=15, bg="#ddd", font=("Consolas", 10))
result_text.pack(fill="both", expand=True)

# Grafik
fig = plt.figure(figsize=(5,5))
canvas = FigureCanvasTkAgg(fig, master=right)
canvas.get_tk_widget().pack(fill="both", expand=True)

window.mainloop()