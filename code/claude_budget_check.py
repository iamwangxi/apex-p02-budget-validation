#!/usr/bin/env python3
"""Third, separately written implementation of the Budget predicates (standard library only).

Written by Claude, a different AI model family, directly from Definitions 8.2 and 9.1-9.4 of the
paper, without importing the package's other modules. For every nonempty edge subset of every host
it tests pure badness and, for purely bad systems S:

  Lemma 9.11  two free gaps with disjoint atom sets exist, and every free gap is a face of Gamma_S;
  Lemma 9.14  every free gap contains at least one mark;
  Lemma 9.15  some gap is simultaneously a face of Gamma_S, free, clean, with k in {1, 2};
  Cor. 9.16   at most four marks are used by S;
  Cor. 9.13   (auxiliary) every free gap is clean.

Regions of the complement of an edge set Q are unions of open host triangles merged across edges
outside Q, recorded by three atom kinds: triangles, open edges outside Q, and marks unused by Q.
Another object lies in the closure of a gap exactly when all its open edges are edge atoms of the gap.
The boundary marks of a gap of an object O are the marks of O having a corner in the gap; the corner
between darts d and sigma(d) lies in the face of sigma(d).

It also checks legality of every host (loops and repeated-endpoint pairs bound no empty monogon or
digon) and reports sensitivity controls: counts of pure witnesses for which a strengthened or altered
statement would fail, showing that the predicates are not vacuous.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def orbit_index(perm):
    index, count = [-1] * len(perm), 0
    for start in range(len(perm)):
        if index[start] >= 0:
            continue
        dart = start
        while index[dart] < 0:
            index[dart] = count
            dart = perm[dart]
        count += 1
    return index, count


class Host:
    def __init__(self, alpha, sigma):
        n = len(alpha)
        phi = [sigma[alpha[d]] for d in range(n)]
        vertex, self.marks = orbit_index(sigma)
        face, self.faces = orbit_index(phi)
        reps = sorted({min(d, alpha[d]) for d in range(n)})
        self.ends = [(vertex[d], vertex[alpha[d]]) for d in reps]
        self.sides = [(face[d], face[alpha[d]]) for d in reps]
        self.corners = [[face[sigma[d]] for d in range(n) if vertex[d] == v] for v in range(self.marks)]

    def regions(self, selected):
        """Atom triples of the complementary regions of the selected edge set, and the used marks."""
        parent = list(range(self.faces))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for edge, (a, b) in enumerate(self.sides):
            if edge not in selected:
                parent[find(a)] = find(b)
        used = {v for edge in selected for v in self.ends[edge]}
        atoms = {}
        for f in range(self.faces):
            atoms.setdefault(find(f), (set(), set(), set()))[0].add(f)
        for edge, (a, _) in enumerate(self.sides):
            if edge not in selected:
                atoms[find(a)][1].add(edge)
        for v in range(self.marks):
            if v not in used:
                atoms[find(self.corners[v][0])][2].add(v)
        frozen = [tuple(frozenset(part) for part in triple) for triple in atoms.values()]
        return frozen, used


def disjoint(a, b):
    return not (a[0] & b[0]) and not (a[1] & b[1]) and not (a[2] & b[2])


def check_system(host, edges):
    """Return None if S is not purely bad, else a dict of predicate values and diagnostics."""
    loops = [e for e in edges if host.ends[e][0] == host.ends[e][1]]
    families = {}
    for e in edges:
        if e not in loops:
            families.setdefault(frozenset(host.ends[e]), []).append(e)
    if any(len(members) < 2 for members in families.values()):
        return None
    objects = [[e] for e in loops] + list(families.values())
    repeated_pairs = set(families)
    whole, used_by_s = host.regions(set(edges))
    faces_of_s = set(whole)

    def clean(marks):
        ordered = sorted(marks)
        return all(frozenset((ordered[i], ordered[j])) in repeated_pairs
                   for i in range(len(ordered)) for j in range(i + 1, len(ordered)))

    free = []
    for index, obj in enumerate(objects):
        gaps, used_by_o = host.regions(set(obj))
        for atoms in gaps:
            others_inside = any(all(e in atoms[1] for e in objects[j])
                                for j in range(len(objects)) if j != index)
            if others_inside:
                continue
            boundary = {v for v in used_by_o if any(c in atoms[0] for c in host.corners[v])}
            free.append((atoms, len(atoms[2]), boundary))

    def good(gap, allowed):
        return gap[0] in faces_of_s and clean(gap[2]) and gap[1] in allowed

    return {
        "9.11": any(disjoint(a[0], b[0]) for i, a in enumerate(free) for b in free[i + 1:])
        and all(g[0] in faces_of_s for g in free),
        "9.13": all(clean(g[2]) for g in free),
        "9.14": all(g[1] >= 1 for g in free),
        "9.15": any(good(g, (1, 2)) for g in free),
        "9.16": len(used_by_s) <= 4,
        "used_marks": len(used_by_s),
        "control_good_face_k1_missing": not any(good(g, (1,)) for g in free),
        "control_three_disjoint_free_gaps_missing": not any(
            disjoint(a[0], b[0]) and disjoint(a[0], c[0]) and disjoint(b[0], c[0])
            for i, a in enumerate(free) for j, b in enumerate(free[i + 1:], i + 1) for c in free[j + 1:]),
        "control_free_gap_with_k_at_least_3": any(g[1] >= 3 for g in free),
        "control_free_gap_with_more_than_2_boundary_marks": any(len(g[2]) > 2 for g in free),
    }


def legality_violations(host):
    checks = violations = 0
    m = len(host.ends)
    for e in range(m):
        a, b = host.ends[e]
        if a == b:
            regions, _ = host.regions({e})
            checks += 1
            violations += any(len(r[2]) == 0 for r in regions)
        for f in range(e + 1, m):
            same_pair = frozenset(host.ends[f]) == frozenset((a, b))
            same_kind = (host.ends[f][0] == host.ends[f][1]) == (a == b)
            if same_pair and same_kind:
                regions, _ = host.regions({e, f})
                checks += 1
                violations += any(len(r[2]) == 0 for r in regions)
    return checks, violations


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hosts", default="certificates/hosts.json", type=Path)
    args = parser.parse_args()
    hosts = json.loads(args.hosts.read_text())["hosts"]
    failures, controls = Counter(), Counter()
    by_edges, by_marks = Counter(), Counter()
    subsets = pure = legality_checks = legality_bad = 0
    for record in hosts:
        host = Host(record["alpha"], record["sigma"])
        checks, bad = legality_violations(host)
        legality_checks += checks
        legality_bad += bad
        m = len(host.ends)
        for mask in range(1, 1 << m):
            subsets += 1
            edges = [e for e in range(m) if mask >> e & 1]
            result = check_system(host, edges)
            if result is None:
                continue
            pure += 1
            by_edges[len(edges)] += 1
            by_marks[result["used_marks"]] += 1
            for key in ("9.11", "9.13", "9.14", "9.15", "9.16"):
                failures[key] += not result[key]
            for key, value in result.items():
                if key.startswith("control_"):
                    controls[key] += bool(value)
    print(f"hosts={len(hosts)} subsets={subsets} purely_bad_witnesses={pure}")
    print("witnesses_by_edge_count_1_to_12=" + ",".join(str(by_edges[e]) for e in range(1, 13)))
    print("witnesses_by_used_marks_1_to_6=" + ",".join(str(by_marks[v]) for v in range(1, 7)))
    print("predicate_failures=" + json.dumps({k: failures[k] for k in ("9.11", "9.13", "9.14", "9.15", "9.16")}))
    print(f"host_legality_checks={legality_checks} violations={legality_bad}")
    print("sensitivity_controls=" + json.dumps(dict(sorted(controls.items()))))
    passed = sum(failures.values()) == 0 and legality_bad == 0 and pure > 0
    print(f"passed={passed}")
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
