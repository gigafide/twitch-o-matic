#!/usr/bin/env python3 
import subprocess
import picamera
import time
import RPi.GPIO as GPIO


#SETUP GPIO CONTROLS
GPIO.setmode(GPIO.BCM)
#BUTTON GPIO
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#BUTTON LED GPIO
GPIO.setup(17, GPIO.OUT)
#LIGHT PANEL 1
GPIO.setup(23, GPIO.OUT)
#LIGHT PANEL 2
GPIO.setup(25, GPIO.OUT)

#SETUP STREAMING COMMAND VARIABLES
TWITCH = "rtmp://live.justin.tv/app/"
KEY= "ENTER YOUR PRIVATE KEY HERE"
#todo: clean up command to make stream faster
stream_cmd = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + TWITCH + KEY 
stream_pipe = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE) 

#SETUP CAMERA VARIABLES
camera = picamera.PiCamera(resolution=(1080, 720), framerate=25) 

#CREATE VARIABLE TO SIGNIFY WHEN STREAMING
start_stream = 0

try: 
	#MAKE SURE ALL LED'S ARE OFF
	GPIO.output(17, False)
	GPIO.output(23, False)
	GPIO.output(25, False)
	while True:
		#SET VARIABLE FOR BUTTON
		input_state = GPIO.input(14)
		#IF BUTTON IS TRIGGERED AND NOT STREAMING, THEN START STREAM
		if input_state == False and start_stream == 0:
			start_stream = 1
			camera.start_recording(stream_pipe.stdin, format='h264', bitrate = 2000000)
			GPIO.output(17, True)
			GPIO.output(23, True)
			GPIO.output(25, True)
			print('recording started')
			time.sleep(0.2)
		#IF BUTTON IS TREGGERED AND STREAMING, CONTINUE STREAM
		elif input_state == False and start_stream == 1:
			camera.wait_recording(1)
		#IF BUTTON IS NOT TRIGGERED AND STREAMING, STOP STREAM
		elif input_state == True and start_stream ==1:
			start_stream = 0
			camera.stop_recording()
			print("stopped recording")
			time.sleep(0.2)
		#IF BUTTON IS NOT TRIGGERED AND NOT STREAMING, TURN LED'S OFF
		elif input_state == True and start_stream == 0:
			GPIO.output(17, False)
			GPIO.output(23, False)
			GPIO.output(25, False)
			time.sleep(0.2)
			print('awaiting input')
#ON KEYBOARD INTERRUPT, CLOSE CAMERA, STREAM AND CLEAN UP GPIO
except KeyboardInterrupt:
	camera.close()
	print("keyboard interrupt")
finally:
	stream_pipe.stdin.close()
	stream_pipe.wait()
	GPIO.cleanup()
	print("Camera safely shut down")
	print("Good bye")
