import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from keras.models import load_model
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
from gtts import gTTS
import os
import playsound #note: pip install playsound==1.2.2
import json
import random
from tkinter import *
from googletrans import Translator #note: pip install googletrans==4.0.0rc1
import wikipedia
import requests
import webbrowser
from googlesearch import search
model = load_model('chatbot_model.h5')

intents = json.loads(open('intents.json', encoding="utf8").read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

#---------------------------Open app--------------------------------------
def open_application(text):
    note = ""
    text = text.lower()
    if text == "google" or text == "chrome":
        os.startfile(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')
        note = "Google Chrome đã được mở"
    elif "word" in text:
        os.startfile(r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE')
        note = "Word đã được mở"
    elif "excel" in text:
        os.startfile(r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE')
        note = "Excel đã được mở"
    else:
        note ="Ứng dụng chưa được cài đặt. Bạn hãy thử lại!"
    return note

#----------------------Weather---------------------------
def current_weather(name):
    ow_url = "http://api.openweathermap.org/data/2.5/weather?"
    city = name
    api_key = "fe8d8c65cf345889139d8e545f57819a"
    call_url = ow_url + "appid=" + api_key + "&q=" + city + "&units=metric"
    response = requests.get(call_url)
    data = response.json()
    if data["cod"] != "404":
        city_res = data["main"]
        current_temperature = city_res["temp"]
        current_humidity = city_res["humidity"]
        suntime = data["sys"]
        sunrise = datetime.fromtimestamp(suntime["sunrise"])
        sunset = datetime.fromtimestamp(suntime["sunset"]) 
        now = datetime.now()
        content = """Hôm nay là ngày {day} tháng {month} năm {year}
Mặt trời mọc vào {hourrise} giờ {minrise} phút
Mặt trời lặn vào {hourset} giờ {minset} phút
Nhiệt độ trung bình là {temp} độ C
Độ ẩm là {humidity}%""".format(day = now.day,month = now.month, year= now.year, hourrise = sunrise.hour, minrise = sunrise.minute,
                                                                           hourset = sunset.hour, minset = sunset.minute, 
                                                                           temp = current_temperature, humidity = current_humidity)
        return content
    else:
        return "Không tìm thấy địa chỉ của bạn"
#--------------------open web----------------------------
def open_website(text):
    # to search
    query = str(text)
    for j in search(query, tld="co.in", num=1, stop=1, pause=2):
        url = str(j)
    webbrowser.open(url)
    note = "Trang web bạn yêu cầu đã được mở."
    return note
#--------------------Window_Chatbox---------------------
base = Tk()
base.title("Chatbox")
base.geometry("400x600")
base.resizable(width=FALSE, height=FALSE)

#----------------(Image)--------------------
mic= tk.PhotoImage(file = 'E:/python/chatbot/Mic_button.png')
sendbut= tk.PhotoImage(file = 'E:/python/chatbot/Send_button.png')

#------------------micro<input>-----------------------
r = sr.Recognizer()
class set:
    check = ""
    def add(self, check):
        self.check = check
is_on = set() 
is_on.add("False")
def switch():
    is_on.add("True")
    with sr.Microphone() as source:
        audio_data = r.record(source, duration=3)
        try:
            text = (r.recognize_google(audio_data, language="vi"))
        except:
            text = "Tôi không hiểu.."
        if text == "Tôi không hiểu..":
            is_on.check = "False"
        EntryBox.insert(INSERT, text)

#----------------set_voice_bot------------------------
def speak(text):
    tts = gTTS(text = text, lang ='vi')
    tts.save('voice.mp3')
    playsound.playsound('voice.mp3')
    os.remove('voice.mp3')

#----------------Send_mess-------------------------
def send(event):

    #-----------------Keyboard---------------------
    msg = EntryBox.get().strip()
    EntryBox.delete(0, 'end')
    if msg != '':
    #------------time_now----------------
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.strftime("%a, %d %B, %Y")
    #--------------msg<output>-------------
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, " ", ("right"))
        ChatLog.tag_config("right", justify="right")
        ChatLog.insert(END, current_time , ("small", "right", "greycolour"))
        ChatLog.yview(END)
        ChatLog.insert(END, "\n")
        ChatLog.insert(END, " ", ("right"))
        ChatLog.tag_config("right", justify="right")
        ChatLog.window_create(END, window=Label(ChatLog, fg="white", text= str(msg), 
        wraplength=201, font=("Arial", 13), bg="#1a8ade", bd=4, justify="left"))
        ChatLog.insert(END,'\n')
        ChatLog.config(foreground="#0000CC", font=("Helvetica", 9))
        ChatLog.yview(END)

    #--------------bot<output>---------------
        res = ''
        #------------------today-----------------
        if "1" in msg:
            res = str(today)
        #-----------search with wiki------------
        elif "2" in msg:
            wikipedia.set_lang("vi")
            res = wikipedia.summary(msg[2:], sentences = 1)
        #-----------Translate vi-en-vi-----------
        elif "3" in msg:
            translator = Translator()
            trans = translator.translate(str(msg[2:]), src = 'vi', dest = 'en')
            res = trans.text
        elif "4" in msg:
            translator = Translator()
            trans = translator.translate(str(msg[2:]), src = 'en', dest = 'vi')
            res = trans.text
        #----------weather----------------------
        elif "5" in msg:
            res = current_weather(str(msg[2:]))
        elif "6" in msg:
            x = open_application(str(msg[2:]))
            res = x
        elif "7" in msg:
            res = open_website(str(msg[2:]))
        else:
            res = chatbot_response(msg)
        ChatLog.insert(END, current_time+'\n', ("small", "left", "greycolour"))
        ChatLog.window_create(END, window=Label(ChatLog, fg="#000000", text=res, 
        wraplength=200, font=("Arial", 13), bg="#DDDDDD", bd=4, justify="left"))
        ChatLog.insert(END, '\n')
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
    #------------voice_bot<output>------------
        if is_on.check == "True":
            is_on.check = "False"
            speak(res)       

#-----------------background----------------------------
img = tk.PhotoImage(file = 'E:/python/chatbot/Background.png')
bgr = ttk.Label(base,
                 image = img)
#---------------Create Chat window----------------------
ChatLog = Text(base, bd=0, bg="#f0f0f0", height="8", width="50", font="Arial",)
ChatLog.config(state=DISABLED)

#-------------------Bind scrollbar to Chat window--------------------
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

#------------------Create Button to on/off micro------------------------  
t_btn = Button(base, image = mic, bg="white", bd=0, width=35, height = 35, activebackground="red", command = switch)
#------------------Create Button to send message------------------------  
SendButton = Button(base, image = sendbut, width= 50, height=50,
                    bd=0, activebackground="white",
                    command = send )
base.bind('<Return>', send)
#-------------------Create the box to enter message-----------------------
EntryBox = Entry(base, bd=0, bg="white",width="29", font="Arial")

#--------------Place all components on the screen--------------------
bgr.place(x=0,y=0, width= 400, height=600)
scrollbar.place(x=378,y=100, height=420)
ChatLog.place(x=8,y=100, height=404, width=365)
EntryBox.place(x=28, y=538, height=35, width=235)
SendButton.place(x=332, y=530, height=50, width = 50)
t_btn.place(x=266, y=537, width=35, height = 35)
base.mainloop()
#---------------------------------------------------------------------
#python chatboxtest.py