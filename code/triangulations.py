#!/usr/bin/env python3
"""Six-marked spherical triangulations from plane trivalent trees and stem matchings.

Uses only the standard library. See proof/expanded-validation.md for completeness.
alpha reverses darts; sigma is the oriented vertex rotation; faces use sigma o alpha.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import json
from math import comb
from pathlib import Path
from time import perf_counter


def cycles(perm):
    """Return permutation orbits, starting each at its smallest element."""
    seen = set()
    result = []
    for first in range(len(perm)):
        if first in seen:
            continue
        orbit = []
        dart = first
        while dart not in seen:
            seen.add(dart)
            orbit.append(dart)
            dart = perm[dart]
        if dart != first:
            raise ValueError("Input is not a permutation")
        result.append(tuple(orbit))
    return tuple(result)


def canonical(alpha, sigma):
    """Canonical unrooted encoding of a connected oriented map; do not merge mirrors."""
    size = len(alpha)
    if len(sigma) != size:
        raise ValueError("alpha and sigma have different lengths")
    best = None
    for root in range(size):
        old_order = [root]
        new_id = [-1] * size
        new_id[root] = 0
        for dart in old_order:
            for successor in (alpha[dart], sigma[dart]):
                if new_id[successor] < 0:
                    new_id[successor] = len(old_order)
                    old_order.append(successor)
        if len(old_order) != size:
            raise ValueError("canonical requires a connected map")
        candidate = (
            tuple(new_id[alpha[dart]] for dart in old_order),
            tuple(new_id[sigma[dart]] for dart in old_order),
        )
        if best is None or candidate < best:
            best = candidate
    return best


@lru_cache(maxsize=None)
def binary_trees(n):
    """All ordered full binary trees with n internal nodes; None is a leaf."""
    if n < 0:
        return ()
    if n == 0:
        return (None,)
    return tuple(
        (left, right)
        for left_size in range(n)
        for left in binary_trees(left_size)
        for right in binary_trees(n - 1 - left_size)
    )


@lru_cache(maxsize=None)
def noncrossing_matchings(size):
    """All noncrossing perfect matchings of size cyclically ordered points."""
    if size == 0:
        return ((),)
    if size < 0 or size % 2:
        return ()
    result = []
    for partner in range(1, size, 2):
        for inner in noncrossing_matchings(partner - 1):
            for outer in noncrossing_matchings(size - partner - 1):
                result.append(
                    ((0, partner),)
                    + tuple((a + 1, b + 1) for a, b in inner)
                    + tuple(
                        (a + partner + 1, b + partner + 1)
                        for a, b in outer
                    )
                )
    return tuple(result)


def tree_with_stems(tree):
    """Return dual tau, tree alpha (stems temporarily fixed), and boundary stem order."""
    tau = []
    alpha = []

    def visit(node):
        first = len(tau)
        tau.extend((first + 1, first + 2, first))
        alpha.extend((first, first + 1, first + 2))
        for offset, child in enumerate(node, start=1):
            if child is not None:
                child_parent = visit(child)
                alpha[first + offset] = child_parent
                alpha[child_parent] = first + offset
        return first

    if tree is None:
        raise ValueError("At least one trivalent node is required")
    visit(tree)
    contour = cycles(tuple(tau[alpha[dart]] for dart in range(len(tau))))
    if len(contour) != 1:
        raise AssertionError("A regular neighborhood of the embedded tree must have one boundary component")
    stems = tuple(dart for dart in contour[0] if alpha[dart] == dart)
    return tuple(tau), tuple(alpha), stems


def validate_map(alpha, sigma, n=8):
    """Check triangulation inputs, without assuming any assertion under test."""
    size = 3 * n
    if len(alpha) != size or len(sigma) != size:
        raise AssertionError("Incorrect dart count")
    if any(alpha[d] == d or alpha[alpha[d]] != d for d in range(size)):
        raise AssertionError("alpha is not a fixed-point-free involution")
    if sorted(sigma) != list(range(size)):
        raise AssertionError("sigma is not a permutation")
    face_cycles = cycles(tuple(sigma[alpha[d]] for d in range(size)))
    if len(face_cycles) != n or any(len(face) != 3 for face in face_cycles):
        raise AssertionError("Triangular-face condition failed")
    vertices = cycles(sigma)
    if len(vertices) - size // 2 + len(face_cycles) != 2:
        raise AssertionError("Euler characteristic is not 2")
    reached = {0}
    pending = [0]
    for dart in pending:
        for adjacent in (alpha[dart], sigma[dart]):
            if adjacent not in reached:
                reached.add(adjacent)
                pending.append(adjacent)
    if len(reached) != size:
        raise AssertionError("Triangulation is disconnected")


def iter_constructions(n=8):
    """Generate raw hosts; n is an even number of trivalent dual nodes."""
    if n < 2 or n % 2:
        raise ValueError("The number of trivalent nodes must be positive and even")
    matchings = noncrossing_matchings(n + 2)
    for tree in binary_trees(n):
        tau, tree_alpha, stems = tree_with_stems(tree)
        if len(stems) != n + 2:
            raise AssertionError("Incorrect stem count")
        for matching in matchings:
            alpha = list(tree_alpha)
            for a, b in matching:
                u, v = stems[a], stems[b]
                alpha[u], alpha[v] = v, u
            alpha = tuple(alpha)
            sigma = tuple(tau[alpha[d]] for d in range(3 * n))
            yield alpha, sigma


def generate_hosts(n=8, limit=None):
    """Return sorted canonical hosts and audit counts; limit selects a diagnostic prefix."""
    start = perf_counter()
    unique = set()
    raw_count = 0
    for alpha, sigma in iter_constructions(n):
        if limit is not None and raw_count >= limit:
            break
        validate_map(alpha, sigma, n)
        unique.add(canonical(alpha, sigma))
        raw_count += 1
    tree_count = comb(2 * n, n) // (n + 1)
    pairs = (n + 2) // 2
    matching_count = comb(2 * pairs, pairs) // (pairs + 1)
    stats = {
        "dual_vertices": n,
        "primal_vertices": n // 2 + 2,
        "edges": 3 * n // 2,
        "ordered_binary_tree_count": tree_count,
        "noncrossing_matching_count": matching_count,
        "expected_raw_constructions": tree_count * matching_count,
        "processed_raw_constructions": raw_count,
        "canonical_oriented_hosts": len(unique),
        "complete": raw_count == tree_count * matching_count,
        "elapsed_seconds": round(perf_counter() - start, 6),
    }
    return sorted(unique), stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dual-vertices", type=int, default=8)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    hosts, stats = generate_hosts(args.dual_vertices, args.limit)
    if args.output is not None:
        args.output.write_text(
            json.dumps(
                {
                    "schema": "oriented-spherical-triangulations-v1",
                    "convention": "phi[d] = sigma[alpha[d]]",
                    "stats": stats,
                    "hosts": [
                        {"id": i, "alpha": alpha, "sigma": sigma}
                        for i, (alpha, sigma) in enumerate(hosts)
                    ],
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
