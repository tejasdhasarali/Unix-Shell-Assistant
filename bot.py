#!/usr/bin/env python
import sys
import re
import subprocess
import nltk
import spacy
import json
from textblob import TextBlob
from nltk.tokenize.toktok import ToktokTokenizer
# nltk.download('stopwords')
nlp=spacy.load('en')
tokenizer = ToktokTokenizer()
stopword_list = nltk.corpus.stopwords.words('english')

option="OPTIONS"
description="DESCRIPTION"
synopsis="SYNOPSIS"

def remove_special_characters(text):
    pattern = r'[^a-zA-z\s]'
    text = re.sub(pattern, '', text)
    return text

def remove_newline(text):
    return re.sub(r'[\r|\n|\r\n]+', ' ',text)

def getPOSTag(sentence):
    sentence_nlp = nlp(sentence)
    spacy_pos_tagged = [(word, word.tag_, word.pos_) for word in sentence_nlp]
    return spacy_pos_tagged

def lemmatize_text(text):
    text = nlp(text)
    text = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in text])
    return text


def remove_stopwords(text):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)    
    return filtered_text

def lemmatize_all(document):
    document=TextBlob(document)
    return " ".join([word.lemmatize() for word in document.words])
        

def checkTheNumberOfHipen(manFormattedDictionaryName):
    pattern=r"^[\t ]*-"
    cPattern=re.compile(pattern)
    count=0
    for line in manFormattedDictionaryName.split():
        if(re.search(cPattern,line)):
            count=count+1
    return count!=len(manFormattedDictionaryName.split())

def saveTheDict(dictionary):
    f = open('dict.txt', 'w+')
    f.write(json.dumps(dictionary))

def getTheDict():
    import os
    import json
    exists = os.path.isfile('dict.txt')
    if exists:
        f = open('dict.txt', 'r')
        return dict(json.loads(f.read()))
    else:
        return {}

def main():
    searchImprovementDict=getTheDict()
    status = True
    
    while(status):
        documents = []
        actions = []
        entities = []
        manualCount = {}
        selectedCommand=""

        print("\n")
        line = input("Ask me anything: ")
        
        if not (line):
            print("Please type the question to help you better!")
        else:
            if (line == "exit"):
                saveTheDict(searchImprovementDict)
                searchImprovementDict = getTheDict()
                break
            else:
                line = remove_special_characters(remove_newline(line))
                tokens = getPOSTag(line)
                action=""
                for token in tokens:
                    if (token[1].startswith("VB")):
                        action = lemmatize_all(str(token[0]))
                    elif (token[1].startswith("NN")):
                        entities.append(lemmatize_all(str(token[0])))

                
                if action:
                    actions.append(action+" "+" ".join(entities))
                    if(len(entities)>1):
                        for entity in entities:
                            actions.append(action+" "+entity)
                    actions.append(action)
                else:
                    actions.append(" ".join(entities))

                isManPagePresent=False
            
                for action in actions:
                    manuals = subprocess.Popen(('man -ks 1 "%s"' % action), shell = True, stdout = subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')

                    result = manuals.communicate()[0]

                    if (result) and ("nothing appropriate" not in result):
                        searchToken = action
                        isManPagePresent=True
                        manuals.stdout.close()
                        break
                    else:
                        manuals.stdout.close()    
            
                if not (isManPagePresent):
                    print("We could not find any matching query. Please try again!")
                else:
                    commandList=[]
                    for line in result.splitlines():
                        command = line.split(' ')
                        manual = subprocess.Popen(('man -P cat %s' % command[0]), shell = True, stdout = subprocess.PIPE, encoding='utf8')

                        manualText = manual.communicate()[0]
                        if ("GNU" in manualText):
                            commandList.append(command[0])
                            documents.append(manualText)
                    if not documents:
                        print("We could not find any matching query. Please try again!")
                    else:
                        print("...\n")

                        for action in actions:
                            for index, document in enumerate(documents):
                                document = remove_stopwords(document)
                                lem_doc = lemmatize_all(document)
                                manualCount[index] = len(re.findall('\\b'+searchToken+'\\b',lem_doc,flags=re.IGNORECASE))
                            doc = max(manualCount, key=manualCount.get)

                            if (manualCount[doc] !=0):
                                while((action+" "+commandList[doc]) in searchImprovementDict and len(manualCount)>1):
                                    if (searchImprovementDict[action+" "+commandList[doc]]<0):
                                        manualCount.pop(doc)
                                        doc= max(manualCount, key=manualCount.get)
                                    else:
                                        break
                                searchToken=action
                                break
                                
                        nlpOutput=searchToken

                        file = documents[doc].split('\n')
                        # for line in documents[doc]:
                        # print (file)
                        file.pop(0)
                        file.pop()

                        # print (file)
                        pattern=r"^[A-Z]"
                        cPattern=re.compile(pattern)
                        manFormattedDictionary={}
                        manFormattedDictionaryName=""
                        tempList=[]
                        
                        for line in file:
                            if (re.search(cPattern,line)):
                                if (manFormattedDictionaryName and tempList):
                                    manFormattedDictionary[manFormattedDictionaryName]=tempList
                                manFormattedDictionaryName=line.split()[0]
                                tempList=[] 
                            elif(manFormattedDictionaryName):
                                tempList.append(line)

                        searchKey=""
                        if(option in manFormattedDictionary):
                            searchKey=option
                        else:
                            searchKey=description

                        pattern=r"^[\t ]+(-[a-z|A-Z|0-9]{1})|^[\t ]+(--[a-z|A-Z|0-9]+)"
                        cPattern=re.compile(pattern)

                        manFormattedDictionaryName=""
                        tempList=[]
                        manFormattedDictionaryOptions={}
                        ifLineBreak=False
                        for line in manFormattedDictionary[searchKey]:
                            if(re.search(cPattern,line) and ifLineBreak):
                                if(manFormattedDictionaryName):
                                    if not(tempList):
                                        tempList.append(' '.join(manFormattedDictionaryName.split()[1:]))
                                        manFormattedDictionaryName=manFormattedDictionaryName.split()[0]
                                    if(checkTheNumberOfHipen(manFormattedDictionaryName)):
                                        tempList.insert(0,' '.join(manFormattedDictionaryName.split()[1:]))
                                        manFormattedDictionaryName=manFormattedDictionaryName.split()[0]
                                    manFormattedDictionaryOptions[manFormattedDictionaryName.strip()]=tempList
                                manFormattedDictionaryName=line
                                tempList=[]
                            elif(manFormattedDictionaryName and line):
                                tempList.append(line.strip())
                            
                            if (line):
                                ifLineBreak=False
                            else:
                                ifLineBreak=True

                        if(manFormattedDictionaryName and len(tempList)>0):
                            if not(tempList):
                                tempList.append(' '.join(manFormattedDictionaryName.split()[1:]))
                                manFormattedDictionaryName=manFormattedDictionaryName.split()[0]
                            if(checkTheNumberOfHipen(manFormattedDictionaryName)):
                                tempList.insert(0,' '.join(manFormattedDictionaryName.split()[1:]))
                                manFormattedDictionaryName=manFormattedDictionaryName.split()[0]
                                manFormattedDictionaryOptions[manFormattedDictionaryName.strip()]=tempList
                        if(manFormattedDictionaryName and tempList):
                            manFormattedDictionaryOptions[manFormattedDictionaryName.strip()]=tempList[0]
                        # print(searchToken)
                        print("Command: ", manFormattedDictionary[synopsis][0].strip())
                        print("\n")
                        isOptionPrinted=False

                        for key,value in manFormattedDictionaryOptions.items():
                                if(nlpOutput in lemmatize_all(key.lower()) or any(nlpOutput in lemmatize_all(string.lower()) for string in value)):
                                    if not (isOptionPrinted):
                                        print("Option(s): ")
                                        isOptionPrinted=True
                                    print(key)
                                    [print(v) for v in value]
                                    print("\n")
                        print("Please provide feedback to improve the assistant")
                        answer=input("Type 'y' if the result is correct or type 'n' if the result is incorrect: ")
                        selectedCommand=commandList[doc]
                        temp=nlpOutput+" "+selectedCommand

                        if(answer=='y' or answer=='Y'):
                            if temp in searchImprovementDict:
                                searchImprovementDict[temp]+=1
                            else:
                                searchImprovementDict[temp]=1
                        elif(answer=='n' or answer=='N'):
                            if temp in searchImprovementDict:
                                searchImprovementDict[temp]-=1
                            else:
                                searchImprovementDict[temp]=-1
    return

if __name__ == '__main__':
    main()