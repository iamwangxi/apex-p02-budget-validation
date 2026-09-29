Exhaustive finite validation of the six-point Budget lemmas in the genus-two curve-complex paper

This submission contributes a reproducible finite verification of Lemmas 9.11, 9.14, 9.15 and Corollary 9.16 in Apex Intelligence's [*The complex of curves pairwise intersecting at most once is contractible in genus two*](https://math.apexin.net/papers/curve-complex-genus-two.pdf), dated 11 September 2026. The target is the 35-page PDF with SHA-256 `d1eadd01f94e9af17ee9f5fb2ee1b05b326430f37296309fd9417340ea366fd4`.

The completed computation found 191 oriented hosts, 782,145 nonempty subsets and 11,504 purely bad witnesses representing 658 types. Every Budget assertion passed. The contribution is this exhaustive audit and reconstruction specification; the paper's lemmas and standard surface topology are not claimed as new results.

## 1. Precise claim and dependencies

Let $B$ be six marked points of an oriented sphere. A legal arc system is a finite collection of pairwise non-isotopic essential arcs with pairwise disjoint interiors, including loops. Isotopies fix the marks; endpoint rotations are allowed. A nonempty system $S$ is *purely bad* in Definition 8.2 precisely when each non-loop arc has another arc of $S$ with the same unordered endpoint pair; loops are automatically bad.

Types are taken up to orientation-preserving homeomorphism, allowing permutation of the six marked labels. Mirrors merge only if an orientation-preserving isomorphism exists. These are not the infinitely many fixed-mark isotopy classes. All tested properties are invariant under the stated equivalence, so the completeness inputs below ensure coverage of every fixed-label system.

Inputs are embedded representatives of disjoint systems, the usual essential-arc and empty-disc isotopy conventions, the independent bound $E\leq12$, and generalized triangulation extension. Their topological justification below makes the cutoff inspectable. Neither truncated enumeration nor program agreement independently proves these inputs; the observed ten-edge maximum cannot justify the cutoff at twelve.

Excluded are the spectral sequence, whole contractibility theorem, hyperelliptic dictionary, intersection formula, all arc-complex dimension statements and geometric Cone lemma. Experiment 1B was not performed: zero new exact intersection samples. The finite audit stops at Section 9's Budget assertions; it does not certify Section 10.

## 2. Why the finite host space suffices

The reduction uses no Budget conclusion. Generalized triangulations allow loops, repeated triangle vertices or sides and self-folding, as in [Hatcher, *Triangulations of Surfaces*, revised version, pp. 1–2](https://pi.math.cornell.edu/~hatcher/Papers/TriangSurf.pdf). These are standard topological inputs.

**Edge bound.** Include all six marks, even unused isolated marks, in a regular neighborhood $N$ of a legal $E$-edge system. The compact complementary pieces $R_i$ satisfy

$$
\chi(N)=6-E,\qquad \sum_i\chi(R_i)=E-4,\qquad \sum_i\ell_i=2E,
$$

where $\ell_i$ counts edge sides on the boundary, with repetitions. The pieces are planar; a non-disc piece has Euler characteristic at most zero. Every disc piece has at least three edge sides. Indeed, length zero would leave a sphere with only one isolated vertex; length one would bound an inessential loop. At length two, distinct non-loop edges form an empty bigon and are isotopic. Two same-basepoint loops bounding the mixed two-sided region give the same conclusion after normalizing that region to a disc at the basepoint. A loop and a non-loop cannot form a closed two-step boundary walk. The same non-loop edge traversed twice would be an isolated one-edge component whose disc complement leaves no place for the other marks; the two sides of a loop are separated on the sphere. Thus, if $D$ is the number of disc pieces,

$$
E-4\leq D\leq\frac{2E}{3},\qquad E\leq12.
$$

Empty-disc isotopy slides one side to the other, supported near the disc with endpoints fixed and rotations allowed. For same-basepoint loops normalize the mixed region at the basepoint, slide and reglue. This does not classify arbitrary loop isotopy classes by enclosed marked sets.

**Extension.** Starting from a nonempty legal system, add a legal disjoint arc whenever possible. The independent bound above makes this process terminate at a maximal system $T$. Any unused mark could be joined inside its complementary region to an existing boundary vertex; the new endpoint ensures a new isotopy class. If $T$ were disconnected, a complementary region incident to two components would admit an arc joining them, again a new class. Hence $T$ uses all six marks and is connected, so its complementary regions on the sphere are open discs.

Cut these discs open along their boundary walks, retaining repeated labels and sides. Empty monogons and digons are excluded by essentiality and distinctness; a face traversing a single edge twice would force the whole connected graph to be that edge. If a face has at least four sides, draw a diagonal between nonadjacent corners. Repeated labels may make the diagonal a loop, which is allowed. An allegedly inessential diagonal would cut off an empty disc whose original edges must themselves be inessential loops. An allegedly isotopic diagonal would form an empty bigon or, for same-basepoint loops, an empty normalized mixed disc with an existing edge. Any original edge inside that disc would be an inessential loop or parallel to its boundary edge. Legality excludes these possibilities; with no interior original edges, the two corners would have been adjacent. Thus the diagonal is legal, contrary to maximality. This is the local content of generalized triangulation extension, including repeated boundary labels and self-folding.

Consequently the host has

$$
V=6,\qquad 3F=2E,\qquad V-E+F=2,
\qquad E=12,\quad F=8.
$$

Conversely, a connected sphere map with six vertices and triangular faces is legal. If an edge or pair of edges bounded an empty monogon or digon, normalize it to a triangulated disc with boundary length $b\in\{1,2\}$ and no interior vertices. Euler characteristic and triangle-side counting would require $b-3<0$ interior edges. The normalized empty mixed region between same-basepoint loops is covered by the same count. Thus every host subset is legal, and every legal system appears as a subset of at least one host. This reduction uses none of Lemmas 9.11, 9.14, 9.15 or Corollary 9.16.

## 3. Generate all oriented hosts

The following specification permits reconstruction without any particular canonical-labeling library.

The dual host is a connected cubic sphere map with eight vertices and twelve edges, allowing loops, multiple edges and bridges. Choose a spanning tree, cut its five other edges into ten stems, and root at one stem. The oriented tree is then an ordered full binary tree with eight internal nodes. Its neighborhood and exterior are discs, so the cut edges are a noncrossing perfect matching of the ten stems in exterior-boundary order. Conversely every such tree and matching glues in the exterior disc to produce a cubic sphere map. Thus all target maps occur without relying on flip-graph connectivity.

Generate ordered trees recursively:

$$
\mathcal T_0=\{\text{empty}\},\qquad
\mathcal T_n=\bigcup_{i=0}^{n-1}
\{(L,R):L\in\mathcal T_i,\ R\in\mathcal T_{n-1-i}\}.
$$

At each internal node assign three darts in the cyclic order (parent, left, right), defining a permutation $\tau$. Pair parent/child slots along tree edges using $\alpha$; temporarily fix the root parent slot and every empty child slot. Read these ten stems in the unique orbit of $\tau\circ\alpha$. Generate all noncrossing matchings recursively by pairing position zero with each odd-numbered position and independently matching the two remaining even intervals. Replace the fixed stems by the matching pairs and set

$$
\sigma=\tau\circ\alpha,\qquad
\varphi=\sigma\circ\alpha=\tau.
$$

Here $\alpha$ pairs edges, $\sigma$ cycles are vertices and $\varphi$ cycles are triangular faces. Check these permutation identities, connectedness and six vertex cycles for every construction. There are

$$
C_8C_5=1430\cdot42=60{,}060
$$

raw constructions. Deduplicate by rooting at each of the 24 darts, breadth-first relabeling in the fixed successor order $[\alpha(d),\sigma(d)]$, and minimizing the concatenated relabeled permutation arrays. Equal codes are exactly oriented map isomorphisms: a rooted isomorphism preserves the traversal, and equal arrays exhibit the inverse correspondence. Never invert $\sigma$. The result is 191 hosts.

In each host order its twelve edge pairs by their smaller dart and traverse every nonempty bit mask from 1 through 4095. Test pure badness only by counting selected non-loop endpoint pairs; each must occur at least twice. Each selected loop forms its own object. Do not prune by used-mark count, gap count, freeness, cleanliness or any Budget conclusion.

## 4. Reconstruct regions and test the assertions

For any retained edge set $Q$, compute $R(Q)$ as follows. Begin with the eight host triangles and merge across every edge outside $Q$, including self-joins. Each component is an open complementary region. Represent it by three disjoint kinds of atoms:

- its open triangles;
- the open edges outside $Q$ incident to those triangles;
- the marked vertices unused by $Q$ whose incident triangles belong to that component.

All incident sectors of an unused vertex merge, since all its incident edges are outside $Q$. A used vertex is on a region's boundary exactly when a selected dart at that vertex has the region on one of its sides. Restrict each vertex cycle of $\sigma$ to retained darts, giving $\sigma_Q$. The cycles of $\sigma_Q\circ\alpha$ are boundary walks; attach each to the component of its adjacent host triangle. Retain every boundary walk of each region. A region need not be a disc when $Q$ is disconnected. The interior marked-point count $k$ is the number of vertex atoms.

Retaining all boundary groups and unused marks preserves disconnected nesting. A slit edge can change an open region without changing its triangles, so all equality and disjointness tests use the complete three-kind atom sets.

Legality is also checked directly on hosts and rechecked on retained representatives. A loop must have another mark on each side in $R(\{e\})$. Two non-loop edges with the same endpoints must have marks on both sides in $R(\{e,f\})$. Two loops at the same basepoint may not have an unmarked mixed digon whose boundary uses one side of each. These are essentiality and empty-disc tests independent of the Budget assertions; host subsets inherit legality.

For a pure system $S$, the objects are single loops and entire repeated non-loop endpoint families. The gaps of an object $O$ are the regions $R(O)$. Another object $O'$ is contained in the closure of a gap $g$ if and only if every open edge atom of $O'$ belongs to $g$; its endpoints then belong to the closure automatically. A gap is free if no other object satisfies this test. This computes the definition directly, without assuming Lemma 9.8. In counting $k(g)$, include all marks in the gap, including any used by other objects.

For each gap, compare its full atom set with each region of $R(S)$ to decide whether it is a face of the whole system. Let $X(g)$ be its actual boundary-mark set and let $\mathcal F$ be the repeated non-loop endpoint pairs of $S$. Test cleanliness by checking that every distinct pair in $X(g)$ belongs to $\mathcal F$; do not assume the boundary has at most two marks. A good face must simultaneously be a whole-system face, a free gap, clean, and have $k(g)\in\{1,2\}$.

The recorded predicates are:

1. Lemma 9.11: two free gaps have disjoint complete atom sets, and every free gap equals a whole-system face.
2. Lemma 9.14: every free gap has $k(g)\geq1$.
3. Lemma 9.15: at least one good face exists.
4. Corollary 9.16: the actual number $V'$ of marks used by $S$ satisfies $V'\leq4$.
5. Auxiliary Corollary 9.13: every free gap is clean, checked separately for diagnostic purposes.

## 5. Exact type deduplication and independent checks

For each subset construct a four-colored directed graph with six mark nodes, selected dart nodes, selected edge nodes and complementary-region nodes. Each dart points to its endpoint mark, its edge, its side-region (the component of its host $\varphi$-face), and the next selected dart at its vertex. Each unused mark points to its containing region. The four target colors distinguish the four dart relations.

Define a canonical certificate as the lexicographically least adjacency matrix over all permutations within each color, prefixed by the four color sizes. Brute-force canonicalization is sufficient in principle; the implementation uses `pynauty==2.8.8.1`. Edge membership recovers $\alpha$, dart successors recover the oriented rotation, and region incidence groups all boundary walks and locates unused marks. These data determine the regular neighborhood and its genus-zero complementary surfaces, hence the oriented embedding up to the stated equivalence. In particular, disconnected components are not classified merely by an unordered list of their separate rotations.

Full certificates decide equality; SHA-256 only labels records. Different canonical-labeling implementations can produce different bytes and identifiers for the same types, predicates and counts.

An independent Whitehead-move closure from an explicit octahedron made 1,924 transitions. Separate canonicalization confirmed the same 191 hosts and empty set differences. The tree/stem proof supplies coverage; list agreement alone does not.

The main predicates use union-find and half-edge boundary walks; the separate implementation uses dual-graph BFS and its own atom/object calculations. They share definitions and encoding conventions, not region or predicate functions. Before deduplication a supplementary audit checked all 11,504 pure witnesses, comparing ten fields: combined and separate 9.11 predicates, 9.13, 9.14, 9.15, 9.16, free-gap count, good-face count and $V'$. All 115,040 comparisons agreed; every conclusion passed.

The audit also checked atom conservation, Euler relations, 658 full record reconstructions, 658 deterministic dart relabelings and five hand-built positive/negative legality examples. It calls the existing predicates and is not a third independent implementation or host generator.

**Cross-model reimplementation and host census.** After this text was frozen, Claude, a different model family, reviewed the reduction and wrote two standard-library scripts without importing any module above. The first checks the host list independently of every generator: the 191 hosts are valid, pairwise non-isomorphic oriented triangulations, and

$$
\sum_{h}\frac{24}{|\mathrm{Aut}^+(h)|}=4096,
$$

where $\mathrm{Aut}^+(h)$ is the group of orientation-preserving map automorphisms, computed by rooted relabeling. The right side is the number of rooted planar cubic maps with eight vertices (OEIS A002005, $a(4)$). Every valid host contributes a positive amount and all oriented hosts together sum to $a(4)$, so none is missing. A brute-force count of rooted cubic sphere maps with two and four vertices, allowing loops and multiple edges, reproduces $a(1)=4$ and $a(2)=32$, confirming that the sequence counts exactly these duals.

The second script is a third predicate implementation written directly from Definitions 8.2 and 9.1–9.4. On all 782,145 subsets it reproduces the 11,504 purely bad witnesses, their edge-count distribution $(504,1218,2121,2607,2375,1599,765,255,54,6,0,0)$ and used-mark distribution $(1310,5916,3718,560,0,0)$, with zero failures of 9.11, 9.13, 9.14, 9.15 and 9.16. It rechecks host legality directly: 1,465 loop and repeated-pair tests find no empty monogon or digon. Controls show that the predicates discriminate: 459 witnesses have no good face with $k=1$, 560 use four marks, and 7,515 lack three pairwise disjoint free gaps. It shares only the host data and the paper's definitions with the implementations above.

## 6. Results and evidential limits

| Quantity | Completed result |
|---|---:|
| Tree/stem constructions | 60,060 |
| Oriented hosts | 191 |
| Nonempty host subsets | 782,145 |
| Rejected solely as not purely bad | 770,641 |
| Purely bad host witnesses | 11,504 |
| Distinct oriented types | 658 |
| Failed Budget predicates | 0 |

The type counts by edge count $E=1,\ldots,12$ are

$$
(2,10,26,69,114,164,142,95,30,6,0,0).
$$

The type counts by used-mark count $V'=1,\ldots,6$ are

$$
(32,238,303,85,0,0).
$$

The $V'=5,6$ ranges contained 295,711 and 165,188 candidates: all underwent the pure-badness test, none passed, and none was pruned using Corollary 9.16. Of the 658 types, 170 are disconnected with multiple-boundary regions, 647 contain loops and 464 contain multiple same-basepoint loops. Counts for one through four components are 488, 151, 18 and 1. The observed ten-edge maximum applies only to purely bad types.

Submission text version: **v1.2**. Repository snapshot: [apex-p02-budget-validation](https://github.com/iamwangxi/apex-p02-budget-validation), tag **v1.0**. The repository contains the code, certificates and two cross-model scripts with their recorded output. The certificates include all 191 hosts, one reconstructible record per type, the full 72-cell edge-count/used-mark table, comparison results and file hashes. The type-record SHA-256 is `bc1a30fe32b3f357a3c94688e69e3a36979c60cd103017e0a4c1dd3f30244b4a`; the full strata CSV SHA-256 is `11da4b46f89c08e1e614eefd87878737d30cde9d2bfb17e2c066d34dac809bde`. These hashes identify the reported artifacts. The algorithm above supplies reconstruction independently of repository availability. The accepted packaged implementation was fully rerun on 29 September 2026; preparation of this focused submission preserves its source and scientific certificate bytes.

Conditional on the geometric reduction, the audit is exhaustive for these Budget assertions, including disconnected and degenerate cases. Standard topology, AI mathematical review, separate implementations and executions are distinct evidence, not formal proof or human expert certification.

AI disclosure: GPT-6 Astra and Claude Opus 5.5 assisted the broader mathematical drafting and checking. GPT-based agents produced and reviewed the finite reduction, code and audits. OpenAI Codex prepared the earlier focused text, which a fresh GPT context reviewed; Claude reviewed v1.1 and added the cross-model reimplementation and host census above. For v1.2, Codex updated the repository reference and version information. A new GPT session reviewed the v1.2 changes and their affected context; this was not a new review of the geometric inputs or computation. No human expert review, proof-assistant verification or new intersection experiment is claimed.
