import importlib.util, json, math, sys, os, numpy as np
os.environ["OT_CELL"]="ghost"
sp=importlib.util.spec_from_file_location('sk','/home/user/exo-shoulder/docs/concepts/models/shortk-onetooth-knuckle-3r.py');SK=importlib.util.module_from_spec(sp);sp.loader.exec_module(SK)
S=SK.S; CB=SK.CB
rho=float(sys.argv[1]); r0,az0=float(sys.argv[2]),float(sys.argv[3]); Lt=float(sys.argv[4]); base=json.load(open(sys.argv[5])); outp=sys.argv[6]
P=SK._clamp(dict(SK.PARAMS,rho=rho)); os.environ.pop("CB_EXACT",None); B=CB.Bench(n_clip=60,n_ws=160)
M=SK.OT.OTModel(B,dict(P)); r=M.run(); D=M.D; L=D.law()
G=dict(base['G']); Pv=dict(base['P']); Pv.update({k:P[k] for k in ('bk1','bk2','smhi','kK','kA','kB','a1max','J3MIN','J3MAX') if k in P}); Pv['rho']=rho; Pv['DKLIM']=P['DKLIM']
r3=lambda a: [round(float(x),3) for x in a]
G['uK']=r3(D.uK); G['psiA']=round(math.degrees(D.psiA),4); G['f']=[round(float(x),2) for x in M.f]; G['fK']=round(float(M.fK),2)
sub=lambda X,n: [r3(x) for x in X[np.linspace(0,len(X)-1,min(n,len(X))).astype(int)]]
for nm,n in (('L1a',7),('L1b',7),('L2',40)):
    X=np.asarray(M.link_pts[nm][1]); G[nm]=sub(X,n)
th=np.asarray(L['th']); q2t=np.degrees(np.asarray(L['q2t'])); dK=np.degrees(np.asarray(L['dK'])); idx=np.linspace(0,len(th)-1,min(48,len(th))).astype(int)
G['lawTh']=r3(th[idx]); G['lawQ2']=r3(q2t[idx]); G['lawDK']=r3(dK[idx]); G['thHi']=round(float(D.th_hi),4); G['thLo']=round(float(D.th_lo),4)
G['q2s']=[G['q2s'][0], round(float(math.degrees(L['q2hi'])),4)]; G['dKlim']=round(float(P['DKLIM']),2)
u2,uK=D.u[1],D.uK; spn=float(np.sign(D.psiA)) or 1.0; s_q=float(L['s_q']); q2hi=float(L['q2hi'])
e=S.unit(np.cross(u2,np.cross(uK,u2))); f=np.cross(u2,e); t=r0/62.0; C0=math.cos(t)*u2+math.sin(t)*(math.cos(math.radians(az0))*e+math.sin(math.radians(az0))*f)
ks=np.radians(np.linspace(0,float(P['DKLIM']),12)); C=np.einsum('nij,j->ni',S.rotm(uK,-spn*ks),C0); X=np.einsum('nij,nj->ni',S.rotm(u2,-(s_q/rho)*ks),C)
Rb=S.rotm(u2,-q2hi)[0]; tooth=(X@Rb.T)*(Lt+1.5)
G['pin']=r3(C0*(float(M.fK)+6.0)); G['pinAx']=r3(C0); G['tooth']=[r3(x) for x in tooth]
for k in ('armA','armB','armPts','rocker','rockerAx','rodA','rodB','roller','rollerAx','lugPts','g','sig','cprog'): G.pop(k,None)
json.dump(dict(P=Pv,G=G,fast=dict(gap=r['gap'],reach=r['reach'],inband14=r['inband14'],follow=r['follow'])),open(outp,'w'))
print('ok',r['gap'],G['fK'],G['dKlim'])
