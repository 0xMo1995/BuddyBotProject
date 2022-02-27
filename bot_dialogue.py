import nltk
import random
import string
import re, string,unicodedata
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
import wikipedia as wk
from collections import defaultdict
import warnings
from googlesearch import search
import pyaudio
import wave
import convo_dictionary as cd

warnings.filterwarnings("ignore")
#nltk.download("punkt")
#nltk.download("wordnet")
#nltk.download("averaged_perceptron_tagger")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity,linear_kernel
#from gtts import gTTS
from newspaper import Article

def convo_reload():
    
    data = open('conversation_dialogue.txt','r',errors = 'ignore')
    raw = data.read()
    raw =raw.lower()
    sent_tokens = nltk.sent_tokenize(raw)
    return sent_tokens



#query = "roasts on afros"
def google_search(query):
    url_list = []
    for j in search(query,tld = "com",lang = 'en', num = 10,start = 3, stop = 5, pause =2):
        url_list.append(j)
        
    return url_list
    
def get_article_text(urls):
    url_text = []
    for a in urls:
        article = Article(url = a, language = 'en')
        article.download()
        article.parse()
        article.nlp()
        url_text.append(article.text)
        
    with open('conversation_dialogue.txt','r+') as filehandle:
        for item in url_text:
            filehandle.write("{}\n".format(item))
            
def Normalize(text):
    remove_punct_dict = dict((ord(punct),None) for punct in string.punctuation)
    #word tokenization
    
    word_token = nltk.word_tokenize(text.lower().translate(remove_punct_dict))
    
    #remove ascii
    new_words = []
    for word in word_token:
        new_word = unicodedata.normalize('NFKD',word).encode('ascii','ignore').decode('utf-8','ignore')
        new_words.append(new_word)
        
    rmv = []
    for w in new_words:
        text = re.sub("&lt;/?.*gt;","&lt;&gt;",w)
        rmv.append(text)
        
    tag_map = defaultdict(lambda : wn.NOUN)
    tag_map['J'] = wn.ADJ
    tag_map['V'] = wn.VERB
    tag_map['R'] = wn.ADV
    lmtzr = WordNetLemmatizer()
    lemma_list = []
    rmv = [i for i in rmv if i]
    for token,tag in nltk.pos_tag(rmv):
        lemma = lmtzr.lemmatize(token, tag_map[tag[0]])
        lemma_list.append(lemma)
    return lemma_list

welcome_input = ('hello', 'hi', 'sup dawg', "what's up","hey man")

welcome_response = ["hi","hey","what's up mauricio", "*nods*", "hi there", "hello"]

def welcome(user_response):
    for word in user_response.split():
        if word.lower() in welcome_input:
            return random.choice(welcome_response)
        
def generateResponse(user_response):
    sent_tokens = convo_reload()
    robo_response = ""
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer = Normalize, stop_words = 'english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = linear_kernel(tfidf[-1],tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    
    if(req_tfidf==0) or "tell me about" in user_response:
        print("Checking the Interwebs")
        if user_response:
            #reg_ex = re.search("tell me about (.*)", user_response)
            #topic = reg_ex.group(1)
            #generateResponse(topic)
            robo_response = str(wikipedia_data(user_response))
            return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        
    sent_tokens.remove(user_response)
    return robo_response
    
def wikipedia_data(inp):
    reg_ex = re.search('tell me about (.*)', inp)
    try:
        if reg_ex:
            topic = reg_ex.group(1)
            wiki = wk.summary(topic, sentences = 3)
            return wiki
    except Exception as e:
        return 'No Content has been found'
        
#url = google_search(query)
#get_article_text(url)

