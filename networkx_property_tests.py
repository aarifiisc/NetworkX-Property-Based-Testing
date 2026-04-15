"""
E0 251o (2026) Project: Property-Based Testing for NetworkX

Team Member(s): AARIF ZAFAR (solo)

Algorithms Tested:
- networkx.minimum_spanning_tree (weighted undirected graphs, including disconnected cases)
- networkx.shortest_path_length (unweighted undirected graphs)

All tests use Hypothesis for diverse random graph generation.
No genuine bugs discovered in NetworkX after extensive randomized testing.
One metamorphic test was refined after a falsifying example revealed an incorrect assumption
(only holds on connected graphs).

"""

import networkx as nx
from hypothesis import given, strategies as st, assume
import pytest  # for expected exception tests


# ==================== MST Basic Tests ====================

@given(st.integers(min_value=3, max_value=12), st.data())
def test_mst_edge_count_for_connected_graph(n: int, data):
    """
    Property: A minimum spanning tree of a connected undirected weighted graph
    with n nodes has exactly n-1 edges.

    Mathematical basis: A tree on n vertices is connected and acyclic.
    """
    G = nx.gnp_random_graph(n, 0.5)
    assume(nx.is_connected(G))
    for u, v in list(G.edges()):
        G.edges[u, v]["weight"] = data.draw(st.integers(min_value=1, max_value=20))

    mst = nx.minimum_spanning_tree(G)
    assert len(mst.edges()) == n - 1


@given(st.integers(min_value=3, max_value=12), st.data())
def test_mst_is_acyclic(n: int, data):
    """
    Property: The minimum spanning tree is acyclic.
    """
    G = nx.gnp_random_graph(n, 0.5)
    assume(nx.is_connected(G))
    for u, v in list(G.edges()):
        G.edges[u, v]["weight"] = data.draw(st.integers(min_value=1, max_value=20))

    mst = nx.minimum_spanning_tree(G)
    try:
        nx.find_cycle(mst)
        assert False, "MST contains a cycle"
    except nx.NetworkXNoCycle:
        pass


@given(st.integers(min_value=3, max_value=12), st.data())
def test_mst_spans_all_vertices(n: int, data):
    """
    Property: The MST includes every original vertex.
    """
    G = nx.gnp_random_graph(n, 0.5)
    assume(nx.is_connected(G))
    for u, v in list(G.edges()):
        G.edges[u, v]["weight"] = data.draw(st.integers(min_value=1, max_value=20))

    mst = nx.minimum_spanning_tree(G)
    assert set(mst.nodes()) == set(G.nodes())


# ==================== Shortest Path Tests ====================

@given(st.integers(min_value=3, max_value=12))
def test_shortest_path_length_matches_actual_path(n: int):
    """
    Property: shortest_path_length equals number of edges in shortest_path.
    """
    G = nx.gnp_random_graph(n, 0.5)
    assume(nx.is_connected(G))

    for source in G.nodes():
        for target in G.nodes():
            length = nx.shortest_path_length(G, source, target)
            path = nx.shortest_path(G, source, target)
            assert len(path) - 1 == length


@given(st.integers(min_value=3, max_value=12))
def test_shortest_path_satisfies_triangle_inequality(n: int):
    """
    Property: Shortest-path distances obey triangle inequality.
    """
    G = nx.gnp_random_graph(n, 0.5)
    assume(nx.is_connected(G))

    dist = dict(nx.shortest_path_length(G))
    for u in G.nodes():
        for v in G.nodes():
            for w in G.nodes():
                assert dist[u][v] <= dist[u][w] + dist[w][v]


@given(st.integers(min_value=1, max_value=12))
def test_shortest_path_self_distance_is_zero(n: int):
    """
    Property: Distance from any node to itself is 0 (boundary case).
    """
    if n == 1:
        G = nx.Graph()
        G.add_node(0)
    else:
        G = nx.gnp_random_graph(n, 0.5)
        assume(nx.is_connected(G))

    for v in G.nodes():
        assert nx.shortest_path_length(G, v, v) == 0


# ==================== MST Advanced Tests ====================

@given(st.integers(min_value=3, max_value=15), st.data())
def test_mst_on_disconnected_graph_returns_forest(n: int, data):
    """
    Property: On a disconnected graph, minimum_spanning_tree
    returns a minimum spanning *forest* with edge count = n - num_components.
    """
    G = nx.gnp_random_graph(n, 0.3)
    for u, v in list(G.edges()):
        G.edges[u, v]["weight"] = data.draw(st.integers(min_value=1, max_value=20))

    forest = nx.minimum_spanning_tree(G)
    num_components = nx.number_connected_components(G)
    expected_edges = n - num_components
    assert len(forest.edges()) == expected_edges


@given(st.integers(min_value=3, max_value=10), st.data())
def test_mst_total_weight_non_increasing_when_adding_positive_edge(n: int, data):
    """
    Property: On a *connected* graph, adding any genuinely new 
    edge with positive weight never increases the total weight of the MST.

    Mathematical basis: The original MST is still a valid spanning tree of the
    new graph, so the minimum cannot get worse (it can only stay the same or
    improve if the new edge creates a cheaper shortcut).
    """
    G = nx.gnp_random_graph(n, 0.5)
    
    # FIX 1: Ensure the graph is fully connected (prevents the Forest MSF issue)
    assume(nx.is_connected(G))          

    # Assign random weights to existing edges
    for u, v in list(G.edges()):
        G.edges[u, v]["weight"] = data.draw(st.integers(min_value=1, max_value=20))

    mst1 = nx.minimum_spanning_tree(G)
    weight1 = sum(d["weight"] for u, v, d in mst1.edges(data=True))

    # FIX 2: Ensure we only pick an edge that does NOT already exist
    non_edges = list(nx.non_edges(G))
    assume(len(non_edges) > 0) # Skip if the graph is a complete graph (all edges exist)

    u, v = data.draw(st.sampled_from(non_edges))
    new_weight = data.draw(st.integers(min_value=1, max_value=20))
    
    G.add_edge(u, v, weight=new_weight)

    mst2 = nx.minimum_spanning_tree(G)
    weight2 = sum(d["weight"] for u, v, d in mst2.edges(data=True))
    
    assert weight2 <= weight1



@given(st.integers(min_value=3, max_value=10))
def test_shortest_path_length_raises_on_no_path(n: int):
    """
    Property: shortest_path_length raises NetworkXNoPath when no path exists.
    """
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n // 2):
        if i + 1 < n // 2:
            G.add_edge(i, i + 1)

    with pytest.raises(nx.NetworkXNoPath):
        nx.shortest_path_length(G, 0, n - 1)


@given(st.integers(min_value=3, max_value=8), st.data())
def test_mst_with_negative_weights(n: int, data):
    """
    Property (Boundary): minimum_spanning_tree correctly handles negative weights.
    """
    G = nx.gnp_random_graph(n, 0.5)
    assume(nx.is_connected(G))
    for u, v in list(G.edges()):
        G.edges[u, v]["weight"] = data.draw(st.integers(min_value=-10, max_value=20))

    mst = nx.minimum_spanning_tree(G)
    assert len(mst.edges()) == n - 1
    try:
        nx.find_cycle(mst)
        assert False
    except nx.NetworkXNoCycle:
        pass


import networkx as nx
from hypothesis import given, assume, strategies as st

@given(st.integers(min_value=4, max_value=15), st.data())
def test_group_betweenness_centrality_non_negative(n: int, data):
    """
    Property (Invariant): Group betweenness centrality must never be negative.

    Mathematical basis: Betweenness centrality represents the fraction of 
    shortest paths that pass through a given group of nodes. Since path 
    counts and fractions cannot be negative, the resulting centrality 
    metric must always be >= 0.

    Test strategy: Generate a random directed graph. Ensure the graph is NOT 
    strongly connected (as this triggers the algorithmic flaw). Randomly sample 
    a valid subset of nodes to act as the 'group'. Compute the group betweenness 
    centrality and assert that the result is non-negative.
    
    Why this matters: If this property fails, it indicates a severe flaw in the 
    underlying shortest-path accounting logic of the algorithm.
    """
    # 1. Generate a directed graph
    G = nx.gnp_random_graph(n, 0.3, directed=True)
    
    # 2. The bug explicitly occurs on directed graphs that are NOT strongly connected
    assume(not nx.is_strongly_connected(G))
    
    # 3. Pick a random group size (at least 1 node, but not the whole graph)
    k = data.draw(st.integers(min_value=1, max_value=n-1))
    
    # 4. Sample a unique group of 'k' nodes
    nodes_list = list(G.nodes())
    group = set(data.draw(st.lists(st.sampled_from(nodes_list), min_size=k, max_size=k, unique=True)))
    
    # 5. Execute algorithm
    centrality = nx.group_betweenness_centrality(G, group)
    
    # 6. Assert the mathematical invariant
    assert centrality >= 0.0, f"Bug discovered! Negative centrality: {centrality}"


import networkx as nx
from hypothesis import given, strategies as st

@given(st.integers(min_value=2, max_value=10), st.data())
def test_group_betweenness_normalization_bounds(n: int, data):
    """
    Property (Postcondition): Normalized group betweenness centrality must 
    always be less than or equal to 1.0.

    Feature tested: The `normalized=True` parameter.

    Mathematical basis: Normalization scales the raw centrality score by dividing 
    it by the maximum possible number of shortest paths that could exist between 
    all non-group nodes. Because you cannot have more paths than the theoretical 
    maximum, the resulting fraction must strictly be <= 1.0.

    Test strategy: Generate random graphs of various small-to-medium sizes. 
    Select a random group of nodes, explicitly call the algorithm with 
    `normalized=True`, and verify the upper bound.
    """
    G = nx.gnp_random_graph(n, 0.5)
    
    # Pick a random group size (must leave at least 1 node outside the group)
    k = data.draw(st.integers(min_value=1, max_value=n-1))
    
    # Sample the group uniquely
    nodes_list = list(G.nodes())
    group = set(data.draw(st.lists(
        st.sampled_from(nodes_list), 
        min_size=k, 
        max_size=k, 
        unique=True
    )))
    
    # Test the specific feature
    centrality = nx.group_betweenness_centrality(G, group, normalized=True)
    
    # Assert the mathematical bound
    assert centrality <= 1.0, f"Centrality exceeded 1.0: {centrality}"
