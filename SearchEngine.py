import tkinter as tk
import requests
import time
from math import log, sqrt # scoring requires math
from collections import defaultdict
import nltk # inbuilt lib functions for porting and stemming
import os 
import sys
from PIL import Image, ImageTk

# GUI
HEIGHT = 600
WIDTH = 600
#invIndexDict = defaultdict(list)
numDocs = 0 # global number of dcouments
vectOfDocs = []  # each vector is a dictionary and each dict is a map from token to frequency for one document ( TF )
mapOfDocs = {} # Inverted indexing. Doc - > Vector with line numbers for tokens
docFreqVector = {} # ( IDF )
directory="" # global



### DOCUMENT INDEXING FUNCTIONS ###

# get N
def getNumDocs():
    """
    Get number of documents.
    """
    global numDocs
    x=directory
    count=0
    for file in os.listdir(x):
        count=count+1
    numDocs = count+1

# like an init function for creating vectors
def getTFforAllDocs():
    """
    Run various processing functions for each document sequentially.
    """
    x=directory  
    for file in os.listdir(x):
        RawText = getText(x,file)
        toks = getTokens(RawText)
        vect = getCurrentDocVector(toks)
        vectOfDocs.append(vect)

# open and read file 
def getText(x,file):
    """
    Parse documents to get text.
    """
    try:
        text = open(x+'/'+file).read() # open and read text
    except:
        text = ""
    return text

# tokenizing by porting, stemming using nltk lib functs
def getTokens(RawText):
    """
    Tokenization, stemming using the nltk PorterStemmer.
    """
    tokens = nltk.word_tokenize(RawText)
    portStem = nltk.stem.PorterStemmer()
    toks = [] # new list with PSed tokens
    for word in tokens:
        toks.append(portStem.stem(word))
    return toks

# vector from list (toks) containing token -> freq 
def getCurrentDocVector(toks):
    """
    Builds TF vector and also updates IDF value.
    """
    mapTokToFreq = {}  # current doc map
    global docFreqVector # for all docs map
    for token in toks:
        if token in mapTokToFreq:
            mapTokToFreq[token] += 1 # tf
        else:
            mapTokToFreq[token] = 1
            if token in docFreqVector:
                docFreqVector[token] += 1 # number of docs with this token
            else:
                docFreqVector[token] = 1
    return mapTokToFreq

# uses vectofdocs for gen inverted index ( doc - line number - tokens )
def getInvIndexes(): 
    """
    Makes a map for each document from tokens to line number. 
    """
    for file in os.listdir(directory):
        lineNum=1
        tempvect = defaultdict(list)
        f = directory+'/'+file
        lines=open(f,encoding="latin-1").read().splitlines() # might need to change encoding w.r.t type of data
        ps = nltk.stem.PorterStemmer()
        for cur_line in lines:
            toks = nltk.word_tokenize(cur_line)
            for word in toks:
                tempvect[ps.stem(word)].append(lineNum)
            lineNum=lineNum+1;      
        mapOfDocs[file] = tempvect

# changes all the freq vectors to tf-idf unit vectors with scores
def getTfIdf():
    """
    Converts term frequency and inverse document frequency to TF-IDF score.
    """
    for vect in vectOfDocs: # for each document
        length = 0.0
        for word in vect:
            word_freq = vect[word]
            temp = calcTfIdfScoreX(word, word_freq)
            vect[word] = temp
            length += temp ** 2

        length = sqrt(length)
        if length != 0:
            for word in vect:
                vect[word] /= length # length normalize to unit vector so that 
                # cosine similarity can be calculated properly later on cos_sim = dot(a, b)/(norm(a)*norm(b))

# Calculates tf-idf score for each document using number of docs, docfreq of token, freq of token
def calcTfIdfScoreX(word, freq):
    """
    Calculates td-idf square using formula - log(1 + freq) * log(numDocs / docFreqVector[word])
    """
    return log(1 + freq) * log(numDocs / docFreqVector[word])


### QUERY FUNCTIONS ###

# creates a tf dict from a query 
def getCurrentDocVectorQuery(toks):
    """
    Build term frequency dictionary for document.
    """
    vect = {}
    for token in toks:
        if token in vect:
            vect[token] += 1.0
        else:
            vect[token] = 1.0
    return vect

# query into a tf-idf unit vector 
def convertQToTfIdf(qvec):
    """
    Converts term frequency and inverse document frequency to TF-IDF score for query.
    """
    length = 0.0
    for word in qvec:
        word_freq = qvec[word]
        if word in docFreqVector:  
            qvec[word] = calcTfIdfScore(word, word_freq)
        else:
            qvec[word] = log(1 + word_freq) * log(numDocs)  
            # special case ( w1 w2 w3 0.12 0.14 0.15 ) then ( w4 added but suppose it is in none of the docs, 
            # hence we want result different from the pervious query )
        length += qvec[word] ** 2 # norm
    length = sqrt(length)
    if length != 0:
        for word in qvec:
            qvec[word] /= length

# dot product of vector1 and vector2
def getDotProduct(v1, v2):
    """
    Get product between one document and query vector.
    """
    # v1.len < v2.len
    if len(v1) > len(v2):
        temp = v1
        v1 = v2
        v2 = temp
    keys1 = v1.keys()
    keys2 = v2.keys()
    sum = 0
    for i in keys1:
        if i in keys2:
            sum += v1[i] * v2[i]
    return sum

# Calculates tf-idf score for query using number of docs, docfreq of tokens, freq of tokens
def calcTfIdfScore(word, freq):
    """
    Calculates td-idf square for query using formula - log(1 + freq) * log(numDocs / docFreqVector[word])
    """
    return log(1 + freq) * log(numDocs / docFreqVector[word])

# get sorted list of relevant docs based on cosine similarity
def resFromQuery(qvec):
    """
    Get dot product of between query vector and each document vector.
    """
    listOfDocWeights = []
    x=directory
    count=0;
    for file in os.listdir(x):
        dotProd = getDotProduct(qvec, vectOfDocs[count]) # since vects already normalized, dot product = cos_sim
        listOfDocWeights.append((file, dotProd))
        listOfDocWeights = sorted(listOfDocWeights, key=lambda x: x[1], reverse=True) # rank by weights
        count=count+1
    return listOfDocWeights


### GUI CODE BEGINS ### 

# Called by GUI when user enters corpus address. Runs all pre-processing functions sequentially.
def getDir(dir):
    """
    Get directory of documents and then call pre-processing and indexing functions sequentially.
    """
    global directory
    directory = dir
    while True: 
        if directory == '9' :
            label['text'] = "Exited."
            break
        elif os.path.isdir(directory):
            label['text'] = f"Indexing {directory}. Please wait."
            break
        else :
            label['text'] = "Wrong directory. Please check or Press 9 to exit."
            break
    if directory == '9':
        root.destroy()
    # begin indexing and scoring!
    start_time = time.time()
    getNumDocs() # num docs
    getTFforAllDocs() # initialize vectOfDocs 
    getInvIndexes()
    getTfIdf() # vectOfDocs to tf-idf scores
    te = time.time() - start_time
    label['text'] = f"Successfully Indexed {directory}\n Please query now. --- Time (in seconds) for indexing is --- {te}"

# Called by GUI when user enters query. Runs retrieval functions sequentially
def getQuery(query):
    """
    Get query input and process the query.
    """
    # label['text'] = f "Your query is {query}."
    # begin querying
    if len(query) == 0 or query == "9" :
        label['text'] = "Goodbye. It's been real."
        root.after(3000,root.destroy())
    start_time = time.time()
    queryToks = getTokens(query)
    qvec = getCurrentDocVectorQuery(queryToks)
    convertQToTfIdf(qvec)
    res = resFromQuery(qvec)
    fin_str = f"Here are are the top 10 documents for the query - {query}\n"
    te = time.time() - start_time
    for doc in res[:10]:
        fin_str += ("\nDocument "+str(doc[0])+" with weight "+str(doc[1]))
    label['text'] = f"{fin_str}\n --- Time (in seconds) for retrieval is --- {te}"
    docIndexesPairs = set()
    ps = nltk.stem.PorterStemmer()
    for word in queryToks: 
        for doc in mapOfDocs:
            for linenum in mapOfDocs[doc][ps.stem(word)]:
                docIndexesPairs.add((linenum,doc))
    #for t in docIndexesPairs:
        #print(t)

    
### Begin GUI Tkinter ###

root = tk.Tk()

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

imagex = Image.open('apples.jpg')
photo = ImageTk.PhotoImage(imagex,master=root)
background_label = tk.Label(root, image=photo)
background_label.image = photo
background_label.place(relwidth=1, relheight=1)

frame = tk.Frame(root, bg='#C0C0C0', bd=5)
frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.085, anchor='n')

entry = tk.Entry(frame, font=40)
entry.place(relwidth=0.65, relheight=0.8)

button = tk.Button(frame, text="Enter Folder", font=30, command=lambda: getDir(entry.get()))
button.place(relx=0.7, relheight=0.8, relwidth=0.3)

frame2 = tk.Frame(root, bg='#C0C0C0', bd=5)
frame2.place(relx=0.5, rely=0.3, relwidth=0.75, relheight=0.085, anchor='n') 

entry2 = tk.Entry(frame2, font=40)
entry2.place(relwidth=0.65, relheight=0.8)

button2 = tk.Button(frame2, text="Enter Query", font=30, command=lambda: getQuery(entry2.get()))
button2.place(relx=0.7, relheight=0.8, relwidth=0.3)

lower_frame = tk.Frame(root, bg='#4F2412', bd=10)
lower_frame.place(relx=0.5, rely=0.45, relwidth=0.75, relheight=0.5, anchor='n')

label = tk.Label(lower_frame)
label.place(relwidth=1, relheight=1)

root.mainloop()