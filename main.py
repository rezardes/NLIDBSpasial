import re
import itertools

import nltk
from nltk.grammar import Nonterminal, Production, CFG

# import StemmerFactory class
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# bagaimana agar values bersatu
# ambil pohon pertama
# ambigu antara untuk kondisi atau untuk seleksi
# bagaimana penanganan spasi
# keuntungannya bermakna
# penanganan serta

grammar = CFG.fromstring("""
S -> COMMAND1 QUERY | COMMAND2 QUERY
COMMAND1 -> 'tampil'
COMMAND2 -> 'tunjuk' | 'lihat'
QUERY -> CONDITION | CONDITION CONDITION | CONDITION CONJ CONDITION | CONDITION QUERY | CONDITION CONJ QUERY
CONJ -> 'atau' | 'dan' | 'serta'
CONDITION -> RELATION VALUES | RELATION FIELD VALUE | FIELDS RELATION | OPERATION RELATION VALUES | OPERATION OPERATOR NUMBER | FIELD OPERATOR NUMBER | VALUES
OPERATOR -> 'lebih' 'dari' | 'kurang' 'dari' | 'sama' 'dengan' | 'lebih' 'dari 'sama 'dengan' | 'kurang' 'dari' 'sama' 'dengan'
OPERATION -> 'luas' | 'panjang' | 'keliling'
FIELDS -> FIELD FIELD | FIELD | FIELD FIELDS | FIELD CONJ FIELDS
VALUES -> VALUE VALUE | VALUE | VALUE VALUES
""")

#'dari' | 'kurang' 'dari' | 'sama' 'dengan'
# FIELDS -> FIELD FIELD | FIELD | FIELD FIELDS

productions = grammar.productions()

def literal_production(key, rhs):
    """ Return a production <key> -> n 

    :param key: symbol for lhs:
    :param rhs: string literal:
    """
    lhs = Nonterminal(key)
    return Production(lhs, [rhs])

def parse(text):
    """ Parse some text.
"""
    '''
    # extract new words and numbers
    words = set([match.group(0) for match in re.finditer(r"[a-zA-Z]+", text)])
    numbers = set([match.group(0) for match in re.finditer(r"\d+", text)])
    '''

    numbers = set([match.group(0) for match in re.finditer(r"\d+", text)])
    relations = ["negara", "kota", "provinsi", "sungai", "mahasiswa"]
    values = ["jakarta", "indonesia"]
    fields = ["nama", "ibukota", "nilai", "usia", "hobi"]
    
    # Make a local copy of productions
    lproductions = list(productions)
    
    # Add a production for every words and number
    lproductions.extend([literal_production("NUMBER", number) for number in numbers])
    lproductions.extend([literal_production("RELATION", relation) for relation in relations])
    lproductions.extend([literal_production("VALUE", value) for value in values])
    lproductions.extend([literal_production("FIELD", field) for field in fields])

    key = "VALUE"
    lhs = Nonterminal(key)
    lproductions.extend([Production(lhs, ["bengawan","solo"])])
    
    # Make a local copy of the grammar with extra productions
    lgrammar = CFG(grammar.start(), lproductions)

    # Load grammar into a parser
    parser = nltk.RecursiveDescentParser(lgrammar)

    tokens = text.split()

    return parser.parse(tokens)

hasil = None
# menghilangkan 'di', 'yang', 'ada di', 'dengan'
removeList = ['tiap', 'di', 'yang', 'ada di', 'masing-masing']
stemList = ['beribukota', 'ibukota']

# tampilkan nama mahasiswa yang nilainya lebih dari 50 dan kurang dari 100
# stemming process
sentence = input()
sentence = sentence.lower()
output   = stemmer.stem(sentence)
for elem in removeList:
    output = output.replace(elem+' ', '')
for i in range(0, len(stemList), 2):
    output = output.replace(stemList[i], stemList[i+1])
print(output)

for t in parse(output):
    hasil = t
    break

def takeElements(arr):

    fieldlist = []

    for k in range(0, len(arr)):
        #print(":",arr[k])
        if (isinstance(arr[k],str)):
            if (arr.label()!="CONJ"):
                fieldlist.append(arr[k])
        else:
            temp = takeElements(arr[k])
            for elem in temp:
                fieldlist.append(elem)
    
    return fieldlist

def collect(cond_node, result):

    if (cond_node.label()=="CONJ"):
        if (cond_node[0]=="dan"):
            result["cond"].append("AND")
    elif (cond_node[0].label()=="FIELDS" and cond_node[1].label()=="RELATION"):
        for j in range(0, len(cond_node)):
            if (cond_node[j].label()=="FIELDS"):
                fields = cond_node[j]
                result["fields"] = takeElements(fields) #
            elif(cond_node[j].label()=="RELATION"):
                result["relation"] = cond_node[j,0]
    elif (cond_node[0].label()=="FIELD" and cond_node[1].label()=="OPERATOR"):
        temp = []
        for j in range(0, len(cond_node)):
            # kalau fields
            if (cond_node[j].label()=="FIELD"):
                extract = cond_node[j,0]
                temp.append(extract)
            elif(cond_node[j].label()=="OPERATOR"):
                if (cond_node[j,0]=="lebih" and cond_node[j,1]=="dari"):
                    temp.append(">")
                elif (cond_node[j,0]=="kurang" and cond_node[j,1]=="dari"):
                    temp.append("<")
                elif (cond_node[j,0]=="sama" and cond_node[j,1]=="dengan"):
                    temp.append("=")
            elif(cond_node[j].label()=="NUMBER"):
                extract = cond_node[j,0]
                temp.append(extract)
        if "cond" in result:
            result["cond"] = result["cond"] + temp
        else:
            result["cond"] = temp
    #elif (cond_node[0].label()=="RELATION" and cond_node[0].label()=="FIELD" and cond_node[0].label()=="VALUE"):
    
    return result

def recursiveWalk(cond_node, result):

    for node in cond_node:
        if (node.label()=="QUERY"):
            result = recursiveWalk(node, result)
        result = collect(node, result)

    return result

print(hasil)

fieldlist = []
relation = ""
wherecond = []
result = {}

result = recursiveWalk(hasil[1], result)
    
    
print(result)
query = "SELECT "
for elem in result["fields"]:
    query = query + elem + ", "
query = query[:-2] + '\n'
query = query + "FROM " + result["relation"]

if ("cond" in result):
    query = query + "\nWHERE "
    for elem in result["cond"]:
        query = query + elem + " "
    print(query[:-1])
else:
    print(query)