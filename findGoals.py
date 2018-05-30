import numpy as np
from scipy.spatial import distance
import cv2
from collections import deque
import imageio
import matplotlib.pyplot as plt
import sys
import os
import db

scoreThresh=30 #measure of vibration
showFrames = False
waitAfterGif=10 #seconds
allScores20=[]
allScores10=[]
allScores30=[]

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,500)
fontScale              = 1
fontColor              = (255,255,255)
lineType               = 2

# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )
# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# Create some random colors
color = np.random.randint(0,255,(100,3))

def main():
    movs = ['Videos/180517_v1.MP4','Videos/180517_v2.MP4']
    mov2gifs(movs, timeDelay=30)

def mov2gifs(movieNames, dbConn, gifFolder, timeDelay=0, buffLen=30):
    if not os.path.exists(gifFolder):
        os.makedirs(gifFolder)

    numMovies=len(movieNames)
    movieCount=0

    cap = cv2.VideoCapture(movieNames[movieCount])
    print(movieNames[movieCount])
    movieCount+=1
    cap.set(0, timeDelay*1000)
    frames = deque(buffLen*[0], buffLen) #keep buffer of last frames for gif
    ret, old_frame = cap.read()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(old_frame) #for drawing
    p0=None
    counter=0
    gifCount=0
    frmsSinceGif=30*waitAfterGif-30
    frameStamp=0#number of frames into movie

    while(1):
        ret,frame = cap.read()
        frameStamp+=1
        frmsSinceGif+=1
        if ret is False: #If at end of movie, go to next
            if movieCount < numMovies:
                cap = cv2.VideoCapture(movieNames[movieCount])
                print(movieNames[movieCount])
                db.printDB(dbConn)
                frameStamp=0
                ret,frame = cap.read()
                p0=None
                movieCount+=1
            else:
                break
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(cv2.resize(frame_gray, (0,0), fx=0.5, fy=0.5) ) #add frame to buffer

        if counter > 10 or p0 is None: #Find feature to track
            p0=getGrid(1280, 720)
            mask = np.zeros_like(old_frame)
            counter=0
        else:
            counter+=1
            try:
                p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
            except:
                p1=None
            if p1 is not None: #Found features
                good_new = p1[st==1]
                good_old = p0[st==1]
                scores=[]
                for i,(new,old) in enumerate(zip(good_new,good_old)):
                    a,b = new.ravel()
                    c,d = old.ravel()
                    scores.append(distance.euclidean((a,b),(c,d)))
                    if showFrames:
                        mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
                        frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)
                # score=sum(scores)/len(scores)
                score = 100*(sum(i > 20 for i in scores)/(len(scores)+1 ))
                if isShakeEvt(scores) and frmsSinceGif > 30*waitAfterGif:
                        makeGif(frames, gifCount, gifFolder, dbConn, int(frameStamp/30), movieNames[movieCount-1])
                        gifCount+=1
                        frmsSinceGif=0
                if showFrames:
                    img = cv2.add(frame,mask)
                    cv2.line(img, (10,450),(10,450-int(score)), color[i].tolist(), 30)
                    cv2.putText(img, str(int(score)), bottomLeftCornerOfText, font, fontScale,fontColor, lineType)
                    cv2.imshow('frame',img)
                    k = cv2.waitKey(30) & 0xff
                    if k == 27:
                        break
                p0 = good_new.reshape(-1,1,2)
                old_gray = frame_gray.copy()
            else: #If no feature found
                p0=None
                mask = np.zeros_like(old_frame)

    cv2.destroyAllWindows()
    cap.release()

def isShakeEvt(scores):
    sco = (sum(i > 20 for i in scores)/(len(scores)+1) )
    # allScores20.append(sco)
    # allScores10.append((sum(i > 10 for i in scores)/len(scores) ))
    # allScores30.append((sum(i > 30 for i in scores)/len(scores) ))
    return (sco > 0.5)

def makeGif(frames, gifCount, folder, conn, timeStamp, vidName):
    name='/m'+str(gifCount)+'.gif'
    frs = np.asarray(frames)
    imageio.mimsave(folder+name, frs)
    db.newEntry(conn, ID=folder+name, status='gif', time=timeStamp, vidID=vidName)
    print('added to DB')
    # db.printDB(conn)
    # (date, ID, vidID, time, status, url, mtID, isGoal)



def getGrid(x,y):
    out=[]
    for i in range(10):
        for j in range(10):
            out.append([[np.float32(int((i+1)*x/11)), np.float32(int((j+1)*y/11))]])
    return np.asarray(out)

if __name__ == '__main__':
    main()
