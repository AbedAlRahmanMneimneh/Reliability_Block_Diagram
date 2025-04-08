import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import combinations
import numpy as np
import math
import random
from datetime import datetime

class ReliabilityBlockDiagramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reliability Block Diagram Builder")
        self.root.geometry("1200x800")
        
        # Display current date/time and user
        current_datetime = "2025-04-06 08:12:40"  # UTC format
        current_user = "AbedAlRahmanMneimneh"
        
        header_frame = ttk.Frame(root, padding=10)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text=f"Current Date/Time (UTC): {current_datetime}").pack(side=tk.LEFT)
        ttk.Label(header_frame, text=f"User: {current_user}").pack(side=tk.RIGHT)
        
        # Initialize the graph
        self.G = nx.DiGraph()
        self.G.add_node('source')
        self.G.add_node('sink')
        
        # Component data
        self.components = {}  # name: failure_prob
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        left_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Component section
        component_frame = ttk.LabelFrame(left_frame, text="Components", padding=10)
        component_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(component_frame, text="Component Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.comp_name_var = tk.StringVar()
        ttk.Entry(component_frame, textvariable=self.comp_name_var).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(component_frame, text="Failure Probability:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.comp_prob_var = tk.StringVar(value="0.01")
        ttk.Entry(component_frame, textvariable=self.comp_prob_var).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Button(component_frame, text="Add Component", command=self.add_component).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Components list
        ttk.Label(component_frame, text="Existing Components:").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.comp_listbox = tk.Listbox(component_frame, height=6, width=30)
        self.comp_listbox.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=2)
        ttk.Button(component_frame, text="Remove Component", command=self.remove_component).grid(row=5, column=0, columnspan=2, pady=5)
        
        # Connection section
        connection_frame = ttk.LabelFrame(left_frame, text="Connections", padding=10)
        connection_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(connection_frame, text="From Node:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.from_node_var = tk.StringVar()
        self.from_node_combo = ttk.Combobox(connection_frame, textvariable=self.from_node_var)
        self.from_node_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(connection_frame, text="To Node:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.to_node_var = tk.StringVar()
        self.to_node_combo = ttk.Combobox(connection_frame, textvariable=self.to_node_var)
        self.to_node_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(connection_frame, text="Component:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.conn_comp_var = tk.StringVar()
        self.conn_comp_combo = ttk.Combobox(connection_frame, textvariable=self.conn_comp_var)
        self.conn_comp_combo.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Button(connection_frame, text="Add Connection", command=self.add_connection).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Nodes section
        node_frame = ttk.LabelFrame(left_frame, text="Nodes", padding=10)
        node_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(node_frame, text="Node Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.node_name_var = tk.StringVar()
        ttk.Entry(node_frame, textvariable=self.node_name_var).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Button(node_frame, text="Add Node", command=self.add_node).grid(row=1, column=0, columnspan=2, pady=5)
        
        # Calculation section
        calc_frame = ttk.LabelFrame(left_frame, text="Analysis", padding=10)
        calc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(calc_frame, text="Calculate Reliability", command=self.calculate_reliability).pack(fill=tk.X, pady=5)
        ttk.Button(calc_frame, text="Clear System", command=self.clear_system).pack(fill=tk.X, pady=5)
        
        # Right panel for graph and results
        right_frame = ttk.LabelFrame(main_frame, text="System Diagram & Results", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Graph canvas
        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, right_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        
        # Results text box
        self.results_text = tk.Text(right_frame, height=15, width=50)
        self.results_text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=5)
        self.results_text.insert(tk.END, "System results will appear here.\n")
        
        # Update node combos
        self.update_combos()
        
        # Display initial empty graph
        self.update_graph()
    
    def add_component(self):
        name = self.comp_name_var.get().strip()
        prob_str = self.comp_prob_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Component name cannot be empty")
            return
        
        if name in self.components:
            messagebox.showerror("Error", f"Component '{name}' already exists")
            return
        
        try:
            prob = float(prob_str)
            if not 0 <= prob <= 1:
                raise ValueError("Probability must be between 0 and 1")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid probability: {str(e)}")
            return
        
        # Add component to dictionary
        self.components[name] = prob
        
        # Update GUI
        self.comp_listbox.insert(tk.END, f"{name}: {prob:.4f}")
        self.comp_name_var.set("")
        self.comp_prob_var.set("0.01")
        self.update_combos()
        
        # Update results text instead of showing a pop-up
        self.results_text.insert(tk.END, f"Component '{name}' added with failure probability {prob:.4f}\n")
        self.results_text.see(tk.END)
    
    def remove_component(self):
        selected = self.comp_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No component selected")
            return
        
        # Get the selected component name
        comp_text = self.comp_listbox.get(selected[0])
        comp_name = comp_text.split(":")[0].strip()
        
        # Check if component is used in the graph
        component_in_use = False
        for _, _, data in self.G.edges(data=True):
            if data.get('component') == comp_name:
                component_in_use = True
                break
        
        if component_in_use:
            messagebox.showerror("Error", f"Cannot remove component '{comp_name}' because it is used in the system")
            return
        
        # Remove component
        del self.components[comp_name]
        self.comp_listbox.delete(selected[0])
        self.update_combos()
        
        messagebox.showinfo("Success", f"Component '{comp_name}' removed")
    
    def add_node(self):
        name = self.node_name_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Node name cannot be empty")
            return
        
        if name in self.G.nodes():
            messagebox.showerror("Error", f"Node '{name}' already exists")
            return
        
        # Add node to the graph
        self.G.add_node(name)
        
        # Update GUI
        self.node_name_var.set("")
        self.update_combos()
        self.update_graph()
        
        # Update results text instead of showing a pop-up
        self.results_text.insert(tk.END, f"Node '{name}' added to the system\n")
        self.results_text.see(tk.END)
    
    def add_connection(self):
        from_node = self.from_node_var.get()
        to_node = self.to_node_var.get()
        component = self.conn_comp_var.get()
        
        if not from_node or not to_node:
            messagebox.showerror("Error", "Must select both from and to nodes")
            return
        
        if not component:
            messagebox.showerror("Error", "Must select a component for the connection")
            return
        
        if from_node == to_node:
            messagebox.showerror("Error", "Cannot connect a node to itself")
            return
        
        # Check if this edge already exists
        if self.G.has_edge(from_node, to_node):
            messagebox.showerror("Error", f"Connection from '{from_node}' to '{to_node}' already exists")
            return
        
        # Add edge to the graph
        self.G.add_edge(from_node, to_node, 
                        component=component, 
                        name=component, 
                        failure_prob=self.components[component])
        
        self.update_graph()
        
        # Update results text instead of showing a pop-up
        self.results_text.insert(tk.END, f"Added connection from '{from_node}' to '{to_node}' with component '{component}'\n")
        self.results_text.see(tk.END)
    
    def update_combos(self):
        # Update node combos
        nodes = list(self.G.nodes())
        self.from_node_combo['values'] = nodes
        self.to_node_combo['values'] = nodes
        
        # Update component combo
        components = list(self.components.keys())
        self.conn_comp_combo['values'] = components
    
    def update_graph(self):
        self.ax.clear()
        
        # Check if graph is empty
        if len(self.G.nodes()) <= 2:  # Only source and sink
            self.ax.text(0.5, 0.5, "Add nodes and connections to build your system", 
                        ha='center', va='center', fontsize=12)
            self.ax.axis('off')
            self.canvas.draw()
            return
        
        # Set positions for nodes (using spring layout)
        pos = nx.spring_layout(self.G, seed=42)  # For consistent layouts
        
        # Draw nodes
        nx.draw_networkx_nodes(self.G, pos, node_size=1500, ax=self.ax)
        
        # Draw edges
        nx.draw_networkx_edges(self.G, pos, width=2, arrowsize=20, ax=self.ax)
        
        # Draw edge labels (component names)
        edge_labels = {(u, v): d['name'] for u, v, d in self.G.edges(data=True)}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=10, ax=self.ax)
        
        # Draw node labels
        nx.draw_networkx_labels(self.G, pos, font_size=10, font_weight='bold', ax=self.ax)
        
        self.ax.set_title("Reliability Block Diagram")
        self.ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()
    
    def calculate_reliability(self):
        # Check if graph has both source and sink and at least one path
        if 'source' not in self.G.nodes() or 'sink' not in self.G.nodes():
            messagebox.showerror("Error", "System must have both 'source' and 'sink' nodes")
            return
        
        try:
            # Check if there's at least one path from source to sink
            paths = list(nx.all_simple_paths(self.G, 'source', 'sink'))
            if not paths:
                messagebox.showerror("Error", "No path found from source to sink")
                return
            
            # Extract component paths
            component_paths = []
            for path in paths:
                comp_path = []
                for i in range(len(path) - 1):
                    edge_data = self.G.get_edge_data(path[i], path[i+1])
                    comp_path.append(edge_data['component'])
                component_paths.append(comp_path)
            
            # Find minimal cut sets
            min_cut_sets = self.find_minimal_cut_sets(component_paths)
            
            # Calculate reliability using cut sets
            unreliability = self.calc_system_unreliability_from_cut_sets(min_cut_sets)
            reliability = 1 - unreliability
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "===== RELIABILITY ANALYSIS RESULTS =====\n\n")
            
            self.results_text.insert(tk.END, "Success Paths:\n")
            for i, path in enumerate(component_paths, 1):
                path_str = f"  Path {i}: " + " → ".join(path) + "\n"
                self.results_text.insert(tk.END, path_str)
            
            self.results_text.insert(tk.END, "\nMinimal Cut Sets:\n")
            for i, cut_set in enumerate(min_cut_sets, 1):
                cut_set_str = f"  Cut Set {i}: {{{', '.join(cut_set)}}} (Order {len(cut_set)})\n"
                self.results_text.insert(tk.END, cut_set_str)
            
            # Generate and display reliability expression
            reliability_expression = self.generate_reliability_expression(min_cut_sets)
            self.results_text.insert(tk.END, f"\nReliability Expression:\n{reliability_expression}\n\n")
            
            self.results_text.insert(tk.END, f"System Reliability: {reliability:.12f}\n")
            self.results_text.insert(tk.END, f"System Unreliability: {unreliability:.12f}\n\n")
            
            self.results_text.insert(tk.END, "Contribution of each minimal cut set to system unreliability:\n")
            for i, cut_set in enumerate(min_cut_sets, 1):
                prob = 1
                for comp in cut_set:
                    prob *= self.components.get(comp, 0.1)
                
                percent = (prob / unreliability) * 100 if unreliability > 0 else 0
                cut_set_str = f"  Set {i} {{{', '.join(cut_set)}}}: {prob:.9f} ({percent:.2f}%)\n"
                self.results_text.insert(tk.END, cut_set_str)
            
            messagebox.showinfo("Success", f"Analysis complete. System reliability: {reliability:.12f}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    def generate_reliability_expression(self, min_cut_sets):
        """Generate a mathematical expression of system reliability based on minimal cut sets"""
        # System reliability R = 1 - Unreliability
        # Unreliability = P(C₁ ∪ C₂ ∪ ... ∪ Cₙ)
        # Where Cᵢ is the event that cut set i fails
        
        expression = "R = 1 - P(system failure)\n"
        expression += "  = 1 - P(at least one minimal cut set fails)\n"
        
        # First line shows the general form using cut sets
        cut_sets_union = " ∪ ".join([f"C{i}" for i in range(1, len(min_cut_sets) + 1)])
        expression += f"  = 1 - P({cut_sets_union})\n\n"
        
        # Define each cut set
        for i, cut_set in enumerate(min_cut_sets, 1):
            components_prod = " × ".join([f"q{comp}" for comp in cut_set])
            expression += f"Where C{i} = {components_prod}\n"
        
        expression += "\nWhere for each component i:\n"
        expression += "  qᵢ = component failure probability\n"
        expression += "  rᵢ = 1 - qᵢ = component reliability\n\n"
        
        # Using inclusion-exclusion principle
        expression += "Using the inclusion-exclusion principle:\n"
        expression += "R = 1 - [∑P(Cᵢ) - ∑P(Cᵢ∩Cⱼ) + ∑P(Cᵢ∩Cⱼ∩Cₖ) - ...]\n\n"
        
        # First-order terms
        expression += "First-order terms:\n"
        for i, cut_set in enumerate(min_cut_sets, 1):
            components_list = ", ".join(cut_set)
            components_prod = " × ".join([f"q{comp}" for comp in cut_set])
            expression += f"P(C{i}) = P({{{components_list}}}) = {components_prod}\n"
        
        return expression
    
    def find_minimal_cut_sets(self, paths):
        """Find minimal cut sets from the system paths"""
        # Get all unique components
        all_comps = set()
        for path in paths:
            all_comps.update(path)
        all_comps = list(all_comps)
        
        # Generate and check potential cut sets of all sizes
        cut_sets = []
        
        # Progress information in results text
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyzing system...\n\n")
        self.results_text.insert(tk.END, f"Found {len(paths)} success paths\n")
        self.results_text.insert(tk.END, f"Total components: {len(all_comps)}\n\n")
        self.results_text.insert(tk.END, "Finding minimal cut sets...\n")
        self.root.update()  # Update the GUI to show progress
        
        # Check all possible sizes of cut sets
        for set_size in range(1, len(all_comps) + 1):
            self.results_text.insert(tk.END, f"Checking potential cut sets of size {set_size}...\n")
            self.root.update()
            
            size_cut_sets = []
            for combo in combinations(all_comps, set_size):
                if self.is_cut_set(list(combo), paths):
                    size_cut_sets.append(list(combo))
            
            # Add to our list of potential cut sets
            cut_sets.extend(size_cut_sets)
            
            self.results_text.insert(tk.END, f"  Found {len(size_cut_sets)} cut sets of size {set_size}\n")
            self.root.update()
        
        # Remove non-minimal cut sets
        self.results_text.insert(tk.END, "\nRemoving non-minimal cut sets...\n")
        self.root.update()
        
        # First sort by size for efficiency
        cut_sets.sort(key=len)
        
        minimal_cut_sets = []
        for cs in cut_sets:
            # A cut set is minimal if no proper subset of it is also a cut set
            is_minimal = True
            for other_cs in minimal_cut_sets:  # Only check against already-identified minimal sets
                if self.is_subset(other_cs, cs):
                    is_minimal = False
                    break
            
            if is_minimal:
                minimal_cut_sets.append(cs)
        
        # Count by order (size)
        orders = {}
        for cs in minimal_cut_sets:
            order = len(cs)
            if order not in orders:
                orders[order] = 0
            orders[order] += 1
        
        self.results_text.insert(tk.END, f"\nIdentified {len(minimal_cut_sets)} minimal cut sets:\n")
        for order in sorted(orders.keys()):
            self.results_text.insert(tk.END, f"  Order {order}: {orders[order]} cut sets\n")
        
        return minimal_cut_sets
    
    def is_cut_set(self, comp_set, paths):
        """Check if a component set is a cut set"""
        for path in paths:
            # If this component set doesn't intersect with a path,
            # then it's not a cut set
            if not any(comp in path for comp in comp_set):
                return False
        return True
    
    def is_subset(self, set1, set2):
        """Check if set1 is a subset of set2"""
        return all(item in set2 for item in set1) and len(set1) < len(set2)
    
    def calc_system_unreliability_from_cut_sets(self, min_cut_sets):
        """Calculate system unreliability from minimal cut sets"""
        if not min_cut_sets:
            return 0
        
        self.results_text.insert(tk.END, "\nCalculating system unreliability from cut sets...\n")
        self.root.update()
        
        # For a system with minimal cut sets, the unreliability can be calculated as:
        # The probability of the union of events where each cut set fails
        
        # Calculate probability of each cut set
        cut_set_probs = []
        for i, cut_set in enumerate(min_cut_sets):
            cut_prob = 1.0
            for comp in cut_set:
                comp_fail_prob = self.components.get(comp, 0.1)
                cut_prob *= comp_fail_prob
            
            cut_set_probs.append(cut_prob)
            self.results_text.insert(tk.END, f"  Cut set {i+1} probability: {cut_prob:.9f}\n")
        
        # Apply the inclusion-exclusion principle more systematically
        n = len(min_cut_sets)
        unreliability = 0.0
        print(n)
        
        # Apply inclusion-exclusion principle
        for r in range(1, n + 1):  
            sign = (-1)**(r+1)  # Alternating sign: +, -, +, ...

            for combo in combinations(range(n), r):
                # Calculate probability of intersection of these cut sets failing
                # For cut set intersections, we need the union of component sets
                prob = 1.0
                
                # Special case for r=1 (individual cut sets)
                if r == 1:
                    prob = cut_set_probs[combo[0]]
                else:
                    # For the intersection of cut sets, we need the probability that
                    # all components in at least one of the cut sets fail
                    intersection_components = set()
                    for idx in combo:
                        intersection_components.update(min_cut_sets[idx])
                    
                    # Then compute the probability that all these components fail
                    prob = 1.0
                    for comp in intersection_components:
                        comp_fail_prob = self.components.get(comp, 0.1)
                        prob *= comp_fail_prob

                unreliability += sign * prob

        
        # Ensure results are reasonable
        if unreliability < 0:
            unreliability = 0
        elif unreliability > 1:
            unreliability = 1
            
        return unreliability
    
    def clear_system(self):
        """Clear the current system and start fresh"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the entire system?"):
            # Recreate the graph with only source and sink
            self.G = nx.DiGraph()
            self.G.add_node('source')
            self.G.add_node('sink')
            
            # Clear components
            self.components = {}
            self.comp_listbox.delete(0, tk.END)
            
            # Update GUI
            self.update_combos()
            self.update_graph()
            
            # Clear results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "System cleared. Results will appear here when you analyze a new system.\n")
            
            messagebox.showinfo("System Cleared", "System has been reset")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReliabilityBlockDiagramApp(root)
    root.mainloop()