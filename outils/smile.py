import cv2, numpy as np, mediapipe as mp, json
fm=mp.solutions.face_mesh.FaceMesh(max_num_faces=1,refine_landmarks=True)
cap=cv2.VideoCapture("rush4.mp4"); out=[]; i=0
while True:
    ok,fr=cap.read()
    if not ok: break
    r=fm.process(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)); t=i/4; i+=1
    if not r.multi_face_landmarks: continue
    L=r.multi_face_landmarks[0].landmark; P=lambda k: np.array([L[k].x*540,L[k].y*960])
    fw=np.linalg.norm(P(234)-P(454))
    mw=np.linalg.norm(P(61)-P(291))/fw            # largeur de bouche
    lift=((P(13)[1]+P(14)[1])/2-(P(61)[1]+P(291)[1])/2)/fw  # coins plus hauts que le centre
    openm=np.linalg.norm(P(13)-P(14))/fw
    gx=((P(468)[0]-P(33)[0])/(P(133)[0]-P(33)[0])+(P(473)[0]-P(362)[0])/(P(263)[0]-P(362)[0]))/2
    eye=(P(33)+P(263))/2; yaw=(P(1)[0]-eye[0])/np.linalg.norm(P(33)-P(263))
    out.append(dict(t=t,mw=float(mw),lift=float(lift),open=float(openm),gx=float(gx),yaw=float(yaw),fw=float(fw)))
json.dump(out,open("smile.json","w"))
a=np.array([[o["mw"],o["lift"],o["gx"],o["yaw"],o["fw"]] for o in out]); med=np.median(a,0)
sc=[(o["mw"]-med[0])*4+(o["lift"]-med[1])*6-abs(o["gx"]-med[2])*3-abs(o["yaw"]-med[3])*2 for o in out]
best=sorted(zip(sc,[o["t"] for o in out],[o["fw"] for o in out]),reverse=True)[:16]
# instants espacés d'au moins 2 s
choix=[]
for s_,t_,f_ in best:
    if all(abs(t_-c)>2 for c in choix): choix.append(t_)
json.dump(choix,open("meilleurs.json","w"))
for s,t,fw in best: print(round(t,2),round(s,3),round(fw))
