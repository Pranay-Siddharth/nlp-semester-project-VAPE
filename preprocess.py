import re
import spacy
class Word():#Also only does a so-so job, leaves commas attached to the words they are part of
    def __init__(self,text):
        self.text=text
    def __repr__(self):
        return "("+self.text+")"
class Sentence():
    def __init__(self,text):
        self.text=text
        self.words=re.split(" ",text)
        self.words=[Word(word) for word in self.words if len(word)>0]
        print(self.words)
    def __repr__(self):
        return self.text

class Document():
    def __init__(self,text):
        self.text=text
        parts=re.split("\.|\n",text)
        #This segmentation is weak, it splits "p.m." and "6.2" into two sentences. 
        #It lackes any context
        #Perhaps replace with spacy?
        self.sentences=[]
        for part in parts:
            if(len(part)>0):
                self.sentences.append(Sentence(part))


def load_file(path):
    with open(path,'r') as f:
        text=f.read()
        return Document(text)

load_file("../Course-Project-Data/set2/a5.txt")