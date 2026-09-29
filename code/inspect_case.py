"""Reconstruct a certificate record and recompute both predicate implementations."""
import argparse
import json
from pathlib import Path
from subsets import Host
from independent_predicates import check

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--id',help='Combinatorial-type SHA-256 identifier prefix')
p.add_argument('--line',type=int,default=1,help='One-based certificate line; --id takes precedence')
p.add_argument('--file',type=Path,default=Path(__file__).resolve().parent.parent/'certificates'/'types.jsonl')
a=p.parse_args()
records=[json.loads(x) for x in a.file.read_text().splitlines()]
matches=[r for i,r in enumerate(records,1) if (r['id'].startswith(a.id) if a.id else i==a.line)]
if len(matches)!=1: raise SystemExit('Exactly one combinatorial type must match')
r=matches[0];h=Host(r['alpha'],r['sigma']);main,gaps=h.checks(r['mask']);ind=check(h.a,h.s,r['mask'])
assert main==r['checks']
assert all(main[k]==ind[k] for k in main)
print(json.dumps(dict(id=r['id'],host=r['host'],mask=r['mask'],legal=h.legal(r['mask']),
                     encoding=h.encoding(r['mask']),checks=main,independent=ind,gaps=gaps),ensure_ascii=False,indent=2))
