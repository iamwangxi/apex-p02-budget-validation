"""Purely bad six-point arc systems: host subsets, atom predicates, oriented types."""
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import time
import pynauty

BASE = Path(__file__).resolve().parent

def cycles(p):
    unseen = set(range(len(p)))
    out = []
    while unseen:
        x = min(unseen)
        c = []
        while x in unseen:
            unseen.remove(x)
            c.append(x)
            x = p[x]
        out.append(tuple(c))
    return out

class Host:
    def __init__(self, alpha, sigma):
        self.a, self.s = tuple(alpha), tuple(sigma)
        self.vertices = cycles(sigma)
        self.faces = cycles([sigma[alpha[d]] for d in range(len(alpha))])
        self.edges = [(d, alpha[d]) for d in range(len(alpha)) if d < alpha[d]]
        self.vd = {d:v for v,c in enumerate(self.vertices) for d in c}
        self.fd = {d:f for f,c in enumerate(self.faces) for d in c}
        self.ed = {d:e for e,ds in enumerate(self.edges) for d in ds}
        self.ep = [tuple(sorted((self.vd[d], self.vd[a]))) for d,a in self.edges]
        self.cache = {}

    def regions(self, mask):
        if mask in self.cache:
            return self.cache[mask]
        par = list(range(len(self.faces)))
        def find(i):
            while par[i] != i:
                par[i] = par[par[i]]
                i = par[i]
            return i
        for e,(d,a) in enumerate(self.edges):
            if not mask >> e & 1:
                x,y = find(self.fd[d]),find(self.fd[a])
                par[x] = y
        roots = sorted({find(f) for f in range(len(self.faces))})
        idx = {r:i for i,r in enumerate(roots)}
        fr = [idx[find(f)] for f in range(len(self.faces))]
        data = [dict(tri=0, edge=0, vertex=0, boundary=[], X=set()) for _ in roots]
        for f,r in enumerate(fr):
            data[r]['tri'] |= 1 << f
        used = set()
        kept = set()
        er = {}
        for e,(d,a) in enumerate(self.edges):
            if mask >> e & 1:
                used.update(self.ep[e]); kept.update((d,a))
            else:
                r=fr[self.fd[d]]
                assert r == fr[self.fd[a]]
                er[e] = r
                data[r]['edge'] |= 1 << e
        for v,ds in enumerate(self.vertices):
            if v not in used:
                rr={fr[self.fd[d]] for d in ds}
                assert len(rr)==1
                data[rr.pop()]['vertex'] |= 1 << v
        restricted={}
        for d in kept:
            x=self.s[d]
            while x not in kept:
                x=self.s[x]
            restricted[d]=x
        unseen=set(kept)
        while unseen:
            d=min(unseen); x=d; walk=[]
            while x in unseen:
                unseen.remove(x); walk.append(x)
                x=restricted[self.a[x]]
            assert x==d
            rr={fr[self.fd[x]] for x in walk}
            assert len(rr)==1
            r=rr.pop()
            data[r]['boundary'].append(walk)
            data[r]['X'].update(self.vd[x] for x in walk)
        for r in data:
            r['X']=tuple(sorted(r['X']))
            r['atoms']=(r['tri'],r['edge'],r['vertex'])
            r['k']=bin(r['vertex']).count('1')
        result=(data,fr,er,restricted,used)
        self.cache[mask]=result
        return result

    def legal(self, mask):
        chosen=[e for e in range(len(self.edges)) if mask>>e&1]
        for e in chosen:
            if self.ep[e][0]==self.ep[e][1]:
                if any(r['k']==0 for r in self.regions(1<<e)[0]):
                    return False, ('inessential_loop', e)
        for e,f in itertools.combinations(chosen,2):
            if self.ep[e]!=self.ep[f]:
                continue
            rs=self.regions((1<<e)|(1<<f))[0]
            for r in rs:
                ds=[d for w in r['boundary'] for d in w]
                # Empty digons between same-basepoint loops or same-endpoint non-loop arcs.
                if len(ds)==2 and {self.ed[d] for d in ds}=={e,f} and r['k']==0:
                    return False, ('isotopic_pair',e,f)
        return True,None

    def objects(self, mask):
        loops=[]; groups=defaultdict(list)
        for e,pair in enumerate(self.ep):
            if mask>>e&1:
                if pair[0]==pair[1]: loops.append([e])
                else: groups[pair].append(e)
        if any(len(es)==1 for es in groups.values()):
            return None
        return loops+list(groups.values())

    def checks(self,mask):
        objects=self.objects(mask)
        assert objects
        rs,_,_,_,used=self.regions(mask)
        face_atoms={r['atoms'] for r in rs}
        F={self.ep[o[0]] for o in objects if len(o)>=2}
        gaps=[]
        for oi,obj in enumerate(objects):
            om=sum(1<<e for e in obj)
            gr,_,er,_,_=self.regions(om)
            for gi,g in enumerate(gr):
                occupied=[j for j,o in enumerate(objects) if j!=oi and all(er[e]==gi for e in o)]
                clean=all(tuple(p) in F for p in itertools.combinations(g['X'],2))
                gaps.append(dict(object=oi, gap=gi, atoms=g['atoms'], X=g['X'], k=g['k'],
                                 contained_objects=occupied, free=not occupied,
                                 face=g['atoms'] in face_atoms, clean=clean,
                                 good=not occupied and g['atoms'] in face_atoms and clean and g['k'] in (1,2)))
        free=[g for g in gaps if g['free']]
        disjoint=any(all(not(a&b) for a,b in zip(g['atoms'],h['atoms'])) for g,h in itertools.combinations(free,2))
        result={'9.11':disjoint and all(g['face'] for g in free),
                '9.11_disjoint':disjoint,'9.11_faces':all(g['face'] for g in free),
                '9.13':all(g['clean'] for g in free),
                '9.14':all(g['k']>=1 for g in free),
                '9.15':any(g['good'] for g in gaps), '9.16':len(used)<=4,
                'free_count':len(free),'good_count':sum(g['good'] for g in gaps),'V':len(used)}
        return result,gaps

    def certificate(self,mask):
        rs,fr,_,restricted,used=self.regions(mask)
        ds=sorted(restricted)
        es=[e for e in range(len(self.edges)) if mask>>e&1]
        vbase=0; dbase=len(self.vertices); ebase=dbase+len(ds); rbase=ebase+len(es)
        dm={d:dbase+i for i,d in enumerate(ds)}
        em={e:ebase+i for i,e in enumerate(es)}
        adj={i:[] for i in range(rbase+len(rs))}
        for d in ds:
            adj[dm[d]]=[self.vd[d], em[self.ed[d]],rbase+fr[self.fd[d]], dm[restricted[d]]]
        for v in range(len(self.vertices)):
            if v not in used:
                adj[v]=[rbase+fr[self.fd[self.vertices[v][0]]]]
        color=[set(range(dbase)),set(range(dbase,ebase)),set(range(ebase,rbase)),set(range(rbase,rbase+len(rs)))]
        graph=pynauty.Graph(rbase+len(rs),directed=True,adjacency_dict=adj,vertex_coloring=color)
        # Include color-class sizes to distinguish certificates of different graph sizes.
        prefix=bytes([len(self.vertices),len(ds),len(es),len(rs)])
        return prefix+pynauty.certificate(graph)

    def encoding(self,mask):
        rs,fr,er,restricted,used=self.regions(mask)
        return dict(alpha=list(self.a),sigma=list(self.s),mask=mask,
                    edges=[list(p) for p in self.edges], endpoints=[list(p) for p in self.ep],
                    selected_edges=[e for e in range(len(self.edges)) if mask>>e&1],
                    vertex_cycles=[list(c) for c in self.vertices],
                    selected_rotation={str(d):x for d,x in restricted.items()},
                    regions=[{k:v for k,v in r.items()} for r in rs],unused_vertices=sorted(set(range(6))-used))

def run(hostfile, outdir, limit=None):
    from independent_predicates import check as independent_check
    outdir.mkdir(parents=True, exist_ok=True)
    raw=json.loads(hostfile.read_text())
    if limit is None and not raw.get('stats',{}).get('complete',False):
        raise ValueError('Host enumeration is incomplete; diagnostics must explicitly use --limit')
    hosts=raw['hosts']
    if limit is not None: hosts=hosts[:limit]
    stats=defaultdict(Counter); seen={}; failures=[]; witness_count=0
    t=time.time()
    with (outdir/'types.jsonl').open('w') as fp:
        for hi,h in enumerate(hosts):
            host=Host(h['alpha'],h['sigma'])
            assert len(host.vertices)==6 and len(host.faces)==8 and all(len(f)==3 for f in host.faces)
            legal,why=host.legal((1<<12)-1)
            if not legal:
                raise RuntimeError(('Host legality failed',hi,why))
            for mask in range(1,1<<12):
                e=bin(mask).count('1')
                v=len({x for j,p in enumerate(host.ep) if mask>>j&1 for x in p})
                row=stats[(e,v)]; row['candidates']+=1; row['legal']+=1
                objects=host.objects(mask)
                if objects is None:
                    row['not_pure']+=1; continue
                row['pure']+=1
                cert=host.certificate(mask)
                if cert in seen:
                    row['duplicates']+=1; continue
                key=hashlib.sha256(cert).hexdigest()
                # Deduplicate by full nauty certificate, not its hash.
                seen[cert]=(hi,mask)
                row['unique']+=1; witness_count+=1
                legal,why=host.legal(mask)
                if not legal: raise RuntimeError(('Subset legality failed',hi,mask,why))
                a,gaps=host.checks(mask)
                b=independent_check(host.a,host.s,mask)
                compared=['9.11','9.11_disjoint','9.11_faces','9.13','9.14','9.15','9.16','free_count','good_count','V']
                agree=all(a[k]==b[k] for k in compared)
                passed=all(a[k] for k in ['9.11','9.13','9.14','9.15','9.16'])
                rec=dict(id=key,host=hi,**host.encoding(mask),checks=a,independent=b,gaps=gaps)
                fp.write(json.dumps(rec,ensure_ascii=False,sort_keys=True)+'\n')
                if not agree or not passed:
                    failures.append(dict(host=hi,mask=mask,agree=agree,main=a,independent=b))
                    (outdir/'failure.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
                    raise RuntimeError(('Potential counterexample or implementation error; stopping immediately',hi,mask,a,b))
                row['checked']+=1
            if hi%25==0:
                print(json.dumps(dict(host=hi+1,total=len(hosts),unique=witness_count,seconds=round(time.time()-t,2)),ensure_ascii=False),flush=True)
    result=dict(complete=limit is None,hosts=len(hosts),unique=len(seen),failures=failures,
                seconds=time.time()-t,strata=[dict(E=e,V=v,**c) for (e,v),c in sorted(stats.items())])
    (outdir/'statistics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='strata'},ensure_ascii=False),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--hosts',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--limit',type=int)
    args=p.parse_args();run(args.hosts,args.out,args.limit)
