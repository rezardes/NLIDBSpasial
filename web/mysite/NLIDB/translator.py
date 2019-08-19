import re
import sys
import itertools
import psycopg2

#! Implementasi headers
#! JANGAN LUPA OBJECT SPATIALOP REPRESENTATIF RELASI
#! JANGAN LUPA CARI TAHU TENTANG PERLUKAN IMPLEMENTASI KONDISI RELASI BERNAMA
from NLIDB.parsing import checkNode

def getDefaultAttribute():

    defAttrs = {}

    f = open("default-attribute.txt", "r")
    contents = f.readlines()
    for content in contents:
        words = content.split(':')
        defAttrs[words[0].strip()] = words[1].strip()

    return defAttrs

# Daftar Variabel Global
defAttrs = getDefaultAttribute()
#print(defAttrs)
semantics = {'jangkauan': 'circleRadius'}
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
result = {"cond": [], "relation": [], "fields": []}
indices = {}
appendWhere = ""
whereList = []
headers = []
substitute = {}
manyValues = {}
values = {}
relations = {}
fields = {}
connections = {}
attrs = {}
geoms = {}
geoColumns = {}
synSet = {}

#! Mungkin bisa digabung atau dioptimasi
def isConnected(rel1, rel2):

    for i in rangeDestinationRel(connections[rel1]):
        if (connections[rel1][i]==rel2):
            return True

    return False

'''def addSeparator():

    idxList = []
    prevRel = ""
    for idx, rel in enumerate(result["relation"]):
        if (not isNonFieldinFields(rel)):
            if (prevRel!=""):
                if (not isConnected(prevRel, rel)):
                    idxList.append(idx)
            prevRel = rel'''

def getIdxDestRel(rel1, rel2):

    for i in rangeDestinationRel(connections[rel1]):
        if (connections[rel1][i]==rel2):
            return i

    return -1

def addSeparator():

    prevRel = ""
    idxList = []
    for idx, rel in enumerate(result["relation"]):
        if (not isNonFieldinFields(rel) and rel!='|'):
            if (prevRel!=""):
                if (not isConnected(prevRel, rel)):
                    idxList.append(idx)
            prevRel = rel
            #print("prevRel rel", prevRel, rel)
        else:
            prevRel = ""

    #print("idxList", idxList)
    print("bef insert", result["relation"])
    for idx in idxList:
        result["relation"].insert(idx, '|')
    print("after insert", result["relation"])

def makeAppend():

    query = ""
    prevRel = ""
    for i, rel in enumerate(result["relation"]):
        
        if (not isNonFieldinFields(rel)):
            if (prevRel!=""):
                if (isConnected(prevRel, rel)):

                    prevVal = ""
                    if (result["relation"][prevIdx].startswith("V:")):
                        prevVal = result["relation"][prevIdx+1].replace("V: ", "")

                    val = ""
                    if (result["relation"][i+1].startswith("V:")):
                        val = result["relation"][i+1].replace("V: ", "")

                    idxPrevDestRel = getIdxDestRel(prevRel, rel)
                    srcRel, srcVal = getSrcRelation(i)
                    if (srcRel == srcVal):
                        srcRel = ""
                        srcVal = ""
                    #print("prevRel prevVal srcRel srcVal", prevRel, prevVal, srcRel, srcVal)
                    query = query + "r" + getIndexRelation(prevRel, prevVal, srcRel, srcVal)  + "."
                    query = query + connections[prevRel][idxPrevDestRel-1]
                    query = query + " = "
                    query = query + "r" + getIndexRelation(rel, val, srcRel, srcVal)  + "."
                    query = query + connections[prevRel][idxPrevDestRel+1] + " AND "
            
            prevRel = rel
            prevIdx = i

    #print("connect", query)
    query = query[:-5]
    return query

def getSrcRelation(idxTarget):

    currentRel = ""
    currentVal = ""
    subRelations = result["relation"][:idxTarget+1]
    subRelations.reverse()
    #print("sub", subRelations)
    for i, rel in enumerate(subRelations):
        #print("rel", rel)
        
        if (rel=='|'):
            break
        '''if (rel.startswith("V:")):
            currentVal = rel'''
        #(i+1, result["relation"][i+1])
        #print("i", i)
        if (i+1 == len(subRelations)):
            #print(rel, " ", subRelations[i-1])
            currentRel = rel
            if (subRelations[i-1].startswith("V: ")):
                currentVal = subRelations[i-1].replace("V: ", "")
            break
        if (subRelations[i+1]=='|'):
            #print(rel, " ", subRelations[i-1])
            currentRel = rel
            if (subRelations[i-1].startswith("V: ")):
                currentVal = subRelations[i-1].replace("V: ", "")
            break

        '''if (i==len(subRelations)-1):
            break'''
        '''if (i==0):
            currentRel = rel
            if (result["relation"][i+1].startswith("V:")):
                currentVal = result["relation"][i+1].replace("V: ", "")
        if (rel=='|'):
            currentRel = result["relation"][i+1]
            if (result["relation"][i+2].startswith("V:")):
                currentVal = result["relation"][i+2].replace("V: ", "")
            else:
                currentVal = ""
        if (rel==relation):
            findElmtInArr(result["relation"][i:])'''

    return currentRel, currentVal

'''print("testResult")
print(result["relation"])
print(result["relation"][:3])
print(getSrcRelation(2))
print(getSrcRelation(1))
print(getSrcRelation(0))'''

#! Kasus multiple relation masih belum ditangani
def getIndex(keyword):
    answer = ""
    #print("keyword", keyword)
    if (keyword in indices):
        answer = indices[keyword]
    else:
        for key in indices.keys():
            if (key.startswith(keyword)):
                answer = indices[key]
                
    return answer

def convertToSQL(parsing, metadata, synonyms):

    global result
    global values
    global relations
    global fields
    global connections
    global attrs
    global manyValues
    global geoms
    global geoColumns
    global synSet

    '''relations = metadata["relations"]
    fields = metadata["fields"]
    values = metadata["values"]
    manyValues = metadata["manyValues"]
    connections = metadata["connection"]
    connections["|"] = []
    attrs = metadata["attrs"]
    geoms = metadata["geoms"]
    geoColumns = metadata["geoColumns"]
    synSet = synonyms'''

    relations = ['provinsi', 'kota', 'restoran', 'negara', 'area', 'wifi']
    fields = ['nama', 'alamat', 'franchise', 'posisi', 'populasi']
    values = ['bandung', 'medan', 'connex', 'indonesia']
    manyValues = ['jawa barat', 'yagami ramen']
    connections = {}
    connections["|"] = []
    attrs = {'provinsi':['nama', 'geom'], 'kota': ['nama', 'geom', 'populasi'], 'restoran': ['nama', 'geom', 'franchise'], 'posisi': ['posisi'], 'negara': ['nama', 'populasi'], 'wifi': ['nama', 'jangkauan'], 'area': ['nama', 'geom']}
    geoms = {'provinsi': ['geom', '4326', 'poligon'], 'negara': ['geom', '4326', 'poligon'], 'kota': ['geom', '4326', 'point'], 'restoran': ['geom', '4326', 'point'], 'posisi':['posisi', '4326', 'point'],  'area': ['geom', '4326', 'poligon']}
    geoColumns = ['geom']
    synSet = synonyms

    #print("geomsinit", geoms)
    result = recursiveWalk(parsing[0], result)
    query, headers = translate(result)
    #print("headers", headers)
    
    return query, headers

# Pemetaan ke fungsi PostGIS
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

SRID_Params = {'JARAK': 3857, 'PANJANG': 3857, 'LUAS': 3857, 'KELILING': 3857, 'ABSIS': 4326, 'ORDINAT': 4326}
SRID_Result = {'OVERLAP': 4326}
def declareFunctions(keyword, params, *types):

    function = mapToFunctions(keyword)
    if (len(types)>0):
        if ( ("point" in types[0] or "line" in types[0]) and ("point" in types[1] or "line" in types[1]) and keyword=="IN" ):  
            function = "ST_Intersects"

    if (parameter[keyword]==1):
        appendParam1 = ""
        appendParam2 = ""
        if (keyword in SRID_Params):
            appendParam1 = 'ST_Transform('
            appendParam2 = ', ' + SRID_Params[keyword] + ')'
        return function + '(' + appendParam1 + params[0] + appendParam2 + ')'
    elif (parameter[keyword]==2):
        if (keyword in SRID_Result):
            appendParam1 = 'ST_Transform('
            appendParam2 = ', ' + SRID_Params[keyword] + ')'
        return appendParam1 + function + '(' + params[0] + ', ' + params[1] + ')'
    else:
        return ''

# Ambiguitas Agregat
def declareAgg(agg):
    
    aggs = {
        "SUM": "SUM",
        "MAX": "MAX",
        "MIN": "MIN",
        "COUNT": "COUNT"
    }

    return aggs[agg]

# Perhitungan Konversi
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

#! Bagaimana dengan multifield
def findMissingField():

    key = "fields"

    isField = False
    idxList = []
    missList = []
    prevField = ""
    for idx, field in enumerate(result[key]):
        if (field.startswith("R:")):
            if (not isField):
                idxList.append(idx)
                missList.append(prevField)
            else:
                isField = False
        elif (not isNonFieldinFields(field)):
            prevField = field
            isField = True

    return missList, idxList

def getFromCodeField(idx, key, code):

    for i, arr in enumerate(result[key][idx:]):
        if (arr.startswith(code)):
            return arr.replace(code, ''), idx+i
        if (arr.startswith("V: ")):
            break

    return '', ''

def findElmtInArr(arrs, elmt):    

    #print("arrs", arrs)
    for index, value in enumerate(arrs):
        if (value == elmt):
            #print("valelmt", value, elmt)
            return index

    return -1

def getSynonym(elem):

    if (elem in synSet):
        return synSet[elem]
    else:
        return elem

#! Fixing result
def isElmtInArrs(elmt, key):

    found = False
    for arr in result[key]:
        if (arr == elmt):
            found = True

    return found

def appendUnique(key, elmt):

    temp = result[key]
    if not isElmtInArrs(elmt, key):
        temp.append(elmt)

    return temp

# Sementara cari kolom untuk satu relasi dulu
def findRel(column):

    for relation in relations:
        if (column in attrs[relation]):
            return relation
    return ''

def isNonFieldinFields(temp):

    return temp.startswith("R: ") or temp.startswith("V: ") or temp.startswith("O: ") or temp.startswith("G: ")

def getIndexRelation(relation, value="", srcRelation="", srcValue=""):

    counter = 0
    relActive = ""
    valActive = ""
    for idx, val in enumerate(result["relation"]):

        if (idx==0):
            relActive = result["relation"][0]
            if (1 < len(result["relation"]) and result["relation"][1].startswith("V:")):
                valActive = result["relation"][1].replace("V: ", "")
        #print("val", val)
        #print("relActive valActive", relActive, valActive)
        if (val=='|'):
            if (idx+1 < len(result["relation"])):
                relActive = result["relation"][idx+1]
                if (result["relation"][idx+2].startswith("V:")):
                    valActive = result["relation"][idx+2].replace("V: ", "")
        else:
            if (not isNonFieldinFields(val)):
                counter = counter + 1
            if (val==relation and (srcRelation!="" or srcValue!="")):
                if (value!=""):
                    if (result["relation"][idx+1].startswith("V: ")):
                        if (result["relation"][idx+1].replace("V: ", "")==value):
                            if (srcValue!=""):
                                #print("tes1")
                                if (relActive==srcRelation):
                                    return str(counter)
                            else:
                                #print("tes2")
                                #print(relActive, srcRelation, valActive, srcValue)
                                if (relActive==srcRelation and valActive==srcValue):
                                    return str(counter)
                else:
                    if (srcValue!=""):
                                #print("tes1")
                        if (relActive==srcRelation and valActive==srcValue):
                            return str(counter)
                    else:
                        #print("tes2")
                        #print(relActive, srcRelation, valActive, srcValue)
                        if (relActive==srcRelation):
                            return str(counter)

            if (val==relation and srcRelation=="" and srcValue==""):
                #print("tes")
                if (value!=""):
                    if (result["relation"][idx+1].replace("V: ", "")==value):
                        return str(counter)
                else:
                    return str(counter)
        
    counter = -1
    return str(counter)

def getNthStartingIdxCond(N):

    key = "cond"

    if (N==1):
        return 0
    
    counter = 1
    turn = 0
    breakPhase = False
    for temp in result[key]:
        turn = turn + 1
        if (temp=="AND"):
            counter = counter + 1
        if (counter==N):
            turn = turn + 1
            breakPhase = True
            break

    if (breakPhase):
        turn = turn - 1
    else:
        turn = -1

    return turn

def getNthStartingIdxField(N):

    key = "fields"

    '''if (N==1):
        return 0'''

    fieldPhase = True
    counter = 0
    turn = 0
    breakPhase = False
    for temp in result[key]:
        
        if (fieldPhase):
            #! Mungkin disini kurang "code"
            if (isNonFieldinFields(temp)):
                fieldPhase = False
        else:
            if (not isNonFieldinFields(temp)):
                #print("temp", temp)
                fieldPhase = True
                counter = counter + 1
                if (counter==N):
                    #print("breakPhase")
                    breakPhase = True
                    #turn = turn + 1
                    break

        turn = turn + 1
    
    if (not breakPhase):
        '''print("turn", turn)
        #turn = turn - 1
    else:'''
        turn = -1

    return turn

def findRelation(field):

    field = getSynonym(field)
    for rel in attrs:
        if (field in attrs[rel]):
            return rel
    return ''

def getConnectionHasField(relation, field):

    relAns = ''
    for i in rangeDestinationRel(connections[relation]):
        if (field in attrs[connections[relation][i]]):
            relAns = connections[relation][i]

    return relAns 

#! Mungkin Algoritmanya masih salah
def getConnectionHasGeom(source, relation):

    relAns = ''
    #print("relation", relation)
    for i in rangeDestinationRel(connections[relation]):
        #print(source, connections[relation][i])
        if ( connections[relation][i] not in source):
            if (hasGeom(connections[relation][i])):
                relAns = connections[relation][i]
                source.append(relation)
                break
            else:
                source.append(relation)
                relAns, source = getConnectionHasGeom(source, connections[relation][i])
                #source.pop()

    #print("sourceResult", source)
    return relAns, source

#! Jangan lupa implementasi delimiternya
def getSearchFields(idx):

    #print(idx)
    searchFields = {}
    searchFields["fields"] = []
    searchFields["idx"] = []
    counter = 0
    for word in result["fields"][idx:]:
        if (not isNonFieldinFields(word) and word!='|'):
            searchFields["fields"].append(word)
            searchFields["idx"].append(idx+counter)
        else:
            break
        counter = counter + 1

    searchFields["fields"].reverse()
    searchFields["idx"].reverse()

    return searchFields

def getFromCode(idx, key, code):

    for i, arr in enumerate(result[key][idx:]):
        if (arr=="AND"):
            break
        if (arr.startswith(code)):
            return arr.replace(code, ''), idx+i
    return '', ''

def traverseRelation(counter):

    if (counter==0):
        return 0

    count = -1
    for index, value in enumerate(result["relation"]):
        if not value.startswith("V:"):
            count = count + 1
        if (count == counter):
            return index

    return -1

#! Bagaimana dengan time?
# value berupa "V: "
#! Belum menangani untuk relation yang sendiri tanpa value (periksa dari keterhubungan)
#! SEKARANG MUNGKIN SUDAH TERTANGANI
def insertConnectivity(insertion, relation, value):
    idxInsertion = -1
    if (insertion != relation):
        for i in range(0, len(result["relation"])):
            if (result["relation"][i]==relation):
                if (value != "" and i+1 < len(result["relation"])):
                    if (result["relation"][i+1]==value):
                        for i in range(i+1, len(result["relation"])):
                            if (result["relation"][i] == "|"):
                                idxInsertion = i
                                break
                            elif (i == len(result["relation"])-1):
                                idxInsertion = len(result["relation"])
                            elif (result["relation"][i]==insertion):
                                idxInsertion = -1
                                break
                else:
                    for i in range(i+1, len(result["relation"])):
                        if (result["relation"][i]==insertion):
                            idxInsertion = -1
                            break
                        elif (i == len(result["relation"])-1):
                            idxInsertion = len(result["relation"])
                        elif (result["relation"][i] == "|"):
                            idxInsertion = i
                            break

    #print("idxInsertion", insertion, idxInsertion)
    
    if (idxInsertion != -1):
        found = False
        for i in range(idxInsertion, len(result["relation"])):
            if (result["relation"][i].startswith("V:")):
                break
            elif (result["relation"][i]==insertion):
                found = True

        #print("found", found)

        if (not found):
            result["relation"].insert(idxInsertion, insertion)

#! Bisa dioptimasi menjadi sudah ada silsilahnya terlebih dahulu
traversed = []
def getConnection(srcRel, destRel):

    global traversed
    
    hasil = [srcRel]
    if (isConnected(srcRel, destRel)):
       hasil = hasil + [destRel]
    else:
        for idx in rangeDestinationRel(connections[srcRel]):
            if (not srcRel in traversed):
                hasil = hasil + getConnection(connections[srcRel][idx], destRel)
            traversed.append(srcRel)

    return hasil

# Sebelumnya dikasih kodenya
#! Bagaimana kalau ada kasus yang kemunculan lebih dari 1 kali?
def findThreeElmts(elmt1, elmt2, elmt3):

    for idx, elmt in enumerate(wordList):
        if (elmt == elmt1):
            if (elmt2!=""):
                if (idx+1 >= len(wordList)):
                    if (wordList[idx+1]!=elmt2):
                        continue
            if (elmt3!=""):
                if (idx+2 >= len(wordList)):
                    if (wordList[idx+2]!=elmt3):
                        continue
            return idx

    return -1

def fixResult():

    global whereList
    global substitute
    global headers
    global traversed

    # Perbaikan separator
    addSeparator()
    #print("fase 1", result["relation"])
    #result["fields"].append("R: area")
    #result["fields"].append("V: yagami ramen")

    # PENGHILANGAN REDUDANSI result["cond"]
    #! Kenapa AND nya dua kali untuk JARAK
    prevRel = ""
    for idx, elmt in enumerate(result["cond"]):
        if (elmt==prevRel):
            del result["cond"][idx]
        prevRel = elmt

    # Jangan lupa bagaimana kalau ada spatialop
    # PERBAIKAN result["cond"]
    counter = 1
    idx = getNthStartingIdxCond(counter)
    key = "cond"
    while (idx != -1):
        
        spatialOp, idxSp = getFromCode(idx, key, 'O: ')
        relation, idxRel = getFromCode(idx, key, 'R: ') 
        field, idxField  = getFromCode(idx, key, 'F: ')
        value, idxVal = getFromCode(idx, key, 'V: ')
        times, idxTime = getFromCode(idx, key, 'T: ')

        #print("idx", idx)
        #print("getOp", spatialOp, idxSp)

        # TAHAP 1: PELENGKAPAN RELATION, FIELD, VALUE, dan SPATIALOP

        #! Jangan lupa mungkin juga OR
        #! Jangan lupa mungkin berupa time
        #! Taruh sebelum kelengkapan rel field kah?
        if (idxSp!=""):
            if (idxSp-1 < 0 or result["cond"][idxSp-1] == "AND"):
                relAns = ""
                valAns = ""
                if (relation!=""):
                    relAns = "R: "+relation
                if (value!=""):
                    valAns = "V: "+value
                idxFix = findThreeElmts("O: "+spatialOp, relAns, valAns)
                
                relFix = ""
                temp = wordList[:idxFix].copy()
                temp.reverse()
                for elmt in temp:
                    if (elmt.startswith("R: ")):
                        relFix = elmt.replace("R: ", "")
                        break

                if (not hasGeom(relFix)):
                    relTemp, source = getConnectionHasGeom([], relFix)
                    print("source", source)
                    for src in source:
                        insertConnectivity(src, relFix, "")
                    insertConnectivity(relTemp, relFix, "")
                    relFix = relTemp

                result["cond"].insert(idxSp, "R: "+relFix)
                result["cond"].insert(idxSp, "F: "+geoms[relFix][0])
                field = geoms[relFix][0]


        if (relation == "" and field != ""): #Lihat dari relation sebelumnya; Untuk dia di tempat pertama mungkin?
            idx2 = getNthStartingIdxCond(counter-1)
            relation, idxPrevRel = getFromCode(idx2, key, 'R: ')
            result["cond"].insert(idx, 'R: '+relation)
        elif (relation != "" and (value != "" or times != "") and field == ""):
            field = defAttrs[relation]
            result["cond"].insert(idx, 'F: '+field)
        #elif (relation != "" and times != "" and field == "")

        relation, idxRel = getFromCode(idx, key, 'R: ')
        field, idxField  = getFromCode(idx, key, 'F: ')
        value, idxVal = getFromCode(idx, key, 'V: ')
        times, idxTime = getFromCode(idx, key, 'T: ')

        # TAHAP 2: PERBAIKAN RELATION FIELD VALUE
        # SEMENTARA PAKE findRelation bukan connectivity
        if (field!="" and relation!="" and synSet[field] not in attrs[relation]):
            relName = findRelation(field)
            #print("tes", relName)
            result["cond"][idxRel] = "R: "+relName
            result["cond"][idxField] = "F: "+synSet[field]

            #! SEMENTARA LANGSUNG TARO DI RELATION AJA
            #result["relation"] = appendUnique("relation", relName)

            #print("relation", relName, relation)
            '''if (relName in connections[relation]):
                index = findElmtInArr(connections[relation], relName)
                #indexOrigin = findElmtInArr(connections[relation], relName)
                print("index", index)
                #print("indexOrigin", indexOrigin)
                whereList.append("R: "+relation+value)
                whereList.append("F: "+connections[relation][index-1])
                whereList.append("R: "+relName)
                whereList.append("F: "+connections[relation][index+1])'''

        counter = counter + 1
        idx = getNthStartingIdxCond(counter)

    # PENGHILANGAN REDUDANSI result["fields"]
    prevRel = ""
    for idx, rel in enumerate(result["fields"]):
        if (rel==prevRel):
            del result["fields"][idx]
        prevRel = rel

    # PERBAIKAN KELENGKAPAN FIELDS
    missField, indexList = findMissingField()
    #print("MISSING", missField, indexList)
    indexList.reverse()
    for i, idx in enumerate(indexList):
        if (missField[i]==''):
            rel = result["fields"][idx].replace("R: ", "")
            '''if (idx+1 < len(result["fields"]) and result["fields"][idx+1]):
                val = result["fields"][idx+1].replace("V: ", "")'''
            if (len(geoms[rel])==0):
                #print("gak ada geom")
                relAns, source = getConnectionHasGeom([], rel)
                result["fields"].insert(idx, geoms[relAns][0])
            else:
                result["fields"].insert(idx, geoms[rel][0])
        else:
            result["fields"].insert(idx, missField[i])

    #print("hasil", result["fields"])

    counter = 1
    idx = getNthStartingIdxField(1)
    key = "fields"
    while (idx != -1):

        relation, idxRel = getFromCodeField(idx, key, 'R: ')
        value, idxVal = getFromCodeField(idx, key, 'V: ')
        times, idxTime = getFromCodeField(idx, key, 'T: ')
        # = getFromCode(idx, key, 'F: ')
        searchFields = getSearchFields(idx)
        #print("searchFields", searchFields)
        #print(relation, " ", value)
        #print("r f v t", relation, value, times)

        # PERBAIKAN ASAL RELASI dan PENGECEKAN ANOTASI
        if (len(searchFields["fields"])-1 > 1):

            for index, field in enumerate(searchFields["fields"]):
                #print("semantics", index, field)
                #! jari-jari dan titik bersebalahan?
                if (field in semantics):
                    #print("Yes in semantics!")
                    #print("Hmm", semantics[field])
                    if (semantics[field]=="circleRadius"):
                        #! Apakah mungkin bisa relasi sudah ada atau redundan?
                        #! Jangan lupa pemeriksaan geom ada di dalam relasi yang sama
                        # Ingat sekarang pake hasil query!!!
                        #print("tes")
                        #relAns = getConnectionHasGeom('', 'wifi')
                        relAns, source = getConnectionHasGeom([], relation)
                        fieldAns = geoms[relAns][0]
                        substitute[field] = fieldAns
                        #print("src", source)
                        #! Bagaimana untuk tampilkan irisan jangkauan
                        for src in source:
                            #print("src", src)
                            insertConnectivity(src, relation, "V: "+value)
                        #print("relAns", relAns)
                        insertConnectivity(relAns, relation, "V: "+value)
                        '''if (index+1 < len(searchFields["idx"])):
                            result["fields"].insert(searchFields["idx"][index+1], fieldAns)
                        else:
                            idxPut = getNthStartingIdxField(counter+1)
                            if (idxPut == -1):
                                result["fields"].insert(len(searchFields["idx"]), fieldAns)
                            else:
                                result["fields"].insert(idxPut, fieldAns)'''

                        #result["relation"].append(relAns)

                #! Mungkin ada kasus dimana relation yang diubah butuh Value
                #! Mungkin ada kasus field ada di lebih dari satu relasi (pake connectivity)
                if (field!="" and relation!="" and synSet[field] not in attrs[relation]):
                    traversed = []
                    relName = findRelation(field)
                    relList = getConnection(relation, relName)

                    for rel in relList:
                        insertConnectivity(rel, relation, "V: "+value)    
                    '''relName = findRelation(field)
                    insertConnectivity(relName, relation, value)

                    #! Ingat!!! Jangan lupa implementasi insertRelation nanti
                    #insertRelation(searchFields["idx"][index], relName)
                    result["fields"][idxRel] = "R: "+relName
                    result["fields"][idxField] = synSet[field]

                    if (value):
                        result["fields"][idxVal] = "" 
                    if (times):
                        result["fields"][idxTime] = ""

                    #! SEMENTARA LANGSUNG TARO DI RELATION AJA
                    result["relation"] = appendUnique("relation", relName)
                    print("relation", relName, relation)'''
                    '''if (relName in connections[relation]):
                        index = findElmtInArr(connections[relation], relName)
                        whereList.append("R: "+relation+value)
                        whereList.append("F: "+connections[relation][index-1])
                        whereList.append("R: "+relName)
                        whereList.append("F: "+connections[relation][index+1])'''

        else:

            for index, field in enumerate(searchFields["fields"]):

                #! Apakah ada penghapusan field redundan?
                headers.append(field)
                
                for index, field in enumerate(searchFields["fields"]):
                #! jari-jari dan titik bersebelahan?
                    if (field in semantics):
                        if (semantics[field]=="circleRadius"):
                            #! Apakah mungkin bisa relasi sudah ada atau redundan?
                            #! Jangan lupa pemeriksaan geom ada di dalam relasi yang sama
                            headers[len(headers)-1] = "~radCircle"
                            relAns, source = getConnectionHasGeom([], relation)
                            fieldAns = geoms[relAns][0]
                            substitute[field] = fieldAns
                            
                            for src in source:
                                #print("src", src)
                                insertConnectivity(src, relation, "V: "+value)
                            insertConnectivity(relAns, relation, "V: "+value)
                            '''if (index+1 < len(searchFields["idx"])):
                                result["fields"].insert(searchFields["idx"][index+1], "R: "+relAns)
                                result["fields"].insert(searchFields["idx"][index+1], fieldAns)
                            else:
                                idxPut = getNthStartingIdxField(counter+1)
                                print("idxPut", idxPut)
                                
                                if (idxPut == -1):
                                    result["fields"].append(fieldAns)
                                    result["fields"].append("R: "+relAns)
                                else:
                                    result["fields"].insert(idxPut, fieldAns)'''

                            headers.append("~pointCircle")
                            #print("relAns", relAns)
                            #result["relation"].append(relAns)

                #! Apakah tidak apa-apa kalo value = "V: " saja
                if (field!="" and relation!="" and synSet[field] not in attrs[relation]):
                    traversed = []
                    relName = findRelation(field)
                    relList = getConnection(relation, relName)
                    #print("relList", relList)

                    for rel in relList:
                        insertConnectivity(rel, relation, "V: "+value)
                    #result["fields"][searchFields["idx"][index]] = synSet[field]
                    #result["fields"][idxRel] = "R: "+relName
                    '''if (value):
                        result["fields"][idxVal] = "" 
                    if (times):
                        result["fields"][idxTime] = ""'''

                    #! SEMENTARA LANGSUNG TARO DI RELATION AJA
                    #result["relation"] = appendUnique("relation", relName)

                    '''print("relation", relName, relation)
                    if (relName in connections[relation]):
                        index = findElmtInArr(connections[relation], relName)
                        whereList.append("R: "+relation+value)
                        whereList.append("F: "+connections[relation][index-1])
                        whereList.append("R: "+relName)
                        whereList.append("F: "+connections[relation][index+1])'''

        # TAHAP 2: PEMBERSIHAN DAN DEFFERED EXECUTION
        delList = []
        for index, value in enumerate(result["fields"]):
            if (value == ""):
                delList.append(index)

        delList.reverse()

        for index in delList:
            del(result["fields"][index])

        '''index = findElmtInArr(connections[relation], relName)
        whereList.append("R: "+relation+value)
        whereList.append("F: "+connections[relation][index-1])
        whereList.append("R: "+relName)
        whereList.append("F: "+connections[relation][index+1])'''

        counter = counter + 1
        idx = getNthStartingIdxCond(counter)

    # TAHAP 3: PENARUHAN KONDISI CONNECTIVITY
    #! YANG INI HANYA BISA KALO RELASI DITARUH BERURUT
    '''counterRel = 0
    j = traverseRelation(counterRel)
    k = traverseRelation(counterRel+1)
    while (j!=-1 and k!=-1):
        ##print("connections", connections)
        #print("index", index)
        rel1 = result["relation"][j]
        val1 = ""
        if (result["relation"][j+1].startswith("V:")):
            val1 = result["relation"][j+1].replace("V: ", "").replace(" ", "")
        rel2 = result["relation"][k]
        val2 = ""
        if (k+1 < len(result["relation"])):
            if (result["relation"][k+1].startswith("V:")):
                val2 = result["relation"][k+1].replace("V: ", "").replace(" ", "")
        index = findElmtInArr(connections[rel1], rel2)
        if (index!=-1 and index!=None):
            whereList.append("R: "+rel1+val1)
            #print("relindex", rel1, index-1)
            if (index<=0):
                whereList.append("F: "+connections[rel1][index-1])
            whereList.append("R: "+rel2+val2)
            if (index<len(connections[rel1])):
                whereList.append("F: "+connections[rel1][index+1])
        counterRel = counterRel + 1
        j = traverseRelation(counterRel)
        k = traverseRelation(counterRel+1)'''
        
def getIndexTwoElmt(arrs, rel, code):

    for i in range(0, len(arrs)-1):

        if (arrs[i]==rel and arrs[i+1]==code):
            return i
    return -1

def extractFirstRelation(arrs):

    relation = ""
    value = ""
    for idx, arr in enumerate(arrs):
        if (arr.startswith('R:')):
            relation = arr.replace('R: ', '')
            if (idx+1 < len(arrs) and arrs[idx+1].startswith('V:')):
                value = arrs[idx+1].replace('V: ', '')
            break
    
    return relation, value

'''def addSeparator():

    tempList = result["relation"].copy()
    idxList = []
    tempList.reverse()
    prevRel = ""
    for idx, rel in enumerate(tempList):
        if (not isNonFieldinFields(rel)):
            if (prevRel!=""):
                if (not isConnected(prevRel, rel)):
                    idxList.append(idx)
            prevRel = rel

    for idx in idxList:
        result["relation"].insert(idx, '|')'''

# Pengolah connections
def rangeDestinationId(connections):

    return range(2, len(connections), 3)

def rangeDestinationRel(connections):

    return range(1, len(connections), 3)

def findCode(arrs, code):

    results = []
    for i in range(0, len(arrs)):
        if (code==arrs[i]):
            results.append(i)
    
    return results

def getFromCodeInArr(arrs, code):

    for arr in arrs:
        if (arr.startswith(code)):
            return arr.replace(code, '')
    return ''

def addUniqueCode(arrs, rel, code):

    indices = getIndexTwoElmt(arrs, rel, code)
    if (indices!=-1):
        arrs.pop()
    else:
        arrs.append(code)

    return arrs

# Fungsi Pengolah geoms
def hasGeom(relation):

    return len(geoms[relation])>0

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

def processCond(object1, operation, object2, query):

    right = ""
    if (len(object2)>0):
        right = object2[0]

    op = ""
    if (len(operation)>0):
        op = operation[0]

    if (op=="IN" or op=="OUTSIDE"):
        #print("IN")
        geom1 = ""
        geom2 = ""
        #print("object1", object1)
        rel1 = getFromCodeInArr(object1, 'R: ')
        val1 = getFromCodeInArr(object1, 'V: ')
        #print("rel val", rel1, val1)
        if (not hasGeom(rel1)):
            for i in rangeDestinationRel(connections[rel1]):
                if (hasGeom(connections[rel1][i])):
                    rel1 = connections[rel1][i]
                    val1 = ""
        rel2 = ""
        val2 = ""
        val1Id = val1.replace(' ', '')
        if (object2[0]=="RECTANGLE"):
            geom2 = makeRectangle(object2[1:])
        else:
            rel2 = getFromCodeInArr(object2, 'R: ')
            val2 = getFromCodeInArr(object2, 'V: ')
            
            if (not hasGeom(rel2)):
                for i in rangeDestinationRel(connections[rel2]):
                    if hasGeom(connections[rel2][i]):
                        rel2 = connections[rel2][i]
                        val2 = ""
            #val2Id = val2.replace(' ', '')
            geom2 = "r" + getIndexRelation(rel2, val2) + "." + geoms[rel2][0]

        geom1 = "r" + getIndexRelation(rel1, val1) + "." + geoms[rel1][0]
        
        query = query + declareFunctions(op, [geom1, geom2], geoms[rel1][1], geoms[rel2][1])
        if (val2!=""):
            query = query + " AND "
            #val2Id = val2.replace(' ', '')
            query = query + "lower(r" + getIndexRelation(rel2, val2) + "." + defAttrs[rel2] + ") = '" + val2 + "' "
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
            satuan = getFromCodeInArr(object2, 'U: ')
            geom1 = "r" + indices[rel1] + "." + geoms[relation1][0]
            geom2 = "r" + indices[rel2] + "." + geoms[relation2][0]
            query = query + declareFunctions(op, [geom1, geom2])
            query = query + " " + operation[1] + " " + convert(int(right), satuan, units[geoms[relation1][2]]) + " "
    
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
                geom1 = geom1 + indices[result["relation"][0]] + "." + geoms[result["relation"][0]][0]
            else:
                temp = result["relation"][1].replace("V: ", "")
                geom1 = geom1 + indices[result["relation"][0]+temp] + "." + geoms[result["relation"][0]]
        else:
            rel1 = getFromCodeInArr(object1, 'R: ')
            val1 = getFromCodeInArr(object1, 'V: ')
            fld1 = getFromCodeInArr(object1, 'F: ')
            val1Id = val1.replace(' ', '')
            geom1 = geom1 + indices[rel1+val1] + "." + geoms[rel1][0]

        if (len(object2)==0):
            if (not result["relation"][1].startswith("V:")):
                if (not result["relation"][2].startswith("V:")):
                    geom2 = geom2 + indices[result["relation"][1]] + "." + geoms[result["relation"][1]][0]
                else:
                    temp = result["relation"][2].replace("V: ", "")
                    geom2 = geom2 + indices[result["relation"][1]+temp] + "." + geoms[result["relation"][1]][0]
            else:
                if (result["relation"][3].startswith("V:")):
                    temp = result["relation"][3].replace("V: ", "")
                    geom2 = geom2 + indices[result["relation"][2]+temp] + "." + geoms[result["relation"][2]][0]
                else:
                    geom2 = geom2 + indices[result["relation"][2]] + "." + geoms[result["relation"][2]][0]
        elif (object2[0].startswith('G:')):
            geom2 = makeRectangle(object2[1:])
        else:
            rel2 = getFromCodeInArr(object2, 'R: ')
            fld2 = getFromCodeInArr(object2, 'F: ')
            val2 = getFromCodeInArr(object2, 'V: ')
            val2Id = val2.replace(' ', '')
            geom2 = geom2 + indices[rel2+val2] + "." + geoms[rel2]

        query = query + declareFunctions(op, [geom1, geom2]) + " "
        # mungkin saja penambahannya duplikat. Tangani itu!!!!
        if (fld1=="" and val1!=""):
            query = query + "AND "
            query = query + "lower(r" + indices[rel1+val1Id] + "." + defAttrs[rel1] + ") = '" + val1 + "'"
            #query = searchValQuery(query, rel1, val1) + " "
        elif (fld1!="" and val1!=""):
            query = query + "AND lower(r" + indices[rel1+val1Id] + "." + fld1 + ") = '" + val1 + "'"

        if (fld2=="" and val2!=""):
            query = query + "AND "
            query = query + "lower(r" + indices[rel2+val2Id] + "." + defAttrs[rel2] + ") = '" + val2 + "'"
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
            field = getFromCodeInArr(object1, 'F: ')
            relation = getFromCodeInArr(object1, 'R: ')
            value = getFromCodeInArr(object1, 'V: ')
            valueId = value#.replace(' ', '') 

            if (field==""):
                if (op==""):
                    if (value!=""):
                        query = query + "lower(r" + indices[relation+valueId] + "." + defAttrs[relation] + ") = '" + value + "' "
                    else:
                        val = object1[len(object1)-1].replace("V: ", "").replace("T: ", "")
                        # Apakah efektif penangangan seperti ini?
                        if (relation+val in indices):
                            query = query + "lower(r" + getIndexRelation(relation,val) + "." + defAttrs[relation] + ") = '" + val + "' "
                        else:
                            query = query + "lower(r" + getIndexRelation(relation) + "." + defAttrs[relation] + ") = '" + val + "' "

            else:
                if (op==""):
                    if (value!=""):
                        query = query + "lower(r" + getIndexRelation(relation, valueId) + "." + field + ") = '" + value + "' "
                    else:
                        num = object1[len(object1)-1]
                        if (relation+field+num in indices):
                            query = query + "r" + getIndexRelation(relation,field+num) + "." + field + " = " + num + " "
                        elif (num.startswith("T: ")):
                            num = num.replace("T: ", "")
                            query = query + "r" + getIndexRelation(relation,"") + "." + field + " = '" + num + "' "
                        else:
                            num = num.replace("V: ", "")
                            query = query + "r" + getIndexRelation(relation,"") + "." + field + " = " + num + " "
                else:
                    query = query + "r" + getIndexRelation(relation,valueId) + "." + field + " " + op + " " + right + " "

    return query

prevTwo = ""
prevValTwo = ""
prevThree = ""
prevValThree = ""
prevFour = ""
prevValFour = ""
prevNode = ""
prevValNode = ""
counter = 0
spatialOp = ""
isColumn = True
isGeoCond = False
isPart = False
isSpatialOps = False
isField = False
isComma = False
isRelation = False
wordList = []

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
    global spatialOp
    global wordList
    # Perhatikan kasus komma di kondisi lain
    global isComma
    global isRelation

    #print("tes", result)
    
    if (checkNode(node, "QUERY", "QUERIES","COND", "CONDITION", "FIELDS", "OPERATOR", "GEOCONDS", "GEOCOND", "SPATIALOPS", "WORDS", "WORD")):
        #print("dalem checkNode",node.label())
        if (node.label()=="SPATIALOPS"):
            isSpatialOps = True
            #print("isSpatialOps", isSpatialOps)
        
        for elmt in node:
            result = collect(elmt, result)
        
        return result
    else:
        #print("luar checkNode",node.label())
        #print("isSpatialOps", isSpatialOps)
        if (node.label()=="FIELD"):
            wordList.append("F: "+node[0])

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
            wordList.append("R: "+node[0])
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
                result["relation"].append("|")
            if (prevNode=="RELATION" and isSpatialOps):
                #! JANGAN LUPA PEMERIKSAAN OVERLAP ATAU BUKAN
                #print("MASUK!")
                #print(prevValNode)
                #print("isSpatialOps", isSpatialOps)
                result["cond"].append("R: "+prevValNode)
                #print("spatialOp", spatialOp)
                if (spatialOp!="OVERLAP" and isColumn):
                    result["fields"].append("R: "+prevValNode)
                #result["cond"].append("V: "+prevValNode)
                if (isColumn):
                    result["fields"].append("V: "+val)
                #result["fields"].append("G: "+prevValNode+" "+val)
            elif (prevTwo=="FIELD" and prevNode=="RELATION"):
                #print("3")
                #result["fields"].append("R: "+prevValNode)
                result["fields"].append("V: "+val)
                result["cond"].append("R: "+prevValNode)
            elif (prevNode=="RELATION"):
                result["cond"].append("R: "+prevValNode)
                #if (isColumn and not isSpatialOps and not isField and not isComma):
                    #result["fields"].append("G: "+prevValNode+" "+val)
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
            if (prevTwo=="SPATIALOP" and result["cond"][len(result["cond"])-3] != 'O: JARAK'):
                result["cond"].append("AND")
            #print(val, isColumn)
            if (isColumn):
                result["cond"].append("AND")
            elif (prevTwo!="SPATIALOP" and prevFour!="SPATIALOP"):
                result["cond"].append("AND")

            wordList.append("V: "+val)

        elif (node.label()=="AGGREGATE"):
            result["fields"].append("A: "+node[0].label())
            wordList.append("A: "+node[0].label())
            
        elif (node.label()=="NOT"):
            result["cond"].append("O: NOT")
            wordList.append(node.label())

        elif (node.label()=="SPATIALOP"):

            spatialOp = node[0].label()
            wordList.append("O: "+node[0].label())

            # len(result["cond"]) == 0 dihilangin
            if (len(result["cond"]) > 0):
                if (result["cond"][len(result["cond"])-1]=="AND" or result["cond"][len(result["cond"])-1]=="OR"):
                    if (prevTwo=="RELATION"):
                        #print("YAAY!!!")
                        result["cond"].append("R: "+prevValTwo)
                        if (prevNode=="VALUE"):
                            result["cond"].append("V: "+prevValNode)
                            #result["cond"].append("AND")
                        
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

            #print("colField", isColumn, " ", isField)
            if (isColumn and not isField):
                result["fields"].append("O: "+node[0].label())
            else:
                result["cond"].append("O: "+node[0].label())

        elif (node.label()=="SEPARATOR"):
            if (prevNode=="RELATION" and prevTwo!="FIELD"):
                result["fields"].append("G: "+prevValNode)
            isColumn = False
            wordList.append(node.label())
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
            wordList.append("OP: "+node.label())
        elif (node.label()=="NUMBER"):
            if (prevNode=="FIELD"):
                result["relation"].append("F: "+prevValNode)
                result["relation"].append("N: "+node[0])
                if (prevTwo=="RELATION"):
                    result["cond"].append("R: "+prevValTwo)
                result["cond"].append("F: "+prevValNode)
            result["cond"].append(node[0])
            result["cond"].append("AND")
            wordList.append(node[0])
        elif (node.label()=="UNIT"):
            result["cond"][len(result["cond"])-1] = "U: "+node[0].label()
            result["cond"].append("AND")
            wordList.append("U: "+node[0].label())
        elif (node.label()=="GEOMETRY"): 
            result["cond"].append("G: "+node[0].label())
            wordList.append("G: "+node[0].label())
        elif (node.label()=="POINT" or node.label()=="SIZE"):
            result["cond"].append(node[0].label())
            wordList.append("G: "+node[0].label())
        elif (node.label()=="COOR"):
            result["cond"].append(node[0])
            wordList.append("G: "+node[0])
        elif (node.label()=="PART"):
            isPart = True
            wordList.append(node.label())
        elif (node.label()=="COMMA"):
            isComma = True
            wordList.append(node.label())
        elif (node.label()=="TIME"):
            if (prevNode=="FIELD"):
                result["cond"].append("F: "+prevValNode)
            elif (prevNode=="RELATION"):
                result["cond"].append("R: "+prevValNode)
            result["cond"].append("T: "+node[0])
            wordList.append("T: "+node[0])

        prevFour = prevThree
        prevValFour = prevValThree
        prevThree = prevTwo
        prevValThree = prevValTwo
        prevTwo = prevNode
        prevValTwo = prevValNode
        prevNode = node.label()
        prevValNode = node[0]

        return result

def recursiveWalk(cond_node, result):

    global appendWhere
    isPart = False

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
                    connection = connections[rel]
                    for j in rangeDestinationRel(connection):
                        #print("j", j)
                        if (elem in attrs[connection[j]]):
                            relAns = connection[j]
                    if (relAns!=""):
                        result["relation"].append(relAns)

    print("resultBefore", result)
    fixResult()
    #print("whereResult", whereList)
    print("result", result)
    #print("wordList", wordList)

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

    return result

def translate(result):

    global indices

    counter = 1
    for i in range(0, len(result["relation"])):
        if (not result["relation"][i].startswith('V:') and not result["relation"][i].startswith('F:') and not result["relation"][i].startswith('N:') and not result["relation"][i] == '|'):
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
                elif (result["relation"][i+1] != '|'):
                    indices[result["relation"][i]] = str(counter)
            else:
                indices[result["relation"][i]] = str(counter)
            counter = counter + 1

    #print("indices", indices)

    isFunction = False
    query = "SELECT DISTINCT "
    index = 1
    # Sementara cuma query berupa tampilkan clipping dengan tidak ada atribut lain
    '''if (isPart):
        rel = getFromCodeInArr(result["fields"], 'R: ')
        val = getFromCodeInArr(result["fields"], 'V: ')
        
        geom1 = "r" + indices[rel+val] + "." + geoms[rel][0]
        geom2 = ""

        idx = findCode(result["fields"], 'O: OVERLAPS')[0]
        rel = getFromCodeInArr(result["fields"][idx:], 'R: ')
        val = getFromCodeInArr(result["fields"][idx:], 'V: ')
        if (rel==""):
            #print("elmt right")
            geom2 = makeRectangle(result["fields"][idx+2:])
            for elmt in result["fields"][idx+1:]:
                makeRectangle(result["fields"][:])
                print(elmt)
        else:
            geom2 = "r" + indices[rel+val] + "." + geoms[rel][0]

        query = query + declareFunctions('OVERLAP', [geom1, geom2]) + "\n"
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
            query = query + "AND r" + indices[rel2+val2] + "." + fld2 + " = " + val2'''

    # Perhatikan! Ini metode ketemu paling akhir
    '''elif (len(result["fields"])>0):passing = 0'''
    passing = 0
    isAgg = False
    for idx, elem in enumerate(result["fields"]):
        #print("elem", elem)
        if (not elem.startswith("V: ") and not elem.startswith("R: ") and not elem.startswith("G: ") and not elem.startswith("O: ") and not elem.startswith("A: ")):
            #print("fields")
            #print(result["fields"][index:])
            if (passing == 0):
                rel, val = extractFirstRelation(result["fields"][idx:])
                print("rel val", rel, val)
                '''if (not elem in attrs[rel]):
                    for i in rangeDestinationRel(connections[rel]):
                        if (elem in attrs[connections[rel][i]]):
                            rel = connections[rel][i]
                            val = ""
                            whereAppend = "r" + indices[rel+val] + "." '''
                #val = val.replace(" ", "")
                if (elem in geoColumns):
                    query = query + "ST_AsGeoJSON(r" + getIndexRelation(rel, val) + "." + getSynonym(elem) + ")"
                else:
                    query = query + "r" + getIndexRelation(rel, val) + "." + getSynonym(elem)
                if (isAgg):
                    query = query + "), "
                    isAgg = False
                else:
                    query = query + ", "
            else:
                passing = passing - 1
            
        elif (elem.startswith("G: ")):
            if (not isFunction):
                elem = elem.replace("G: ", "")
                founds = re.findall("\w+", elem)
                #print("foundlist", founds)
                if (len(founds)>=2):
                    val = ""
                    for i in range(1, len(founds)):
                        val = val + founds[i]
                    #print("founds", founds[0])
                    #print("val", val)
                    #print("geoms", geoms)
                    query = query + "r" + indices[founds[0]+val] + "." + geoms[founds[0]][0] + ", "
                else:
                    query = query + "r" + indices[founds[0]] + "." + geoms[founds[0]][0] + ", "
        elif (elem.startswith("A: ")):
            elem = elem.replace("A: ", "")
            isAgg = True
            #aggVal = elem
            query = query + declareAgg(elem) + "("
        #! Masih berlaku untuk yang spatialOp pertama
        elif (elem.startswith("O: ")):
            elem = elem.replace("O: ", "")
            if (parameter[elem]==2):
                passing = 2
                #i = index
                #while (result["fields"][i].startswith('O:')):
                #    i = i + 1
                
                '''elem2 = result["fields"][i]
                elem2 = elem2.replace("G: ", "")
                founds2 = re.findall("\w+", elem2)
                elem3 = result["fields"][index+1]
                elem3 = elem3.replace("G: ", "")
                founds3 = re.findall("\w+", elem3)'''
                
                counter = 1
                idxField = getNthStartingIdxField(counter)
                print("idxField idx", idxField, idx)
                while ( idxField < idx and idxField != -1 ):
                    counter = counter + 1
                    idxField = getNthStartingIdxField(counter)

                idxField2 = getNthStartingIdxField(counter+1)

                fld2 = result['fields'][idxField]
                fld3 = result['fields'][idxField2]
                rel2, idxTemp = getFromCodeField(idxField, 'fields', 'R: ')
                val2, idxTemp = getFromCodeField(idxField, 'fields', 'V: ')
                rel3, idxTemp = getFromCodeField(idxField2, 'fields', 'R: ')
                val3, idxTemp = getFromCodeField(idxField2, 'fields', 'V: ')

                #print("rel2 rel3", rel2, val2, rel3, val3)
                #print("fld2 fld3", fld2, fld3)

                #val2 = val2.replace(" ", "")
                #val3 = val3.replace(" ", "")

                param1 = ""
                param2 = ""
                if (fld2 in semantics):
                    if (semantics[fld2]=="circleRadius"):
                        param1 = "ST_Transform(ST_Buffer(ST_Transform(r"
                        relAns, source = getConnectionHasGeom([], rel2)
                        #print("geom", relAns)
                        #print(rel2, val2)
                        #print("hasil", getIndexRelation(relAns, "", rel2, val2))
                        param1 = param1 + getIndexRelation(relAns, "", rel2, val2)
                        param1 = param1 + "." + geoms[relAns][0]
                        param1 = param1 + ", 3857)"
                        param1 = param1 + ", r" + getIndexRelation(rel2, val2)
                        param1 = param1 + "." +  fld2 + "), 4326)"
                else:
                    param1 = param1 + "r" + getIndexRelation(rel2, val2) + "." +  fld2
        
                if (fld3 in semantics):
                    if (semantics[fld3]=="circleRadius"):
                        param2 = "ST_Transform(ST_Buffer(ST_Transform(r"
                        relAns, source = getConnectionHasGeom([], rel3)
                        param2 = param2 + getIndexRelation(relAns, "", rel3, val3)
                        param2 = param2 + "." + geoms[relAns][0]
                        param2 = param2 + ", 3857)"
                        param2 = param2 + ", r" + getIndexRelation(rel3, val3)
                        param2 = param2 + "." +  fld2 + "), 4326)"
                else:
                    param2 = param2 + "r" + getIndexRelation(rel3, val3) + "." + fld3

                #print("tes")
                #print("param1", param1)
                #print("param2", param2)
                query = query + declareFunctions(elem, [param1, param2] )
                if (isAgg):
                    query = query + "), "
                    isAgg = False
                else:
                    query = query + ", "
            else:
                #! Lihat juga semantik lingkaran!
                #! Asumsikan tidak perlu srcRelation dan srcValue
                passing = 1
                counter = 1
                idxField = getNthStartingIdxField(counter)
                #print("idxField idx", idxField)
                rel = result["fields"][idxField+1].replace("R: ", "")
                val = ""
                if (idxField+2 < len(result["fields"]) and result["fields"][idxField+2].startswith("V: ")):
                    val = result["fields"][idxField+2].replace("V: ", "")
                if len(geoms[rel])==0:
                    relGeom, source = getConnectionHasGeom([], rel)
                else:
                    relGeom = rel
                #print("SELECT", rel, val)
                query = query + declareFunctions(elem, ["r"+getIndexRelation(rel, val)+"."+geoms[relGeom][0]]) + ", "
                '''while (result["fields"][idx].startswith('O:')):
                    idx = idx + 1
                elem2 = result["fields"][idx]
                elem2 = elem2.replace("G: ", "")
                founds2 = re.findall("\w+", elem2)
                rel = founds2[0]
                val = ""
                for i in range(1, len(founds2)):
                    val = val + founds2[idx]
                query = query + declareFunctions(elem, ["r"+indices[rel+val]+"."+geoms[rel][0]])
                if (isAgg):
                    query = query + "), "
                    isAgg = False
                else:
                    query = query + ", "'''
            isFunction = True
    '''else:
        # sementara seperti ini dulu
        # ada kasus tunjukkan titik A dan titik B jika kedua titik bersinggungan!
        # tunjukkan dua garis yang saling bersinggungan!
        #print("relation")
        #print(result["relation"][1])
        if (len(result["relation"])==1):
            query = query + "r" + indices[result["relation"][0]] + "." + geoms[result["relation"][0]][0]
            query = query + '\n'
    '''

    #! Bagaimana kalau field sama lebih dari 1?
    '''for field in result["fields"]:
        if (not field.startswith("V: ") and not field.startswith("R: ")):
            headers.append(field)'''

    '''query = query + "FROM "
    activeRel = ""
    activeVal = ""
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
                    query = query + result["relation"][i] + " r" + getIndexRelation(result["relation"]) + ", "
            else:
                query = query + result["relation"][i] + " r" + indices[result["relation"][i]] + ", "
    '''

    query = query[:-2] + "\n"
    query = query + "FROM "
    counter = 1
    for i, rel in enumerate(result["relation"]):
        if (not isNonFieldinFields(rel) and rel != '|'):
            query = query + rel + " r" + str(counter) + ", "
            counter = counter + 1

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
        if (makeAppend()!=""):
            query = query + "AND " + makeAppend()
        '''counter = 0
        print("whereList", whereList)
        for condition in whereList:
            if (counter == 0):
                query = query + "AND "
                condition = condition.replace("R: ", "")
                query = query + "r" + getIndex(condition) + "."
            elif (counter == 1):
                condition = condition.replace("F: ", "")
                query = query + condition + " = "
            elif (counter == 2):
                condition = condition.replace("R: ", "")
                query = query + "r" + getIndex(condition) + "."
            elif (counter == 3):
                condition = condition.replace("F: ", "")
                query = query + condition + " "
                counter = -1
            counter = counter + 1'''

        #query = query[:-1]
 
        return query, headers
    else:
        return query, headers