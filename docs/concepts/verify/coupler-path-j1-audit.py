import sys,os,json,time,importlib.util
R='/home/user/exo-shoulder'; sys.path.insert(0,R+'/tools'); sys.path.insert(0,R+'/docs/concepts/models')
sp=importlib.util.spec_from_file_location('pk',R+'/docs/concepts/models/skin-normal-3r-pin-knee.py'); PK=importlib.util.module_from_spec(sp); sp.loader.exec_module(PK)
P=dict(az1=99.7847,el1=65.0641,az2=23.7454,el2=48.5131,wd=66.6237,wa=-9.5334,b3=0.3041,lE=50.2799,lc=17.8289,phiE=-4.2338,phib=-66.4684,stk=5.0,ang_min=30.0,neck=13.0)
t=time.time(); out=PK.frozen(P); out['secs']=time.time()-t; out['params']=P
json.dump(out,open(sys.argv[1],'w'),indent=1,default=str); print(json.dumps({k:out[k] for k in ('fit_fast','frozen','mode','why','knee_ang','secs')},default=str))
