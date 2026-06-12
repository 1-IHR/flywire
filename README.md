# FlyWire Summer Internship: Qualification Challenge

**Ibtisam Haseeb** ·  ibtisam.haseeb@tamu.edu

---

## Result

> **45 neurons · 84 directed edges · BANC × FAFB × MCNS · score 46.86**
> Score ranked across triplets by N × (1 + edge density) to jointly reward subgraph size and connectivity; the winning triplet also has the highest raw N. Verified by exhaustive pairwise isomorphism check: 2,025 ordered pairs, 0 violations.

> In FAFB, the 45 neurons annotate as the optic lobe Elementary Motion Detector (T4/T5/Tm/Mi1/CT1; Schlegel et al. 2024). The same topology maps to optic lobe neurons in MCNS and to mushroom body neurons (Kenyon cells, APL, MBON30) in BANC.
---

## Key Observations

The five graphs span a 10x density range (FAFB ~27 edges per node, MANC ~224). Node-level degree signatures applied directly produced either zero cross-dataset matches (threshold too strict) or compatibility graphs with density ~0.97 (threshold too coarse, making clique search intractable). Integer node IDs carry no shared identity across datasets, so the problem is purely structural with no label information to exploit.

---

## Approach

This problem is NP-hard, so rather than searching exhaustively, the problem is reduced to maximum clique on a bounded compatibility graph, then verified exactly.

**Edge signatures.** The density gap rules out node signatures. Constraining both endpoints of a directed edge jointly, via a log2-binned 4-tuple of in/out degrees, yields signatures substantially more selective than single-node fingerprints, since both source and target degree profiles must match simultaneously:

```
sig(u->v) = ( floor(log2 in_deg(u)),  floor(log2 out_deg(u)),
              floor(log2 in_deg(v)),  floor(log2 out_deg(v)) )   values capped at 6
```

Edges sharing a signature across all three graphs in a triplet seed the candidate pool. Within each bucket, the top 8 edges per graph by combined endpoint degree are kept, preferring hub-centred neighbourhoods that empirically produce denser compatibility graphs and larger cliques.

**Compatibility graph.** A candidate edge triple is a tuple of three directed edges, one from each graph, sharing the same signature. Two edge triples involve four node positions in total (two sources and two targets). They are connected in the compatibility graph iff those four positions satisfy injectivity (equality relationships between all four cross-position pairs are consistent across all three graphs) and edge consistency (all eight directed cross-edges between the four positions, both directions for each of the four pairs, are present or absent identically across all three graphs). A clique in this undirected graph corresponds to a valid common induced subgraph by construction: every pair of edge triples is mutually compatible, guaranteeing an injective, edge-consistent mapping across all three datasets.

**Search.** 2-core pruning discards nodes that cannot belong to any clique of size 3 or greater. Bron-Kerbosch with degree ordering then runs on the pruned graph. All C(5,3) = 10 dataset triplets are evaluated, each with a one-hour time budget chosen to allow a full sweep overnight. On the winning triplet, the maximum clique was found within the first minute; a subsequent extended run stalled at the same result after 189 minutes with no improvement, suggesting N=45 is stable under this candidate set.

**Verification.** The edge-clique-to-node-triple conversion can introduce violations from reverse edges not visible at the compatibility graph level. An O(N^2) pairwise directed check is run over the extracted node set, and a greedy repair removes the most-violated node triple iteratively until the mapping is clean. The final result passed with 0 violations across all 2,025 directed pairs.

---

## Heuristics

1. **`MAX_EDGES_PER_SIG = 8` (bucket size).** On the winning triplet, k=8 yields a compatibility graph density of 0.214 and a maximum clique of 61 edge triples (45 nodes). Raising to k=12 drops density to 0.125 and the clique to 29; k=9 and k=10 degraded similarly. Lower-ranked candidates dilute the dense core of the compatibility graph rather than extending it, so a tighter bucket consistently outperforms a looser one. Confirmed optimal by testing k in {8, 9, 10, 11, 12}.

2. **`MAX_EDGE_TRIPLES = 10,000` (candidate cap).** At this cap the compatibility graph carries approximately 10.7M edges (around 4 GB RAM). At 15,000 triples, compatibility graph density fell to 0.144 and the best clique shrank to 28. Higher candidate counts dilute the dense core of the compatibility graph rather than extending it, so 10,000 was retained as optimal.
   
4. **`KCORE_K = 2` (pruning threshold).** After pruning, 9,620 of 10,000 nodes survived on the winning triplet. The compatibility graph is genuinely dense throughout and pruning removes very little, so the threshold imposes no meaningful quality trade-off while reducing clique search time.

---

## Assumptions

1. Structural similarity is captured by coarse log2-binned degree profiles. Two non-isomorphic neighbourhoods can share a 4-tuple signature (false positives), and the reverse is also possible given the density gap (false negatives). False positives are eliminated downstream by the compatibility check and O(N^2) verification. False negatives would result in a smaller recovered subgraph. The result is a **certified lower bound**, not a proven global optimum. Re-runs across the full hyperparameter grid tested did not exceed N=45 on any triplet.

2. Hub-degree ordering in candidate selection assumes the largest common subgraph is anchored on high-degree nodes. This held empirically: the recovered circuit is centred on CT1, the highest-degree node in the FAFB subgraph. It is a heuristic, not a guarantee.

3. No biological metadata was used at any stage. The algorithm operates purely on graph structure; node IDs are treated as opaque integers throughout.

---

## Files in Repository

```
├── 3d.png               3D rendering of 45 neurons; FAFB; Brain regions shown
├── interactive.html     visualization of circuit
├── README.md            technical strategy and algorithm used
├── flywire.py           source code, full search across all 10 dataset triplets
├── network.csv          45 matched neuron IDs (columns: BANC, FAFB, MCNS)
├── network.png          Network graph of connections betweeen neurons; labelled
├── poster.pdf           Scientific poster; with visualizations and biological relevance
├── verify.py            code for isomomorphism check; independent of source code
├── science.md           scientific poster; biological investigation of the circuit in FAFB 

```

---

## Reproducing

```bash
pip install networkx==3.6.1 pandas==3.0.3
python flywire.py
```

The five edge-list CSVs must be present in the same directory as `flywire.py`, named exactly:

```
banc_626_edge_list.csv
fafb_783_edge_list.csv
manc_1.2.1_edge_list.csv
maol_1.1_edge_list.csv
mcns_0.9_edge_list.csv
```

Runtime is approximately 10 hours on a machine with 20 GB available RAM (one-hour search budget per triplet across all 10 combinations). The best result is written to `network.csv` on completion.


## Verification

`verify.py` checks the result in `network.csv` independently of the pipeline. For every ordered pair (i, j) across all 45 rows, it queries whether the directed edge i→j is present in each of the three graphs and checks that the answer is identical across BANC, FAFB, and MCNS. This covers all N² = 2,025 directed pairs. Any mismatch is printed as a violation.

```bash
python verify.py
# VERIFIED: all 2025 directed pairs are isomorphic
```

