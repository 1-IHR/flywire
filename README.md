# FlyWire Qualification Challenge

## Objective

Find the largest directed induced subgraph shared across at least 3 of the 5 connectome datasets, where "shared" means the subgraphs are mutually isomorphic: same nodes, same directed edges, across all three datasets simultaneously.

## Approach

This is the Maximum Common Induced Subgraph (MCIS) problem, which is NP-hard. For graphs with 100K+ nodes, brute-force search over node mappings is infeasible.

Each dataset is provided as a CSV edge list where each row is a directed synapse: the left integer is the presynaptic neuron ID and the right integer is the postsynaptic neuron ID. The algorithm operates entirely on these raw integer IDs and the connectivity structure they define. No biological labels or metadata are used at any stage.

Node-level filtering fails here because connectome density varies widely across datasets (average degree ranges from \~27 in FAFB to \~224 in MANC), so any node signature either produces zero cross-dataset matches or a near-complete compatibility graph that makes clique search intractable.

The solution uses an edge-first approach that reduces MCIS to Maximum Clique:

**Stage 1: Edge signatures.** For each directed edge u→v, compute a 4-tuple signature: (log2-binned in-degree of u, log2-binned out-degree of u, log2-binned in-degree of v, log2-binned out-degree of v). Log-binning on a scale of 0-6 bridges the density gap between datasets while still being discriminative. Constraining both endpoints jointly makes edge signatures \~|G| times more selective than node signatures.

**Stage 2: Candidate edge triples.** All C(5,3) \= 10 triplet combinations of the five datasets are evaluated. For each triplet, find signatures shared across all three graphs. Within each shared signature bucket, take the top 4 edges per graph ranked by combined endpoint degree. Prioritizing high-degree edges targets hub-centered connectivity patterns, where a single highly-connected node anchors edges to many neighbors across multiple cell types. This is the structural profile most likely to yield a large isomorphic subgraph. Form all combinations, capped at 3000 triples total.

**Stage 3: Compatibility graph.** Build a graph where nodes are edge triples and two triples are connected if they are mutually compatible: (a) their implied node mappings are injective and consistent across all three graphs, and (b) all 8 cross-directed edges between the 4 involved nodes agree across all three graphs. A clique in this graph corresponds to a valid common induced subgraph because every pair of edge triples in the clique is mutually compatible, guaranteeing that the combined node mapping is injective and all edge relationships are consistent across all three datasets.

**Stage 4: Maximum clique.** Apply 2-core pruning (any node with fewer than 2 compatible neighbors cannot be in a clique of size \>= 3), then run Bron-Kerbosch on the pruned graph. The compatibility graph is undirected because compatibility between two edge triples is a symmetric relationship: if triple A is consistent with triple B, then B is consistent with A. Directionality of the original connectomes is preserved through the compatibility check itself, which requires all 8 cross-directed edge relationships between the 4 involved nodes to agree across all three datasets before two triples are considered compatible. A 600-second timeout returns the best clique found.

**Stage 5: Verification.** Extract node triples from the winning edge clique and run a full O(N^2) pairwise isomorphism check covering both edge directions for all pairs. This step is necessary because the compatibility graph checks pairs of edge triples, but a clique of size k can have multi-way inconsistencies not caught pairwise, specifically the reverse edges v→u and q→p which are not among the 8 cross-directed edges checked in Stage 3\. A greedy repair removes the node triple with the most violations and repeats until the set is clean. A separate verification script confirms 0 violations across all N\*N directed pairs.

**Scoring.** Each triplet is scored as N \* (1 \+ edge\_density) on the largest weakly connected component of the matched node set, requiring N \>= 3 and edges \>= N. This penalises isolated matched pairs that form no coherent circuit and selects the best triplet across all 10 combinations.

## Assumptions

- Self-loops removed (a neuron synapsing onto itself is not meaningful cross-dataset structural information)  
- Edge weights ignored as specified  
- Edge direction preserved throughout  
- Only the largest weakly connected component of the matched node set is reported

## Hyperparameters

| Parameter | Value | Reasoning |
| :---- | :---- | :---- |
| MAX\_EDGES\_PER\_SIG | 4 | Keeps compatibility graph construction tractable (O(n^2) at n\<=3000) |
| MAX\_EDGE\_TRIPLES | 3000 | Hard cap; degree-sorted so best candidates are retained |
| KCORE\_K | 2 | Removes nodes that cannot belong to any clique of size \>= 3 |
| TIMEOUT\_S | 600 | Sufficient for Bron-Kerbosch to exhaust the pruned search space |

## Reproducing the result

**Dependencies**

python \>= 3.9

networkx

pandas

collections, math, itertools, os, threading, time (standard library)

**File structure**

Place the five edge list CSVs in the same directory as `pipeline.py`:

banc\_626\_edge\_list.csv

fafb\_783\_edge\_list.csv

manc\_1.2.1\_edge\_list.csv

maol\_1.1\_edge\_list.csv

mcns\_0.9\_edge\_list.csv

**Run**

python pipeline.py

Output: `network.csv` with 3 columns (dataset names) and N rows (matched neuron IDs).

To verify the result:

python verify.py

Expected output: `VERIFIED: all 1024 directed pairs isomorphic`

## Results across all 10 triplets

| Triplet | Matched neurons | Induced edges | Score |
| :---- | :---- | :---- | :---- |
| BANC x FAFB x MCNS | 32 | 55 | 36.88 |
| FAFB x MANC x MCNS | 37 | 42 | 36.21 |
| FAFB x MAOL x MCNS | 38 | 57 | 29.63 |
| FAFB x MANC x MAOL | 24 | 29 | 23.33 |
| BANC x MAOL x MCNS | 20 | 30 | 17.80 |
| BANC x FAFB x MAOL | 20 | 23 | 15.77 |
| MANC x MAOL x MCNS | 16 | 17 | 15.23 |
| BANC x MANC x MCNS | 10 | 9 | 10.12 |
| BANC x MANC x MAOL | 10 | 11 | 9.29 |
| BANC x FAFB x MANC | 12 | 10 | 0.00 |

BANC x FAFB x MCNS was selected as the best result by the scoring function.

## Final result

Best triplet: **BANC x FAFB x MCNS** 
Matched neurons: **32** 
Induced directed edges: **55** 
Isomorphism violations: **0**  
