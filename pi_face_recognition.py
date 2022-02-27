from imutils.video import VideoStream
from imutils.video import FPS
from gpiozero import LED
#import gpiozero
#from gpiozero.pins.mock import MockFactory
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import os

#gpiozero.Device.pin_factory = MockFactory()
#led = LED(2)
ap = argparse.ArgumentParser()
#ap.add_argument("-c","--cascade",required = True,
#    help = "path to where the face cascade resides")
ap.add_argument("-e","--encodings",required = True,
    help = "path to serialized db of facial encodings")
args = vars(ap.parse_args())

#reads in the enconding pickle file and then uses the cascade I pick
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"],"rb").read())
detector = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades,"haarcascade_frontalface_default.xml"))

print("[INFO] starting video stream...")
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

fps = FPS().start()

while True:
    frame = vs.read()
    frame = imutils.resize(frame,width=500)
    
    #converts the fram into grayscale and then rgb for the classifier
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    
    #output from the classifier after passing in frame, you get rectangles!!!
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
        minNeighbors=5, minSize =(30,30))
    
    #massaging the outputs of rects to get boxes
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
    print(boxes)
    #passing in the rgb for encodings
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []
    
    for encoding in encodings:
        
        # tries to find  matches with our dataset
        matches = face_recognition.compare_faces(data["encodings"],encoding)
        name = "Unknown"
        print(matches)
        # check if there's a match
        if True in matches:
        
            # grabs the index of the matched face then puts it into a dictionary
            matchedIdxs = [i for (i,b) in enumerate(matches) if b]
            counts = {}
            
            #goes through matches and see how many times a name appears in the dictionary

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name,0) + 1 

            
            name = max(counts, key = counts.get)
            print(name)
        else:
            name = "Unknown"
            print(name)
            #need another dataset to distinguish myself  and have something more tangible         
        if name == "Mauricio":
            led.blink(2,2)
        else:
            led.off()
        names.append(name)
        
    #i can use for diagnistics
    for ((top,right,bottom,left),name) in zip(boxes,names):
        
        #draws rectangle over the face based on encodings
        cv2.rectangle(frame, (left,top), (right,bottom),
            (0,255,0), 2)
        #gets a coordinate to place the name on the image
        y = top - 15 if top - 15 > 15 else top + 15
        cv2. putText(frame,name,(left,y), cv2.FONT_HERSHEY_SIMPLEX,
            .75, (0,255,0),2)
    
    #shows final image with name higlighted and nonsense
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
    #gtfo of program
    if key == ord("q"):
        break
    
    fps.update()

fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()
