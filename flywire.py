import collections
import math
import os
import threading
import time

import networkx as nx
import pandas as pd

FILES = {
    "BANC": "banc_626_edge_list.csv",
    "FAFB": "fafb_783_edge_list.csv",
    "MANC": "manc_1.2.1_edge_list.csv",
    "MAOL": "maol_1.1_edge_list.csv",
    "MCNS": "mcns_0.9_edge_list.csv",
}

# Hyperparameters 
MAX_EDGES_PER_SIG = 8      # best result at 8; 9+ diluted candidate quality in previous run 
MAX_EDGE_TRIPLES  = 10000  # compatible with device memory
KCORE_K           = 2      # min compatible neighbours to survive pruning
STALL_MINUTES     = 60    # stop if no improvement for 1 hour

FOCUS_TRIPLET = None 


def load_graph(path):
    df = pd.read_csv(path)
    df = df.iloc[:, :2]
    df.columns = ["source", "target"]
    df = df[df["source"] != df["target"]]
    return nx.from_pandas_edgelist(
        df, "source", "target", create_using=nx.DiGraph()
    )


def log_bin(d):
    return min(int(math.log2(max(d, 1))), 6)


def build_out_adj(G):
    return {n: set(G.successors(n)) for n in G.nodes()}


def edge_signatures(G):
    sigs = collections.defaultdict(list)
    for u, v in G.edges():
        sig = (
            log_bin(G.in_degree(u)),  log_bin(G.out_degree(u)),
            log_bin(G.in_degree(v)),  log_bin(G.out_degree(v)),
        )
        sigs[sig].append((u, v))
    return sigs


def sample_edge_triples(sigs_trio, graphs_trio):
    shared_sigs = set(sigs_trio[0]) & set(sigs_trio[1]) & set(sigs_trio[2])

    sorted_sigs = [{}, {}, {}]
    for i, (sig_map, G) in enumerate(zip(sigs_trio, graphs_trio)):
        for sig in shared_sigs:
            edges = sorted(sig_map[sig],
                           key=lambda e: G.degree(e[0]) + G.degree(e[1]),
                           reverse=True)
            sorted_sigs[i][sig] = edges

    triples = []
    for sig in shared_sigs:
        es0 = sorted_sigs[0][sig][:MAX_EDGES_PER_SIG]
        es1 = sorted_sigs[1][sig][:MAX_EDGES_PER_SIG]
        es2 = sorted_sigs[2][sig][:MAX_EDGES_PER_SIG]
        for e0 in es0:
            for e1 in es1:
                for e2 in es2:
                    triples.append((e0, e1, e2))

    if len(triples) > MAX_EDGE_TRIPLES:
        def score(t):
            return (graphs_trio[0].degree(t[0][0]) + graphs_trio[0].degree(t[0][1]) +
                    graphs_trio[1].degree(t[1][0]) + graphs_trio[1].degree(t[1][1]) +
                    graphs_trio[2].degree(t[2][0]) + graphs_trio[2].degree(t[2][1]))
        triples.sort(key=score, reverse=True)
        triples = triples[:MAX_EDGE_TRIPLES]

    return triples


def verified_node_triples(edge_triples, adj_trio):
    adj0, adj1, adj2 = adj_trio

    node_map = {}
    for (u1, v1), (u2, v2), (u3, v3) in edge_triples:
        node_map[(u1, u2, u3)] = True
        node_map[(v1, v2, v3)] = True
    node_triples = list(node_map.keys())

    def pair_ok(i, j):
        n1a, n2a, n3a = node_triples[i]
        n1b, n2b, n3b = node_triples[j]
        if n1a == n1b or n2a == n2b or n3a == n3b:
            return False
        fwd = (n1b in adj0.get(n1a, set()),
               n2b in adj1.get(n2a, set()),
               n3b in adj2.get(n3a, set()))
        bwd = (n1a in adj0.get(n1b, set()),
               n2a in adj1.get(n2b, set()),
               n3a in adj2.get(n3b, set()))
        return fwd[0] == fwd[1] == fwd[2] and bwd[0] == bwd[1] == bwd[2]

    active = list(range(len(node_triples)))
    while True:
        # FIX: guard against empty active list to prevent max([]) ValueError
        if not active:
            break
        violations = [0] * len(active)
        for ii in range(len(active)):
            for jj in range(ii + 1, len(active)):
                if not pair_ok(active[ii], active[jj]):
                    violations[ii] += 1
                    violations[jj] += 1
        worst = max(violations)
        if worst == 0:
            break
        active.pop(violations.index(worst))

    return [node_triples[i] for i in active]


def build_compat_graph(edge_triples, adj_trio):
    n = len(edge_triples)
    CG = nx.Graph()
    CG.add_nodes_from(range(n))
    adj0, adj1, adj2 = adj_trio

    for i in range(n):
        (u1, v1), (u2, v2), (u3, v3) = edge_triples[i]
        for j in range(i + 1, n):
            (p1, q1), (p2, q2), (p3, q3) = edge_triples[j]

            skip = False
            for (x1, x2, x3), (y1, y2, y3) in (
                ((u1, u2, u3), (p1, p2, p3)),
                ((u1, u2, u3), (q1, q2, q3)),
                ((v1, v2, v3), (p1, p2, p3)),
                ((v1, v2, v3), (q1, q2, q3)),
            ):
                if not ((x1 == y1) == (x2 == y2) == (x3 == y3)):
                    skip = True
                    break
            if skip:
                continue

            cross_edges = [
                ((p1 in adj0.get(u1, set())), (p2 in adj1.get(u2, set())), (p3 in adj2.get(u3, set()))),
                ((u1 in adj0.get(p1, set())), (u2 in adj1.get(p2, set())), (u3 in adj2.get(p3, set()))),
                ((q1 in adj0.get(v1, set())), (q2 in adj1.get(v2, set())), (q3 in adj2.get(v3, set()))),
                ((v1 in adj0.get(q1, set())), (v2 in adj1.get(q2, set())), (v3 in adj2.get(q3, set()))),
                ((q1 in adj0.get(u1, set())), (q2 in adj1.get(u2, set())), (q3 in adj2.get(u3, set()))),
                ((u1 in adj0.get(q1, set())), (u2 in adj1.get(q2, set())), (u3 in adj2.get(q3, set()))),
                ((p1 in adj0.get(v1, set())), (p2 in adj1.get(v2, set())), (p3 in adj2.get(v3, set()))),
                ((v1 in adj0.get(p1, set())), (v2 in adj1.get(p2, set())), (v3 in adj2.get(p3, set()))),
            ]

            if all(a == b == c for a, b, c in cross_edges):
                CG.add_edge(i, j)

    return CG


def find_max_clique_deep(CG, edge_triples, adj_trio, graphs, g1, g2, g3,
                         stall_minutes=STALL_MINUTES):
    """
    Run Bron-Kerbosch until fully exhausted or stalled.
    No hard time limit — stops only when:
      (a) search space is exhausted naturally, or
      (b) no improvement for stall_minutes minutes.

    Saves network.csv every time a new best clique is found so the run
    can be safely interrupted without losing the best result seen so far.
    """
    if CG.number_of_nodes() == 0:
        return []

    deg_order = sorted(CG.nodes(), key=lambda n: CG.degree(n), reverse=True)
    fwd_map   = {n: i for i, n in enumerate(deg_order)}
    rev_map   = {i: n for n, i in fwd_map.items()}
    CG_sorted = nx.relabel_nodes(CG, fwd_map)

    best          = []
    last_improved = [time.time()]
    done          = threading.Event()

    def save_checkpoint(clique_ids):
        """Verify and save network.csv for current best clique."""
        try:
            winning_edges = [edge_triples[i] for i in clique_ids]
            nt = verified_node_triples(
                winning_edges, [adj_trio[0], adj_trio[1], adj_trio[2]]
            )
            if not nt:
                return
            nodes = [t[0] for t in nt]
            sub   = graphs[g1].subgraph(nodes)
            wcc   = list(nx.weakly_connected_components(sub))
            if not wcc:
                return
            largest = max(wcc, key=len)
            final   = [t for t in nt if t[0] in largest]
            pd.DataFrame(final, columns=[g1, g2, g3]).to_csv("network1.csv", index=False)
            print(f"    -> checkpoint saved: {len(final)} neurons, network1.csv updated")
        except Exception as e:
            print(f"    -> checkpoint save failed: {e}")

    def run():
        nonlocal best
        try:
            for clique in nx.find_cliques(CG_sorted):
                if done.is_set():
                    return
                if len(clique) > len(best):
                    best = clique[:]
                    last_improved[0] = time.time()
                    elapsed = time.time() - t_run_start
                    print(f"  [+{elapsed/60:.1f}min] new best edge clique: {len(best)}")
                    # Save immediately so killing the script never loses progress
                    save_checkpoint([rev_map[i] for i in best])
        except Exception as e:
            print(f"  [warning] clique search error: {e}")
        done.set()

    t_run_start = time.time()
    worker = threading.Thread(target=run, daemon=True)
    worker.start()

    stall_seconds = stall_minutes * 60
    while not done.is_set():
        time.sleep(30)
        elapsed_since_improvement = time.time() - last_improved[0]
        elapsed_total = time.time() - t_run_start
        print(f"  [running {elapsed_total/60:.1f}min] "
              f"best={len(best)}, "
              f"stall={elapsed_since_improvement/60:.1f}/{stall_minutes}min")
        if elapsed_since_improvement > stall_seconds:
            print(f"  [stall] no improvement for {stall_minutes} min — stopping")
            done.set()

    worker.join(2.0)
    return [rev_map[i] for i in best]


def circuit_score(node_triples, G_primary):
    if not node_triples:
        return 0.0
    nodes = [t[0] for t in node_triples]
    sub   = G_primary.subgraph(nodes)
    wcc   = list(nx.weakly_connected_components(sub))
    if not wcc:
        return 0.0
    largest    = max(wcc, key=len)
    sub_conn   = sub.subgraph(largest)
    n = sub_conn.number_of_nodes()
    e = sub_conn.number_of_edges()
    if n < 3 or e < n:
        return 0.0
    density = e / (n * (n - 1)) if n > 1 else 0.0
    return float(n) * (1.0 + density)


def main():
    t_start = time.time()

    print(f"DEEP SEARCH: {FOCUS_TRIPLET[0]} x {FOCUS_TRIPLET[1]} x {FOCUS_TRIPLET[2]}")
    print(f"MAX_EDGES_PER_SIG={MAX_EDGES_PER_SIG}, MAX_EDGE_TRIPLES={MAX_EDGE_TRIPLES}")
    print(f"Stall limit: {STALL_MINUTES} minutes")
    print(f"network1.csv is saved on every new best — safe to kill at any time\n")

    graphs, sigs, adj_sets = {}, {}, {}
    for name in FOCUS_TRIPLET:
        path = FILES[name]
        if not os.path.exists(path):
            print(f"{name}: file not found at '{path}' — aborting")
            return
        print(f"Loading {name}...")
        G = load_graph(path)
        graphs[name]   = G
        sigs[name]     = edge_signatures(G)
        adj_sets[name] = build_out_adj(G)
        print(f"  {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    g1, g2, g3 = FOCUS_TRIPLET

    print(f"\nGenerating candidate edge triples...")
    edge_triples = sample_edge_triples(
        [sigs[g1],    sigs[g2],    sigs[g3]],
        [graphs[g1],  graphs[g2],  graphs[g3]],
    )
    print(f"  {len(edge_triples)} candidate triples")

    if len(edge_triples) < 2:
        print("Too few candidates — check data files.")
        return

    print(f"\nBuilding compatibility graph (this takes ~5-8 minutes)...")
    CG = build_compat_graph(
        edge_triples,
        [adj_sets[g1], adj_sets[g2], adj_sets[g3]],
    )
    density = nx.density(CG)
    print(f"  {CG.number_of_nodes()} nodes, {CG.number_of_edges()} edges, density={density:.3f}")

    core = nx.k_core(CG, k=KCORE_K)
    print(f"  After {KCORE_K}-core pruning: {core.number_of_nodes()} nodes")

    if core.number_of_nodes() < 2:
        print("Too small after pruning.")
        return

    print(f"\nStarting deep clique search (stall limit: {STALL_MINUTES} min)...")
    clique_ids = find_max_clique_deep(
        core, edge_triples,
        [adj_sets[g1], adj_sets[g2], adj_sets[g3]],
        graphs, g1, g2, g3,
        stall_minutes=STALL_MINUTES
    )

    if not clique_ids:
        print("No clique found.")
        return

    print(f"\nFinal verification...")
    winning_edges = [edge_triples[i] for i in clique_ids]
    node_triples  = verified_node_triples(
        winning_edges,
        [adj_sets[g1], adj_sets[g2], adj_sets[g3]]
    )

    # FIX: guard against empty node_triples after verification
    if not node_triples:
        print("No valid node triples survived verification.")
        return

    score = circuit_score(node_triples, graphs[g1])

    nodes_g1  = [t[0] for t in node_triples]
    sub       = graphs[g1].subgraph(nodes_g1)
    wcc       = list(nx.weakly_connected_components(sub))

    # FIX: guard against empty wcc
    if not wcc:
        print("No weakly connected component found.")
        return

    largest   = max(wcc, key=len)
    final     = [t for t in node_triples if t[0] in largest]
    sub_final = graphs[g1].subgraph([t[0] for t in final])

    print(f"\n{'='*50}")
    print(f"RESULT: {g1} x {g2} x {g3}")
    print(f"  Matched neurons : {len(final)}")
    print(f"  Induced edges   : {sub_final.number_of_edges()}")
    print(f"  Score           : {score:.2f}")
    print(f"  Runtime         : {(time.time()-t_start)/60:.1f} min")
    print(f"{'='*50}\n")

    df = pd.DataFrame(final, columns=[g1, g2, g3])
    df.to_csv("network.csv", index=False)
    print("Saved final network.csv")


if __name__ == "__main__":
    main()