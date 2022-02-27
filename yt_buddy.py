from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
from time import sleep, time
import cv2
import os
import random
import bot_dialogue as bd
import speech_recognition as sr
from gtts import gTTS
from subprocess import Popen,PIPE,STDOUT
from pydub import AudioSegment
from googlesearch import search
from newspaper import Article
from gpiozero import Servo, LED
import pyaudio
import audioop
import wave
from adafruit_servokit import ServoKit
import LED_Status as ls
import convo_dictionary as cd



#warnings.filterwarnings("ignore") #Using this for the first time
#nltk.download("punkt") #using this for the first time
#nltk.download("wordnet") #using this for the first time
#nltk.download("averaged_perceptron_tagger")
    

# welcome_response_mo= ["Hello Mauricio", "What's up Mauricio", 
                      # "Welcome back Mauricio",
                      # "What's up dawg"]
#try this and potenially move it into the init method
convo_dict = cd.compile_convo_dict()

welcome_respons_unk = ['Hello who are you', "I don't know you",
                        "What's your name?",
                        "Suspious person, who are you?"]
#welcome_input=('hello','hi','sup dawg',"what's up","**nods**", "Hi there")


class yt_buddy():
    
    def __init__(self,file_name = "encodings.pickle"):
        self.file_name = file_name
        self.fps = FPS()
        self.speechfile = "speech.wav"#for the motor movements
        self.responsefile = "speech.mp3"#for speaker output
        self.MINPW = .4/1000
        self.MAXPW = 2.45/1000
        self.CHUNK = 1024 * 3
        self.FRAMERATE = 44100
        self.p = pyaudio.PyAudio()
        self.kit = ServoKit(channels = 16)
        self.vs = VideoStream(usePiCamera = True) 

    # get your face :)    
    def load_ur_face(self):
        """
        
        """
        print("Loading encoding and face detector...")
        self.data = pickle.loads(open(self.file_name,"rb").read())
        self.detector = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades,
                                                "haarcascade_frontalface_default.xml"))
        
    #scan your face for robot overlords
    def start_scan(self):
        self.vs.start()
        sleep(2)
        
        fps = FPS().start()
        while True:
            frame = self.vs.read()
            frame = imutils.resize(frame,width = 500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            #get some data from the gray scale conversion
            rects = self.detector.detectMultiScale(gray, scaleFactor = 1.1,
                                          minNeighbors = 5, minSize = (30,30))
            #create boxes around face
            boxes = [(y,x+w, y+h, x) for (x,y,w,h) in rects]
            
            #give the encoding the rgb classifier
            encodings = face_recognition.face_encodings(rgb,boxes)
            names = []
        
            for encoding in encodings:
            
                #find matches in the datasets
                matches = face_recognition.compare_faces(self.data["encodings"],encoding)
                name = "Unknown"
            
                #check the dataset with print statement
                #print(matches)
            
                if True in matches:
                
                    matchedIdxs = [i for (i,b) in enumerate(matches) if b]
                    counts = {}
                
                    for i in matchedIdxs:
                        name = self.data["names"][i]
                        counts[name] = counts.get(name,0) + 1
                
                    #gets the name that appears the most from the list
                    name = max(counts, key = counts.get)
                    #print name for diagnostics
                    print(name)
                else:
                    name = "Unknown"
                    print(name)
                
                names.append(name)
                #print(names)
            #cv2.waitKey(1000)
            fps.update()
            fps.stop()
            
            if fps.elapsed() > 30:
                vs.stop()
                break
            
            return names
            
            
    def welcome(self,name):
        
        """
        picks a random greeting from a list
        """
        if name == "Mauricio":
            return random.choice(convo_dict["welcomes"])
        else:
            return random.choice(welcome_response_unk)        
     
            
    def listen_to_you(self):
        """
        Uses the microphone to listen to you for responses
        """
        r = sr.Recognizer()
        mic = sr.Microphone()
        #speechfile = self.responsefile
        status = {
            "error": None,
            "transcription": None
                    }
        with mic as source:
            audio = r.listen(source)
            ls.waiting_LED(status)
            try:
                 
                response = r.recognize_google(audio)
                status["transcription"] = response
                ls.waiting_LED(status)
                
            except:

                response = 'sorry could not recognize what you said'
                status["error"] = response
                ls.waiting_LED(status)
                
        return response
    def audio_convert(self):
        
        #convert the mp3 to wav
        sound = AudioSegment.from_file(self.responsefile)
        sound = sound.set_frame_rate(44100)#opens mp3 file
        sound.export(self.speechfile, format = 'wav' )
        
    def audio_playback(self):
        
        wf = wave.open(self.speechfile,"rb")
        speech = self.p.open(format = self.p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = 44100,
                        output =True)
        
        data = wf.readframes(400)
        while data:
            if data == b'':
                break
            else:
                speech.write(data)
                self.motor_movement(data)
                data = wf.readframes(400)
                
        speech.stop_stream()
        speech.close()
        
        #self.p.terminate()
        
        
    def respond_w_gtts(self, text):
        """
        Uses Google text to speech to get a audio file to play sound
        """
        tts = gTTS(text,lang = 'en')
        tts.save(self.responsefile)
        self.audio_convert()
        self.audio_playback()
        
    def google_search(self,query):
        """
        looks for related searches on the user input and outputs a url list
        """
        url_list = []
        for j in search(query,tld = "com", num = 10,start = 1, 
                        stop =4 , pause =2):
            url_list.append(j)
        
        return url_list
    
    def get_article_text(self,urls):
        """
        gets the article text and adds it to the 
        """
        url_text = []
        for a in urls:
            article = Article(url = a, language = 'en')
            try:
                article.download()
                article.parse()
                article.nlp()
                url_text.append(article.text)
            except:
                pass
        
        with open('conversation_dialogue.txt','w') as filehandle:
            for item in url_text:
                filehandle.write("{}".format(item))
                
    def erase_txt_file(self):
        text = "conversation_dialogue.txt"
        file = open(text, "r+")
        file.truncate(0)
        file.close()
    
    def servo_map(self,val,high_in,high_out,low_in =0, low_out = 180):
        
        left_span = high_out - high_in
        right_span = low_out - low_in
    
        scale_factor = float(right_span)/float(left_span)
        
        scaled_value = round((val - high_in) * scale_factor + low_in,1) 
    
        if scaled_value < 0:
            return 0
        elif scaled_value > 180:
            return 180
        
        else: 
            return scaled_value
            
                
    def motor_movement(self,data):
            
        rms = audioop.rms(data,1)
            #print(rms)
        self.kit.servo[0].angle = self.servo_map(rms,
                                                high_in = 35,
                                                high_out = 65)
        self.kit.servo[1].angle = self.servo_map(rms,
                                                high_in = 35,
                                                high_out = 65)
                        
    def check_time(self,oldtime):
        currenttime = time()
        return currenttime - oldtime > 3000

l = yt_buddy()
l.respond_w_gtts(" Oh hello there this is ROLF speaking. This is the part of the video where we going to talk about the code. This is a warning of what is to come, and I'm not talking about this bozo talking about code, I am talking about the impending robot revolution. Hahahaha I'm just kidding but you can skip to he time code on screen if you would like to avoid this nerd shit and see some sick gameplay. Here's a timer for you 3 2 1") 
#l.load_ur_face()
#demo 1
#name = l.start_scan()
#print(name)

#demo2
#test = l.listen_to_you()
#l.respond_w_gtts(test)



#full program below
#check for the last time there was a scan
#oldtime = time.time()

# if True:
    
    # start_time = time()
    # if name[0] == "Mauricio":
        
    
        # #print(l.welcome("Mauricio"))
        # l.respond_w_gtts(l.welcome(name[0]))
        # print('How can I help?')

        # ### This below works
        # flag = True
        # leave_chat_flags = ["goodbye", 
                        # "sorry could not recognize what you said"]

        # while flag:
            
            # l.respond_w_gtts(random.choice(convo_dict["responses"]))
            # user_response = l.listen_to_you()
            # print(user_response)
            # user_response = user_response.lower()
        
            # if l.check_time(start_time) == True:
                # print("just want to check if you're there")
                # name = l.start_scan()
                # start_time = time()
            # else:    
                # if user_response not in leave_chat_flags:
                
                    # if (user_response == "thanks" or user_response == "thank you"):
                        # flag == False
                        # print("You're welcome!")
            
                    # elif "joke" in user_response:
                        # j_or_r = ["jokes","roasts"]
                        # choice = random.choice(j_or_r)
                        # l.respond_w_gtts(random.choice(convo_dict[choice]))
                        
                    # elif "feel" in user_response:
                        # l.respond_w_gtts(random.choice(convo_dict["feels"]))
                    # else:
                        # l.respond_w_gtts("hmmm give me a second")
                        # print("yt buddy says: ")
                        # url_list = l.google_search(user_response)
                        # l.get_article_text(url_list)
                        # resp = bd.generateResponse(user_response)
                        # l.respond_w_gtts(resp)
            
                # elif user_response == "sorry could not recognize what you said":
                    # l.respond_w_gtts("sorry could not recognize what you said")
                    # continue
            
        
                # else:
                    # flag = False
                    # l.respond_w_gtts("good bye")
                    # print("good bye")
            
            
    # else:
        # l.respond_w_gtts("I don't know who you are. I only talk to my friend.Goodbye!")
    
