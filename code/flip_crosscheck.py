"""Separate Whitehead closure without the tree/stem generator or its canonicalizer."""
import argparse
from collections import deque
import json
from pathlib import Path
import time
import pynauty

def canon(alpha,sigma):
    # Typed relation graph: alpha uses edge nodes; sigma uses directed dart successors.
    n=len(alpha); es=[(d,alpha[d]) for d in range(n) if d<alpha[d]]
    em={d:n+i for i,ds in enumerate(es) for d in ds}
    adj={d:[sigma[d],em[d]] for d in range(n)}
    adj.update({n+i:[] for i in range(len(es))})
    g=pynauty.Graph(n+len(es),directed=True,adjacency_dict=adj,
                     vertex_coloring=[set(range(n)),set(range(n,n+len(es)))])
    return pynauty.certificate(g)

def flips(alpha,sigma):
    # Two trivalent dual tau nodes: (d,b,c) and (a,e,f).
    tau=[sigma[alpha[d]] for d in range(len(alpha))]
    for d in range(len(alpha)):
        a=alpha[d]
        if d>a: continue
        b=tau[d];c=tau[b]
        if a in (b,c): continue   # Dual loops have no quadrilateral flip.
        e=tau[a];f=tau[e]
        t=tau[:]
        for x,y,z in [(d,c,e),(a,f,b)]:
            t[x]=y;t[y]=z;t[z]=x
        yield tuple(alpha),tuple(t[alpha[x]] for x in range(len(alpha)))

def octahedron():
    # Fixed geometric seed: equator 0..3, poles 4,5, and eight oriented triangles.
    faces=[]
    for i in range(4):
        j=(i+1)%4
        faces.append((4,i,j));faces.append((5,j,i))
    directed=[(face[i],face[(i+1)%3]) for face in faces for i in range(3)]
    lookup={e:i for i,e in enumerate(directed)}
    alpha=tuple(lookup[(v,u)] for u,v in directed)
    phi=[3*(d//3)+(d+1)%3 for d in range(24)]
    sigma=tuple(phi[alpha[d]] for d in range(24))
    return alpha,sigma

def main():
    p=argparse.ArgumentParser();p.add_argument('--hosts',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    start=time.time();seed=octahedron();seen={canon(*seed):seed};queue=deque([seed]);attempts=0
    while queue:
        h=queue.popleft()
        for hh in flips(*h):
            attempts+=1;c=canon(*hh)
            if c not in seen:
                seen[c]=hh;queue.append(hh)
    src=json.loads(args.hosts.read_text())
    expected={canon(h['alpha'],h['sigma']) for h in src['hosts']}
    result=dict(complete=True,seed='explicit octahedral triangulation',hosts=len(seen),transitions=attempts,
                main_host_count=len(src['hosts']),main_distinct_under_independent_canon=len(expected),
                only_main=len(expected-set(seen)),only_flip=len(set(seen)-expected),
                agree=expected==set(seen),seconds=time.time()-start,
                independent_of=['binary-tree enumeration','stem order','noncrossing matchings','main canonical labeling'])
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    assert result['agree'] and len(expected)==len(src['hosts'])

if __name__=='__main__': main()
