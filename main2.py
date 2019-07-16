import re
import sys
import itertools
import psycopg2

from parsers import *

import nltk
from nltk.grammar import Nonterminal, Production, CFG

print("Masukkan basis data yang digunakan: ")
database_name = input()

# Jangan lupa ganti jadi posisi robot

#def extractPrevLeft():


# IMPLEMENTASI MASIH SALAH
def getElmtConds(conds):

    indices = []
    
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

def getAttrs():

        temp = ['id', 'nama', 'geom']
        temp2 = ['id', 'nama', 'id_ibukota', 'geom']
        restoran = ['franchise', 'alamat', 'id', 'geom']
        jalan = ['gid', 'fitur', 'nama', 'daerah', 'geom']
        burung = ['id', 'nama']
        posisi = ['id', 'id_burung', 'waktu', 'coordinates']
        #posisi = ['id', 'id_robot', 'waktu', 'coordinates']
        franchise = ['id', 'franchise']

        attrs = {
            "segitiga": temp,
            "lingkaran": temp,
            "kotak": temp,
            "titik": temp,
            "garis": temp,
            "poligon": temp,
            "negara": temp2,
            "sungai": temp,
            "provinsi":temp2,
            "kota": temp,
            "jalan": jalan,
            "restoran": restoran,
            "burung": burung,
            "posisi": posisi,
            "franchise": franchise,
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
        "sungai": temp,
        "provinsi": temp,
        "kota": temp,
        "restoran": temp,
        "jalan": temp,
        "posisi": "coordinates",
        "lingkaran": temp,
    }

    return geoms

def getTypeGeom():

    temp = "polygon"

    types = {
        "segitiga": temp,
        "kotak": temp,
        "titik": temp,
        "garis": temp,
        "poligon": temp,
        "negara": temp,
        "sungaigeom": temp,
        "provinsi": temp,
        "kota": "point",
        "restorangeom": "point",
        "jalangeom": "line",
        "posisicoordinates": "point",
        "lingkarangeom": "polygon",
    }

    return types

def getConnection(rel):

    connection = {
        "restoran": ["franchise"],
        "franchise": ["restoran"],
        "robot": ["posisi"],
        "posisi": ["burung"], #robot
        "burung": ["posisi"],
    }

    if rel in connection:
        return connection[rel]
    else:
        return ''

def displacement(fromUnit, toUnit):

    basicUnit = ["KM", "HM", "DAM", "M", "DM", "CM", "MM"]
    otherUnit = {"MIL": 1000}
    calc = 1

    if (fromUnit in basicUnit and toUnit in basicUnit):
        idxF = basicUnit.index(fromUnit)
        idxT = basicUnit.index(toUnit)
        calc = pow(10, idxT-idxF)
    elif (fromUnit in otherUnit):
        idxF = basicUnit.index("M")
        idxT = basicUnit.index(toUnit)
        calc = pow(10, idxT-idxF)*otherUnit[fromUnit]

    return calc


def convert(value, fromUnit, toUnit):

    return str(value*displacement(fromUnit, toUnit))


def getSRID():

    temp = "2163"

    geoms = {
        "segitigageom": temp,
        "kotakgeom": temp,
        "titikgeom": temp,
        "garisgeom": temp,
        "poligongeom": temp,
        "negarageom": temp,
        "sungaigeom": temp,
        "provinsigeom": temp,
        "kotageom": temp,
        "restorangeom": temp,
        "jalangeom": temp,
        "posisicoordinates": "2163",
    }

    return geoms

def getUnit():

    temp = "M"

    units = {
        "2163": temp
    }

    return units

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

print("\nMasukkan query:")
attrs = getAttrs()
geoms = getGeom()
units = getUnit()
srids = getSRID()
types = getTypeGeom()

# menghilangkan 'di', 'yang', 'ada di', 'dengan'
# ada harus bener-bener kata; alternatif sementara: yang ada
# jangan ada kata ada dulu
removeList = ['ada', 'masing', 'tiap', 'dengan', 'besar', 'hadap', 'milik', 'antara', 'meter', 'seluruh']
prefixList = ['ber-']
stemList = ['beribukota', 'ibukota']

# tampilkan nama mahasiswa yang nilainya lebih dari 50 dan kurang dari 100
# stemming process
sentence = input()
#print("\nMenguraikan kalimat...")
sentence = parse(sentence)
print(sentence)

# sementara pake :

'''extractor = re.compile(r'\(\s*\d+\s*,\s*\d+\s*\)')
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
print("Hasil remove: "+output)'''

parameter = {
        "PANJANG": 1,
        "LUAS": 1,
        "KELILING": 1,
        "IN": 2,
        "OUTSIDE": 2,
        "JARAK": 2,
        "OVERLAP": 2,
        "OVERLAPS": 2,
        "MEETS": 2,
        "ABSIS": 1,
        "ORDINAT": 1,
    }

'''print("parsing the sentence...")
for t in parse(output):
    hasil = t
    break'''

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
        "IN": 'ST_Within',
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

def declareAgg(agg):
    
    aggs = {
        "SUM": "SUM",
        "MAX": "MAX",
        "MIN": "MIN",
        "COUNT": "COUNT"
    }

    return aggs[agg]

def declareFunctions(keyword, params, *types):

    function = mapToFunctions(keyword)
    if (len(types)>0):
        if ( ("point" in types[0] or "line" in types[0]) and ("point" in types[1] or "line" in types[1]) and keyword=="IN" ):  
            function = "ST_Intersects"

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
isField = False
isComma = False
isRelation = False

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
    
    return relation, value

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
    global isField
    global isPart
    global isSpatialOps
    # Perhatikan kasus komma di kondisi lain
    global isComma
    global isRelation
    #global isGeoCond

    #if (type(node)==type("tes")):
        #print("tes")

    if (checkNode(node, "QUERY", "QUERIES", "COND", "CONDITION", "FIELDS", "OPERATOR", "GEOCONDS", "GEOCOND", "SPATIALOPS")):
        
        if (node.label()=="SPATIALOPS"):
            isSpatialOps = True
        
        for elmt in node:
            result = collect(elmt, result)
        #if (isGeoCond):
        #    isGeoCond = False
    else:
        #print("prevNode "+prevNode)
        if (node.label()=="FIELD" and not isRelation):
            if (isColumn):
                result["fields"].append(node[0])
            isField = True
        elif (node.label()=="RELATION"):
            isRelation = True
            result["relation"].append(node[0])
            if (prevNode=="FIELD"):
                isField = True
                result["fields"].append('R: '+node[0])
        elif (node.label()=="VALUE"):
            val = ""
            if (len(node)>1):
                for temp in node:
                    val = val + temp + " "

                temp = list(val)
                temp[len(temp)-1] = ""
                val = "".join(temp)
                #val = val.reverse()
                #val.replace(" ", "")
                #val = val.reverse()
            else:
                val = node[0]
            #print(prevValNode, " ", val)
            if (prevNode=="RELATION"):
                addUniqueCode(result["relation"], prevValNode, "V: "+val)
            if (prevNode=="RELATION" and isSpatialOps):
                #print("MASUK!")
                #print(prevValNode)
                result["cond"].append("R: "+prevValNode)
                result["fields"].append("G: "+prevValNode+" "+val)
            elif (prevTwo=="FIELD" and prevNode=="RELATION"):
                #print("3")
                #result["fields"].append("R: "+prevValNode)
                result["fields"].append("V: "+val)
                result["cond"].append("R: "+prevValNode)
            elif (prevNode=="RELATION"):
                result["cond"].append("R: "+prevValNode)
                if (isColumn and not isSpatialOps and not isField and not isComma):
                    result["fields"].append("G: "+prevValNode+" "+val)
            elif (prevNode=="FIELD" and prevTwo=="RELATION"):
                #print("2")
                result["cond"].append("R: "+prevValTwo)
                result["cond"].append("F: "+prevValNode)
                result["fields"].append("G: "+prevValTwo+" "+val)
                #result["fields"].append("R: "+prevValTwo)
                #result["fields"].append("V: "+node[0])
            elif (prevNode=="FIELD" and prevTwo=="RELATION" and isSpatialOps):
                #print("1")
                #print(isSpatialOps)
                result["fields"].append("G: "+prevValTwo+" "+val)
            elif (prevNode=="FIELD"):
                result["cond"].append("F: "+prevValNode)
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

        elif (node.label()=="AGGREGATE"):
            result["fields"].append("A: "+node[0].label())
            
        elif (node.label()=="NOT"):
            result["cond"].append("O: NOT")

        elif (node.label()=="SPATIALOP"):

            # len(result["cond"]) == 0 dihilangin
            if (len(result["cond"]) > 0):
                if (result["cond"][len(result["cond"])-1]=="AND" or result["cond"][len(result["cond"])-1]=="OR"):
                    if (prevTwo=="RELATION"):
                        #print("YAAY!!!")
                        result["cond"].append("R: "+prevValTwo)
                        if (prevNode=="VALUE"):
                            result["cond"].append("V: "+prevValNode)
                        
            # Untuk dua kolom bagaimana?
            # Mungkin bagian ini akan menyebabkan redudansi
            #elif (prevNode=="SEPARATOR" and prevTwo=="RELATION"):
                #result["cond"].append("R: "+prevValTwo)

                # KASUS: Tampilkan id titik A dan id titik B jika berjarak kurang dari 5! tidak berlaku
                # PERHATIKAN: Tampilkan seluruh id jalan "State Route 3" dan id jalan "State Route 2" jika bersinggungan!
                '''elif (prevTwo=="VALUE"):
                    if (prevThree=="FIELD"):
                        result["cond"].append("R: "+prevValFour)
                    else:
                        result["cond"].append("R: "+prevValThree)
                    result["cond"].append("V: "+prevValTwo)'''

            if (isColumn and not isField):
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
        elif (node.label()=="UNIT"):
            result["cond"][len(result["cond"])-1] = "U: "+node[0].label()
            result["cond"].append("AND")
        elif (node.label()=="GEOMETRY"): 
            result["cond"].append("G: "+node[0].label())
        elif (node.label()=="POINT" or node.label()=="SIZE"):
            result["cond"].append(node[0].label())
        elif (node.label()=="COOR"):
            result["cond"].append(node[0])
        elif (node.label()=="PART"):
            isPart = True
        elif (node.label()=="COMMA"):
            isComma = True


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

appendWhere = ''

def recursiveWalk(cond_node, result):

    global appendWhere

    result = collect(cond_node, result)

    if (len(result["cond"])>0):
        if (result["cond"][len(result["cond"])-1] == "AND"):
            result["cond"].pop()

    # CHANGE
    # Bisa dengan ketelusuran pohon
    # Bisa juga dengan menggunakan "separator"
    # Sementara pake relation 0
    # KASUS Tampilkan segitiga A yang ... dan segitiga B yang ...

    # PERHATIKAN pula kasus relasi lebih dari satu
    for i in range(0, len(result["fields"])):
        elem = result["fields"][i]
        if (not elem.startswith("V: ") and not elem.startswith("R: ") and not elem.startswith("G: ") and not elem.startswith("O: ") and not elem.startswith("A: ")):
            if (i+1 < len(result["fields"])):
                if (result["fields"][i+1].startswith("R: ")):
                    rel = result["fields"][i+1].replace('R: ', '')
                    relAns = ""
                    connection = getConnection(rel)
                    for connect in connection:
                        if (elem in attrs[connect]):
                            relAns = connect
                    if (relAns!=""):
                        result["relation"].append(relAns)
                    #appendWhere = rel + "." +  + " = " +  relAns + "." + 

    if (isPart):
        del(result["fields"][:])
        indices = findCode(result["cond"], "O: OVERLAPS")
        for idx in indices:

            #print(result["fields"])

            idxFound = len(result["cond"])-1
            for i in range(idx+1, len(result["cond"])):
                if (result["cond"][i]=="AND"):
                    idxFound = i
                    break
                if (result["cond"][i].startswith("G:")):
                    result["fields"].append(result["cond"][i])
                else:
                    result["fields"].append("G: "+result["cond"][i])

                #print(result["fields"])

            #print(idx, idxFound)
            for i in range(idxFound, idx, -1):
                result["cond"].pop(i)

            result["fields"].insert(0, result["cond"][idx])
            result["cond"].pop(idx)
            #print(result["fields"])

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
                #print(result["fields"])

            #print(idx-1, idxFound-1)
            for i in range(idx-1, idxFound-1, -1):
                #print(i)
                result["fields"].insert(0, result["cond"][i])
                result["cond"].pop(i)
            
        
        #print("cond", result["cond"])
   
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

def getDefaultAttr(relation):

    temp = "nama"
    relations = {
        "segitiga": temp,
        "kotak": temp,
        "titik": temp,
        "garis": temp,
        "poligon": temp,
        "negara": temp,
        "sungai": temp,
        "provinsi": temp,
        "kota": temp,
        "restoran": "franchise",
        "jalan": temp,
        "robot": temp,
        "burung": temp,
        "posisi": "coordinates",
        "franchise": "franchise",
        "lingkaran": temp,
    }

    return relations[relation]

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

    '''if (len(operation)>1):
        if (operation[1]=="IN"):
            op = "OUTSIDE"
        elif (operation[1]=="OUTSIDE"):
            op = "IN"
        elif (operation[0]=="LUAS" or operation[0]=="KELILING" or operation[0]=="PANJANG"):
            op = operation[0]'''

    if (op=="IN" or op=="OUTSIDE"):
        #print("IN")
        geom1 = ""
        geom2 = ""
        rel1 = getFromCode(object1, 'R: ')
        val1 = getFromCode(object1, 'V: ')
        if (not rel1 in geoms):
            for con in getConnection(rel1):
                if (con in geoms):
                    rel1 = con
                    val1 = ""
        rel2 = ""
        val2 = ""
        val1Id = val1.replace(' ', '')
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
            
            if (not rel2 in geoms):
                for con in getConnection(rel2):
                    if (con in geoms):
                        rel2 = con
                        val2 = ""
            val2Id = val2.replace(' ', '')
            geom2 = "r" + indices[rel2+val2Id] + "." + geoms[rel2]

        geom1 = "r" + indices[rel1+val1] + "." + geoms[rel1]
        
        query = query + declareFunctions(op, [geom1, geom2], types[rel1+geoms[rel1]], types[rel2+geoms[rel2]])
        if (val2!=""):
            query = query + " AND "
            #val2Id = val2.replace(' ', '')
            query = query + "r" + indices[rel2+val2Id] + "." + getDefaultAttr(rel2) + " = '" + val2 + "'"
            #query = searchValQuery(query, rel2, val2)
    elif (op=="JARAK"):
        if (len(object1)==0):
            if (len(object2)==1 or len(object2)==2):
                relation1 = result["relation"][0]
                
                if (result["relation"][1].startswith("V: ")):
                    temp = result["relation"][1].replace("V: ", "")
                    temp = temp.replace(" ", "")
                    rel1 = result["relation"][0]+temp
                    if (len(result["relation"])>=3):
                        temp = result["relation"][3].replace("V: ", "")
                        temp = temp.replace(" ", "")
                        rel2 = result["relation"][2]+temp
                    else:
                        rel2 = result["relation"][2]
                    relation2 = result["relation"][2]
                else:
                    rel1 = result["relation"][0]
                    if (len(result["relation"])>=2):
                        if (result["relation"][2].startswith('F')):
                            temp = result["relation"][2].replace("F: ", "")
                            temp = temp.replace(" ", "")
                            rel2 = result["relation"][1]+temp+result["relation"][3].replace("N: ", "")
                        else:
                            temp = result["relation"][2].replace("V: ", "")
                            temp = temp.replace(" ", "")
                            rel2 = result["relation"][1]+temp
                    else:
                        rel2 = result["relation"][1] 
                    relation2 = result["relation"][1]             
            else:
                right = object2[4]
                relation1 = object2[0].replace("R: ", "")
                relation2 = object2[2].replace("R: ", "")
                temp = object2[1].replace("V: ", "")
                temp = temp.replace(" ", "")
                rel1 = object2[0].replace("R: ", "")+temp
                temp = object2[3].replace("V: ", "")
                temp = temp.replace(" ", "")
                rel2 = object2[2].replace("R: ", "")+temp
            #print(rel1, relation1)
            satuan = getFromCode(object2, 'U: ')
            #print("satuan", satuan)
            #print("tujuan", units[srids[relation1+geoms[relation1]]])
            geom1 = "r" + indices[rel1] + "." + geoms[relation1]
            geom2 = "r" + indices[rel2] + "." + geoms[relation2]
            query = query + declareFunctions(op, [geom1, geom2])
            query = query + " " + operation[1] + " " + convert(int(right), satuan, units[srids[relation1+geoms[relation1]]]) + " "
    
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
            val1Id = val1.replace(' ', '')
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
            val2Id = val2.replace(' ', '')
            geom2 = geom2 + indices[rel2+val2] + "." + geoms[rel2]

        query = query + declareFunctions(op, [geom1, geom2]) + " "
        # mungkin saja penambahannya duplikat. Tangani itu!!!!
        if (fld1=="" and val1!=""):
            query = query + "AND "
            query = query + "lower(r" + indices[rel1+val1Id] + "." + getDefaultAttr(rel1) + ") = '" + val1 + "'"
            #query = searchValQuery(query, rel1, val1) + " "
        elif (fld1!="" and val1!=""):
            query = query + "AND lower(r" + indices[rel1+val1Id] + "." + fld1 + ") = '" + val1 + "'"

        if (fld2=="" and val2!=""):
            query = query + "AND "
            query = query + "lower(r" + indices[rel2+val2Id] + "." + getDefaultAttr(rel2) + ") = '" + val2 + "'"
            #query = searchValQuery(query, rel2, val2) + " "
        elif (fld2!="" and val2!=""):
            query = query + "AND r" + indices[rel2+val2Id] + "." + fld2 + " = '" + val2 + "'"


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
            valueId = value.replace(' ', '') 

            if (field==""):
                if (op==""):
                    if (value!=""):
                        #query = searchValQuery(query, relation, value) + " "
                        query = query + "lower(r" + indices[relation+valueId] + "." + getDefaultAttr(relation) + ") = '" + value + "' "
                    else:
                        query = query + "lower(r" + indices[relation+object1[len(object1)-1]] + "." + getDefaultAttr(relation) + ") = '" + object1[len(object1)-1] + "' "
                        #query = searchValQuery(query, relation, object1[len(object1)-1]) + " "
                #else:
                #    query = query + "r" + indices[result["relation"][0]] + "." + left + " " + op + " " + right + " "
            else:
                if (op==""):
                    if (value!=""):
                        query = query + "lower(r" + indices[relation+valueId] + "." + field + ") = '" + value + "' "
                    else:
                        num = object1[len(object1)-1]
                        query = query + "r" + indices[relation+field+num] + "." + field + " = " + num + " "
                else:
                    query = query + "r" + indices[relation+valueId] + "." + field + " " + op + " " + right + " "
        #query = query + "r" + indices[result["relation"][0]] + "." + left + " " + op + " " + right + " "

    return query

#print(hasil)

fieldlist = []
wherecond = []
indices = {}
result = {"cond": [], "relation": [], "fields": []}

print("\nmenerjemahkan kalimat menjadi SQL...")
result = recursiveWalk(sentence[0], result)
#print(result)

counter = 1
for i in range(0, len(result["relation"])):
    if (not result["relation"][i].startswith('V:') and not result["relation"][i].startswith('F:') and not result["relation"][i].startswith('N:')):
        if (i+1!=len(result["relation"])):
            if (result["relation"][i+1].startswith('V:')):
                temp = result["relation"][i+1].replace('V: ', '')
                temp = temp.replace(' ', '')
                #print("temp", temp)
                indices[result["relation"][i]+temp] = str(counter)
            elif (result["relation"][i+1].startswith('F:')):
                field = result["relation"][i+1].replace('F: ', '')
                field = field.replace(' ', '')
                val = result["relation"][i+2].replace('N: ', '')
                indices[result["relation"][i]+field+val] = str(counter)
            else:
                indices[result["relation"][i]] = str(counter)
        else:
            indices[result["relation"][i]] = str(counter)
        counter = counter + 1

#print("indices", indices)

isFunction = False
whereAppend = ""
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
        #print("elmt right")
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

# Perhatikan! Ini metode ketemu paling akhir
elif (len(result["fields"])>0):
    isAgg = False
    #aggVal = None
    for elem in result["fields"]:
        if (not elem.startswith("V: ") and not elem.startswith("R: ") and not elem.startswith("G: ") and not elem.startswith("O: ") and not elem.startswith("A: ")):
            #print("fields")
            #print(result["fields"][index:])
            rel, val = extractFirstRelation(result["fields"][index:])
            if (not elem in attrs[rel]):
                for connect in getConnection(rel):
                    if (elem in attrs[connect]):
                        rel = connect
                        val = ""
                        whereAppend = "r" + indices[rel+val] + "." 
            query = query + "r" + indices[rel+val] + "." + getSynonym(elem)
            if (isAgg):
                query = query + "), "
                isAgg = False
            else:
                query = query + ", "
        elif (elem.startswith("G: ")):
            if (not isFunction):
                elem = elem.replace("G: ", "")
                founds = re.findall("\w+", elem)
                if (len(founds)>=2):
                    #print(founds[0])
                    #print(founds[1])
                    #print("indices", indices)
                    val = ""
                    for i in range(1, len(founds)):
                        val = val + founds[i]
                    query = query + "r" + indices[founds[0]+val] + "." + geoms[founds[0]] + ", "
                else:
                    query = query + "r" + indices[founds[0]] + "." + geoms[founds[0]] + ", "
        elif (elem.startswith("A: ")):
            elem = elem.replace("A: ", "")
            isAgg = True
            #aggVal = elem
            query = query + declareAgg(elem) + "("
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

                val2 = ""
                for i in range(1, len(founds2)):
                    val2 = val2 + founds2[i]
                
                val3 = ""                
                for i in range(1, len(founds3)):
                    val3 = val3 + founds3[i]
                
                query = query + declareFunctions(elem, ["r"+indices[founds2[0]+val2]+"."+geoms[founds2[0]], "r"+indices[founds3[0]+val3]+"."+geoms[founds3[0]]])
                if (isAgg):
                    query = query + "), "
                    isAgg = False
                else:
                    query = query + ", "
            else:
                i = index
                while (result["fields"][i].startswith('O:')):
                    i = i + 1
                elem2 = result["fields"][i]
                elem2 = elem2.replace("G: ", "")
                founds2 = re.findall("\w+", elem2)
                rel = founds2[0]
                val = ""
                for i in range(1, len(founds2)):
                    val = val + founds2[i]
                query = query + declareFunctions(elem, ["r"+indices[rel+val]+"."+geoms[rel]])
                if (isAgg):
                    query = query + "), "
                    isAgg = False
                else:
                    query = query + ", "
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
                temp = temp.replace(' ', '')
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

print("\nmemproses hasil query SQL...")
import pandas as pd

conn = psycopg2.connect(host="localhost", database=database_name, user="postgres", password="1234")
cur = conn.cursor()
cur.execute(query)
hasil = cur.fetchall()
#print(hasil)
cur.close()

temp = []
counter = 0
for val in hasil:
    if (counter > 5):
        temp.append('...')
        break
    if (val[0]!=None):
        temp.append(val[0])
        counter = counter + 1

print(pd.DataFrame({'hasil': temp}))