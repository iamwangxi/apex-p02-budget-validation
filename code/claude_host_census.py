#!/usr/bin/env python3
"""Generator-independent completeness check of the 191 oriented hosts (standard library only).

Written separately (by Claude, a different AI model family) without importing the package's
other modules. Each host is a triangulation of the six-marked sphere given by dart permutations
alpha (edge reversal) and sigma (vertex rotation); its faces are the cycles of sigma*alpha.
Its dual is a connected cubic sphere map with eight vertices; loops and multiple edges allowed.

Check: every host is a valid connected oriented map with 6 vertices, 12 edges and 8 triangular
faces; the hosts are pairwise non-isomorphic; and the automorphism-weighted count
    sum over hosts of 24 / |Aut+(host)|
equals the number of rooted planar cubic maps with eight vertices, OEIS A002005 a(4) = 4096,
a(n) = 2^(2n+1) (3n)!! / ((n+2)! n!!). Since each valid host contributes a positive amount and
the full set of oriented hosts sums to a(4), a list of distinct valid hosts reaching a(4) is complete.

With --small-cases, a brute-force enumeration of rooted planar cubic maps with 2 and 4 vertices
(loops and multiple edges allowed) reproduces a(1) = 4 and a(2) = 32, confirming that the formula
counts exactly this family.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


def cycles(perm):
    seen, out = set(), []
    for start in range(len(perm)):
        if start in seen:
            continue
        cycle, dart = [], start
        while dart not in seen:
            seen.add(dart)
            cycle.append(dart)
            dart = perm[dart]
        out.append(cycle)
    return out


def rooted_code(alpha, sigma, root):
    """Breadth-first relabeling from a root dart; None if the map is disconnected."""
    label, order, i = {root: 0}, [root], 0
    while i < len(order):
        dart = order[i]
        i += 1
        for nxt in (alpha[dart], sigma[dart]):
            if nxt not in label:
                label[nxt] = len(order)
                order.append(nxt)
    if len(order) != len(alpha):
        return None
    return tuple(label[alpha[d]] for d in order) + tuple(label[sigma[d]] for d in order)


def double_factorial(n):
    result = 1
    while n > 1:
        result *= n
        n -= 2
    return result


def a002005(n):
    return 2 ** (2 * n + 1) * double_factorial(3 * n) // (math.factorial(n + 2) * double_factorial(n))


def census(hosts):
    total, codes, invalid, aut_sizes = Fraction(0), set(), 0, {}
    for host in hosts:
        alpha, sigma = host["alpha"], host["sigma"]
        n = len(alpha)
        valid = n == 24 and all(alpha[alpha[d]] == d != alpha[d] for d in range(n))
        valid = valid and sorted(sigma) == list(range(n))
        if valid:
            faces = cycles([sigma[alpha[d]] for d in range(n)])
            valid = len(cycles(sigma)) == 6 and len(faces) == 8 and all(len(f) == 3 for f in faces)
        codes_by_root = [rooted_code(alpha, sigma, r) for r in range(n)] if valid else []
        if not valid or any(code is None for code in codes_by_root):
            invalid += 1
            continue
        aut = sum(1 for code in codes_by_root if code == codes_by_root[0])
        aut_sizes[aut] = aut_sizes.get(aut, 0) + 1
        codes.add(min(codes_by_root))
        total += Fraction(n, aut)
    return total, len(codes), invalid, dict(sorted(aut_sizes.items()))


def three_cycle_permutations(n):
    def build(remaining):
        if not remaining:
            yield []
            return
        first = remaining[0]
        for b, c in itertools.permutations(remaining[1:], 2):
            rest = [x for x in remaining if x not in (first, b, c)]
            for tail in build(rest):
                yield [(first, b, c)] + tail
    seen = set()
    for cycle_list in build(list(range(n))):
        perm = [0] * n
        for a, b, c in cycle_list:
            perm[a], perm[b], perm[c] = b, c, a
        key = tuple(perm)
        if key not in seen:
            seen.add(key)
            yield perm


def rooted_planar_cubic(vertices):
    darts = 3 * vertices
    alpha = [d ^ 1 for d in range(darts)]
    count = 0
    for sigma in three_cycle_permutations(darts):
        if rooted_code(alpha, sigma, 0) is None:
            continue
        faces = len(cycles([sigma[alpha[d]] for d in range(darts)]))
        if vertices - darts // 2 + faces == 2:
            count += 1
    # labeled maps with a fixed alpha, times the number of alphas, divided by (darts-1)!
    return count * double_factorial(darts - 1) // math.factorial(darts - 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hosts", default="certificates/hosts.json", type=Path)
    parser.add_argument("--small-cases", action="store_true", help="brute-force a(1) and a(2)")
    args = parser.parse_args()
    hosts = json.loads(args.hosts.read_text())["hosts"]
    total, distinct, invalid, aut_sizes = census(hosts)
    expected = a002005(4)
    print(f"hosts={len(hosts)} invalid={invalid} distinct_oriented_codes={distinct}")
    print(f"automorphism_group_sizes={aut_sizes}")
    print(f"sum_24_over_aut={total} expected_A002005_a4={expected} match={total == expected}")
    ok = invalid == 0 and distinct == len(hosts) and total == expected
    if args.small_cases:
        for n in (1, 2):
            found = rooted_planar_cubic(2 * n)
            print(f"brute_force_rooted_planar_cubic_maps vertices={2 * n} count={found} formula={a002005(n)}")
            ok = ok and found == a002005(n)
    print(f"passed={ok}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
