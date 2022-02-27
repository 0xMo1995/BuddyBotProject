from gpiozero import RGBLED
from time import sleep

led = RGBLED(17,27,22,initial_value = (0,0,1))

#status = {
			#"error": None,
			#"transcription": None
			#}

def waiting_LED(status):
	
		if status["error"] is None and status["transcription"] is None:
			#blinks blue
			# led.pulse(fade_in_time = 1, fade_out_time = 10, 
			# on_color = (0,0,1), off_color = (0,0,0))
			led.color = (0,0,1)
			sleep(1)
		elif status["error"] == "sorry could not recognize what you said":
			deny_LED()
		else:
			rec_LED()
		
def rec_LED():
	
	#blinks green
	#led.pulse(fade_in_time = 1, fade_out_time = 10, 
	#on_color = (0,1,0), off_color = (0,0,0))
	led.color = (0,1,0)
	sleep(1) 
		
def deny_LED():
	
	#blinks red
	#led.pulse(fade_in_time = 1, fade_out_time = 10, 
	#on_color = (1,0,0), off_color = (0,0,0))
	led.color = (1,0,0)	
	sleep(1)
		
def reply_LED():
	led.color = (0,1,0)
	sleep(1)
	
#waiting_LED(status)

#reply_LED()	
# i = 0
# while i < 10:
	
	# led.pulse(fade_in_time = 1, fade_out_time = 10, on_color = (1,0,0), 
				# off_color = (0,0,0))
	# sleep(1)
	#led.color = (1,0,0)# red
	#sleep(1)
	#led.color = (1,,1)#green
	#sleep(1)
	#led.color = (0,0,1)#blue
	#sleep(1)
	#i += 1

#(0,1,1)  = cyan
#(1,1,0) = ???
#(1,0,1) = purple
