
import networkx as nx
import matplotlib.pyplot as plt

def create_library_graph():
    graph = nx.Graph()

    # Library sections (vertices)
    sections = [
        "Entrance",
        "Computer Science",
        "Mathematics",
        "Science",
        "Reference",
        "Reading Room"
    ]

    graph.add_nodes_from(sections)

    # Connections and distances (edges)
    connections = [
        ("Entrance", "Computer Science", 2),
        ("Entrance", "Mathematics", 4),
        ("Computer Science", "Science", 3),
        ("Computer Science", "Reference", 5),
        ("Mathematics", "Reading Room", 2),
        ("Science", "Reading Room", 4),
        ("Reference", "Reading Room", 3)
    ]

    graph.add_weighted_edges_from(connections)
    return graph


def display_graph(graph):
    print("\n--- LIBRARY GRAPH ---")
    print("Vertices:", list(graph.nodes()))
    print("Edges:", list(graph.edges(data=True)))


def display_adjacency_matrix(graph):
    print("\n--- ADJACENCY MATRIX ---")
    matrix = nx.to_numpy_array(
        graph,
        nodelist=list(graph.nodes()),
        weight=None,
        dtype=int
    )
    print(matrix)


def perform_bfs(graph):
    print("\n--- BREADTH FIRST SEARCH ---")
    result = list(nx.bfs_tree(graph, "Entrance").nodes())
    print("BFS Traversal:", result)


def perform_dfs(graph):
    print("\n--- DEPTH FIRST SEARCH ---")
    result = list(nx.dfs_preorder_nodes(graph, "Entrance"))
    print("DFS Traversal:", result)


def find_shortest_path(graph):
    print("\n--- SHORTEST PATH ---")
    path = nx.shortest_path(
        graph,
        source="Entrance",
        target="Reading Room",
        weight="weight"
    )

    distance = nx.shortest_path_length(
        graph,
        source="Entrance",
        target="Reading Room",
        weight="weight"
    )

    print("Shortest Path:", path)
    print("Total Distance:", distance)


def find_minimum_spanning_tree(graph):
    print("\n--- MINIMUM SPANNING TREE ---")
    mst = nx.minimum_spanning_tree(graph, weight="weight")

    print("MST Edges:")
    for edge in mst.edges(data=True):
        print(edge)

    print("Total MST Weight:", mst.size(weight="weight"))


def draw_graph(graph):
    position = nx.spring_layout(graph, seed=42)

    nx.draw(
        graph,
        position,
        with_labels=True,
        node_color="lightblue",
        node_size=2500,
        font_size=8
    )

    labels = nx.get_edge_attributes(graph, "weight")
    nx.draw_networkx_edge_labels(
        graph,
        position,
        edge_labels=labels
    )

    plt.title("Intelligent Library - Graph Theory")
    plt.savefig("library_graph.png")
    print("\nGraph image saved as library_graph.png")
    plt.show()


if __name__ == "__main__":
    library_graph = create_library_graph()

    display_graph(library_graph)
    display_adjacency_matrix(library_graph)
    perform_bfs(library_graph)
    perform_dfs(library_graph)
    find_shortest_path(library_graph)
    find_minimum_spanning_tree(library_graph)
    draw_graph(library_graph)
