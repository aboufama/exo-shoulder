"""built-flank scan of the one pair on the re-seated dyad: max drive range from stop A over pin starts (exact; dk 0.05)"""
import importlib.util, json, math, sys, time, numpy as np
from scipy.spatial import cKDTree
sp=importlib.util.spec_from_file_location('sk','/home/user/exo-shoulder/docs/concepts/models/shortk-onetooth-knuckle-3r.py');SK=importlib.util.module_from_spec(sp);sp.loader.exec_module(SK)
OT,S,SN,FL=SK.OT,SK.S,SK.SN,SK.FL
rhos=[float(x) for x in sys.argv[1].split(',')]; rs=np.arange(*[float(x) for x in sys.argv[2].split(',')]); azs=np.arange(*[float(x) for x in sys.argv[3].split(',')])
extra=json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
out=[]; R_mm=62.0; nose_r=1.25; win=1.0; dk=0.05; mu=float(extra.pop("mu",0.087)); gate=SN.pa_kin(mu)
for rho in rhos:
    P=SK._clamp(dict(SK.PARAMS,rho=rho,**extra)); D=FL.G.KR.KB.KDesign(P); D.q2sgn=-1.0; L=D.law()
    u2,uK=D.u[1],D.uK; spn=float(np.sign(D.psiA)) or 1.0; s_q=float(L['s_q']); kmax=float(P['DKLIM'])
    e=S.unit(np.cross(u2,np.cross(uK,u2))); f=np.cross(u2,e); ks=np.radians(np.arange(0.0,kmax+1e-9,dk)); n=len(ks)
    RK=S.rotm(uK,-spn*ks); R2t=S.rotm(u2,-(s_q/rho)*ks); best=None; t0=time.time()
    for r0 in rs:
        for az0 in azs:
            t=r0/R_mm; C0=math.cos(t)*u2+math.sin(t)*(math.cos(math.radians(az0))*e+math.sin(math.radians(az0))*f)
            C=np.einsum('nij,j->ni',RK,C0); v1=-spn*np.cross(uK,C); v2=(s_q/rho)*np.cross(u2,C); vr=v1-v2
            nn=np.cross(C,vr/np.maximum(np.linalg.norm(vr,axis=1),1e-15)[:,None]); F=nn*np.sign(np.einsum('ij,ij->i',nn,v1))[:,None]
            pa=lambda nv,v: np.degrees(np.arccos(np.clip(np.abs(np.einsum('ij,ij->i',nv,v))/np.maximum(np.linalg.norm(v,axis=1),1e-15),0,1)))
            p1,p2=pa(F,v1),pa(F,v2); okk=(p1<=gate)&(p2<=gate)
            klim_kin=n if okk.all() else int(np.argmin(okk))
            if klim_kin*dk<20: out.append(dict(rho=rho,r0=float(r0),az0=float(az0),range=round(klim_kin*dk,2),kin=round(klim_kin*dk,2))); continue
            X=np.einsum('nij,nj->ni',R2t,C); Fl=np.einsum('nij,nj->ni',R2t,F); rn=nose_r/R_mm; Pc=S.unit(X-rn*Fl)
            tree=cKDTree(X); w=int(round(win/dk)); depth=np.zeros(n)
            for j in range(klim_kin):
                idx=[i for i in tree.query_ball_point(Pc[j],rn*0.999) if abs(i-j)>w]
                if idx: depth[j]=(rn-float(np.min(np.linalg.norm(X[idx]-Pc[j],axis=1))))*R_mm
            ok=okk&(depth<=0.005); lim=n if ok.all() else int(np.argmin(ok))
            vmin=int(np.argmin(np.linalg.norm(vr,axis=1)))
            rr=np.degrees(np.arccos(np.clip(C[:lim]@u2,-1,1)))*math.pi/180*R_mm if lim>0 else np.array([0.0])
            rec=dict(rho=rho,r0=float(r0),az0=float(az0),range=round(lim*dk,2),kin=round(klim_kin*dk,2),pole=round(float(np.degrees(ks[vmin])),2),
                     pa=[round(float(p1[:max(lim,1)].max()),1),round(float(p2[:max(lim,1)].max()),1)],cr=[round(float(rr.min()),1),round(float(rr.max()),1)],
                     r_uK=round(math.degrees(math.acos(float(C0@uK)))*math.pi/180*R_mm,2))
            out.append(rec)
            if best is None or rec['range']>best['range']: best=rec
    print(extra.get('bk1'),extra.get('bk2'),'mu',mu,'rho',rho,'kmax %.2f k_end %.2f'%(kmax,SK.law_for(P)['k_end']),'best',best,'secs %.0f'%(time.time()-t0),flush=True)
json.dump(out,open(sys.argv[5] if len(sys.argv)>5 else '/dev/null','w'))
