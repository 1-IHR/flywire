# The Elementary Motion Detector in the Female *Drosophila* Optic Lobe: Circuit Structure and Biological Significance from the FAFB

**Ibtisam Haseeb** &nbsp;·&nbsp; ibtisam.haseeb@tamu.edu &nbsp;·&nbsp; 

---

## Abstract

The *Drosophila* Elementary Motion Detector (EMD) implements the Hassenstein-Reichardt correlator for visual motion computation. T4 neurons respond to moving ON (bright edge) and T5 neurons to OFF (dark edge) stimuli, each comprising four subtypes tuned to the four cardinal directions of motion [1,2]. Silencing both T4 and T5 completely abolishes direction-selective responses in lobula plate tangential cells and eliminates all optomotor behavioral responses [2]. The GABAergic hub CT1 spans medulla M10 and lobula Lo1, providing approximately 15 inhibitory synapses per column to T4 and approximately 60 to T5, and is the sole inhibitory columnar input to T5 [3,4]. CT1 receives excitatory input from Tm9 and Tm1 and implements null-direction suppression via a disynaptic mechanism [7]. Maximum common induced subgraph (MCIS) search across five *Drosophila* connectome datasets recovers a 45-neuron, 84-directed-edge circuit in FAFB, verified by exhaustive pairwise isomorphism check (2,025 ordered pairs, 0 violations). FlyWire Codex identifies all 45 neurons as this optic lobe EMD circuit. Three neurons are left hemisphere (CT1, cMLLP02, DNc02); 42 are right hemisphere [5,6].

---

## Circuit Composition (FlyWire Codex, FAFB v783)

| Layer | Cell types | n | NT |
|---|---|:---:|---|
| Input | Tm9×8, Tm1×2, Tm2×1 | 11 | ACH |
| Columnar | Mi1×2 | 2 | ACH |
| ON detectors (a-c) | T4a×6, T4b×5, T4c×3 | 14 | ACH |
| ON detectors (d) \* | T4d×2 | 2 | GLUT |
| OFF detectors \*\* | T5a×4, T5b×2, T5c×5, T5d×1 | 12 | ACH |
| Hub (left hemisphere) | CT1×1 | 1 | GABA |
| Modulator (right hemisphere) | OA-AL2i2×1 | 1 | OCT |
| Modulator (left hemisphere) | cMLLP02×1 | 1 | ACH |
| Output (left hemisphere) \*\*\* | DNc02×1 | 1 | DA |
| **Total** | | **45** | **3L / 42R** |

\* T4d is glutamatergic per FlyWire Codex annotation; T4a, T4b, T4c are cholinergic.  
\*\* One T5c (LO.LOP.3810) has no NT annotation in Codex.  
\*\*\* DNc02 is additionally labeled "putative SIFamide" in Codex.  
Source: FlyWire Codex, FAFB v783 [5,6].

---

## Visualizations

![Figure 1. Network graph of the 45-neuron EMD circuit in FAFB (FlyWire Codex). CT1 (L) is the sole GABAergic hub, connecting cross-midline to all T4 and T5 subtypes. Edge weights represent synapse counts. Node color: ACH (blue), GABA/CT1 (gold), OCT (purple), GLUT (green), DA (brown). Source: FlyWire Codex, FAFB [5,6].](network.png)

**Figure 1.** Network graph of the 45-neuron EMD circuit in FAFB (FlyWire Codex). `CT1 (L)` is the sole GABAergic hub, connecting cross-midline to all T4 and T5 subtypes. Edge weights represent synapse counts. Node color: ACH (blue), GABA/CT1 (gold), OCT (purple), GLUT (green), DA (brown). Source: FlyWire Codex, FAFB [5,6].

![Figure 2. 3D skeleton rendering of all 45 neurons in FAFB (FlyWire Codex). The optic lobe columnar array occupies the right neuropil region; the descending DNc02 projection extends toward the central brain and ventral nerve cord. Source: FlyWire Codex, FAFB [5,6].](3d.png)

**Figure 2.** 3D skeleton rendering of all 45 neurons in FAFB (FlyWire Codex). The optic lobe columnar array occupies the right neuropil region; the descending `DNc02` projection extends toward the central brain and ventral nerve cord. Source: FlyWire Codex, FAFB [5,6].

---

## What This Circuit Computes

T4 and T5 cells are the first direction-selective neurons in the fly visual pathway, responding respectively to ON (bright edge) and OFF (dark edge) motion stimuli through parallel streams originating from lamina neurons L1 and L2 [1,2]. Each class comprises four subtypes (a-d) tuned to front-to-back, back-to-front, upward, and downward motion, projecting to corresponding layers of the lobula plate [2]. All four subtypes of both T4 and T5 are represented in this circuit, providing complete 360-degree directional coverage.

Direction selectivity in all four subtypes arises through two mechanisms operating simultaneously on opposing sides of the receptive field: preferred-direction enhancement and null-direction suppression [1]. When both T4 and T5 are genetically silenced, lobula plate tangential cells lose all direction-selective responses and flies fail all optomotor behavioral tasks [2]. The columnar interneuron Mi1 is absolutely essential for ON-pathway computation; blocking Mi1 abolishes T4 responses under all tested conditions [1]. The transmedullary neurons Tm1, Tm2, and Tm9 relay signals to T5 dendrites in lobula stratum Lo1 [4].

---

## CT1: The Inhibitory Hub

CT1 is a single giant GABAergic tangential neuron whose neurites span medulla stratum M10 and lobula stratum Lo1, forming one synaptic module per column across both neuropils [3]. CT1 is GAD1-immunopositive and provides approximately 15 inhibitory synapses per column to T4 dendrites and approximately 60 per column to T5 dendrites, with equal innervation across all four directional subtypes [3,4]. CT1 is the sole GABAergic columnar input to T5 dendrites, making it the dominant source of inhibition within the direction-selective layer [4].

Within each column, CT1 receives excitatory input from Tm9 (23.3 +/- 2.6 synapses per terminal) and Tm1 (7.0 +/- 3.1 synapses per terminal) in Lo1, and provides recurrent output back to Tm9 (14.9 +/- 3.2 synapses per terminal) [4]. Ablating CT1 or knocking down the GABA receptor subunit Rdl significantly broadens directional tuning in T5 cells, confirming that CT1 mediates null-direction suppression through a Tm9/Tm1-CT1-T5 disynaptic mechanism [7]. Three neurons in this circuit are left hemisphere (CT1, cMLLP02, DNc02); the remaining 42 are right hemisphere. CT1's cross-midline architecture enables pan-columnar inhibition across the entire contralateral optic lobe [5,6].

---

## Hypothesis

CT1's structural centrality within the MCIS-recovered circuit reflects its functional role as the sole wide-field GABAergic neuron providing inhibitory input to all direction-selective subtypes simultaneously. By receiving excitatory input from Tm9 and Tm1 and delivering sign-inverted GABA signals onto T5, CT1 converts cholinergic transmedullary inputs into null-direction suppression through a disynaptic microcircuit [7]. This cross-midline, pan-columnar hub topology generates a maximally distinctive graph-structural signature, which likely explains why the EMD circuit is consistently recovered as the largest maximum common induced subgraph across all five connectome datasets without any biological labels. The conservation of this circuit architecture across BANC, FAFB, and MCNS datasets suggests that the CT1-organized inhibitory motif represents a structurally invariant feature of the fly visual system.

---

## References

1. Haag J, Mishra A, Borst A. (2017). Towards a comprehensive account of directed motion detection in insects. *eLife* 6:e29044. https://doi.org/10.7554/eLife.29044
2. Maisak MS, et al. (2013). A directional tuning map of *Drosophila* elementary motion detectors. *Nature* 500:212-216. https://doi.org/10.1038/nature12320
3. Takemura S, et al. (2017). The comprehensive connectome of a neural substrate for 'ON' motion detection in *Drosophila*. *eLife* 6:e24394. https://doi.org/10.7554/eLife.24394
4. Shinomiya K, et al. (2019). Comparisons between the ON- and OFF-edge motion pathways in the *Drosophila* brain. *eLife* 8:e40025. https://doi.org/10.7554/eLife.40025
5. Schlegel P, et al. (2024). Whole-brain annotation and multi-connectome cell typing of *Drosophila*. *Nature* 634:139-152. https://doi.org/10.1038/s41586-024-07686-5
6. Dorkenwald S, et al. (2024). Neuronal wiring diagram of an adult brain. *Nature* 634:124-138. https://doi.org/10.1038/s41586-024-07558-y
7. Braun A, Borst A, Meier M. (2023). Disynaptic inhibition shapes tuning of OFF-motion detectors in *Drosophila*. *Current Biology* 33:2260-2269. https://doi.org/10.1016/j.cub.2023.05.007
