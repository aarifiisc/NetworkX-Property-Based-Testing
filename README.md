# E0 251o (2026) – Property-Based Testing for NetworkX

**Team:** AARIF ZAFAR (solo)  
**Algorithms Tested:**  
- `networkx.minimum_spanning_tree`  
- `networkx.shortest_path_length`  
- `networkx.group_betweenness_centrality` (with **genuine bug discovery**)

## Project Summary
This project implements 11 property-based tests using **Hypothesis** to validate fundamental mathematical invariants, postconditions, metamorphic properties, and boundary conditions of NetworkX graph algorithms.

**Bonus Achieved (2 points):**  
A genuine bug was discovered in `nx.group_betweenness_centrality`:
- Returns **negative** centrality values (mathematically impossible)
- Raises `KeyError` on internal distance matrix `D` for certain valid inputs

## Files
- `networkx_property_tests.py` – All property-based tests + detailed docstrings (the only file required for submission)
- `requirements.txt`
- `report.pdf` – Full LaTeX project report (see `report.tex`)

## How to Run the Tests

```bash
pip install -r requirements.txt
pytest networkx_property_tests.py -q