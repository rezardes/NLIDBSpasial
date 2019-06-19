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
# pengecualian bagian

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
CONDITION -> FIELDS OPERATOR NUMBER | FIELDS RELATION | FIELDS RELATION SPATIALOP RELCOND | FIELDS RELATION NOT SPATIALOP RELCOND | FIELDS RELCOND | PART RELATION SPATIALOP GEOCOND | RELCOND | RELATION SPATIALOP GEOCOND | RELATION NOT SPATIALOP GEOCOND | RELATION SPATIALOP RELCOND | RELATION NOT SPATIALOP RELCOND | SPATIALOP RELATION SPATIALOP RELCOND | SPATIALOP RELATION NOT SPATIALOP RELCOND | SPATIALOP RELCOND |  SPATIALOP RELCOND RELCOND | SPATIALOP OPERATOR NUMBER | VALUES
PART -> 'daerah' | 'bagian' | 'potong'
GEOCOND -> GEOMETRY POINT COOR CONJ POINT COOR | GEOMETRY COOR SIZE NUMBER
GEOMETRY -> SQUARE | RECTANGLE
SQUARE -> 'persegi'
RECTANGLE -> 'segiempat' | 'persegi' 'panjang'
POINT -> LU | RU | LB | RB
LU -> 'titik' 'kiri' 'atas'
RB -> 'titik' 'kanan' 'bawah'
RELCOND -> RELATION VALUES | RELATION FIELDS VALUE | RELATION FIELDS NUMBER | RELATION
OPERATOR -> 'lebih' 'dari' | 'kurang' 'dari' | 'sama' 'dengan' | 'lebih' 'dari 'sama 'dengan' | 'kurang' 'dari' 'sama' 'dengan'
NOT -> 'tidak' | 'bukan'
SPATIALOP -> PANJANG | LUAS | KELILING | INSIDE | OUTSIDE | JARAK
JARAK -> 'jarak'
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
    coordinates = set([match.group(0) for match in re.finditer(r"\(\d+,\d+\)", text)])
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
    lproductions.extend([literal_production("COOR", coor) for coor in coordinates])

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
removeList = ['di', 'yang', 'ada', 'masing-masing', 'tiap', 'dengan', 'besar', 'hadap']
prefixList = ['ber-']
stemList = ['beribukota', 'ibukota']

# tampilkan nama mahasiswa yang nilainya lebih dari 50 dan kurang dari 100
# stemming process
sentence = input()
sentence = sentence.lower()

extractor = re.compile(r'\(\s*\d+\s*,\s*\d+\s*\)')
keepList = extractor.findall(sentence)
print(keepList)
output = stemmer.stem(sentence)
for keep in keepList:
    spaces = re.compile(r'\s+')
    coor = spaces.sub('', keep)
    temp = coor.replace(',', ' ')
    temp = temp.replace('(', '')
    temp = temp.replace(')', '')
    output = output.replace(temp, coor)
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
        "OUTSIDE": 'NOT ST_Within',
        "JARAK": 'ST_Distance',
    }

    if keyword in functions:
        return functions[keyword]
    else:
        return 'NOT FOUND'

def declareFunctions(keyword, params):
    
    parameter = {
        "PANJANG": 1,
        "LUAS": 1,
        "KELILING": 1,
        "INSIDE": 2,
        "OUTSIDE": 2,
        "JARAK": 2,
    }

    function = mapToFunctions(keyword)
    if (parameter[keyword]==1):
        return function + '(' + params[0] + ')'
    elif (parameter[keyword]==2):
        return function + '(' + params[0] + ', ' + params[1] + ')'
    else:
        return ''

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

def addOrdered(arrs, rel):

    if (rel+'1' in arrs):
        for num in range(3, len(arrs)+2):
            if (rel+str(num) not in arrs):
                arrs.append(rel+str(num))
    elif (rel in arrs):
        idx = arrs.index(rel)
        arrs[idx] = rel+'1'
        arrs.append(rel+'2')
    else:
        arrs.append(rel)

    return arrs

'''def addCondition(conds, rel):

    if (rel+'1' in conds):
        for num in range(3, len(conds)+2):
            if (rel+str(num) not in conds):
                conds.append(rel+str(num))
    elif (rel in conds):
        idx = conds.index(rel)
        conds[idx] = rel+'1'
        conds.append(rel+'2')
    else:
        conds.append(rel)

    return conds'''

def delNum(text):

    text = re.sub(r"\d+", "", text)
    return text

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
        #if (cond_node.label() not in result["relation"]):
            #print(cond_node[0])
        #result["relation"].append(cond_node[0])
        result["relation"] = addOrdered(result["relation"], cond_node[0])
        result["cond"] = addOrdered(result["cond"], cond_node[0])
    elif (cond_node.label()=="CONDITION" or cond_node.label()=="RELCOND" or cond_node.label()=="GEOCOND"):
        isOperator = False
        for node in cond_node:
            '''print("counter: "+str(counter))
            print("prev: "+prev)
            print(node)'''
            if (node.label()=="GEOMETRY"):
                prev = node[0].label()
                prevVal = node[0].label()
                result["cond"].append(node[0].label())
            elif (node.label()=="POINT"):
                prev = node[0].label()
                prevVal = node[0].label()
                result["cond"].append(node[0].label())
            elif (node.label()=="COOR"):
                prev = node.label()
                prevVal = node[0]
                result["cond"].append(node[0])
            elif (node.label()=="SPATIALOP" and counter==0):
                prev = node.label()
                prevVal = node[0].label()
                result["colFunctions"] = node[0].label()
            elif (node.label()=="SPATIALOP" and counter>0 and prev=="RELATION"):
                # Apakah perlu append unik?
                #result["cond"].append(prevVal) KARENA Tunjukkan daerah negara yang ada di dalam
                prev = node.label()
                prevVal = node[0].label()
                result["cond"].append("O: "+node[0].label())
            elif (node.label()=="SPATIALOP" and counter>0):
                prev = node.label()
                prevVal = node[0].label()
                result["cond"].append("O: "+node[0].label())
            elif (node.label()=="NOT" and counter>0 and prev=="RELATION"):
                # Apakah perlu append unik?
                result["cond"].append(prevVal)
                prev = node.label()
                prevVal = node.label()
                result["cond"].append("O: "+node.label())
            elif ((prev=="VALUES" or prev=="NUMBER") and node.label()=="RELATION"):
                prev = node.label()
                prevVal = node[0]
                #if (node[0] not in result["relation"]):
                #    result["relation"].append(node[0])
                result["cond"] = addOrdered(result["relation"], node[0])
            elif (node.label()=="RELATION" and prev=="SPATIALOP"):
                prev = node.label()
                prevVal = node[0]
                #if (node[0] not in result["relation"]):
                #result["relation"].append(node[0])
                result["relation"] = addOrdered(result["relation"], node[0])
                result["cond"] = addOrdered(result["cond"], node[0])
                result["cond"].append("AND")
            elif (node.label()=="RELATION"):
                prev = node.label()
                prevVal = node[0]
                #if (node[0] not in result["relation"]):
                #result["relation"].append(node[0])
                result["relation"] = addOrdered(result["relation"], node[0])
                result["cond"] = addOrdered(result["cond"], node[0])
                #result["cond"].append(node[0])
            elif (node.label() == "FIELDS" and counter==0):
                prev = node.label()
                prevVal = ""
                for elem in node:
                    result["fields"].append(elem[0])
            elif (node.label() == "FIELDS"):
                prev = node.label()
                prevVal = node[0][0]
                result["cond"].append(node[0][0])
            elif (node.label() == "VALUES" and prev == "RELATION"):
                prev = node.label()
                prevVal = node[0][0]
                if (len(result["cond"])>0):
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
            elif (node.label()=="CONJ" and prev!="COOR"):
                prev = node.label()
                prevVal = node[0]
                result["cond"].append(node[0].label())
            elif (node.label() == "RELCOND" or node.label() == "GEOCOND"):
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

    if (len(result["cond"])>0):
        if (result["cond"][len(result["cond"])-1] == "AND"):
            result["cond"].pop()

    return result

print(hasil)

fieldlist = []
wherecond = []
indices = {}
result = {"cond": [], "relation": [], "fields": []}

result = recursiveWalk(hasil[1], result)

counter = 1
for relation in result["relation"]:
    indices[relation] = str(counter)
    counter = counter + 1
#print("indices")
#print(indices)

print(result)
query = "SELECT "
if (hasil[0][0].label()=="COMMAND1"):

    if ("colFunctions" in result):
        temp = []
        for rel in result["relation"]:
            temp.append("r"+indices[rel]+"."+geoms[delNum(rel)])
        query = query + declareFunctions(result["colFunctions"], temp) + "\n"
    if ("fields" in result):
        for elem in result["fields"]:
            query = query + "r1." + elem + ", "
    query = query[:-2] + '\n'
    
elif (hasil[0][0].label()=="COMMAND2" or hasil[0][0].label()=="COMMAND3"):

    #print(result)
    query = "SELECT "
    if ("colFunctions" in result):
        temp = []
        for rel in result["relation"]:
            temp.append("r"+indices[rel]+"."+geoms[delNum(rel)])
        query = query + declareFunctions(result["colFunctions"], temp) + "\n"
    else:
        query = query + "r1." + geoms[delNum(result["relation"][0])] + "\n"

query = query + "FROM "
for relation in result["relation"]:
    query = query + delNum(relation) + " r" + indices[relation] + ", "
#print("indicess")
#print(indices)
query = query[:-2] + '\n'

# Masih berupa field value sama relation value untuk opspasial doang

def searchValQuery(query, relation, value):

    query = query + "("
    for attr in attrs[delNum(relation)]:
        query = query + "r" + indices[relation] + "." + attr + " = '" + value + "' OR "
    query = query[:-4] + ")"

    return query

def makeRectangle(point1, point2, srid='2163'):

    return 'ST_MakeEnvelope(' + point1[0] + ',' + point1[1] + ',' + point2[0] + ',' + point2[1] + ',' + srid + ')'

def processCond(object1, operation, object2, query):

    #print("processCond")
    #print(object1)
    #print(object2)

    left = ""
    if (len(object1)>0):
        left = object1[0]

    right = ""
    if (len(object2)>0):
        right = object2[0]

    op = ""
    if (len(operation)>0):
        op = operation[0]

    if (len(operation)>1):
        if (operation[1]=="INSIDE"):
            op = "OUTSIDE"
        else:
            op = "INSIDE"

    if (op=="INSIDE" or op=="OUTSIDE"):
        geom1 = ""
        geom2 = ""
        if (object2[0]=="RECTANGLE"):
            leftUpper = []
            rightBottom = []
            extractor = re.compile('\d+')
            for i in range(2, len(object2), 2):
                if (object2[i-1]=="LU"):
                    leftUpper = extractor.findall(object2[i])
                elif (object2[i-1]=="RB"):
                    rightBottom = extractor.findall(object2[i])
            geom2 = makeRectangle(leftUpper, rightBottom)
        else:
            geom2 = "r" + indices[right] + "." + geoms[right]

        geom1 = "r" + indices[left] + "." + geoms[left]
        
        query = query + declareFunctions(op, [geom1, geom2])
        if (len(object2)>1 and object2[0]!="RECTANGLE"):
            query = query + "AND "
            query = searchValQuery(query, right, object2[1])
    elif (op=="LUAS" or op=="KELILING" or op=="PANJANG"):
        query = query + declareFunctions(op, ["r" + indices[right] + "." + geoms[delNum(right)]])
    elif (op==""):
        if (left in result["relation"]):
            query = searchValQuery(query, left, object1[1]) + " "
            #print("hasil query")
            #print(query)
        if (right in result["relation"]):
            query = query + "AND ("
            query = searchValQuery(query, right, object2[1]) + " "

    else:
        query = query + "r" + indices[result["relation"][0]] + "." + left + " " + op + " " + right + " "

    return query

if (len(result["cond"])>0):
    query = query + "WHERE "
    object1 = []
    op = []
    # op dibuat list
    object2 = []
    isLeft = True
    for elem in result["cond"]: #range(0, len(result["cond"])):

        #print("elem")
        #print(elem)

        if (elem == "AND" or elem == "OR"):
            isLeft = True
            '''print(print("object1")
            print(object1)
            print("object2")
            print(object2)'''
            query = processCond(object1, op, object2, query)
            query = query + elem + " "
            #print("query")
            #print(query)
            object1 = []
        elif (elem.startswith("O: ")):
            op.append(elem.replace('O: ', ''))
            isLeft = False
        elif (isLeft):
            object1.append(elem)
        else:
            object2.append(elem)

    query = processCond(object1, op, object2, query)

    '''
    for elem in result["cond"]:
        query = query + elem + " "
    '''
    print(query)
else:
    print(query)