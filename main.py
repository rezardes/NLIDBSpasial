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
# nanti ada yang dikelompokkan

grammar = CFG.fromstring("""
S -> COMMAND QUERY
COMMAND -> COMMAND1 | COMMAND2 | COMMAND3
COMMAND1 -> 'tampil'
COMMAND2 -> 'tunjuk' | 'lihat'
COMMAND3 -> 'hitung' | 'kalkulasi'
QUERY -> RELATION | CONDITION | CONDITION CONDITION | CONDITION CONJ CONDITION | CONDITION QUERY | CONDITION CONJ QUERY
CONJ -> AND | OR
AND -> 'dan' | 'serta'
OR -> 'atau'
CONDITION -> FIELDS OPERATOR NUMBER | FIELDS RELATION | FIELDS RELATION SPATIALOP RELCOND | FIELDS RELATION NOT SPATIALOP RELCOND | FIELDS RELCOND | RELCOND | RELATION SPATIALOP RELCOND | RELATION NOT SPATIALOP RELCOND | SPATIALOP RELATION SPATIALOP RELCOND | SPATIALOP RELATION NOT SPATIALOP RELCOND | SPATIALOP RELCOND | SPATIALOP OPERATOR NUMBER | VALUES
RELCOND -> RELATION VALUES | RELATION FIELDS VALUE | RELATION FIELDS NUMBER
OPERATOR -> 'lebih' 'dari' | 'kurang' 'dari' | 'sama' 'dengan' | 'lebih' 'dari 'sama 'dengan' | 'kurang' 'dari' 'sama' 'dengan'
NOT -> 'tidak' | 'bukan'
SPATIALOP -> PANJANG | LUAS | KELILING | INSIDE | OUTSIDE
INSIDE -> 'dalam' | 'pada'
OUTSIDE -> 'luar'
PANJANG -> 'panjang'
LUAS -> 'luas'
KELILING -> 'keliling'
FIELDS -> FIELD FIELD | FIELD | FIELD FIELDS | FIELD CONJ FIELDS
VALUES -> VALUE VALUE | VALUE | VALUE VALUES
""")

#'dari' | 'kurang' 'dari' | 'sama' 'dengan'
# FIELDS -> FIELD FIELD | FIELD | FIELD FIELDS

def getAttrs():

        temp = ['id', 'nama', 'geom']
        temp2 = ['id', 'nama', 'id_ibukota', 'geom']

        attrs = {
            "segitiga": temp,
            "kotak": temp,
            "titik": temp,
            "garis": temp,
            "poligon": temp,
            "negara": temp2,
            "provinsi": temp2,
            "kota": temp
        }
        return attrs

def getGeom():

    temp = "geom"

    geoms = {
        "segitiga": temp,
        "kotak": temp,
        "titik": temp,
        "garis": temp,
        "poligon": temp,
        "negara": temp,
        "provinsi": temp,
        "kota": temp
    }

    return geoms

def getValues():

    values = ["jakarta", "indonesia", "a", "b", "c"]
    return values

attrs = getAttrs()
geoms = getGeom()
values = getValues()

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
    relations = ["segitiga", "kotak", "titik", "garis", "poligon", "negara", "kota", "provinsi"]
    fields = ["nama", "ibukota", "geom", "id", "id_ibukota"]

    class Relation:

        def __init__(self, name, attrs, geom):
            self.name = name
            self.attrs = attrs
            self.geom = geom

    # segitiga: id, nama, geom
    # kotak: id, nama, geom
    # titik: id, nama, geom
    # garis: id, nama, geom
    # poligon: id, nama, geom
    # negara: id, nama, id_ibukota, geom
    # provinsi: id, nama, id_ibukota, geom
    # kota: id, nama, geom
    
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
removeList = ['di', 'yang', 'ada', 'masing-masing', 'tiap', 'dengan', 'besar']
prefixList = ['ber-']
stemList = ['beribukota', 'ibukota']

# tampilkan nama mahasiswa yang nilainya lebih dari 50 dan kurang dari 100
# stemming process
sentence = input()
sentence = sentence.lower()
output   = stemmer.stem(sentence)
print("Hasil stemmer: "+output)
for elem in removeList:
    output = output.replace(elem+' ', '')
for elem in prefixList:
    output = output.replace(elem, '')
for i in range(0, len(stemList), 2):
    output = output.replace(stemList[i], stemList[i+1])
print("Hasil remove: "+output)

for t in parse(output):
    hasil = t
    break

def mapToFunctions(keyword):

    functions = {
        "PANJANG": 'ST_Length',
        "LUAS": 'ST_Area',
        "KELILING": 'ST_Perimeter',
        "INSIDE": 'ST_Within',
        "OUTSIDE": 'NOT ST_Within'
    }

    if keyword in functions:
        return functions[keyword]
    else:
        return 'NOT FOUND'


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

def collect(cond_node, result, counter, prev, prevVal):

    '''
    if (cond_node.label()=="CONJ"):
        if (cond_node[0]=="dan"):
            result["cond"].append("AND")
    if (cond_node.label()=="SPATIALOP"):
        result["colFunctions"] = cond_node[0].label()
    '''

    '''
            elif (node.label()=="RELATION" and prev=="FIELDS"):
                prev = node.label()
                result["relation"].append(node[0])
                #result["cond"].pop()
            '''
    '''
    elif ((prev=="VALUES" or prev=="NUMBER" or prev=="RELATION") and node.label()=="FIELDS"):
        prev = node.label()
        if (len(result["cond"])>0):
            result["cond"].append("AND")
        result["cond"].append(node[0][0])
    '''

    if (cond_node.label()=="RELATION"):
        result["relation"].append(cond_node[0])
    elif (cond_node.label()=="CONDITION" or cond_node.label()=="RELCOND"):
        isOperator = False
        for node in cond_node:
            '''print("counter: "+str(counter))
            print("prev: "+prev)
            print(node)'''
            if (node.label()=="SPATIALOP" and counter==0):
                prev = node.label()
                prevVal = node[0].label()
                result["colFunctions"] = node[0].label()
            elif (node.label()=="SPATIALOP" and counter>0):
                # Apakah perlu append unik?
                result["cond"].append(prevVal)
                prev = node.label()
                prevVal = node[0].label()
                result["cond"].append("O: "+node[0].label())
            elif ((prev=="VALUES" or prev=="NUMBER") and node.label()=="RELATION"):
                prev = node.label()
                prevVal = node[0]
                result["cond"].append(node[0])
            elif (node.label()=="RELATION" and prev=="SPATIALOP"):
                prev = node.label()
                prevVal = node[0]
                result["relation"].append(node[0])
                result["cond"].append(node[0])
                result["cond"].append("AND")
            elif (node.label()=="RELATION"):
                prev = node.label()
                prevVal = node[0]
                result["relation"].append(node[0])
                #result["cond"].append(node[0])
            elif (node.label() == "FIELDS" and counter==0):
                prev = node.label()
                prevVal = ""
                for elem in node[0]:
                    result["fields"].append(elem)
            elif (node.label() == "FIELDS"):
                prev = node.label()
                prevVal = node[0][0]
                result["cond"].append(node[0][0])
            elif (node.label() == "VALUES" and prev == "RELATION"):
                prev = node.label()
                prevVal = node[0][0]
                if (result["cond"][len(result["cond"])-1] == "AND"):
                    result["cond"].pop()
                result["cond"].append(node[0][0])
                result["cond"].append("AND")
            elif (node.label() == "VALUES"):
                prev = node.label()
                prevVal = node[0][0]
                result["cond"].append(node[0][0])
                result["cond"].append("AND")
            elif (node.label() == "NUMBER"):
                prev = node.label()
                prevVal = node[0]
                if (not isOperator):
                    result["cond"].append("O: =")
                result["cond"].append(node[0])
                result["cond"].append("AND")
            elif (node.label()=="CONJ"):
                prev = node.label()
                prevVal = node[0]
                result["cond"].append(node[0])
            elif (node.label() == "RELCOND"):
                result = collect(node, result, counter, prev, prevVal)
            else:
                result = collect(node, result, counter, prev, prevVal)
            counter = counter + 1
            

    '''
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
    '''
    #elif (cond_node[0].label()=="RELATION" and cond_node[0].label()=="FIELD" and cond_node[0].label()=="VALUE"):
    
    return result

def recursiveWalk(cond_node, result):

    for node in cond_node:
        if (node.label()=="QUERY"):
            result = recursiveWalk(node, result)
        else:
            result = collect(node, result, 0, "", "")

    if (result["cond"][len(result["cond"])-1] == "AND"):
        result["cond"].pop()

    return result

print(hasil)

fieldlist = []
wherecond = []
indices = {}
result = {"cond": [], "relation": [], "fields": []}

result = recursiveWalk(hasil[1], result)

print(result)
query = "SELECT "
if (hasil[0][0].label()=="COMMAND1"):

    if ("colFunctions" in result):
        spFunction = mapToFunctions(result["colFunctions"])
        query = query + spFunction + "(" + "r1." + geoms[result["relation"][0]] + "), "
    if ("fields" in result):
        for elem in result["fields"]:
            query = query + "r1." + elem + ", "
    query = query[:-2] + '\n'
    
elif (hasil[0][0].label()=="COMMAND2" or hasil[0][0].label()=="COMMAND3"):

    print(result)
    query = "SELECT "
    if ("colFunctions" in result):
        spFunction = mapToFunctions(result["colFunctions"])
        query = query + spFunction + "(" + geoms[result["relation"][0]] + ")\n"
    else:
        query = query + "r1." + geoms[result["relation"][0]] + "\n"

query = query + "FROM "
counter = 1
for relation in result["relation"]:
    indices[relation] = str(counter)
    query = query + relation + " r" + str(counter) + ", "
    counter = counter + 1
query = query[:-2] + '\n'

# Masih berupa field value sama relation value untuk opspasial doang

def processCond(object1, op, object2, query):

    left = object1[0]
    right = object2[0]


    if (op=="INSIDE" or op=="OUTSIDE"):
        query = query + mapToFunctions(op) + "(" + "r" + indices[left] + "." + geoms[left] 
        query = query + ", " + "r" + indices[right] + "." + geoms[right] + ") "
        if (len(object2)>1):
            query = query + "AND ("
            for attr in attrs[object2[0]]:
                query = query + "r" + indices[object2[0]] + "." + attr + " = '" + object2[1] + "' OR "
            query = query[:-4] + ")"
    elif (op=="LUAS" or op=="KELILING" or op=="PANJANG"):
        query = query + mapToFunctions(op) + "(" + "r" + indices[right] + "." + geoms[right] +") "
    else:
        query = query + "r" + indices[result["relation"][0]] + "." + left + " " + op + " " + right + " "

    return query

if ("cond" in result):
    query = query + "WHERE "
    object1 = []
    op = ""
    # op dibuat list
    object2 = []
    isLeft = True
    for elem in result["cond"]: #range(0, len(result["cond"])):
        
        if (isLeft):
            object1.append(elem)
        else:
            object2.append(elem)

        if (elem.startswith("O: ")):
            op = elem.replace('O: ', '')
            isLeft = False

        if (elem == "AND" or elem == "OR"):
            isLeft = True
            '''print(print("object1")
            print(object1)
            print("object2")
            print(object2)'''
            query = processCond(object1, op, object2, query)
            query = query + elem + " "

    query = processCond(object1, op, object2, query)

    '''
    for elem in result["cond"]:
        query = query + elem + " "
    '''
    print(query)
else:
    print(query)