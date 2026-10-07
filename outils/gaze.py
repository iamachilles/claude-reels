import cv2, numpy as np, mediapipe as mp, json
fm=mp.solutions.face_mesh.FaceMesh(max_num_faces=1,refine_landmarks=True)
cap=cv2.VideoCapture("low.mp4"); rows=[]
while True:
    ok,fr=cap.read()
    if not ok: break
    r=fm.process(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB))
    if not r.multi_face_landmarks: rows.append([np.nan]*3); continue
    L=r.multi_face_landmarks[0].landmark
    P=lambda i: np.array([L[i].x,L[i].y])
    # regard horizontal : position de l'iris entre les coins de l'oeil, moyenne des deux yeux
    def h(ir,a,b): return (P(ir)[0]-P(a)[0])/(P(b)[0]-P(a)[0])
    gx=(h(468,33,133)+h(473,362,263))/2
    # regard vertical : iris entre paupière haute et basse
    def v(ir,t,b): return (P(ir)[1]-P(t)[1])/(P(b)[1]-P(t)[1]+1e-6)
    gy=(v(468,159,145)+v(473,386,374))/2
    # tête : nez par rapport au milieu des yeux, normalisé
    eye=(P(33)+P(263))/2; d=np.linalg.norm(P(33)-P(263))
    yaw=(P(1)[0]-eye[0])/d; pitch=(P(1)[1]-eye[1])/d
    rows.append([gx,gy,yaw+0*pitch]); rows[-1].append(pitch)
a=np.array([r if len(r)==4 else r+[np.nan] for r in rows],float)
json.dump(dict(fps=24,cols=["gx","gy","yaw","pitch"],v=np.nan_to_num(a,nan=-9).round(4).tolist()),open("gaze.json","w"))
med=np.nanmedian(a,0); mad=np.nanmedian(abs(a-med),0)
print("médianes",med.round(3),"MAD",mad.round(3), "images",len(a))
