import tkinter as tk             #para fazer interface
import tkinter.ttk as ttk
from tkinter import messagebox
import pulp                      #para lidar com o problema 
import networkx as nx            #para gerar os grafos
import matplotlib.pyplot as plt  #para criar graficos/janelas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------------------------------------------------------------
# classe Grafo
class GrafoResultados:
    def __init__(self, modelo, frame):
        self.modelo = modelo
        self.frame = frame
        self.nomes_tarefas, self.cores_agentes = self.configurar_visualizacao()

        if pulp.LpStatus[self.modelo.modelo.status] == 'Optimal':
            self.exibir_grafo()
        else:
            # messagebox.showerror("Erro", "Nenhuma solução ótima encontrada")
            print("Erro, nenhuma solução ótima encontrada")

    def configurar_visualizacao(self):
        dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        nomes_tarefas = dias_semana[:self.modelo.num_dias]
        cores_agentes = ['red', 'blue', 'green', 'gray', 
                         'purple', 'orange', 'brown', 'pink', 
                         'cyan', 'magenta', 'yellow', 'black', 
                         'aqua', 'lime', 'teal', 'navy', 'olive', 
                         'gold', 'silver', 'indigo'][:self.modelo.num_agentes]
        return nomes_tarefas, cores_agentes

    def exibir_grafo(self):
        G = nx.DiGraph()
        for i in range(self.modelo.num_dias):
            G.add_node(self.nomes_tarefas[i], pos=(1, i * 6))

        for j in range(self.modelo.num_agentes):
            G.add_node(f"Agente {j + 1}", pos=(2, j * 10))

            for i in range(self.modelo.num_dias):
                if self.modelo.x[i][j].value() == 1:
                    G.add_edge(self.nomes_tarefas[i], f"Agente {j + 1}", color=self.cores_agentes[j])

        self.desenhar_grafo(G)

    def desenhar_grafo(self, G):
        pos = nx.get_node_attributes(G, 'pos')
        edges = G.edges()
        colors = [G[u][v]['color'] for u, v in edges]

        # Prepare the node colors
        node_colors = ['lightgray' if 'Agente' not in node else self.cores_agentes[int(node.split()[1]) - 1] for node in G.nodes()]

        # Cria a figura e o eixo para desenhar o grafo
        fig, ax = plt.subplots()
        nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color=colors, node_size=2000, ax=ax)
        ax.set_title("Resultados da Designação de Tarefas")

        # Renderiza no frame do Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ------------------------------------------------------------------------------------
# classe Interface

class InterfaceUsuario:
    def __init__(self, root):
        self.root = root
        self.root.title("Designação de Tarefas a Agentes")
        
        self.criar_interface()
        self.grafo_resultados = None  # Inicializa o grafo como None
        
    def criar_interface(self):
        ttk.Label(self.root, text="Número de dias:").grid(row=0, column=0, padx=5, pady=5)
        self.num_dias_entry = ttk.Entry(self.root)
        self.num_dias_entry.grid(row=0, column=1, padx=5, pady=5)
        self.num_dias_entry.bind("<KeyRelease>", self.atualizar_grafo)

        ttk.Label(self.root, text="Número de agentes:").grid(row=1, column=0, padx=5, pady=5)
        self.num_agentes_entry = ttk.Entry(self.root)
        self.num_agentes_entry.grid(row=1, column=1, padx=5, pady=5)
        self.num_agentes_entry.bind("<KeyRelease>", self.atualizar_grafo)

        ttk.Label(self.root, text="Mínimo de pessoas por dia:").grid(row=2, column=0, padx=5, pady=5)
        self.min_pessoas_dia_entry = ttk.Entry(self.root)
        self.min_pessoas_dia_entry.grid(row=2, column=1, padx=5, pady=5)
        self.min_pessoas_dia_entry.bind("<KeyRelease>", self.atualizar_grafo)

        ttk.Label(self.root, text="Máximo de pessoas por dia:").grid(row=3, column=0, padx=5, pady=5)
        self.max_pessoas_dia_entry = ttk.Entry(self.root)
        self.max_pessoas_dia_entry.grid(row=3, column=1, padx=5, pady=5)
        self.max_pessoas_dia_entry.bind("<KeyRelease>", self.atualizar_grafo)

        ttk.Label(self.root, text="Mínimo de dias que cada trabalhador faz:").grid(row=4, column=0, padx=5, pady=5)
        self.min_dias_trabalho_entry = ttk.Entry(self.root)
        self.min_dias_trabalho_entry.grid(row=4, column=1, padx=5, pady=5)
        self.min_dias_trabalho_entry.bind("<KeyRelease>", self.atualizar_grafo)

        ttk.Label(self.root, text="Máximo de dias que cada trabalhador faz:").grid(row=5, column=0, padx=5, pady=5)
        self.max_dias_trabalho_entry = ttk.Entry(self.root)
        self.max_dias_trabalho_entry.grid(row=5, column=1, padx=5, pady=5)
        self.max_dias_trabalho_entry.bind("<KeyRelease>", self.atualizar_grafo)

        self.usar_custos_personalizados = tk.IntVar()
        self.checkbox = ttk.Checkbutton(self.root, text="Usar custos personalizados", variable=self.usar_custos_personalizados, command=self.on_checkbox_change)
        self.checkbox.grid(row=6, columnspan=2, padx=5, pady=5)

        self.frame_custos = ttk.Frame(self.root)
        self.frame_custos.grid(row=7, columnspan=2, padx=5, pady=5)

        self.frame_grafo = ttk.Frame(self.root)  # Frame para o gráfico
        self.frame_grafo.grid(row=8, columnspan=2, padx=5, pady=5)

        self.atualizar_grafo()

    def on_checkbox_change(self):
        if self.usar_custos_personalizados.get() == 1:
            self.gerar_entradas_custos()
        else:
            for widget in self.frame_custos.winfo_children():
                widget.destroy()
            self.atualizar_grafo()

    def gerar_entradas_custos(self):
        for widget in self.frame_custos.winfo_children():
            widget.destroy()

        try:
            num_dias = int(self.num_dias_entry.get())
            num_agentes = int(self.num_agentes_entry.get())

            global custo_entries
            custo_entries = []

            # Dias da semana
            dias_da_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

            # Limitar o número de dias da semana se necessário
            num_dias = min(num_dias, len(dias_da_semana))

            # Criar entradas de custo
            for i in range(num_dias):
                row_entries = []
                # Label para o dia da semana
                ttk.Label(self.frame_custos, text=dias_da_semana[i]).grid(row=i + 1, column=0, padx=2, pady=2)
                for j in range(num_agentes):
                    entry = ttk.Entry(self.frame_custos, width=5)
                    entry.grid(row=i + 1, column=j + 1, padx=2, pady=2)  # Ajustar a coluna para as entradas
                    row_entries.append(entry)
                custo_entries.append(row_entries)

            # Adicionar números dos trabalhadores no topo das colunas
            for j in range(num_agentes):
                ttk.Label(self.frame_custos, text=f"Agente {j + 1}").grid(row=0, column=j + 1, padx=2, pady=2)

            self.atualizar_grafo()  # Atualiza o gráfico após gerar entradas

        except ValueError:
            print("Erro, por favor insira números válidos para dias e agentes")
            # messagebox.showerror("Erro", "Por favor, insira números válidos para dias e agentes")
            self.usar_custos_personalizados.set(0) # Desativa o uso de custos personalizados

    def atualizar_grafo(self, event=None):
        try:
            num_dias = int(self.num_dias_entry.get())
            num_agentes = int(self.num_agentes_entry.get())
            min_pessoas_dia = int(self.min_pessoas_dia_entry.get())
            max_pessoas_dia = int(self.max_pessoas_dia_entry.get())
            min_dias_trabalho = int(self.min_dias_trabalho_entry.get())
            max_dias_trabalho = int(self.max_dias_trabalho_entry.get())

            if self.usar_custos_personalizados.get() == 1:
                c = self.obter_matriz_custos(num_dias, num_agentes)
            else:
                c = [[1 for _ in range(num_agentes)] for _ in range(num_dias)]  # Usar matriz de custos padrão

            self.modelo = ModeloDesignacao(num_dias, num_agentes, min_pessoas_dia, max_pessoas_dia, min_dias_trabalho, max_dias_trabalho, c)
            self.exibir_grafo_resultados()

        except ValueError:
            pass  # Ignora erros de conversão se os campos não estiverem preenchidos corretamente

    def obter_matriz_custos(self, num_dias, num_agentes):
        c = []
        for i in range(num_dias):
            linha = []
            for j in range(num_agentes):
                try:
                    custo = float(custo_entries[i][j].get())
                    linha.append(custo)
                except (ValueError, IndexError):
                    linha.append(1)  # Valor padrão se houver erro
            c.append(linha)
        return c

    def exibir_grafo_resultados(self):
        if self.grafo_resultados is not None:
            for widget in self.grafo_resultados.frame.winfo_children():
                widget.destroy()  # Limpa o antigo gráfico

        self.grafo_resultados = GrafoResultados(self.modelo, self.frame_grafo)  # Atualiza o gráfico

# -----------------------------------------------------------------------------------------------------------
# classe que modela o problema
class ModeloDesignacao:
    def __init__(self, num_dias, num_agentes, min_pessoas_dia, max_pessoas_dia, min_dias_trabalho, max_dias_trabalho, custos):
        self.num_dias = num_dias
        self.num_agentes = num_agentes
        self.min_pessoas_dia = min_pessoas_dia
        self.max_pessoas_dia = max_pessoas_dia
        self.min_dias_trabalho = min_dias_trabalho
        self.max_dias_trabalho = max_dias_trabalho
        self.custos = custos

        self.x = [[pulp.LpVariable(f'x_{i}_{j}', cat='Binary') for j in range(num_agentes)] for i in range(num_dias)]
        self.modelo = self.criar_modelo()

    def criar_modelo(self):
        modelo = pulp.LpProblem("Designacao", pulp.LpMinimize)

        # Função objetivo
        modelo += pulp.lpSum(self.custos[i][j] * self.x[i][j] for i in range(self.num_dias) for j in range(self.num_agentes))

        # Restrições
        for i in range(self.num_dias):
            modelo += pulp.lpSum(self.x[i][j] for j in range(self.num_agentes)) >= self.min_pessoas_dia
            modelo += pulp.lpSum(self.x[i][j] for j in range(self.num_agentes)) <= self.max_pessoas_dia

        for j in range(self.num_agentes):
            modelo += pulp.lpSum(self.x[i][j] for i in range(self.num_dias)) >= self.min_dias_trabalho
            modelo += pulp.lpSum(self.x[i][j] for i in range(self.num_dias)) <= self.max_dias_trabalho

        modelo.solve()
        return modelo

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceUsuario(root)
    root.mainloop()
