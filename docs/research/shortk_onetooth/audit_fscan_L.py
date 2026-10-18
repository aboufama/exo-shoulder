"""audit: fscan with the undercut test limited to the stroke actually run: L = min(kin, min over cutting pairs max(i, j))"""
import importlib.util, json, math, sys, numpy as np
from scipy.spatial import cKDTree
sp=importlib.util.spec_from_file_location('sk','/home/user/exo-shoulder/docs/concepts/models/shortk-onetooth-knuckle-3r.py');SK=importlib.util.module_from_spec(sp);sp.loader.exec_module(SK)
S,SN,FL=SK.S,SK.SN,SK.FL
rhos=[float(x) for x in sys.argv[1].split(',')]; rs=np.arange(*[float(x) for x in sys.argv[2].split(',')]); azs=np.arange(*[float(x) for x in sys.argv[3].split(',')])
extra=json.loads(sys.argv[4]); mu=float(extra.pop("mu",0.087)); gate=SN.pa_kin(mu); R_mm=62.0; rn=1.25/R_mm; dk=0.05; w=int(round(1.0/dk))
for rho in rhos:
    P=SK._clamp(dict(SK.PARAMS,rho=rho,**extra)); D=FL.G.KR.KB.KDesign(P); D.q2sgn=-1.0; L=D.law()
    u2,uK=D.u[1],D.uK; spn=float(np.sign(D.psiA)) or 1.0; s_q=float(L['s_q']); kmax=float(P['DKLIM'])
    e=S.unit(np.cross(u2,np.cross(uK,u2))); f=np.cross(u2,e); ks=np.radians(np.arange(0.0,kmax+1e-9,dk)); n=len(ks)
    RK=S.rotm(uK,-spn*ks); R2t=S.rotm(u2,-(s_q/rho)*ks); old=[]; new=[]
    for r0 in rs:
        for az0 in azs:
            t=r0/R_mm; C0=math.cos(t)*u2+math.sin(t)*(math.cos(math.radians(az0))*e+math.sin(math.radians(az0))*f)
            C=np.einsum('nij,j->ni',RK,C0); v1=-spn*np.cross(uK,C); v2=(s_q/rho)*np.cross(u2,C); vr=v1-v2
            nn=np.cross(C,vr/np.maximum(np.linalg.norm(vr,axis=1),1e-15)[:,None]); F=nn*np.sign(np.einsum('ij,ij->i',nn,v1))[:,None]
            pa=lambda nv,v: np.degrees(np.arccos(np.clip(np.abs(np.einsum('ij,ij->i',nv,v))/np.maximum(np.linalg.norm(v,axis=1),1e-15),0,1)))
            okk=(pa(F,v1)<=gate)&(pa(F,v2)<=gate); kin=n if okk.all() else int(np.argmin(okk))
            if kin*dk<20: continue
            X=np.einsum('nij,nj->ni',R2t,C); Fl=np.einsum('nij,nj->ni',R2t,F); Pc=S.unit(X-rn*Fl); tree=cKDTree(X)
            Lold=kin; Lnew=kin
            for j in range(kin):
                idx=[i for i in tree.query_ball_point(Pc[j],rn*0.999) if abs(i-j)>w]
                if idx:
                    dep=(rn-float(np.min(np.linalg.norm(X[idx]-Pc[j],axis=1))))*R_mm
                    if dep>0.005:
                        Lold=min(Lold,j)
                        bad=[i for i in idx if (rn-np.linalg.norm(X[i]-Pc[j]))*R_mm>0.005]
                        Lnew=min(Lnew,max(min(bad),j)) if bad else Lnew
            r_uK=math.degrees(math.acos(float(C0@uK)))*math.pi/180*R_mm
            old.append((round(Lold*dk,2),r0,az0,round(r_uK,2))); new.append((round(Lnew*dk,2),r0,az0,round(r_uK,2),round(kin*dk,2)))
    old.sort(reverse=True); new.sort(reverse=True)
    print(extra, 'mu',mu,'rho',rho,'OLD best',old[:3],'| STROKE-LIMITED best',new[:5], '| outside rim (>=12.6)', [x for x in new if x[3]>=12.6][:3], flush=True)
