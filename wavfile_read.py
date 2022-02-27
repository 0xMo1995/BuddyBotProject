#from gpiozero import LED, Servo,AngularServo
from time import sleep
#from scipy.io import wavfile as wave
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt
import 
#from pydub import AudioSegment

servo = Servo(17)

#sound = AudioSegment.from_mp3("speech.mp3")
#sound.export("speech.wav",format ='wav')

fs,x = wave.read('speech.wav')
ti_1 = plt.figure(1)


x = abs(np.asarray(x))
ax1 = plt.subplot(3,1,1)
X = fft.fft(x)
N = len(X)
ser_loc = []
for val in x:
    if val > 10000:
        ser_loc.append(1)
    #elif val < 9999 or val > 5000:
    #   ser_loc.append(.5)
    else:
        ser_loc.append(0)


print(N)
print(np.amax(x))
fbin = np.linspace(0,fs,N)
tbin = np.linspace(0,N/fs,N)


plt.plot(tbin,abs(X))
ax1.set_xlabel('time(s)')
ax1.set_ylabel('val')


plt.show()



#for item in ser_loc:
#    if item == 1:
#        servo.max()
#        sleep(.1)
#        print("max")
        
    #elif item == .5:
        #servo.mid()
        #sleep(.5)
        #print("mid")
#    else:
#        servo.min()
#        sleep(.05)
#        print("min")
#for sample in serv_loc:
#        servo.value = sample
    
#serv_test = np.linspace(-1,.1,1)
#while True:
    
#    servo.value = -1
#    print("min")
#    sleep(.5)
#    servo.value = 1
#   print("max")
#    sleep(.5)
#for pos in serv_test:
    #servo.value = pos
    #sleep(2)
    