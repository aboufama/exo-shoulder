import importlib.util, json, math, sys, os, numpy as np
os.environ["OT_CELL"]="ghost"
sp=importlib.util.spec_from_file_location('sk','/home/user/exo-shoulder/docs/concepts/models/shortk-onetooth-knuckle-3r.py');SK=importlib.util.module_from_spec(sp);sp.loader.exec_module(SK)
S=SK.S; CB=SK.CB; rho=2.0; r0,az0=28.0,24.0
P=SK._clamp(dict(SK.PARAMS,rho=rho)); os.environ.pop("CB_EXACT",None); B=CB.Bench(n_clip=60,n_ws=160)
M=SK.OT.OTModel(B,dict(P)); r=M.run(); D=M.D; L=D.law()
u2,uK=D.u[1],D.uK; spn=float(np.sign(D.psiA)) or 1.0; s_q=float(L['s_q']); q2hi=float(L['q2hi'])
e=S.unit(np.cross(u2,np.cross(uK,u2))); f=np.cross(u2,e); t=r0/62.0; C0=math.cos(t)*u2+math.sin(t)*(math.cos(math.radians(az0))*e+math.sin(math.radians(az0))*f)
ks=np.radians(np.arange(0,float(P['DKLIM']),0.1)); C=np.einsum('nij,j->ni',S.rotm(uK,-spn*ks),C0); X=np.einsum('nij,nj->ni',S.rotm(u2,-(s_q/rho)*ks),C)
Rb=S.rotm(u2,-q2hi)[0]; X2=X@Rb.T
ok=np.nonzero(M.kin_ok)[0]; dK=np.degrees(M.dK); q2=np.degrees(M.q[:,1])
print('q2hi deg',math.degrees(q2hi),'s_q',s_q)
for i in ok[::7][:25]:
    pin=M.X[1][0][i]@C0; T=X2@M.X[2][0][i].T
    d=np.degrees(np.arccos(np.clip(T@pin,-1,1))); j=int(np.argmin(d))
    print(i,'dK %.2f q2 %.2f | pin-to-locus min %.3f deg at locus K %.2f'%(dK[i],q2[i],d.min(),math.degrees(ks[j])))
