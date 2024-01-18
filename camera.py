import cv2
import numpy as np
import os
import myFunction
import threading
from ultralytics import YOLO
import math

def gen_frames(Socketio):
    recognizer = cv2.face.LBPHFaceRecognizer_create()         # 啟用訓練人臉模型方法
    recognizer.read('myface.yml')                               # 讀取人臉模型檔
    cascade_path = "haarcascade_frontalface_default.xml"      # 載入人臉追蹤模型
    face_cascade = cv2.CascadeClassifier(cascade_path)        # 啟用人臉追蹤

    data = myFunction.read_SQL(mydb="topics", table="faces")
    name = {}
    for i in range(len(data)):
        name[i+1] = data[i][2]

    cap = cv2.VideoCapture(0)                                 # 開啟攝影機
    if not cap.isOpened():
        print("Cannot open camera") 
        exit()
    while True:
        ret, img = cap.read()
        if not ret:
            print("Cannot receive frame")
            break
        img = cv2.resize(img,(540,300))              # 縮小尺寸，加快辨識效率
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)  # 轉換成黑白
        faces = face_cascade.detectMultiScale(gray)  # 追蹤人臉 ( 目的在於標記出外框 )

        # 依序判斷每張臉屬於哪個 id
        for(x,y,w,h) in faces:
            # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)            # 標記人臉外框
            idnum,confidence = recognizer.predict(gray[y:y+h,x:x+w])  # 取出 id 號碼以及信心指數 confidence
            if confidence < 80:
                text = name[idnum]                               # 如果信心指數小於 60，取得對應的名字
                success = True

                try:
                    if(success):
                        Socketio.emit('transfer_name', {'name': text})
                        Socketio.emit('recognition_result', {'result': 'success'})
                        
                except KeyboardInterrupt:
                    pass

            else:
                text = '???'+str(confidence)                                          # 不然名字就是 ???
            # 在人臉外框旁加上名字
            # cv2.putText(img, text, (x,y-5),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)

        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def register_video(Socketio):
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')  # 載入人臉追蹤模型
    recog = cv2.face.LBPHFaceRecognizer_create()      # 啟用訓練人臉模型方法
    ids = []     # 記錄該人臉 id 的串列
    faces = []   # 儲存人臉位置大小的串列

    faceSQL = myFunction.read_SQL(mydb="topics", table="faces")
    account = myFunction.read_SQL(mydb="topics", table="person")[-1][1]

    cap = cv2.VideoCapture(0)                                 # 開啟攝影機
    if not cap.isOpened():
        print("Cannot open camera") 
        exit()
    while True:
        ret, img = cap.read()
        if not ret:
            print("Cannot receive frame")
            break
        if (len(faces) == 300):
            def update():
                myFunction.update_faces(mydb="topics", table="faces", id=(len(faceSQL)+1), name=account)
                if os.path.exists("myface.yml"):
                    print("have yml!!")
                    recog.read("myface.yml")
                    new_faces = faces
                    recog.update(new_faces, np.array(ids))
                else:
                    print("no yml!!")
                    recog.train(faces, np.array(ids))
                recog.save("myface.yml")
                print('ok!')
                
                Socketio.emit('trainning_result', {'result': 'success'})

            a = threading.Thread(target=update)
            a.start()

        img = cv2.resize(img,(540,300))              # 縮小尺寸，加快辨識效率
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 色彩轉換成黑白
        img_np = np.array(gray,'uint8')               # 轉換成指定編碼的 numpy 陣列
        face = detector.detectMultiScale(gray)        # 擷取人臉區域
        for(x,y,w,h) in face:
            faces.append(img_np[y:y+h,x:x+w])         # 記錄自己人臉的位置和大小內像素的數值
            ids.append(len(faceSQL)+1)

        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def video_detection(Socketio):
    cap = cv2.VideoCapture(0)

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    model = YOLO("YOLO-Weights/shop_v3.pt")  

    while True:
        success, img = cap.read()
        if not success:
            break
        results = model(img, stream=True)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = math.ceil((box.conf[0] * 100)) / 100
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

        #---------------------------------------------------------------
                Socketio.emit('shopping', {'item': "get!"})
        #-----------------------------------------------------------------

        ref,buffer=cv2.imencode('.jpg',img)
        frame=buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')