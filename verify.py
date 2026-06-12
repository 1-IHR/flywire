import pandas as pd
import networkx as nx

# verifying the highest matched neuron file triple found
FILES = {
    "BANC": "banc_626_edge_list.csv",
    "FAFB": "fafb_783_edge_list.csv",
    "MCNS": "mcns_0.9_edge_list.csv",
}

def load_graph(path):
    df = pd.read_csv(path).iloc[:, :2]
    df.columns = ["source", "target"]
    df = df[df["source"] != df["target"]]
    return nx.from_pandas_edgelist(df, "source", "target", create_using=nx.DiGraph())

print("Loading graphs...")
graphs = {name: load_graph(path) for name, path in FILES.items()}

df = pd.read_csv("network.csv")
nodes = {
    "BANC": df["BANC"].tolist(),
    "FAFB": df["FAFB"].tolist(),
    "MCNS": df["MCNS"].tolist(),
}
violations = 0
n = len(df)
for i in range(n):
    for j in range(n):
        if i == j:
            continue
        for name in ["BANC", "FAFB", "MCNS"]:
            pass  # checked below
        
        e_banc = graphs["BANC"].has_edge(nodes["BANC"][i], nodes["BANC"][j])
        e_fafb = graphs["FAFB"].has_edge(nodes["FAFB"][i], nodes["FAFB"][j])
        e_mcns = graphs["MCNS"].has_edge(nodes["MCNS"][i], nodes["MCNS"][j])
        
        if not (e_banc == e_fafb == e_mcns):
            violations += 1
            print(f"VIOLATION row {i} -> row {j}: "
                  f"BANC={e_banc} FAFB={e_fafb} MCNS={e_mcns}")

if violations == 0:
    print(f"VERIFIED: all {n*n} directed pairs are isomorphic")
else:
    print(f"FAILED: {violations} violations found")
