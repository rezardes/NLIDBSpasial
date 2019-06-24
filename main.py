import re
import sys
import itertools

import nltk
from nltk.grammar import Nonterminal, Production, CFG

# import StemmerFactory class
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

sys.setrecursionlimit(10000)

# bagaimana agar values bersatu
# ambil pohon pertama
# ambigu antara untuk kondisi atau untuk seleksi
# bagaimana penanganan spasi
# keuntungannya bermakna
# nanti ada yang dikelompokkan
# pengecualian bagian
# kurang dari besar hmm
# jangan lupa kasus id dan nama segitiga A serta id dan nama segitiga B

# FIELDS RELATION VALUE FIELDS RELATION VALUE CONJ FIELDS RELATION VALUE SEPARATOR SPATIALOP RELATION VALUE RELATION VALUE OPERATOR NUMBER CONJ SPATIALOP RELATION VALUE RELATION VALUE OPERATOR NUMBER 
# FIELD DOUBLE DIHILANGIN
# GEOCOND jangan dilihat dulu

grammar = CFG.fromstring("""
S -> QUERIES
QUERIES -> QUERY COMMA QUERIES | QUERY CONJ QUERIES | QUERY
QUERY -> COMMAND CONDITION
COMMAND -> COMMAND1 | COMMAND2 | COMMAND3
COMMAND1 -> 'tampil'
COMMAND2 -> 'tunjuk' | 'lihat'
COMMAND3 -> 'hitung' | 'kalkulasi' | 'cari'
COMMA -> ','
FIELDS -> FIELD | SPATIALOP FIELDS | FIELD FIELDS | FIELD CONJ FIELDS | FIELD COMMA CONJ FIELDS | FIELD COMMA FIELDS
VALUES -> VALUE CONJ VALUE | VALUE COMMA VALUE | VALUE | VALUE VALUES
CONDITION -> COND CONJ CONDITION | COND COMMA CONDITION | RELATION SEPARATOR CONDITION | COND SEPARATOR CONDITION | SPATIALOP OPERATOR | SPATIALOP COND OPERATOR | COND SPATIALOP OPERATOR | SPATIALOP GEOCONDS | SPATIALOP CONDITION | NOT SPATIALOP CONDITION | SPATIALOP VALUES | SPATIALOP VALUES CONDITION | COND CONDITION | COND
GEOCONDS -> GEOCOND COMMA GEOCONDS | GEOCOND CONJ COMMA GEOCOND | GEOCOND
GEOCOND -> GEOMETRY POINT COOR CONJ POINT COOR | GEOMETRY POINT COOR SIZE NUMBER
COND -> FIELDS RELATION | FIELDS RELATION VALUE | FIELDS RELATION NOT VALUE | FIELDS RELATION FIELDS VALUE | FIELDS RELATION NOT FIELDS VALUE | RELATION FIELDS VALUE | RELATION FIELDS NOT VALUE | FIELDS VALUE | FIELDS NOT VALUE | RELATION FIELDS | RELATION VALUE | RELATION NOT VALUE
OPERATOR -> OP NUMBER | OP NUMBER UNIT | NUMBER | NUMBER UNIT
GEOMETRY -> SQUARE | RECTANGLE
SQUARE -> 'persegi'
RECTANGLE -> 'segiempat' | 'persegi' 'panjang' | 'kotak'
POINT -> LU | RU | LB | RB | PUSAT
LU -> 'titik' 'kiri' 'atas'
RB -> 'titik' 'kanan' 'bawah'
PUSAT -> 'titik' 'pusat'
SIZE -> 'sisi' | 'panjang' | 'lebar'
CONJ -> AND | OR
AND -> 'dan' | 'serta'
OR -> 'atau'
SEPARATOR -> 'jika' | 'yang'
PART -> 'daerah' | 'bagian' | 'potong'
OP -> MORE | LESS | EQUAL | MORE EQUAL | LESS EQUAL
LESS -> 'kurang' 'dari'
MORE -> 'lebih' 'dari'
EQUAL -> 'sama' 'dengan' | 'besar'
NOT -> 'tidak' | 'bukan'
SPATIALOP -> PANJANG | LUAS | KELILING | INSIDE | OUTSIDE | JARAK | OVERLAP | MEETS
JARAK -> 'jarak'
INSIDE -> 'dalam' | 'pada'
OUTSIDE -> 'luar'
PANJANG -> 'panjang'
LUAS -> 'luas'
KELILING -> 'keliling'
OVERLAP -> 'iris' | 'singgung'
MEETS -> 'di' 'samping' | 'sebelah'
""")

#'dari' | 'kurang' 'dari' | 'sama' 'dengan'
# FIELDS -> FIELD FIELD | FIELD | FIELD FIELDS

def findAmountCode(arr, code):

    counter = 0

    for elmt in arr:
        if elmt.startswith(code):
            counter = counter + 1

    return counter

def deleteMultipleRel(arr, index):

    if (len(arr)!=index):

        prev = ""
        idx = -1
        found = {}
        phase = 1
        for i in range(index, len(arr)):

            if (prev.startswith('V:')):
                phase = 2

            if (phase==2):
                if (not prev.startswith('V:') and (arr[i] in found)):
                    idx = i
                    #print(idx)
                    break
                else:
                    found[arr[i]] = True
            else:
                if not (arr[i] in found):
                    found[arr[i]] = True
                elif ((arr[i] in found) and i+1!=len(arr)):
                    idx = i
                    #print(idx)
                    break
                    

            prev = arr[i]

        if (idx != -1):
            del arr[idx]
            #print(arr)
            deleteMultipleRel(arr, idx)
        elif (not prev.startswith('V:') and (arr[i] in found)):
            arr.pop()
    
    return arr

'''arr = ['titik', 'garis', 'titik', 'titik', 'V: A', 'garis', 'garis', 'V: A', 'titik', 'V: B', 'titik']
print(arr)
print(deleteMultipleRel(arr, 0))''' 

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

    values = ["jakarta", "indonesia", "india", "a", "b", "c"]
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
    #parser = nltk.ShiftReduceParser(lgrammar)

    tokens = text.split()

    return parser.parse(tokens)

hasil = None
# menghilangkan 'di', 'yang', 'ada di', 'dengan'
# ada harus bener-bener kata; alternatif sementara: yang ada
# jangan ada kata ada dulu
removeList = ['ada', 'masing', 'tiap', 'dengan', 'besar', 'hadap', 'milik', 'antara']
prefixList = ['ber-']
stemList = ['beribukota', 'ibukota']

# tampilkan nama mahasiswa yang nilainya lebih dari 50 dan kurang dari 100
# stemming process
sentence = input()
sentence = sentence.lower()

# sementara pake :

extractor = re.compile(r'\(\s*\d+\s*,\s*\d+\s*\)')
keepList = extractor.findall(sentence)
for keep in keepList:
    temp = keep.replace(',', ':')
    sentence = sentence.replace(keep, temp)

sentence = sentence.replace(',', ' xyz')

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
    output = output.replace(' '+elem+' ', ' ')
for elem in prefixList:
    output = output.replace(elem, '')
for i in range(0, len(stemList), 2):
    output = output.replace(stemList[i], stemList[i+1])
output = output.replace(' xyz', ' ,')
print("Hasil remove: "+output)

parameter = {
        "PANJANG": 1,
        "LUAS": 1,
        "KELILING": 1,
        "INSIDE": 2,
        "OUTSIDE": 2,
        "JARAK": 2,
        "OVERLAP": 2,
    }

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
        "OVERLAP": 'ST_Intersection'
    }

    if keyword in functions:
        return functions[keyword]
    else:
        return 'NOT FOUND'

def declareFunctions(keyword, params):

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

'''def getIndices(arrs, code):
    indices = [i for i, x in enumerate(arrs) if x == code]
    return indices'''

def getIndexTwoElmt(arrs, rel, code):

    for i in range(0, len(arrs)-1):

        if (arrs[i]==rel and arrs[i+1]==code):
            return i
    return -1

#arrs = ['titik', 'A', 'titik', 'C', 'titik']
#print(getIndexTwoElmt(arrs, 'titik', 'C'))


def addUniqueCode(arrs, rel, code):

    indices = getIndexTwoElmt(arrs, rel, code)
    if (indices!=-1):
        arrs.pop()
    else:
        arrs.append(code)

    return arrs

#print(addUniqueCode(arrs,'titik', 'D'))

'''def addOrdered(arrs, rel):

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

    return arrs'''

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

prevTwo = ""
prevValTwo = ""
prevNode = ""
prevValNode = ""
counter = 0
isColumn = True

def checkNode(node, *symbols):

    result = False
    for symbol in symbols:
        if (node.label()==symbol):
            result = True
            break
    return result

def isThereNonCode(arrs, *codes):

    result = False
    for arr in arrs:
        for code in codes:
            if (arr == code):
                result = True
                break
        if (result):
            break

    return result

def isCode(elmt):
    
    idx = re.search("[A-Z]:", elmt)

    return idx==None

def extractFirstRelation(arrs):

    relation = ""
    value = ""
    for arr in arrs:
        if (arr.startswith('R:')):
            relation = arr.replace('R: ', '')
        elif (arr.startswith('V:')):
            value = arr.replace('V: ', '')
        else:
            break
    
    return relation+value

def collect(node, result):

    global prevNode
    global prevValNode
    global prevTwo
    global prevValTwo
    global counter
    global isColumn

    if (type(node)==type("tes")):
        print("tes")

    elif (checkNode(node, "QUERY", "QUERIES", "COND", "CONDITION", "FIELDS", "OPERATOR")):
        isOperator = False
        for elmt in node:
            result = collect(elmt, result)
    else:
        if (node.label()=="FIELD" and prevNode!="RELATION"):
            result["fields"].append(node[0])
        elif (node.label()=="RELATION"):
            result["relation"].append(node[0])
            if (prevNode=="FIELD"):
                result["fields"].append('R: '+node[0])
        elif (node.label()=="VALUE"):
            addUniqueCode(result["relation"], prevValNode, "V: "+node[0])
            if (prevTwo=="FIELD" and prevNode=="RELATION"):
                #result["fields"].append("R: "+prevValNode)
                result["fields"].append("V: "+node[0])
                result["cond"].append("R: "+prevValNode)
            elif (prevNode=="RELATION"):
                result["cond"].append("R: "+prevValNode)
                result["fields"].append("G: "+prevValNode+" "+node[0])
            elif (prevNode=="FIELD" and prevTwo=="RELATION"):
                result["cond"].append("R: "+prevValTwo)
                result["cond"].append("F: "+prevValNode)
                result["fields"].append("G: "+prevValTwo+" "+node[0])
                #result["fields"].append("R: "+prevValTwo)
                #result["fields"].append("V: "+node[0])
            result["cond"].append("V: "+node[0])
            result["cond"].append("AND")
        elif (node.label()=="SPATIALOP"):
            if (isColumn):
                result["fields"].append("O: "+node[0].label())
            else:
                result["cond"].append("O: "+node[0].label())
        elif (node.label()=="SEPARATOR"):
            isColumn = False
        elif (node.label() == "OP"):
            print("masuk!")
            if (len(node)==2):
                if (node[0].label()=="LESS" and node[1].label()=="EQUAL"):
                    result["cond"].append("O: <=")
                elif (node[0].label()=="MORE" and node[1].label()=="EQUAL"):
                    result["cond"].append("O: >=")
            else:
                if (node[0].label()=="LESS"):
                    result["cond"].append("O: <")
                elif (node[0].label()=="MORE"):
                    result["cond"].append("O: >")
                elif (node[0].label()=="EQUAL"):
                    result["cond"].append("O: =")
        elif (node.label()=="NUMBER"):
            result["cond"].append(node[0])

        prevTwo = prevNode
        prevValTwo = prevValNode
        prevNode = node.label()
        prevValNode = node[0]
        

            

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

def getFromCode(arrs, code):

    for arr in arrs:
        if (arr.startswith(code)):
            return arr.replace(code, '')
    return ''

def recursiveWalk(cond_node, result):

    result = collect(cond_node, result)

    if (len(result["cond"])>0):
        if (result["cond"][len(result["cond"])-1] == "AND"):
            result["cond"].pop()

    return result

def searchValQuery(query, relation, value):

    query = query + "("
    for attr in attrs[delNum(relation)]:
        query = query + "r" + indices[relation+value] + "." + attr + " = '" + value + "' OR "
    query = query[:-4] + ")"

    return query

def processCond(object1, operation, object2, query):

    print("processCond")
    print(object1)
    print(operation)
    print(object2)

    '''left = ""
    if (len(object1)>0):
        left = object1[0]'''

    right = ""
    if (len(object2)>0):
        right = object2[0]

    op = ""
    if (len(operation)>0):
        op = operation[0]

    if (len(operation)>1):
        if (operation[1]=="INSIDE"):
            op = "OUTSIDE"
        elif (operation[1]=="OUTSIDE"):
            op = "INSIDE"
        elif (operation[0]=="LUAS" or operation[0]=="KELILING" or operation[0]=="PANJANG"):
            op = operation[0]

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
        # result relation CHANGE!!!
        if (not (right in result["relation"])):
            # kasus 1 relasi doang
            query = query + declareFunctions(op, ["r" + indices[result["relation"][0]] + "." + geoms[delNum(result["relation"][0])]]) + " " + operation[1] + " " + right
        else:
            query = query + declareFunctions(op, ["r" + indices[right] + "." + geoms[delNum(right)]])
    else:
        if (len(object1)>0):
            field = getFromCode(object1, 'F: ')
            relation = getFromCode(object1, 'R: ')
            value = getFromCode(object1, 'V: ')

            if (field==""):
                if (op==""):
                    query = searchValQuery(query, relation, value) + " "
                #else:
                #    query = query + "r" + indices[result["relation"][0]] + "." + left + " " + op + " " + right + " "
            else:
                if (op==""):
                    query = query + "r" + indices[relation+value] + "." + field + " = " + value + " "
                else:
                    query = query + "r" + indices[relation+value] + "." + field + " " + op + " " + right + " "
        #query = query + "r" + indices[result["relation"][0]] + "." + left + " " + op + " " + right + " "

    return query

print(hasil)

fieldlist = []
wherecond = []
indices = {}
result = {"cond": [], "relation": [], "fields": []}

result = recursiveWalk(hasil[0], result)

counter = 1
for i in range(0, len(result["relation"])):
    if (not result["relation"][i].startswith('V:')):
        if (i+1!=len(result["relation"])):
            if (result["relation"][i+1].startswith('V:')):
                temp = result["relation"][i+1].replace('V: ', '')
                indices[result["relation"][i]+temp] = str(counter)
        else:
            indices[result["relation"][i]] = str(counter)
        counter = counter + 1
#print("indices")
#print(indices)

tes = ['1', '2', '3']
#print(tes[1:])

isFunction = False
print(result)
query = "SELECT "
index = 1
if (len(result["fields"])>0):
    for elem in result["fields"]:
        if (not elem.startswith("V: ") and not elem.startswith("R: ") and not elem.startswith("G: ") and not elem.startswith("O: ")):
            #print("fields")
            #print(result["fields"][index:])
            query = query + "r" + indices[extractFirstRelation(result["fields"][index:])] + "." + elem + ", "
        elif (elem.startswith("G: ")):
            if (not isFunction):
                elem = elem.replace("G: ", "")
                founds = re.findall("\w+", elem)
                query = query + "r" + indices[founds[0]+founds[1]] + "." + geoms[founds[0]] + ", "
        elif (elem.startswith("O: ")):
            elem = elem.replace("O: ", "")
            if (parameter[elem]==2):
                elem2 = result["fields"][index]
                elem2 = elem2.replace("G: ", "")
                founds2 = re.findall("\w+", elem2)
                elem3 = result["fields"][index+1]
                elem3 = elem3.replace("G: ", "")
                founds3 = re.findall("\w+", elem3)
                query = query + declareFunctions(elem, ["r"+indices[founds2[0]+founds2[1]]+"."+geoms[founds2[0]], "r"+indices[founds3[0]+founds3[1]]+"."+geoms[founds3[0]]]) + ", "
            else:
                elem2 = result["fields"][index]
                elem2 = elem2.replace("G: ", "")
                founds2 = re.findall("\w+", elem2)
                query = query + declareFunctions(elem, ["r"+indices[founds2[0]+founds2[1]]+"."+geoms[founds2[0]]]) + ", "
            isFunction = True

        index = index + 1
    query = query[:-2] + '\n'
else:
    # sementara seperti ini dulu
    # ada kasus tunjukkan titik A dan titik B jika kedua titik bersinggungan!
    print("relation")
    print(result["relation"][1])
    query = query + "r" + indices[result["relation"][0]+result["relation"][1].replace('V: ', '')] + "." + geoms[result["relation"][0]]
    query = query + '\n'



query = query + "FROM "
for i in range(0, len(result["relation"])): #relation in result["relation"]:
    if (not result["relation"][i].startswith('V:')):
        if (i+1 < len(result["relation"])):
            if (result["relation"][i+1].startswith('V:')):
                temp = result["relation"][i+1].replace('V: ','')
                query = query + result["relation"][i] + " r" + indices[result["relation"][i]+temp] + ", "
        else:
            query = query + result["relation"][i] + " r" + indices[result["relation"][i]] + ", "

query = query[:-2] + '\n'
if (len(result["cond"])>0):
    query = query + "WHERE "
    object1 = []
    op = []
    # op dibuat list
    object2 = []
    isLeft = True
    for elem in result["cond"]: #range(0, len(result["cond"])):

        if (elem == "AND" or elem == "OR"):
            isLeft = True
            '''print(print("object1")
            print(object1)
            print("object2")
            print(object2)'''
            query = processCond(object1, op, object2, query)
            query = query + elem + " "
            object1 = []
        elif (elem.startswith("O: ")):
            op.append(elem.replace('O: ', ''))
            isLeft = False
        elif (isLeft):
            object1.append(elem)
        else:
            object2.append(elem)

    query = processCond(object1, op, object2, query)

    print(query)
else:
    print(query)


# Masih berupa field value sama relation value untuk opspasial doang

def makeRectangle(point1, point2, srid='2163'):

    return 'ST_MakeEnvelope(' + point1[0] + ',' + point1[1] + ',' + point2[0] + ',' + point2[1] + ',' + srid + ')'