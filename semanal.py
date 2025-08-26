import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
import pulp
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -------------------------- Classe Grafo ---------------------------------
class GrafoResultados:
    def __init__(self, modelo, frame):
        self.modelo = modelo
        self.frame = frame

        # nomes e cores
        self.nomes_tarefas, self.nomes_agentes, self.cores_agentes = self.configurar_visualizacao()
        if pulp.LpStatus[self.modelo.modelo.status] == 'Optimal':
            self.exibir_grafo()
        else:
            print("Erro, nenhuma solução ótima encontrada")

    def configurar_visualizacao(self):
        if self.modelo.num_dias <= 7:
            dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        else:
            dias = [f"{i:02d}" for i in range(1, 32)]
        nomes_tarefas = dias[:self.modelo.num_dias]
        nomes_agentes = [f"Agente {i+1}" for i in range(self.modelo.num_agentes)]
        cores_agentes = ['red','blue','green','gray','purple','orange','brown','pink',
                         'cyan','magenta','yellow','black','aqua','lime','teal','navy',
                         'olive','gold','silver','indigo'][:self.modelo.num_agentes]
        return nomes_tarefas, nomes_agentes, cores_agentes

    def exibir_grafo(self):
        G = nx.DiGraph()
        largura_total = max(self.modelo.num_dias, self.modelo.num_agentes) * 6
        espacamento_dias = largura_total / (self.modelo.num_dias + 1)
        for i, tarefa in enumerate(self.nomes_tarefas):
            G.add_node(tarefa, pos=((i+1)*espacamento_dias, 2))
        espacamento_agentes = largura_total / (self.modelo.num_agentes + 1)
        for j, agente in enumerate(self.nomes_agentes):
            G.add_node(agente, pos=((j+1)*espacamento_agentes, 1))
            for i in range(self.modelo.num_dias):
                if self.modelo.x[i][j].value() == 1:
                    G.add_edge(self.nomes_tarefas[i], agente, color=self.cores_agentes[j])
        self.desenhar_grafo(G)

    def desenhar_grafo(self, G):
        if hasattr(self, "canvas") and self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.canvas.figure)

        pos = nx.get_node_attributes(G, 'pos')
        edges = G.edges()
        colors = [G[u][v]['color'] for u,v in edges]
        node_colors = ['lightgray' if node not in self.nomes_agentes else self.cores_agentes[self.nomes_agentes.index(node)] for node in G.nodes()]

        fig, ax = plt.subplots(figsize=(max(7,self.modelo.num_dias*0.4),6))
        nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color=colors, node_size=max(2000 - self.modelo.num_dias*40,200), ax=ax)
        ax.set_title("Resultados da Designação de Tarefas")
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Evento de duplo clique
        def on_double_click(event):
            x_click, y_click = event.xdata, event.ydata
            if x_click is None or y_click is None: return
            closest_node = min(pos, key=lambda n: (pos[n][0]-x_click)**2 + (pos[n][1]-y_click)**2)
            novo_nome = simpledialog.askstring("Editar Nó", f"Novo nome para '{closest_node}':")
            if novo_nome:
                if closest_node in self.nomes_tarefas:
                    self.nomes_tarefas[self.nomes_tarefas.index(closest_node)] = novo_nome
                elif closest_node in self.nomes_agentes:
                    self.nomes_agentes[self.nomes_agentes.index(closest_node)] = novo_nome
                self.exibir_grafo()

        self.canvas.mpl_connect("button_press_event", lambda e: e.dblclick and on_double_click(e))

# ----------------------- Interface ----------------------------------------
class InterfaceUsuario:
    def __init__(self, root):
        self.root = root
        self.root.title("Designação de Tarefas a Agentes")
        self.grafo_resultados = None
        self.custo_entries = []
        self.criar_interface()

    def criar_interface(self):
        labels = ["Número de tarefas:", "Número de pessoas:", "Mínimo de pessoas por tarefa:",
                  "Máximo de pessoas por tarefa:", "Mínimo de tarefas que cada pessoa faz:",
                  "Máximo de tarefas que cada pessoa faz:"]
        self.entries = []
        for i, text in enumerate(labels):
            ttk.Label(self.root, text=text).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.root)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.bind("<Leave>", self.atualizar_grafo)
            entry.bind("<Return>", self.atualizar_grafo)
            self.entries.append(entry)

        self.usar_custos_personalizados = tk.IntVar()
        ttk.Checkbutton(self.root, text="Usar custos personalizados", variable=self.usar_custos_personalizados, command=self.on_checkbox_change).grid(row=6,columnspan=2,padx=5,pady=5)
        self.frame_custos = ttk.Frame(self.root)
        self.frame_custos.grid(row=7,columnspan=2,padx=5,pady=5)
        self.frame_grafo = ttk.Frame(self.root)
        self.frame_grafo.grid(row=0,column=2,rowspan=10,padx=10,pady=5,sticky="nsew")
        self.atualizar_grafo()

    def on_checkbox_change(self):
        if self.usar_custos_personalizados.get()==1: self.gerar_entradas_custos()
        else:
            for w in self.frame_custos.winfo_children(): w.destroy()
            self.atualizar_grafo()

    def gerar_entradas_custos(self):
        for w in self.frame_custos.winfo_children(): w.destroy()
        try:
            num_dias = int(self.entries[0].get())
            num_agentes = int(self.entries[1].get())
        except ValueError: return
        self.custo_entries = []
        dias_da_semana = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
        dias_do_mes = [f"{i:02d}" for i in range(1,32)]
        for i in range(num_dias):
            row_entries = []
            dia = dias_da_semana[i] if num_dias<=7 else dias_do_mes[i]
            ttk.Label(self.frame_custos, text=dia).grid(row=i+1,column=0,padx=2,pady=2)
            for j in range(num_agentes):
                e = ttk.Entry(self.frame_custos,width=5)
                e.grid(row=i+1,column=j+1,padx=2,pady=2)
                e.insert(0,0)
                e.bind("<Return>", self.atualizar_grafo)
                e.bind("<Leave>", self.atualizar_grafo)
                row_entries.append(e)
            self.custo_entries.append(row_entries)
        for j in range(num_agentes):
            ttk.Label(self.frame_custos, text=f"Agente {j+1}").grid(row=0,column=j+1,padx=2,pady=2)
        self.atualizar_grafo()

    def obter_matriz_custos(self, num_dias, num_agentes):
        c = []
        for i in range(num_dias):
            linha=[]
            for j in range(num_agentes):
                try: linha.append(float(self.custo_entries[i][j].get()))
                except: linha.append(1)
            c.append(linha)
        return c

    def atualizar_grafo(self, event=None):
        try:
            num_dias, num_agentes = int(self.entries[0].get()), int(self.entries[1].get())
            min_pessoas_dia, max_pessoas_dia = int(self.entries[2].get()), int(self.entries[3].get())
            min_dias_trabalho, max_dias_trabalho = int(self.entries[4].get()), int(self.entries[5].get())
            c = self.obter_matriz_custos(num_dias,num_agentes) if self.usar_custos_personalizados.get()==1 else [[0]*num_agentes for _ in range(num_dias)]
            self.modelo = ModeloDesignacao(num_dias,num_agentes,min_pessoas_dia,max_pessoas_dia,min_dias_trabalho,max_dias_trabalho,c)
            self.exibir_grafo_resultados()
        except: pass

    def exibir_grafo_resultados(self):
        if self.grafo_resultados:
            for w in self.grafo_resultados.frame.winfo_children(): w.destroy()
        self.grafo_resultados = GrafoResultados(self.modelo,self.frame_grafo)

# --------------------------- Modelo ---------------------------------------
class ModeloDesignacao:
    def __init__(self, num_dias,num_agentes,min_pessoas_dia,max_pessoas_dia,min_dias_trabalho,max_dias_trabalho,custos):
        self.num_dias = num_dias
        self.num_agentes = num_agentes
        self.min_pessoas_dia = min_pessoas_dia
        self.max_pessoas_dia = max_pessoas_dia
        self.min_dias_trabalho = min_dias_trabalho
        self.max_dias_trabalho = max_dias_trabalho
        self.custos = custos
        self.x = [[pulp.LpVariable(f'x_{i}_{j}',cat='Binary') for j in range(num_agentes)] for i in range(num_dias)]
        self.modelo = self.criar_modelo()

    def criar_modelo(self):
        modelo = pulp.LpProblem("Designacao", pulp.LpMinimize)
        modelo += pulp.lpSum(self.custos[i][j]*self.x[i][j] for i in range(self.num_dias) for j in range(self.num_agentes))
        for i in range(self.num_dias):
            modelo += pulp.lpSum(self.x[i][j] for j in range(self.num_agentes))>=self.min_pessoas_dia
            modelo += pulp.lpSum(self.x[i][j] for j in range(self.num_agentes))<=self.max_pessoas_dia
        for j in range(self.num_agentes):
            modelo += pulp.lpSum(self.x[i][j] for i in range(self.num_dias))>=self.min_dias_trabalho
            modelo += pulp.lpSum(self.x[i][j] for i in range(self.num_dias))<=self.max_dias_trabalho
        modelo.solve()
        return modelo

# ---------------------------- Main ----------------------------------------
if __name__=="__main__":
    root = tk.Tk()
    app = InterfaceUsuario(root)
    root.mainloop()
