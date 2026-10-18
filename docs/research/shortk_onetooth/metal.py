"""step 0(b) metal proxy: pin (radial O2.5 + O6 boss + 8x3 horn on link 1a) and the link-2 tooth lug (3 mm, flank = the exact
contact locus of the one pair) on the frozen ghost's taken poses (exact bench), counting skin contact / near-touch poses."""
import importlib.util, json, math, sys, os, time, numpy as np
os.environ["OT_CELL"]="ghost"
sp=importlib.util.spec_from_file_location('sk','/home/user/exo-shoulder/docs/concepts/models/shortk-onetooth-knuckle-3r.py');SK=importlib.util.module_from_spec(sp);sp.loader.exec_module(SK)
S=SK.S; SN=SK.SN
rho=float(sys.argv[1]); bench=sys.argv[2]; mu=float(sys.argv[3]); cands=json.loads(sys.argv[4]); outf=sys.argv[5]
XP=json.loads(sys.argv[6]) if len(sys.argv)>6 else {}
out,M,B=SK.wear(dict({"rho":rho},**XP),bench)
print('ghost',bench,rho,out['frozen'],'ws',out['ws_taken'],'near2',out['near2'],flush=True)
D=M.D; L=D.law(); u2,uK=D.u[1],D.uK; spn=float(np.sign(D.psiA)) or 1.0; s_q=float(L['s_q']); q2hi=float(L['q2hi'])
taken=np.array([B.res[j] is not None and float(np.min(B.res[j]))>=0 for j in range(len(B.idx))]); T=np.nonzero(taken)[0]
dKt=np.degrees(np.abs(np.asarray(M.dK,float))); kneed=float(dKt[taken].max())
fK,f2=float(M.fK),float(M.f[1]); R_mm=62.0; rn=1.25/R_mm; gate=SN.pa_kin(mu)
e=S.unit(np.cross(u2,np.cross(uK,u2))); f=np.cross(u2,e)
def world(m,i,X):
    R,t=M.X[m][0][i],M.X[m][1][i]; Y=X@R.T+t
    return Y@B_RS[i].T
B_RS=SK.CB._poses_all()["RS"][B.idx].astype(float)
res=[]
for c in cands:
    r0,az0=c['r0'],c['az0']; t=r0/R_mm; C0=math.cos(t)*u2+math.sin(t)*(math.cos(math.radians(az0))*e+math.sin(math.radians(az0))*f)
    ks=np.radians(np.arange(0.0,kneed+0.5,0.25)); C=np.einsum('nij,j->ni',S.rotm(uK,-spn*ks),C0)
    v1=-spn*np.cross(uK,C); v2=(s_q/rho)*np.cross(u2,C); vr=v1-v2; nn=np.cross(C,vr/np.maximum(np.linalg.norm(vr,axis=1),1e-15)[:,None]); F=nn*np.sign(np.einsum('ij,ij->i',nn,v1))[:,None]
    pa=lambda nv,v: np.degrees(np.arccos(np.clip(np.abs(np.einsum('ij,ij->i',nv,v))/np.maximum(np.linalg.norm(v,axis=1),1e-15),0,1)))
    pamax=[float(pa(F,v1).max()),float(pa(F,v2).max())]
    R2t=S.rotm(u2,-(s_q/rho)*ks); X=np.einsum('nij,nj->ni',R2t,C); Fl=np.einsum('nij,nj->ni',R2t,F); Pc=S.unit(X-rn*Fl)
    Rb=S.rotm(u2,-q2hi)[0]; Pc2=Pc@Rb.T; Fl2=Fl@Rb.T
    for lh in c.get('lh',[fK]):
      for Lt in c.get('Lt',[61.0,63.0,65.0,67.0]):
        # tooth lug (member 2): flank locus + 1.5 / 3.0 mm behind it (away from the pin), underside Lt, top Lt+3 (contact set: underside + top)
        lug=[]
        for off in (0.0,1.5,3.0):
            dirs=S.unit(Pc2-(off/R_mm)*Fl2)
            lug.append(dirs)
        dirs=np.concatenate(lug)
        # root bar from hub 2's rim to the locus mid point, 6 wide
        mid=S.unit(Pc2[len(Pc2)//2]); rim=S.unit(u2+ (10.5/f2)*S.unit(mid-(mid@u2)*u2))
        bar=np.array([S.unit(rim*(1-s)+mid*s) for s in np.linspace(0,1,8)])
        tooth=np.concatenate([np.concatenate([dirs,bar])*Lt,np.concatenate([dirs,bar])*(Lt+3.0)])
        # pin (member 1): O2.5 rings from the horn top to the tooth top, boss O6 at the horn; horn 8 x 3 strap from hub K's rim
        a=S.unit(np.cross(C0,[0.3,0.5,0.8])); b=np.cross(C0,a)
        ring=lambda rr,lev: np.array([C0*lev+rr*(math.cos(q)*a+math.sin(q)*b) for q in np.linspace(0,2*math.pi,10,endpoint=False)])
        pin=np.concatenate([ring(1.25,lev) for lev in np.arange(lh+3.0,Lt+3.01,1.5)]+[ring(3.0,lh),ring(1.5,lh),C0[None]*lh])
        k0=S.unit(uK+(10.5/fK)*S.unit(C0-(C0@uK)*uK)); w_=S.unit(np.cross(k0,C0))
        horn=np.array([S.unit(k0*(1-s)+C0*s)*lh+ww*w_ for s in np.linspace(0,1,8) for ww in (-4,-1.5,1.5,4)])
        mins={'tooth':[], 'pin':[], 'horn':[]}; ib={'tooth':[],'pin':[],'horn':[]}
        for i in T:
            for nm,mem,Xp in (('tooth',2,tooth),('pin',1,pin),('horn',1,horn)):
                d=B.dist(i,world(mem,i,Xp)); mins[nm].append(float(d.min())); ib[nm].append(float(np.mean((d>=2)&(d<=14))))
        rec=dict(r0=r0,az0=az0,lh=round(lh,2),Lt=Lt,pa=[round(x,1) for x in pamax],kneed=round(kneed,2))
        for nm in mins:
            m_=np.array(mins[nm]); rec[nm]=dict(contact=int((m_<0).sum()),near2=int((m_<2).sum()),min=round(float(m_.min()),2),ib14=round(float(np.mean(ib[nm])),3),
                                              worst=[int(T[j]) for j in np.argsort(m_)[:5] if m_[j]<0])
        res.append(rec); print(json.dumps(rec),flush=True)
json.dump(dict(ghost=out['frozen'],ws=out['ws_taken'],fK=fK,f2=f2,res=res),open(outf,'w'),indent=1,default=float)
