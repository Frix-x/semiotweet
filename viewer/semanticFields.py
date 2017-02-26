#coding:utf-8
from lxml import html
import requests
import nltk.data

from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
from collections import Counter,defaultdict

def getSemanticField(word):
    """Get the semantic field of the word"""
    page = requests.get('http://dict.xmatiere.com/mots_en_rapport_avec/'+word.lower())
    tree = html.fromstring(page.content)
    aim = "/mots_en_rapport_avec/"
    semanticField = tree.xpath('//a[starts-with(@href,"'+aim+'")]/text()')
    return semanticField

def tokenizeText(text):
    #NOTE - TODO : to be modify to include hashtag and mentions
    """Tokenize a text : returns a list of the meaningful words"""
    # French Tokenizer :
    # tokenizerLocation = 'tokenizers/punkt/french.pickle' #Python 2
    # tokenizerLocation = 'tokenizers/punkt/PY3/french.pickle' #Python 3
    # tokenizer = nltk.data.load(tokenizerLocation)
    global commonWords

    tokenizer = WordPunctTokenizer()
    words = tokenizer.tokenize(text)

    # French stopwords
    frenchStopwords = set(stopwords.words('french')).union(set(commonWords))

    # Filtering
    words = [w.lower() for w in words if not (len(w) < 2 or w.lower() in frenchStopwords)]

    return words

def countWords(listTweetText,nbWordsToExtract=30):
    """Takes a list of text and returns the words occurences"""
    wordOccurences = defaultdict(lambda: 0)
    for currentTweet in listTweetText:
        currentOccurences = dict(Counter(tokenizeText(currentTweet)))
        for k in currentOccurences.keys():
            wordOccurences[k] += currentOccurences[k]

    return dict(Counter(wordOccurences).most_common(nbWordsToExtract))

def toJson(dict):
    output = []
    for key,val in dict.items():
        output.append({"word":key,"occur":val})

    return output

# ~ 76 most common words in french (see : https://en.wiktionary.org/wiki/Wiktionary:French_frequency_lists/1-2000)
commonWords =["de", "la", "le", "et", "les", "des", "en", "un", "du", "une",
              "que", "est", "pour", "qui", "dans", "a", "par", "plus", "pas",
              "au", "sur", "ne", "se", "ce", "il", "sont",
              "ou", "avec", "son", "aux", "d'un", "cette", "d'une",
              "ont", "ses", "mais", "comme", "on", "tout", "nous", "sa",
              "fait", "été", "aussi", "leur", "bien", "peut", "ces", "y", "deux",
              "à", "ans", "l", "encore", "n'est", "marché", "d", "donc",
              "cours", "qu'il", "moins", "sans", "si", "entre",
              "faire", "elle", "c'est", "peu", "vous","prix",
              "dont", "lui", "également", "effet", "pays", "cas"]

specifiedWords = ["colère","combat","peur","victoire","aide","argent","mensonge","société"]

if __name__ == '__main__':
    # print(getSemanticField("médicament"))
    print dict(Counter(tokenizeText("J'aime les beignets à la framboise #Love @jjerphan prout prout ")))
    # listTweetText = ["J'aime les barbes à papa #swag","Mon cheval mange des carottes-cakes en Hiver ! #Yolo #QuelleIdée !","Quelle idée d'avoir des doigts :'("]
    # res = countWords(listTweetText)
    # for i in res.keys():
    #     print i,res[i]
