import random

def compile_convo_dict():
  welcome_response_mo= ["Hello Mauricio", "What's up Mauricio", 
                      "Welcome back Mauricio",
                      "What's up dawg"]
  waiting_responses = ["How can I help Chief?", 
                      "What can I help you with?", 
                      "You got another question?",
                      "Hey boss, what can I get you with?"]
  
  feels = []
  text = ["jokes.txt","roasts.txt","feels.txt"]
  jokes = [] 
  roasts = [] 
  one_list = [jokes,roasts,feels]
  
  for item in range(len(text)):
    data = open(text[item],"r", errors = "ignore")
    one_list[item] = [j for j in data]
    data.close()
  welcome_dict = {"welcomes":welcome_response_mo,
                  "responses":waiting_responses,
                  "jokes" : one_list[0],
                  "roasts": one_list[1],
                  "feels": one_list[2]}
  return welcome_dict
  
#print(compile_convo_dict())
  
