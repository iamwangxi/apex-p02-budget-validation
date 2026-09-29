"""Supplementary software audit for the finite enumeration.

Shares the main Host and separate check; this is not a third predicate implementation.
Adds checks on every pre-deduplication witness, Euler/atom conservation, reconstruction,
random relabeling, and five legality examples. Read-only unless --output is provided.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import random
import time

from subsets import Host
from independent_predicates import check

BASE = Path(__file__).resolve().parent
KEYS = ['9.11', '9.11_disjoint', '9.11_faces', '9.13', '9.14',
        '9.15', '9.16', 'free_count', 'good_count', 'V']


def bouquet(a_count, c_count, d_count):
    """Two based loops, with five leaf marks in the two monogons and intervening digon."""
    assert a_count + c_count + d_count == 5
    alpha = [1, 0, 3, 2]
    spokes = []
    for _ in range(5):
        x = len(alpha)
        alpha.extend([x + 1, x])
        spokes.append(x)
    cycle = ([0] + spokes[:a_count] + [1]
             + spokes[a_count:a_count + c_count] + [2]
             + spokes[a_count + c_count:] + [3])
    sigma = list(range(len(alpha)))
    for x, y in zip(cycle, cycle[1:] + cycle[:1]):
        sigma[x] = y
    return Host(alpha, sigma)


def dipole(a_count, b_count):
    """Two edges share endpoints; distribute four leaf marks across the two digons."""
    assert a_count + b_count == 4
    alpha = [1, 0, 3, 2]
    spokes = []
    for _ in range(4):
        x = len(alpha)
        alpha.extend([x + 1, x])
        spokes.append(x)
    sigma = list(range(len(alpha)))
    sigma[1], sigma[3] = 3, 1
    cycle = [0] + spokes[:a_count] + [2] + spokes[a_count:]
    for x, y in zip(cycle, cycle[1:] + cycle[:1]):
        sigma[x] = y
    return Host(alpha, sigma)


def legal_examples():
    h = bouquet(2, 0, 3)
    assert len(h.vertices) == 6 and len(h.faces) == 3
    assert h.legal(1)[0] and h.legal(2)[0]
    assert h.legal(3) == (False, ('isotopic_pair', 0, 1))
    assert bouquet(2, 1, 2).legal(3)[0]
    assert bouquet(0, 2, 3).legal(1) == (False, ('inessential_loop', 0))
    h = dipole(4, 0)
    assert len(h.vertices) == 6
    assert h.legal(3) == (False, ('isotopic_pair', 0, 1))
    assert dipole(2, 2).legal(3)[0]
    return ['essential isotopic loops at one basepoint', 'non-isotopic loops at one basepoint', 'inessential loop',
            'isotopic non-loop pair', 'non-isotopic non-loop pair']


def run(results_dir):
    started = time.time()
    src = json.loads((results_dir / 'hosts.json').read_text())
    stats = json.loads((results_dir / 'statistics.json').read_text())
    assert src['stats']['complete'] and stats['complete']
    counts = collections.Counter()
    strata = collections.defaultdict(collections.Counter)
    seen = {}
    for hi, raw in enumerate(src['hosts']):
        h = Host(raw['alpha'], raw['sigma'])
        assert len(h.vertices) == 6 and h.legal(4095)[0]
        for mask in range(1, 4096):
            e_count = bin(mask).count('1')
            v_count = len({v for e, p in enumerate(h.ep)
                           if mask >> e & 1 for v in p})
            row = strata[e_count, v_count]
            row['candidates'] += 1
            if h.objects(mask) is None:
                row['not_pure'] += 1
                continue
            row['pure'] += 1
            counts['all_pure_witnesses'] += 1
            regions, _, _, _, used = h.regions(mask)
            main, _ = h.checks(mask)
            independent = check(h.a, h.s, mask)
            assert all(main[k] == independent[k] for k in KEYS), (hi, mask)
            assert all(main[k] for k in KEYS[:7])
            assert h.legal(mask)[0]
            assert sum(r['tri'] for r in regions) == 255
            assert sum(r['edge'] for r in regions) == 4095 - mask
            assert sum(r['vertex'] for r in regions) == 63 - sum(1 << v for v in used)
            assert sum(r['k'] for r in regions) == 6 - v_count
            adjacency = {v: set() for v in used}
            for e, (u, v) in enumerate(h.ep):
                if mask >> e & 1:
                    adjacency[u].add(v)
                    adjacency[v].add(u)
            todo = set(used)
            components = 0
            while todo:
                components += 1
                stack = [todo.pop()]
                while stack:
                    for v in adjacency[stack.pop()]:
                        if v in todo:
                            todo.remove(v)
                            stack.append(v)
            assert len(regions) == e_count - v_count + components + 1
            assert sum(len(r['boundary']) for r in regions) == 2 * components - v_count + e_count
            cert = h.certificate(mask)
            if cert not in seen:
                seen[cert] = (hi, mask)
                row['unique'] += 1
    assert len(seen) == 658
    for row in stats['strata']:
        for key in ['candidates', 'not_pure', 'pure', 'unique']:
            assert row.get(key, 0) == strata[row['E'], row['V']][key]
    records = [json.loads(line) for line in
               (results_dir / 'types.jsonl').read_text().splitlines()]
    assert len(records) == 658
    ids = set()
    for record in records:
        h = Host(record['alpha'], record['sigma'])
        mask = record['mask']
        cert = h.certificate(mask)
        assert hashlib.sha256(cert).hexdigest() == record['id']
        ids.add(record['id'])
        assert seen[cert] == (record['host'], mask)
        assert all(record['checks'][k] == record['independent'][k] for k in KEYS)
        encoding = json.loads(json.dumps(h.encoding(mask)))
        assert all(encoding[k] == record[k] for k in encoding)
        main, gaps = h.checks(mask)
        assert main == record['checks']
        assert json.loads(json.dumps(gaps)) == record['gaps']
    assert len(ids) == 658
    rng = random.Random(20260929)
    for record in records:
        h = Host(record['alpha'], record['sigma'])
        permutation = list(range(24))
        rng.shuffle(permutation)
        alpha, sigma = [0] * 24, [0] * 24
        for d in range(24):
            alpha[permutation[d]] = permutation[h.a[d]]
            sigma[permutation[d]] = permutation[h.s[d]]
        changed = Host(alpha, sigma)
        selected = {frozenset((permutation[d], permutation[z]))
                    for e, (d, z) in enumerate(h.edges) if record['mask'] >> e & 1}
        changed_mask = sum(1 << e for e, (d, z) in enumerate(changed.edges)
                           if frozenset((d, z)) in selected)
        assert h.certificate(record['mask']) == changed.certificate(changed_mask)
    examples = legal_examples()
    counts.update(all_candidates=sum(r['candidates'] for r in strata.values()),
                  unique=len(seen), checked_record_ids=len(ids),
                  full_record_reconstructions=len(records),
                  random_dart_relabelings=len(records),
                  all_subpredicate_comparisons=counts['all_pure_witnesses'] * len(KEYS),
                  legal_positive_negative_examples=len(examples))
    assert counts['all_candidates'] == 782145 and counts['all_pure_witnesses'] == 11504
    files = [BASE / n for n in ['triangulations.py', 'flip_crosscheck.py',
                               'subsets.py', 'independent_predicates.py', 'audit_checks.py']]
    files += [results_dir / n for n in ['hosts.json', 'host-crosscheck.json',
                                       'types.jsonl', 'statistics.json']]
    return dict(passed=True, counts=dict(counts), random_seed=20260929,
                legal_examples=examples, compared_keys=KEYS,
                shared_functions=['subsets.Host', 'independent_predicates.check'],
                independently_added=['all-witness iteration', 'Euler and atom conservation', 'record reconstruction',
                                     'random relabeling', 'five hand-built legality examples'],
                sha256={("code/" if p.parent == BASE else "results/") + p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in files}, seconds=time.time() - started)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=BASE.parent / 'certificates')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run(args.results.resolve())
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output is not None:
        args.output.write_text(text)
    print(text, end='')
