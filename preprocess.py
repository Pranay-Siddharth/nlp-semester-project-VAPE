import re
import spacy,benepar
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'})
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
    def __repr__(self):
        return self.text

class Document():
    def __init__(self,text):
        self.text=text

        self.doc=nlp(text)
        """for token in self.doc:
            print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)"""
        self.sentences=[]
        parts=re.split("\.|\n",text)
        #This segmentation is weak, it splits "p.m." and "6.2" into two sentences. 
        #It lackes any context
        #Perhaps replace with spacy?
        for part in parts:
            if(len(part)>0):
                self.sentences.append(Sentence(part))
    def answer(self,question):
        q=nlp(question)
        #print(dir(q))
        sent=list(q.sents)[0]
        #print(sent._.parse_string)
        if('SBARQ' in sent._.labels):
            clause=None
            for child in sent._.children:
                if("SQ" in child._.labels):
                    clause=child
            (best_sent,best_phrase,best_sentval)=(None,None,0)
            if clause is not None:
                for child in clause._.children:
                    if("NP" in child._.labels):
                        noun=child 
                        break
                for sent in self.doc.sents:
                    matchnum=phrase_score(sent,clause)
                    if(matchnum[0]>best_sentval):
                        #print(matchnum)
                        best_sentval=matchnum[0]
                        best_sent=sent
                        best_phrase=matchnum[1]
                print("question is: ",question)
                #print(clause._.parse_string)
                print("best sentence is: ",best_sent)
                #print(best_sent._.parse_string)
                #print("best phrase is: ",best_phrase)
                verb=locate_type(clause,"VP")
                answer=None
                vp=None
                if(verb is None):
                    for word in best_sent:
                        if(word.lemma_ =="be"):
                            print("found is!")
                            vp=containing_type(word,"VP")
                            answer=str(noun)+" "+str(vp)
                            break
                else:
                    for i in range(len(best_sent)-len(verb)+1):
                        phraselemma=best_sent[i:i+len(verb)].lemma_
                        if(verb.lemma_ == phraselemma):
                            print("found verb phrase!")
                            vp=containing_type(best_sent[i],"VP")
                            answer=str(noun)+" is "+str(vp)
                            break
                if vp is None:
                    print("error in finding VP")
                    return
                print("VP is: " ,vp)
                print("Answer is: ",answer)
                return answer


def phrase_score(phrase1,phrase2):
    child1=expand_children(phrase1)
    child2=expand_children(phrase2)
    lemma1=set([word.lemma_ for word in child1])
    overlap=[]
    banlist=["be"]
    for word in child2:
        if word.lemma_ in lemma1 and word.lemma_ not in banlist:
            overlap.append(word)
    #print(overlap)
    score=0
    max_len=0
    best_phrase=None
    for phrase in overlap:
        score+=len(phrase)
        if(len(phrase)>max_len):
            max_len=len(phrase)
            best_phrase=phrase
    return (score,best_phrase)
def expand_children(words):
    L=[words]
    for child in words._.children:
        L+=expand_children(child)
    return L                  
        #print(list(sent._.children))
        #print([chunk.text for chunk in self.doc.noun_chunks])

def containing_type(phrase,type):
    if phrase is None:
        return None
    #print(phrase,phrase._.labels)
    if(type in phrase._.labels):
        return phrase 
    return containing_type(phrase._.parent,type)

def find_nearest_np(phrase):
    if phrase is None or phrase._.parent is None:
        return None
    siblings=list(phrase._.parent._.children)
    if(len(siblings)==0):
        return None
    for sibling in siblings:
        if (phrase.lemma_ != sibling.lemma_):
            noun=locate_type(sibling,"NP")
            if(noun is not None):
                return sibling
    return find_nearest_np(phrase._.parent)

def locate_type(sent,type):
    if(type in sent._.labels):
        return sent 
    for child in sent._.children:
        located=locate_type(child,type)
        if located is not None:
            return located

def match_subtree(sent,phrase):
    if(sent.lemma_==phrase.lemma_):
        return sent 
    for child in sent._.children:
        match=match_subtree(child,phrase)
        if(match is not None):
            return match

def load_file(path):
    with open(path,'r') as f:
        text=f.read()
        return Document(text)

answerer=load_file("../Course-Project-Data/set2/a5.txt")
answerer.answer("What is Delta Cancri also known as?")
answerer.answer("What is cancer bordered by?")
#answerer.answer("What is the brightest star in Cancer?")
answerer.answer("What is cancers astrological symbol?")
#answerer.answer("Who placed the crab among the stars?")
answerer.answer("What latitudes can Beta Cancri be seen between?")
answerer.answer("What open cluster is located right in the centre of cancer?")
answerer.answer("What month was cancer assosciated with?")
answerer.answer("What type of star is 55 Cancri?")
"""
s1="Cancer is a medium-sized constellation that is bordered by Gemini to the west, Lynx to the north, Leo Minor to the northeast, Leo to the east, Hydra to the south, and Canis Minor to the southwest."
print(list(nlp(s1).sents)[0]._.parse_string)
s2="bordered by" """