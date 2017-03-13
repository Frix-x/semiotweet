#coding:utf-8
from __future__ import print_function
from builtins import str
from lxml import html
import requests
import nltk.data

import string

from nltk.tokenize import WordPunctTokenizer,TweetTokenizer
from collections import Counter,defaultdict

from .lda_helpers import *

def getSemanticField(word):
    """Get the semantic field of the word"""
    page = requests.get('http://dict.xmatiere.com/mots_en_rapport_avec/'+word.lower())
    tree = html.fromstring(page.content)
    aim = "/mots_en_rapport_avec/"
    semanticField = tree.xpath('//a[starts-with(@href,"'+aim+'")]/text()')
    return semanticField

def personnalTokenizer(text):
    """Personnal Tokenizer"""
    text = str(text, "utf-8")
    text = text.translate(string.maketrans("",""), "!\"$%&()*+,-./:;<=>?[\]^_`{|}~")
    words = text.lower().split()
    return words

def tokenizeText(text):
    #NOTE - TODO : to be modify to include hashtag and mentions and to remove URL
    """Tokenize a text : returns a list of the meaningful words"""
    # French Tokenizer :
    # tokenizerLocation = 'tokenizers/punkt/french.pickle' #Python 2
    # tokenizerLocation = 'tokenizers/punkt/PY3/french.pickle' #Python 3
    # tokenizer = nltk.data.load(tokenizerLocation)
    global frenchStopwords

    # tokenizer = WordPunctTokenizer()
    tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True)
    words = tokenizer.tokenize(text)

    # Filtering
    words = [w.lower() for w in words if not (len(w) < 2 or w.lower() in frenchStopwords)]

    return words

def countWords(listTweetText,nbWordsToExtract=30,lemmat=False):
    """Takes a list of text and returns the words occurences"""
    if lemmat :
        lemmatizer = FrenchLefffLemmatizer()
    wordOccurences = defaultdict(lambda: 0)
    for currentTweet in listTweetText:
        tokenizedTweet = tokenizeText(currentTweet)
        print(tokenizedTweet)
        if lemmat :
            tokenizedTweet = [lemmatizer.lemmatize(word) for word in tokenizedTweet]
            print("lemmes : ")
            print(tokenizedTweet)
        currentOccurences = dict(Counter(tokenizedTweet))
        for k in list(currentOccurences.keys()):
            wordOccurences[k] += currentOccurences[k]

    return dict(Counter(wordOccurences).most_common(nbWordsToExtract))

def toJsonForGraph(dict):
    """Return a list of dict used next for the Bubble Graph"""
    output = []
    for key,val in list(dict.items()):
        output.append({"word":key,"occur":val})

    return output

# French Stop words (see : http://www.ranks.nl/stopwords/french)
stopwords = ["alors","au","aucuns","aussi","autre","avant","avec","avoir","bon",
             "car","ce","cela","ces","ceux","chaque","ci","comme","comment","dans",
             "des","du","dedans","dehors","depuis","devrait","doit","donc","dos",
             "début","elle","elles","en","encore","essai","est","et","eu","fait",
             "faites","fois","font","hors","ici","il","ils","je","juste","la","le",
             "les","leur","là","ma","maintenant","mais","mes","mine","moins","mon",
             "mot","même","ni","nommés","notre","nous","ou","où","par","parce","pas",
             "peut","peu","plupart","pour","pourquoi","quand","que","quel","quelle",
             "quelles","quels","qui","sa","sans","ses","seulement","si","sien","son",
             "sont","sous","soyez","sujet","sur","ta","tandis","tellement","tels",
             "tes","ton","tous","tout","trop","très","tu","voient","vont","votre",
             "vous","vu","ça","étaient","état","étions","été","être"]

# ~ 76 most common words in french (see : https://en.wiktionary.org/wiki/Wiktionary:French_frequency_lists/1-2000)
commonWordsWiki =["de", "la", "le", "et", "les", "des", "en", "un", "du", "une",
              "que", "est", "pour", "qui", "dans", "a", "par", "plus", "pas",
              "au", "sur", "ne", "se", "ce", "il", "sont",
              "ou", "avec", "son", "aux", "d'un", "cette", "d'une",
              "ont", "ses", "mais", "comme", "on", "tout", "nous", "sa",
              "fait", "été", "aussi", "leur", "bien", "peut", "ces", "y", "deux",
              "à", "ans", "l", "encore", "n'est", "marché", "d", "donc",
              "cours", "qu'il", "moins", "sans", "si", "entre",
              "faire", "elle", "c'est", "peu", "vous","prix",
              "dont", "lui", "également", "effet", "pays", "cas"]

# Snowball stopwords (see : http://snowball.tartarus.org/algorithms/french/stop.txt)
commonWordsSnowball = ["au", "aux", "avec", "ce", "ces", "dans", "de", "des", "du",
                    "elle", "en", "et", "eux", "il", "je", "la", "le", "leur", "lui",
                    "ma", "mais", "me", "même", "mes", "moi", "mon", "ne", "nos",
                    "notre", "nous", "on", "ou", "par", "pas", "pour", "qu",
                    "que", "qui", "sa", "se", "ses", "son", "sur", "ta", "te",
                    "tes", "toi", "ton", "tu", "un", "une", "vos", "votre",
                    "vous", "c", "d", "j", "l", "à", "m", "n", "s", "t", "y",
                    "été", "étée", "étées", "étés", "étant", "suis", "es", "est",
                    "sommes", "êtes", "sont", "serai", "seras", "sera", "serons",
                    "serez", "seront", "serais", "serait", "serions", "seriez",
                    "seraient", "étais", "était", "étions", "étiez", "étaient",
                    "fus", "fut", "fûmes", "fûtes", "furent", "sois", "soit",
                    "soyons", "soyez", "soient", "fusse", "fusses", "fût",
                    "fussions", "fussiez", "fussent", "ayant", "eu", "eue",
                    "eues", "eus", "ai", "as", "avons", "avez", "ont", "aurai",
                    "auras", "aura", "aurons", "aurez", "auront", "aurais",
                    "aurait", "aurions", "auriez", "auraient", "avais", "avait",
                    "avions", "aviez", "avaient", "eut", "eûmes", "eûtes",
                    "eurent", "aie", "aies", "ait", "ayons", "ayez", "aient",
                    "eusse", "eusses", "eût", "eussions", "eussiez", "eussent",
                    "ceci", "cela", "celà", "cet", "cette", "ici", "ils", "les",
                    "leurs", "quel", "quels", "quelle", "quelles", "sans", "soi"]


# Others common works on Twitter, not so meaningful
commonWordsTwitter = ["…","rt","ils","faut","https","://","http","...","ça",
                      "to","the","j'ai","via","ça","000","veux","être","devons"
                      ,"doit","j'étais","suis"]

# French stopwords
frenchStopwords = set(stopwords).union(set(commonWordsWiki))
frenchStopwords = frenchStopwords.union(set(commonWordsSnowball))
frenchStopwords = frenchStopwords.union(set(commonWordsTwitter))

specifiedWords = ["colère","combat","peur","victoire","aide","argent","mensonge","société"]

requestToGetSources = 'SELECT DISTINCT source, COUNT(source) AS nb  FROM viewer_tweet GROUP BY source ORDER BY nb DESC'

if __name__ == '__main__':
    # print(getSemanticField("médicament"))
    # listTweetText = ["J'aime les barbes à papa #swag","Mon cheval mange des carottes-cakes en Hiver ! #Yolo #QuelleIdée !","Quelle idée d'avoir des doigts :'("]
    # res = countWords(listTweetText)
    # for i in res.keys():
    #     print i,res[i]
    pass
