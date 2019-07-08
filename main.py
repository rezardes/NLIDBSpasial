import re
import sys
import itertools
import psycopg2

import nltk
from nltk.grammar import Nonterminal, Production, CFG

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
S -> QUERIES | VALUES
QUERIES -> QUERY COMMA QUERIES | QUERY CONJ QUERIES | QUERY
QUERY -> COMMAND CONDITION
COMMAND -> 'tampil' | 'tunjuk' | 'lihat' | 'hitung' | 'kalkulasi' | 'cari'
COMMA -> ','
FIELDS -> FIELD | SPATIALOP FIELDS | FIELD FIELDS | FIELD CONJ FIELDS | FIELD COMMA CONJ FIELDS | FIELD COMMA FIELDS
VALUES -> VALUE CONJ VALUE | VALUE COMMA VALUE | VALUE VALUES | VALUE
CONDITION -> COND CONJ CONDITION | COND COMMA CONDITION | COND COMMA CONJ CONDITION | COND CONDITION | RELATION SEPARATOR CONDITION | COND SEPARATOR CONDITION | SPATIALOP OPERATOR | SPATIALOP COND OPERATOR | COND SPATIALOP OPERATOR | SPATIALOP GEOCONDS | SPATIALOP COND COND | SPATIALOP COND CONJ COND | NOT SPATIALOP COND COND | SPATIALOP COND COND OPERATOR | SPATIALOP COND | NOT SPATIALOP COND | SPATIALOP VALUES | SPATIALOP VALUES CONDITION | SPATIALOPS CONDITION | COND
GEOCONDS -> GEOCOND COMMA GEOCONDS | GEOCOND CONJ COMMA GEOCOND | GEOCOND
GEOCOND -> GEOMETRY POINT COOR CONJ POINT COOR | GEOMETRY POINT COOR SIZE NUMBER | POINT COOR OPERATOR
COND -> PART RELATION | PART RELATION VALUE | PART RELATION FIELD VALUE | FIELDS RELATION | FIELDS OPERATOR | FIELDS RELATION VALUE | FIELDS RELATION NOT VALUE | FIELDS RELATION FIELDS VALUE | FIELDS RELATION NOT FIELDS VALUE | RELATION FIELDS VALUE | RELATION FIELDS NUMBER | RELATION NOT FIELDS NUMBER | RELATION FIELDS NOT VALUE | FIELDS VALUE | FIELDS NOT VALUE | RELATION FIELDS | RELATION VALUE | RELATION NOT VALUE | SPATIALOP COND COND | SPATIALOP COND COND OPERATOR | SPATIALOP GEOCONDS | SPATIALOP OPERATOR | SPATIALOP OPERATOR RELATION VALUE | SPATIALOP
OPERATOR -> OP NUMBER | OP NUMBER UNIT | NUMBER | NUMBER UNIT
UNIT -> KM | M | MIL
KM -> 'kilometer' | 'km'
M -> 'meter' | 'm'
MIL -> 'mil'
GEOMETRY -> SQUARE | RECTANGLE
SQUARE -> 'persegi'
RECTANGLE -> 'segiempat' | 'persegi' 'panjang' | 'kotak'
POINT -> LU | RU | LB | RB | PUSAT | 'titik'
LU -> 'titik' 'kiri' 'atas'
RB -> 'titik' 'kanan' 'bawah'
PUSAT -> 'titik' 'pusat'
SIZE -> SIDE | LENGTH | WIDTH
SIDE -> 'sisi'
LENGTH -> 'panjang'
WIDTH -> 'lebar'
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
SPATIALOP -> PANJANG | LUAS | KELILING | INSIDE | OUTSIDE | JARAK | OVERLAP | OVERLAPS | MEETS | ABSIS | ORDINAT
SPATIALOPS -> SPATIALOP COMMA SPATIALOPS | SPATIALOP CONJ SPATIALOPS | SPATIALOP
ABSIS -> 'absis'
ORDINAT -> 'ordinat'
JARAK -> 'jarak'
INSIDE -> 'dalam' | 'pada'
OUTSIDE -> 'luar'
PANJANG -> 'panjang'
LUAS -> 'luas'
KELILING -> 'keliling'
OVERLAPS -> 'iris' | 'singgung'
OVERLAP -> 'irisan'
MEETS -> 'di' 'samping' | 'sebelah'
""")

# IMPLEMENTASI MASIH SALAH
def getElmtConds(conds):

    indices = []
    #found = False
    for i in range(0, len(conds)):
        if (conds[i]=="AND"):
            indices.append(i-1)
        elif (i==len(conds)-1):
            indices.append(i)

    return indices

# SEMENTARA PAKAI AND; PAKAI OR BELAKANGAN
def removeDup(conds):
    
    indices = getElmtConds(conds)
    #print(indices)

    for i in range(0, len(indices)):
        isDup = False
        idx = -1

        if (i >= len(indices)):
                break

        for j in range(i+1, len(indices)):
            count = 0

            if (j >= len(indices)):
                break

            idxLeft = indices[i]
            idxRight = indices[j]

            #isDup = True
            while (conds[idxLeft]!="AND" and idxLeft>0):
                if (conds[idxLeft]!=conds[idxRight]):
                    #print("FOUND!")
                    #isDup = False
                    idx = j
                    #print("idx", j)
                    count = count + 1
                    break
                idxLeft = idxLeft - 1
                idxRight = idxRight - 1

            if ((idxLeft==0 or conds[idxLeft]=="AND") and (idxRight==0 or conds[idxRight]=="AND")):
                isDup = True
                idx = j
            else:
                isDup = False
            
            if (isDup):
                for k in range(idx+1, len(indices)):
                    indices[k] = indices[k]-count
                trav = indices[idx]
                del conds[trav+1]
                #print("trav", trav)
                while(conds[trav]!="AND" and trav > 0):
                    del conds[trav]
                    trav = trav - 1
                del indices[idx]
                isDup = False

    return conds

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
        restoran = ['franchise', 'alamat', 'id', 'geom']
        jalan = ['gid', 'fitur', 'nama', 'daerah', 'geom']

        attrs = {
            "segitiga": temp,
            "kotak": temp,
            "titik": temp,
            "garis": temp,
            "poligon": temp,
            "negara": temp2,
            "provinsi":temp2,
            "kota": temp,
            "jalan": jalan,
            "restoran": restoran,
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
        "kota": temp,
        "restoran": temp,
        "jalan": temp,
    }

    return geoms

def getValues():

    values = ["jakarta", "indonesia", "india", "a", "b", "c"]
    return values


def makeRectangle(pointList, srid='2163'):

    pusat_X = ""
    pusat_Y = ""
    width = ""
    height = ""
    point1 = []
    point2 = []
    points = [[],[],[],[]]

    #print(len(pointList))
    for i in range(0, len(pointList)):
        pointList[i] = pointList[i].replace('G: ', '')
        if (pointList[i]=="PUSAT"):
            results = re.findall(r"\d+", pointList[i+1])
            pusat_X = results[0]
            pusat_Y = results[1]
            #print("Masuk!")
        elif (pointList[i]=="SIDE"):
            width = pointList[i+1]
            height = pointList[i+1]
        elif (pointList[i]=="WIDTH"):
            width = pointList[i+1]
        elif (pointList[i]=="HEIGHT"):
            height = pointList[i+1]
        elif (pointList[i]=="LU"):
            results = re.findall(r"\d+", pointList[i+1])
            points[0].append(results[0])
            points[0].append(results[1])
        elif (pointList[i]=="RB"):
            results = re.findall(r"\d+", pointList[i+1])
            points[2].append(results[0])
            points[2].append(results[1])

    if (pusat_X!=""):
        point1.append(str(float(pusat_X)-float(width)/2))
        point1.append(str(float(pusat_Y)+float(height)/2))
        point2.append(str(float(pusat_X)+float(width)/2))
        point2.append(str(float(pusat_Y)-float(height)/2))
    else: # sementara lihat dari LU dan RB
        point1.append(points[0][0])
        point1.append(points[0][1])
        point2.append(points[2][0])
        point2.append(points[2][1])

    return 'ST_MakeEnvelope(' + point1[0] + ', ' + point1[1] + ', ' + point2[0] + ', ' + point2[1] + ', ' + srid + ')'

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
    relations = ["segitiga", "kotak", "titik", "garis", "poligon", "negara", "kota", "provinsi", "restoran", "jalan"]
    fields = ["nama", "ibukota", "geom", "id", "id_ibukota", "alamat"]

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
    lproductions.extend([Production(lhs, ["us","route","1"])])
    lproductions.extend([Production(lhs, ["us","route","2"])])
    lproductions.extend([Production(lhs, ["state","route","2"])])
    lproductions.extend([Production(lhs, ["state","route","3"])])
    
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
removeList = ['ada', 'masing', 'tiap', 'dengan', 'besar', 'hadap', 'milik', 'antara', 'meter', 'seluruh']
prefixList = ['ber-']
stemList = ['beribukota', 'ibukota']

# tampilkan nama mahasiswa yang nilainya lebih dari 50 dan kurang dari 100
# stemming process
sentence = input()
print("preprocessing the sentence...")
sentence = sentence.lower()

# sementara pake :

extractor = re.compile(r'\(\s*\d+\s*,\s*\d+\s*\)')
keepList = extractor.findall(sentence)
for keep in keepList:
    temp = keep.replace(',', ':')
    sentence = sentence.replace(keep, temp)

sentence = sentence.replace(',', ' xyz')
sentence = sentence.replace(' irisan', ' irisanabc')

output = stemmer.stem(sentence)
output = output + " "
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
output = output.replace('irisanabc', 'irisan')
print("Hasil remove: "+output)

parameter = {
        "PANJANG": 1,
        "LUAS": 1,
        "KELILING": 1,
        "INSIDE": 2,
        "OUTSIDE": 2,
        "JARAK": 2,
        "OVERLAP": 2,
        "OVERLAPS": 2,
        "MEETS": 2,
        "ABSIS": 1,
        "ORDINAT": 1,
    }

print("parsing the sentence...")
for t in parse(output):
    hasil = t
    break

def findCode(arrs, code):

    results = []
    for i in range(0, len(arrs)):
        if (code==arrs[i]):
            results.append(i)
    
    return results

def mapToFunctions(keyword):

    functions = {
        "PANJANG": 'ST_Length',
        "LUAS": 'ST_Area',
        "KELILING": 'ST_Perimeter',
        "INSIDE": 'ST_Within',
        "OUTSIDE": 'NOT ST_Within',
        "JARAK": 'ST_Distance',
        "OVERLAP": 'ST_Intersection',
        "OVERLAPS": 'ST_Intersects',
        "MEETS": 'ST_Touches',
        "ABSIS": 'ST_X',
        "ORDINAT": 'ST_Y',
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
prevThree = ""
prevValThree = ""
prevFour = ""
prevValFour = ""
prevNode = ""
prevValNode = ""
counter = 0
isColumn = True
isGeoCond = False
isPart = False
isSpatialOps = False

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
    global prevThree
    global prevValThree
    global prevFour
    global prevValFour
    global counter
    global isColumn
    global isPart
    global isSpatialOps
    #global isGeoCond

    if (type(node)==type("tes")):
        print("tes")

    elif (checkNode(node, "QUERY", "QUERIES", "COND", "CONDITION", "FIELDS", "OPERATOR", "GEOCONDS", "GEOCOND", "SPATIALOPS")):
        
        if (node.label()=="SPATIALOPS"):
            isSpatialOps = True
        
        for elmt in node:
            result = collect(elmt, result)
        #if (isGeoCond):
        #    isGeoCond = False
    else:
        #print("prevNode "+prevNode)
        if (node.label()=="FIELD" and prevNode!="RELATION"):
            result["fields"].append(node[0])
        elif (node.label()=="RELATION"):
            result["relation"].append(node[0])
            if (prevNode=="FIELD"):
                result["fields"].append('R: '+node[0])
        elif (node.label()=="VALUE"):
            val = ""
            if (len(node)>0):
                for temp in node:
                    val = val + temp + " "
            else:
                val = node[0]
            addUniqueCode(result["relation"], prevValNode, "V: "+val)
            if (prevNode=="RELATION" and isSpatialOps):
                print("MASUK!")
                #print(prevValNode)
                result["cond"].append("R: "+prevValNode)
                result["fields"].append("G: "+prevValNode+" "+node[0])
            elif (prevTwo=="FIELD" and prevNode=="RELATION"):
                #result["fields"].append("R: "+prevValNode)
                result["fields"].append("V: "+val)
                result["cond"].append("R: "+prevValNode)
            elif (prevNode=="RELATION"):
                result["cond"].append("R: "+prevValNode)
                if (isColumn and not isSpatialOps):
                    result["fields"].append("G: "+prevValNode+" "+node[0])
            elif (prevNode=="FIELD" and prevTwo=="RELATION"):
                result["cond"].append("R: "+prevValTwo)
                result["cond"].append("F: "+prevValNode)
                result["fields"].append("G: "+prevValTwo+" "+node[0])
                #result["fields"].append("R: "+prevValTwo)
                #result["fields"].append("V: "+node[0])
            elif (prevNode=="FIELD" and prevTwo=="RELATION" and isSpatialOps):
                print(isSpatialOps)
                result["fields"].append("G: "+prevValTwo+" "+node[0])
            result["cond"].append("V: "+val)
            # Hitung jarak titik A dengan titik B!
            # Tampilkan id titik A, id titik C, dan id titik B jika jarak titik A dengan titik B kurang dari 5 dan jarak titik B dengan titik C lebih dari 7!
            # Ganti dengan pendekatan pohon!
            # prevTwo="SPATIALOP" and
            #if (prevTwo=="SPATIALOP" and result["cond"][len(result["cond"])-3] != 'O: JARAK'):
                #result["cond"].append("AND")
            if (isColumn):
                result["cond"].append("AND")
            elif (prevTwo!="SPATIALOP" and prevFour!="SPATIALOP"):
                result["cond"].append("AND")
            

        elif (node.label()=="SPATIALOP"):

            # len(result["cond"]) == 0 dihilangin
            if (len(result["cond"]) > 0):
                if (result["cond"][len(result["cond"])-1]=="AND" or result["cond"][len(result["cond"])-1]=="OR"):
                    if (prevTwo=="RELATION"):
                        result["cond"].append("R: "+prevValTwo)
                # KASUS: Tampilkan id titik A dan id titik B jika berjarak kurang dari 5! tidak berlaku
                # PERHATIKAN: Tampilkan seluruh id jalan "State Route 3" dan id jalan "State Route 2" jika bersinggungan!
                '''elif (prevTwo=="VALUE"):
                    if (prevThree=="FIELD"):
                        result["cond"].append("R: "+prevValFour)
                    else:
                        result["cond"].append("R: "+prevValThree)
                    result["cond"].append("V: "+prevValTwo)'''

            if (isColumn):
                result["fields"].append("O: "+node[0].label())
            else:
                result["cond"].append("O: "+node[0].label())

        elif (node.label()=="SEPARATOR"):
            if (prevNode=="RELATION" and prevTwo!="FIELD"):
                result["fields"].append("G: "+prevValNode)
            isColumn = False
        elif (node.label() == "OP"):
            #print("masuk!")
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
            if (prevNode=="FIELD"):
                result["relation"].append("F: "+prevValNode)
                result["relation"].append("N: "+node[0])
                if (prevTwo=="RELATION"):
                    result["cond"].append("R: "+prevValTwo)
                result["cond"].append("F: "+prevValNode)
            result["cond"].append(node[0])
            result["cond"].append("AND")
        elif (node.label()=="GEOMETRY"): 
            result["cond"].append("G: "+node[0].label())
        elif (node.label()=="POINT" or node.label()=="SIZE"):
            result["cond"].append(node[0].label())
        elif (node.label()=="COOR"):
            result["cond"].append(node[0])
        elif (node.label()=="PART"):
            isPart = True


        prevFour = prevThree
        prevValFour = prevValThree
        prevThree = prevTwo
        prevValThree = prevValTwo
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

    # CHANGE
    # Bisa dengan ketelusuran pohon
    # Bisa juga dengan menggunakan "separator"
    # Sementara pake relation 0
    # KASUS Tampilkan segitiga A yang ... dan segitiga B yang ...

    if (isPart):
        del(result["fields"][:])
        indices = findCode(result["cond"], "O: OVERLAPS")
        for idx in indices:

            print(result["fields"])

            idxFound = len(result["cond"])-1
            for i in range(idx+1, len(result["cond"])):
                if (result["cond"][i]=="AND"):
                    idxFound = i
                    break
                if (result["cond"][i].startswith("G:")):
                    result["fields"].append(result["cond"][i])
                else:
                    result["fields"].append("G: "+result["cond"][i])

                print(result["fields"])

            print(idx, idxFound)
            for i in range(idxFound, idx, -1):
                result["cond"].pop(i)

            result["fields"].insert(0, result["cond"][idx])
            result["cond"].pop(idx)
            print(result["fields"])

            idxFound = 0
            for i in range(idx-1, 0, -1):
                if (result["cond"][i]=="AND"):
                    idxFound = i
                    break
                if (result["cond"][i].startswith("G:")):
                    result["fields"].append(result["cond"][i])
                else:
                    result["fields"].append("G: "+result["cond"][i])
                result["fields"].reverse()
                #print(i)
                print(result["fields"])

            print(idx-1, idxFound-1)
            for i in range(idx-1, idxFound-1, -1):
                print(i)
                result["fields"].insert(0, result["cond"][i])
                result["cond"].pop(i)
            
        
        print("cond", result["cond"])
   
    else:
        '''temp = findCode(result["cond"], "O: OVERLAPS") 
        if (len(temp)>0):
            idx = temp[0]
        else:
            idx = -1
        print("idx", idx)
        if (idx != -1 and result["cond"][idx-1]=="AND"):
            if (len(result["relation"])>0):
                if (result["relation"][1].startswith('V:')):
                    #print("MASUK!")
                    result["cond"].insert(idx, result["relation"][1])
                    result["cond"].insert(idx, "R: "+result["relation"][0])
                else:
                    result["cond"].insert(idx, "R: "+result["relation"][0])
            else:
                result["cond"].insert(idx, "R: "+result["relation"][0])
        idx = findCode(result["cond"], "O: OVERLAPS")
        if (idx == len(result["cond"])-1):
            if (not result["relation"][1].startswith('V:')):
                result["cond"].insert(idx+1, "R: "+result["relation"][1])
            elif (len(result["relation"])==3):
                if (result["relation"].startswith('V:')):
                    result["cond"].insert(idx+1, result["relation"][2])
                    result["cond"].insert(idx+1, "R: "+result["relation"][1])
                else:
                    result["cond"].insert(idx+1, "R: "+result["relation"][2])
            elif (len(result["relation"])==4):
                result["cond"].insert(idx+1, result["relation"][3])
                result["cond"].insert(idx+1, "R: "+result["relation"][2])'''

    return result

def searchValQuery(query, relation, value):

    query = query + "("
    for attr in attrs[delNum(relation)]:
        query = query + "r" + indices[relation+value] + "." + attr + " = '" + value + "' OR "
    query = query[:-4] + ")"

    return query

def getSynonym(field):

    if (field!='id'):
        return field

def processCond(object1, operation, object2, query):

    #print("processCond")
    #print(object1)
    #print(operation)
    #print(object2)

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
        rel1 = getFromCode(object1, 'R: ')
        val1 = getFromCode(object1, 'V: ')
        if (object2[0]=="RECTANGLE"):
            geom2 = makeRectangle(object2[1:])
            '''leftUpper = []
            rightBottom = []
            extractor = re.compile('\d+')
            for i in range(2, len(object2), 2):
                if (object2[i-1]=="LU"):
                    leftUpper = extractor.findall(object2[i])
                elif (object2[i-1]=="RB"):
                    rightBottom = extractor.findall(object2[i])'''
            #geom2 = makeRectangle(leftUpper, rightBottom)
        else:
            rel2 = getFromCode(object2, 'R: ')
            val2 = getFromCode(object2, 'V: ')
            geom2 = "r" + indices[rel2+val2] + "." + geoms[rel2]

        geom1 = "r" + indices[rel1+val1] + "." + geoms[rel1]
        
        query = query + declareFunctions(op, [geom1, geom2])
        if (val2!=""):
            query = query + " AND "
            query = searchValQuery(query, rel2, val2)
    elif (op=="JARAK"):
        if (len(object1)==0):
            if (len(object2)==1):
                relation1 = result["relation"][0]
                
                if (result["relation"][1].startswith("V: ")):
                    rel1 = result["relation"][0]+result["relation"][1].replace("V: ", "")
                    if (len(result["relation"])>=3):
                        rel2 = result["relation"][2]+result["relation"][3].replace("V: ", "")
                    else:
                        rel2 = result["relation"][2]
                    relation2 = result["relation"][2]
                else:
                    rel1 = result["relation"][0]
                    if (len(result["relation"])>=2):
                        if (result["relation"][2].startswith('F')):
                            rel2 = result["relation"][1]+result["relation"][2].replace("F: ", "")+result["relation"][3].replace("N: ", "")
                        else:
                            rel2 = result["relation"][1]+result["relation"][2].replace("V: ", "")
                    else:
                        rel2 = result["relation"][1] 
                    relation2 = result["relation"][1]             
            else:
                right = object2[4]
                relation1 = object2[0].replace("R: ", "")
                relation2 = object2[2].replace("R: ", "")
                rel1 = object2[0].replace("R: ", "")+object2[1].replace("V: ", "")
                rel2 = object2[2].replace("R: ", "")+object2[3].replace("V: ", "")
            #print(rel1, relation1)
            geom1 = "r" + indices[rel1] + "." + geoms[relation1]
            geom2 = "r" + indices[rel2] + "." + geoms[relation2]
            query = query + declareFunctions(op, [geom1, geom2])
            query = query + " " + operation[1] + " " + right + " "
    elif (op=="OVERLAPS" or op=="MEETS"):

        geom1 = "r"
        geom2 = "r"
        rel1 = ""
        fld1 = ""
        val1 = ""
        rel2 = ""
        fld2 = ""
        val2 = ""

        # Kasus untuk field belum ada
        if (len(object1)==0):
            if (not result["relation"][1].startswith("V:")):
                geom1 = geom1 + indices[result["relation"][0]] + "." + geoms[result["relation"][0]]
            else:
                temp = result["relation"][1].replace("V: ", "")
                geom1 = geom1 + indices[result["relation"][0]+temp] + "." + geoms[result["relation"][0]]
        else:
            rel1 = getFromCode(object1, 'R: ')
            val1 = getFromCode(object1, 'V: ')
            fld1 = getFromCode(object1, 'F: ')
            geom1 = geom1 + indices[rel1+val1] + "." + geoms[rel1]

        if (len(object2)==0):
            if (not result["relation"][1].startswith("V:")):
                if (not result["relation"][2].startswith("V:")):
                    geom2 = geom2 + indices[result["relation"][1]] + "." + geoms[result["relation"][1]]
                else:
                    temp = result["relation"][2].replace("V: ", "")
                    geom2 = geom2 + indices[result["relation"][1]+temp] + "." + geoms[result["relation"][1]]
            else:
                if (result["relation"][3].startswith("V:")):
                    temp = result["relation"][3].replace("V: ", "")
                    geom2 = geom2 + indices[result["relation"][2]+temp] + "." + geoms[result["relation"][2]]
                else:
                    geom2 = geom2 + indices[result["relation"][2]] + "." + geoms[result["relation"][2]]
        elif (object2[0].startswith('G:')):
            geom2 = makeRectangle(object2[1:])
        else:
            rel2 = getFromCode(object2, 'R: ')
            fld2 = getFromCode(object2, 'F: ')
            val2 = getFromCode(object2, 'V: ')
            geom2 = geom2 + indices[rel2+val2] + "." + geoms[rel2]

        query = query + declareFunctions(op, [geom1, geom2]) + " "
        # mungkin saja penambahannya duplikat. Tangani itu!!!!
        if (fld1=="" and val1!=""):
            query = query + "AND "
            query = searchValQuery(query, rel1, val1) + " "
        elif (fld1!="" and val1!=""):
            query = query + "AND r" + indices[rel1+val1] + "." + fld1 + " = " + val1

        if (fld2=="" and val2!=""):
            query = query + "AND "
            query = searchValQuery(query, rel2, val2) + " "
        elif (fld2!="" and val2!=""):
            query = query + "AND r" + indices[rel2+val2] + "." + fld2 + " = " + val2


    elif (op=="LUAS" or op=="KELILING" or op=="PANJANG"):
        # result relation CHANGE!!!
        if (not (right in result["relation"])):
            # kasus 1 relasi doang
            query = query + declareFunctions(op, ["r" + indices[result["relation"][0]] + "." + geoms[delNum(result["relation"][0])]]) + " " + operation[1] + " " + right + " "
        else:
            query = query + declareFunctions(op, ["r" + indices[right] + "." + geoms[delNum(right)]]) + " "
    else:
        if (len(object1)>0):
            field = getFromCode(object1, 'F: ')
            relation = getFromCode(object1, 'R: ')
            value = getFromCode(object1, 'V: ')

            if (field==""):
                if (op==""):
                    if (value!=""):
                        query = searchValQuery(query, relation, value) + " "
                    else:
                        query = searchValQuery(query, relation, object1[len(object1)-1]) + " "
                #else:
                #    query = query + "r" + indices[result["relation"][0]] + "." + left + " " + op + " " + right + " "
            else:
                if (op==""):
                    if (value!=""):
                        query = query + "r" + indices[relation+value] + "." + field + " = " + value + " "
                    else:
                        num = object1[len(object1)-1]
                        query = query + "r" + indices[relation+field+num] + "." + field + " = " + num + " "
                else:
                    query = query + "r" + indices[relation+value] + "." + field + " " + op + " " + right + " "
        #query = query + "r" + indices[result["relation"][0]] + "." + left + " " + op + " " + right + " "

    return query

print(hasil)

fieldlist = []
wherecond = []
indices = {}
result = {"cond": [], "relation": [], "fields": []}

print("translating the sentence to SQL...")
result = recursiveWalk(hasil[0], result)

counter = 1
for i in range(0, len(result["relation"])):
    if (not result["relation"][i].startswith('V:') and not result["relation"][i].startswith('F:') and not result["relation"][i].startswith('N:')):
        if (i+1!=len(result["relation"])):
            if (result["relation"][i+1].startswith('V:')):
                temp = result["relation"][i+1].replace('V: ', '')
                indices[result["relation"][i]+temp] = str(counter)
            elif (result["relation"][i+1].startswith('F:')):
                field = result["relation"][i+1].replace('F: ', '')
                val = result["relation"][i+2].replace('N: ', '')
                indices[result["relation"][i]+field+val] = str(counter)
            else:
                indices[result["relation"][i]] = str(counter)
        else:
            indices[result["relation"][i]] = str(counter)
        counter = counter + 1

print("indices", indices)

isFunction = False
print(result)
query = "SELECT DISTINCT "
index = 1
# Sementara cuma query berupa tampilkan clipping dengan tidak ada atribut lain
if (isPart):
    rel = getFromCode(result["fields"], 'R: ')
    val = getFromCode(result["fields"], 'V: ')
    #fld = getFromCode(result["fields"], 'F: ')
    
    geom1 = "r" + indices[rel+val] + "." + geoms[rel]
    geom2 = ""

    idx = findCode(result["fields"], 'O: OVERLAPS')[0]
    rel = getFromCode(result["fields"][idx:], 'R: ')
    val = getFromCode(result["fields"][idx:], 'V: ')
    if (rel==""):
        print("elmt right")
        geom2 = makeRectangle(result["fields"][idx+2:])
        '''for elmt in result["fields"][idx+1:]:
            makeRectangle(result["fields"][:])
            print(elmt)'''
    else:
        geom2 = "r" + indices[rel+val] + "." + geoms[rel]

    query = query + declareFunctions('OVERLAP', [geom1, geom2]) + "\n"
        # mungkin saja penambahannya duplikat. Tangani itu!!!!
    '''if (fld1=="" and val1!=""):
        query = query + "AND "
        query = searchValQuery(query, rel1, val1) + " "
    elif (fld1!="" and val1!=""):
        query = query + "AND r" + indices[rel1+val1] + "." + fld1 + " = " + val1

    if (fld2=="" and val2!=""):
        query = query + "AND "
        query = searchValQuery(query, rel2, val2) + " "
    elif (fld2!="" and val2!=""):
        query = query + "AND r" + indices[rel2+val2] + "." + fld2 + " = " + val2'''

elif (len(result["fields"])>0):
    for elem in result["fields"]:
        if (not elem.startswith("V: ") and not elem.startswith("R: ") and not elem.startswith("G: ") and not elem.startswith("O: ")):
            #print("fields")
            #print(result["fields"][index:])
            query = query + "r" + indices[extractFirstRelation(result["fields"][index:])] + "." + getSynonym(elem) + ", "
        elif (elem.startswith("G: ")):
            if (not isFunction):
                elem = elem.replace("G: ", "")
                founds = re.findall("\w+", elem)
                if (len(founds)==2):
                    query = query + "r" + indices[founds[0]+founds[1]] + "." + geoms[founds[0]] + ", "
                else:
                    query = query + "r" + indices[founds[0]] + "." + geoms[founds[0]] + ", "
        elif (elem.startswith("O: ")):
            elem = elem.replace("O: ", "")
            if (parameter[elem]==2):
                i = index
                while (result["fields"][i].startswith('O:')):
                    i = i + 1
                elem2 = result["fields"][i]
                elem2 = elem2.replace("G: ", "")
                founds2 = re.findall("\w+", elem2)
                elem3 = result["fields"][index+1]
                elem3 = elem3.replace("G: ", "")
                founds3 = re.findall("\w+", elem3)
                query = query + declareFunctions(elem, ["r"+indices[founds2[0]+founds2[1]]+"."+geoms[founds2[0]], "r"+indices[founds3[0]+founds3[1]]+"."+geoms[founds3[0]]]) + ", "
            else:
                i = index
                while (result["fields"][i].startswith('O:')):
                    i = i + 1
                elem2 = result["fields"][i]
                elem2 = elem2.replace("G: ", "")
                founds2 = re.findall("\w+", elem2)
                query = query + declareFunctions(elem, ["r"+indices[founds2[0]+founds2[1]]+"."+geoms[founds2[0]]]) + ", "
            isFunction = True

        index = index + 1
    query = query[:-2] + '\n'
else:
    # sementara seperti ini dulu
    # ada kasus tunjukkan titik A dan titik B jika kedua titik bersinggungan!
    # tunjukkan dua garis yang saling bersinggungan!
    #print("relation")
    #print(result["relation"][1])
    if (len(result["relation"])==1):
        query = query + "r" + indices[result["relation"][0]] + "." + geoms[result["relation"][0]]
        query = query + '\n'
    '''else:
        rel = ""
        val = ""
        for i in range(0, len(result["relation"])):
            if (not result["relation"][i].startswith('V:')):
                if (i+1!=len(result["relation"])):
                    if (result["relation"][i+1].startswith('V:')):
                        val = result["relation"][i+1].replace('V: ', '')
                    rel = result["relation"][i]     
                else:
                    rel = result["relation"][i]
                
                query = query + 
        query = query + "r" + indices[result["relation"][0]+result["relation"][1].replace('V: ', '')] + "." + geoms[result["relation"][0]]
        query = query + kurang endline'''

query = query + "FROM "
for i in range(0, len(result["relation"])): #relation in result["relation"]:
    if (not result["relation"][i].startswith('V:') and not result["relation"][i].startswith('F:') and not result["relation"][i].startswith('N:')):
        if (i+1 < len(result["relation"])):
            if (result["relation"][i+1].startswith('V:')):
                temp = result["relation"][i+1].replace('V: ','')
                query = query + result["relation"][i] + " r" + indices[result["relation"][i]+temp] + ", "
            elif (result["relation"][i+1].startswith('F:')):
                temp = result["relation"][i+1].replace('F: ','')
                temp2 = result["relation"][i+2].replace('N: ','')
                query = query + result["relation"][i] + " r" + indices[result["relation"][i]+temp+temp2] + ", "
            else:
                query = query + result["relation"][i] + " r" + indices[result["relation"][i]] + ", "
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
            op = []
            object2 = []
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

'''print("querying to the DB...")
conn = psycopg2.connect(host="localhost", database="sample", user="postgres", password="1234")
cur = conn.cursor()
cur.execute(query)
hasil = cur.fetchall()
print(hasil)
cur.close()'''
