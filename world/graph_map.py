import networkx as nx
import matplotlib.pyplot as plt
import math

# =====================================================================
# 🗺️ TITAN_OPS AIR: DYNAMIC GRAPH PATHFINDING ENGINE
# =====================================================================

class SwarmTacticalMap:
    def __init__(self, grid_width=20, grid_height=20):
        self.width = grid_width
        self.height = grid_height
        # Create a 2D grid graph
        self.G = nx.grid_2d_graph(self.width, self.height)
        
        # Base Agent Mission
        self.ugv_start = (0, 0)      # Top-left of the sector
        self.ugv_target = (19, 19)   # Bottom-right extraction point
        self.blocked_nodes = []

    def translate_camera_to_grid(self, pixel_x, pixel_y, img_width=1000, img_height=1000):
        """
        Translates a 2D YOLO pixel bounding box center into a physical graph node.
        Example: Pixel (750, 500) on a 1000x1000 image becomes Grid Node (15, 10).
        """
        grid_x = min(int((pixel_x / img_width) * self.width), self.width - 1)
        grid_y = min(int((pixel_y / img_height) * self.height), self.height - 1)
        return (grid_x, grid_y)

    def inject_threat(self, grid_node, danger_radius=1):
        """
        Removes the target node and surrounding nodes to create a safe buffer zone.
        """
        cx, cy = grid_node
        print(f"[MAP] INJECTING THREAT AT NODE: {grid_node} | Radius: {danger_radius}")
        
        # Block the node and its immediate neighbors (Blast radius)
        for dx in range(-danger_radius, danger_radius + 1):
            for dy in range(-danger_radius, danger_radius + 1):
                node_to_block = (cx + dx, cy + dy)
                if node_to_block in self.G.nodes():
                    self.G.remove_node(node_to_block)
                    self.blocked_nodes.append(node_to_block)

    def calculate_evasion_route(self):
        """
        Executes the A* (A-Star) search algorithm to find the shortest collision-free path.
        """
        # A* Heuristic: Manhattan Distance
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        try:
            # Calculate the safest route
            path = nx.astar_path(self.G, self.ugv_start, self.ugv_target, heuristic=heuristic)
            print(f"[MAP] SECURE ROUTE CALCULATED. Nodes required: {len(path)}")
            return path
        except nx.NetworkXNoPath:
            print("[CRITICAL] TARGET SURROUNDED. NO SAFE EVASION ROUTE EXISTS.")
            return None

    def visualize_tactical_map(self, path, filename="tactical_map.png"):
        """
        Renders a visual image of the graph, threats, and calculated path.
        """
        plt.figure(figsize=(8, 8))
        pos = {(x, y): (y, -x) for x, y in self.G.nodes()}  # Orient for top-down view
        
        # Draw background grid
        nx.draw_networkx_nodes(self.G, pos, node_size=100, node_color="lightgray")
        nx.draw_networkx_edges(self.G, pos, alpha=0.3)
        
        # Draw the calculated path
        if path:
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_nodes(self.G, pos, nodelist=path, node_size=150, node_color="blue")
            nx.draw_networkx_edges(self.G, pos, edgelist=path_edges, edge_color="blue", width=3)
        
        # Highlight Start and End points
        nx.draw_networkx_nodes(self.G, pos, nodelist=[self.ugv_start], node_size=200, node_color="green", label="UGV Start")
        nx.draw_networkx_nodes(self.G, pos, nodelist=[self.ugv_target], node_size=200, node_color="gold", label="Extraction")
        
        plt.title("TITAN_OPS AIR: Dynamic Graph Routing")
        plt.axis("off")
        plt.savefig(filename, bbox_inches='tight', facecolor='black')
        print(f"[MAP] Visual telemetry saved to {filename}")

# --- STANDALONE TEST SIMULATION ---
if __name__ == "__main__":
    tactical_map = SwarmTacticalMap()
    
    # Simulating the YOLO telemetry you just received in Step 1!
    yolo_threats = [
        (740, 637),
        (143, 651),
        (283, 634),
        (34, 713)
    ]
    
    # 1. Translate pixel vectors to graph nodes and inject obstacles
    for threat_pixel in yolo_threats:
        grid_node = tactical_map.translate_camera_to_grid(threat_pixel[0], threat_pixel[1])
        tactical_map.inject_threat(grid_node, danger_radius=1)
        
    # 2. Command UGV to calculate path around the new threats
    evasion_path = tactical_map.calculate_evasion_route()
    
    # 3. Generate Map Image
    tactical_map.visualize_tactical_map(evasion_path)