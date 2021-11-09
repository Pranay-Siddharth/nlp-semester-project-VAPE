import re
import spacy,benepar
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_lg")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'})

class Document():
    def __init__(self,text):
        self.text=text
        self.doc=nlp(text)
    def answer(self,question):
        print()
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
                noun=None
                for child in clause._.children:
                    if("NP" in child._.labels):
                        noun=child 
                        break
                for qsent in self.doc.sents:
                    matchnum=phrase_score(qsent,sent)
                    if(matchnum>best_sentval):
                        #print(matchnum)
                        best_sentval=matchnum
                        best_sent=qsent
                print("question is: ",question)
                #print(clause._.parse_string)
                print("best sentence is: ",best_sent)
                #print(best_sent._.parse_string)
                #print("best phrase is: ",best_phrase)
                verb=locate_type(clause,"VP")
                answer=None
                vp=None
                q_lemma=set([word.lemma_ for word in q])
                if(verb is None):
                    for i,word in enumerate(best_sent):
                        print(word,word.ent_iob_)
                        if(word.ent_iob==3 and (word.lemma_ not in q_lemma)):
                            end=i+1
                            while(end<len(best_sent) and best_sent[end].ent_iob==1):
                                end=end+1
                            np=best_sent[i:end]
                            answer=str(np)+" "+str(q[1:])
                            break
                    if(answer is None):
                        for word in best_sent:
                            if(word.lemma_=="be"):
                                verb=word
                if(answer is None and verb is not None):
                    print("verb is: ",verb)
                    bestscore=-1
                    for i in range(len(best_sent)-len(verb)+1):
                        score=verb.similarity(best_sent[i:i+len(verb)])
                        if(score>bestscore):
                            bestscore=score
                            vp=containing_type(best_sent[i],"VP")
                            answer=str(noun)+" "+str(vp)
                if answer is None:
                    print("error in finding answer")
                    return
                print("VP is: " ,vp)
                print("Answer is: ",answer)
                return answer

def phrase_score(phrase1,phrase2):
    child1=expand_children(phrase1)
    child2=expand_children(phrase2)
    #print(child1,child2)
    overlap=[]
    thresh=.95
    for word1 in child1:
        for word2 in child2:
            score=word1.similarity(word2)
            if(score>thresh or word1.lemma_==word2.lemma_):
                if(len(word1)<len(word2)):
                    overlap.append(word1)
                else:
                    overlap.append(word2)
    dedup_overlap=[]
    dedup_lemma=set(["be"])
    for word in overlap:
        if word.lemma_ not in dedup_lemma:
            dedup_lemma.add(word.lemma_)
            dedup_overlap.append(word)
    if(len(dedup_overlap)>0):
        pass
        #print(dedup_overlap)
    score=sum([len(phrase) for phrase in dedup_overlap])
    return score
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
#answerer.answer("What is Delta Cancri also known as?")
#answerer.answer("What is cancer bordered by?")
answerer.answer("What is the brightest star in Cancer?")
answerer.answer("What is cancers astrological symbol?")
#answerer.answer("What latitudes can cancer be seen at?")
answerer.answer("What open cluster is located right in the centre of cancer?")
#answerer.answer("What month was cancer associated with?")
#answerer.answer("What did Heracles battle?")
"""
s1="Cancer is a medium-sized constellation that is bordered by Gemini to the west, Lynx to the north, Leo Minor to the northeast, Leo to the east, Hydra to the south, and Canis Minor to the southwest."
print(list(nlp(s1).sents)[0]._.parse_string)
s2="bordered by" """