from flask import Flask, request
import json
app = Flask(__name__)
import serial
import smtplib
import logging
import platform
import subprocess
import sys
import threading
from google.assistant.library.event import EventType
from aiy.assistant import auth_helpers
from aiy.assistant.library import Assistant
from aiy.board import Board, Led
from aiy.voice import tts
import time
SMTP_SERVER = 'smtp.gmail.com' 
SMTP_PORT = 587 
GMAIL_USERNAME = 'tsha813@gmail.com'
GMAIL_PASSWORD = '' #hidden for security ;)


class Emailer:
    def sendmail(self, recipient, subject, content):

        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        #session.sendmail(GMAIL_USERNAME, recipient, headers.decode('utf-8') + "\r\n\r\n" + content.decode('utf-8'))
        session.quit

sender = Emailer()
sendTo = 'tsha813@gmail.com'
ser = serial.Serial('/dev/ttyACM0',9600,timeout=1)
ser.reset_input_buffer()
light = 0
lock = 0
garage = 0
temp = 0
actual_temp = 75
wanted_temp = 0
check_temp = 0
email = 0
light_bool = False
door_bool = False
@app.route('/receive', methods=['POST'])
def receive():
    data = json.loads(request.data.decode('utf-8'))
    global light
    global lock
    global garage
    global temp
    global actual_tmep
    global wanted_temp
    global check_temp
    global email
   # print(data['direction'])
    if data['direction'] == 'unlock1':
        lock = 1
        
    elif data['direction'] == 'lock1':
        lock = 0
          
    if data['direction'] == 'on1':
        light = 1

    elif data['direction'] == 'off1':
        light = 0
    
    if data['direction'] == 'unlock2':
        garage = 1
	

    elif data['direction'] == 'lock2':
        garage = 0
    
    if data['direction'] == 'tempu':
        temp = 1
        if check_temp == 0:
            wanted_temp = actual_temp
            check_temp = 1
        wanted_temp = wanted_temp + 1
        
    elif data['direction'] == 'tempd':
        temp = 0
        if check_temp == 0:
            wanted_temp = actual_temp
            check_temp = 1
        wanted_temp = wanted_temp - 1
    else:
        temp = 2
        
    if data['direction'] == 'email':
        email = 1
	
    ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))
    print(str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n')
    
    if email == 1:
        #line = ser.readline().decode('utf-8')
        email_str = ""
        print("sending email...")
        if light_bool:
            email_str = email_str + "The light is on."
        else:
            email_str = email_str + "The Light is off."
            
        if door_bool:
            email_str = email_str + " The door is locked."
        else:
            email_str = email_str + " The door is unlocked."
        
        email_str = email_str + " The temperature in the house is " + str(actual_temp) + " degrees."
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        sender.sendmail(sendTo,"House devices status", email_str)
        email = 0
    return "Woop Woop this finally worked"

def light_on():
    global light
    light = 1
    ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))
    
    
    
def light_off():
    global light
    light = 0
    ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))
    
def lock_on():
    global lock
    lock = 1
    ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))
    
    
def lock_off():
    global lock
    lock = 0
    ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))

def garage_on():
    global garage
    garage = 1
    ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))

def garage_off():
    global garage
    garage = 0
    ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))

def email_send():
    global email
    email = 1
    ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))
    email_str = ""
    print("sending email...")
    if light_bool:
        email_str = email_str + "The light is on."
    else:
        email_str = email_str + "The Light is off."
        
    if door_bool:
        email_str = email_str + " The door is locked."
    else:
        email_str = email_str + " The door is unlocked."
    
    email_str = email_str + " The temperature in the house is " + str(actual_temp) + " degrees."
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    sender.sendmail(sendTo,"House devices status", email_str)
    email = 0

def temp_up():
	global temp
	temp = 1
	ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))
	temp = 2

def temp_down():
	global temp
	temp = 0
	ser.write((str(light)+ ' ' + str(lock) + ' ' + str(garage) + ' ' + str(temp) + ' ' + str(email) + '\n' ).encode('utf-8'))
	temp = 2

def process_event(assistant, led, event):
    logging.info(event)
    if event.type == EventType.ON_START_FINISHED:
        led.state = Led.BEACON_DARK  # Ready.
        print('Say "OK, Google" then speak, or press Ctrl+C to quit...')
    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        led.state = Led.ON  # Listening.
    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if text == 'turn on the light':
            assistant.stop_conversation()
            light_on()
        elif text == 'turn off the light':
            assistant.stop_conversation()
            light_off()
        elif text == 'unlock the door':
            assistant.stop_conversation()
            lock_on()
        elif text == 'lock the door':
            assistant.stop_conversation()
            lock_off()
        elif text == 'open the garage door':
            assistant.stop_conversation()
            garage_on()
        elif text == 'close the garage door':
            assistant.stop_conversation()
            garage_off()
        elif text == 'send current status':
            assistant.stop_conversation()
            email_send()
        elif text == 'turn up the temperature':
            assistant.stop_conversation()
            temp_up()
        elif text == 'turn down the temperature':
            assistant.stop_conversation()
            temp_down()
   
    elif event.type == EventType.ON_END_OF_UTTERANCE:
        led.state = Led.PULSE_QUICK  # Thinking.
    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
          or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
          or event.type == EventType.ON_NO_RESPONSE):
        led.state = Led.BEACON_DARK  # Ready.
    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)
        
def main():
    logging.basicConfig(level=logging.INFO)
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    credentials = auth_helpers.get_assistant_credentials()
    with Board() as board, Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, board.led, event)
def flask_run():
	app.run(host='192.168.1.201', port=5000)
	
def voice_run():
	main()
if __name__ == '__main__':
    flask_thread = threading.Thread(target=flask_run)
    voice_thread = threading.Thread(target = voice_run)
    flask_thread.start()
    voice_thread.start()
    flask_thread.join()
    voice_thread.join()

