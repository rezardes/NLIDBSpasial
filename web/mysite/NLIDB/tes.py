import psycopg2
import json

#! Ingat betulkan source

import sys
sys.path.insert(0, "D:\\My Documents\\Kuliah\\Tugas Akhir\\Experiment\\NLIDBSpasial\\web\\mysite")

from NLIDB.connector import getMetadata
from NLIDB.translator import defAttrs

metadata, synSet = getMetadata('sample2', True)
geoms = metadata["geoms"]
relations = metadata["relations"]
attrs = metadata["attrs"]
connections = metadata["connection"]
geoColumns = metadata["geoColumns"]
connections['|'] = []
semantics = {'jangkauan': 'circleRadius'}
substitute = [] 

'''
query = 'SELECT ST_AsGeoJSON(geom) FROM area WHERE nama = \'Yagami Ramen\''
conn = psycopg2.connect(host="localhost", database="sample2", user="postgres", password="1234")
cur = conn.cursor()
cur.execute(query)
hasil = cur.fetchall()
json_string = hasil[0][0]
obj = json.loads(json_string)
print(obj['coordinates'])
cur.close()
'''

def getIndexRelation(relation, value="", srcRelation="", srcValue=""):

    counter = 0
    relActive = ""
    valActive = ""
    for idx, val in enumerate(result["relation"]):

        if (idx==0):
            relActive = result["relation"][0]
            if (result["relation"][1].startswith("V:")):
                valActive = result["relation"][1].replace("V: ", "")

        #print("val", val)
        #print("relActive valActive", relActive, valActive)
        if (val=='|'):
            if (idx+1 < len(result["relation"])):
                relActive = result["relation"][idx+1]
                if (result["relation"][idx+2].startswith("V:")):
                    valActive = result["relation"][idx+2].replace("V: ", "")
                else:
                    valActive = ""
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
                                print(relActive, srcRelation, valActive, srcValue)
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


def isNonFieldinFields(temp):

    return temp.startswith("R: ") or temp.startswith("V: ") or temp.startswith("O: ") or temp.startswith("G: ")

#result {'cond': ['R: wifi', 'V: mifi m5', 'AND', 'F: jam', 'T: 13:00'], 'relation': ['wifi', 'V: mifi m5'], 'fields': ['posisi', 'R: wifi', 'V: mifi m5']}

result = {} 
'''result["cond"] = ['F: nama', 'R: wifi', 'V: mifi m5', 'AND', 'F: nama', 'R: wifi', 'V: huawei e5577', 'AND', 'R: posisi_wifi', 'F: waktu', 'T: 13:00']
result["relation"] = ['wifi', 'V: mifi m5', 'posisi_wifi', 'posisi', '|', 'wifi', 'V: huawei e5577', 'posisi_wifi', 'posisi', '|']
#result["fields"] = ['O: OVERLAP', 'jangkauan', 'R: wifi', 'V: mifi m5', 'jangkauan', 'R: wifi', 'V: huawei e5577']
result["fields"] = ['O: JARAK', 'R: wifi', 'V: mifi m5', 'R: wifi', 'V: huawei e5577']'''

result["cond"] = ['R: wifi', 'V: mifi m5', 'AND', 'R: wifi', 'V: huawei e5577', 'AND', 'F: jam', 'T: 13:00']
result["relation"] = ['wifi', 'jalan', 'V: ir. h. juanda']
result["fields"] = ['O: OVERLAP', 'jangkauan', 'R: wifi', 'V: mifi m5', 'R: wifi', 'V: huawei e5577']
whereList = []

'''print("getIndex")
print(getIndexRelation('wifi', 'mifi m5'))
print(getIndexRelation('posisi', '', 'wifi', 'mifi m5'))
print(getIndexRelation('posisi_wifi', '', 'wifi', 'mifi m5'))
print(getIndexRelation('posisi', '', 'wifi', 'huawei e5577'))
print(getIndexRelation('posisi_wifi', '', 'wifi', 'huawei e5577'))
print(getIndexRelation('wifi', 'huawei e5577'))'''

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

#print(findMissingField())

'''def findOccurence(code, key):

    counter = 0
    if (result[key].startswith(code)):
        counter = counter + 1

    return str(counter)'''

def findElmtInArr(arrs, elmt):    

    for index, value in enumerate(arrs):
        if (value == elmt):
            return index
    
    return -1

def getFromCodeField(idx, key, code):

    for i, arr in enumerate(result[key][idx:]):
        if (arr.startswith(code)):
            return arr.replace(code, ''), idx+i
        if (arr.startswith("V: ")):
            break

    return '', ''

def getFromCode(idx, key, code):

    for i, arr in enumerate(result[key][idx:]):
        if (arr=="AND"):
            break
        if (arr.startswith(code)):
            return arr.replace(code, ''), idx+i
    return '', ''

def appendUnique(key, elmt):

    temp = result[key]
    if not isElmtInArrs(elmt, key):
        temp.append(elmt)

    return temp

'''def getGeomRelation(source):
    
    for i in rangeDestinationRel(connections[source]):
        if (hasGeom(connections[source][i])):
            return connections[source][i]
    return 'x'
'''
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

def rangeDestinationId(connections):

    return range(2, len(connections), 3)

def rangeDestinationRel(connections):

    return range(1, len(connections), 3)

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

'''print(traverseRelation(0))
print(traverseRelation(1))
print(traverseRelation(2))
print(traverseRelation(3))'''

def isElmtInArrs(elmt, key):

    found = False
    for arr in result[key]:
        if (arr == elmt):
            found = True

    return found

# Sementara cari kolom untuk satu relasi dulu
def findRel(column):

    for relation in relations:
        if (column in attrs[relation]):
            return relation
    return ''

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

#print(getNthStartingIdxField(1))
#print(getNthStartingIdxField(2))
#print(getNthStartingIdxField(3))

def getSynonym(elem):

    if (elem in synSet):
        return synSet[elem]
    else:
        return elem

'''def getIdxFromCode(idx, code):

    for i, arr in result["cond"][idx:]:
        if (arr=="AND"):
            break
        if (arr.startswith(code)):
            return idx+i
    return -1'''

def hasGeom(relation):

    return len(geoms[relation])>0

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

#print(connections)
#! Mungkin Algoritmanya masih salah
def getConnectionHasGeom(source, relation):

    relAns = ''
    #print("relation", relation)
    for i in rangeDestinationRel(connections[relation]):
        print(source, connections[relation][i])
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

#print(geoms[getConnectionHasGeom('', 'wifi')][0])
#print(hasGeom('posisi'))

'''print("resField", result["fields"])
print("getNth")
print(getNthStartingIdxField(0))
print(getNthStartingIdxField(1))
print(getNthStartingIdxField(2))
print(getNthStartingIdxField(3))
print("====")'''

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

    print(result["relation"])
    print("idxInsertion", insertion, idxInsertion)
    
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

#! Jangan lupa implementasi delimiternya
def getSearchFields(idx):

    print(idx)
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

headers = []
substitute = {}
'''print("tesSearchFields")
print(getSearchFields(0))
print(getSearchFields(1))
print(getSearchFields(2))
print(getSearchFields(3))'''

def fixResult():

    global whereList
    global substitute
    global headers

    # Jangan lupa bagaimana kalau ada spatialop
    # PERBAIKAN result["cond"]
    counter = 1
    idx = getNthStartingIdxCond(counter)
    key = "cond"
    while (idx != -1):
        
        relation, idxRel = getFromCode(idx, key, 'R: ')
        field, idxField  = getFromCode(idx, key, 'F: ')
        value, idxVal = getFromCode(idx, key, 'V: ')
        times, idxTime = getFromCode(idx, key, 'T: ')

        # TAHAP 1: PELENGKAPAN RELATION, FIELD, VALUE
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
            #print("tesRelName", relName)
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

    # PERBAIKAN KELENGKAPAN FIELDS
    missField, indexList = findMissingField()
    print("MISSING", missField, indexList)
    indexList.reverse()
    for i, idx in enumerate(indexList):
        if (missField[i]==''):
            rel = result["fields"][idx].replace("R: ", "")
            '''if (idx+1 < len(result["fields"]) and result["fields"][idx+1]):
                val = result["fields"][idx+1].replace("V: ", "")'''
            if (len(geoms[rel])==0):
                relAns, source = getConnectionHasGeom([], rel)
                result["fields"].insert(idx, geoms[relAns][0])
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
                if (field!="" and relation!="" and synSet[field] not in attrs[relation]):
                        
                    relName = findRelation(field)

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
                    #print("relation", relName, relation)
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

                '''if (field!="" and relation!="" and synSet[field] not in attrs[relation]):
                        
                    relName = findRelation(field)
                    print("relName", relName)
                    result["fields"][searchFields["idx"][index]] = synSet[field]
                    result["fields"][idxRel] = "R: "+relName
                    if (value):
                        result["fields"][idxVal] = "" 
                    if (times):
                        result["fields"][idxTime] = ""

                    #! SEMENTARA LANGSUNG TARO DI RELATION AJA
                    result["relation"] = appendUnique("relation", relName)

                    print("relation", relName, relation)
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
    counterRel = 0
    j = traverseRelation(counterRel)
    k = traverseRelation(counterRel+1)
    while (j!=-1 and k!=-1):
        ##print("connections", connections)
        print("index", index)
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
        k = traverseRelation(counterRel+1)

fixResult()
print(result)

'''def insertRelation(index, relation):

    result["relation"].insert(index, "R: "+relation) 

def fixResult():

    # Jangan lupa bagaimana kalau ada spatialop
    # PERBAIKAN result["cond"]
    counter = 1
    idx = getNthStartingIdxCond(counter)
    key = "cond"
    while (idx != -1):
        
        relation, idxRel = getFromCode(idx, key, 'R: ')
        field, idxField  = getFromCode(idx, key, 'F: ')
        value, idxVal = getFromCode(idx, key, 'V: ')
        times, idxTime = getFromCode(idx, key, 'T: ')

        # TAHAP 1: PELENGKAPAN RELATION, FIELD, VALUE
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
            result["relation"] = appendUnique("relation", relName)

        counter = counter + 1
        idx = getNthStartingIdxCond(counter)

    counter = 1
    idx = getNthStartingIdxField(1)
    key = "fields"
    while (idx != -1):

        relation, idxRel = getFromCode(idx, key, 'R: ')
        value, idxVal = getFromCode(idx, key, 'V: ')
        times, idxTime = getFromCode(idx, key, 'T: ')
        searchFields = getSearchFields(idx)

        if (len(searchFields["fields"])-1 > 1):

            for index, field in enumerate(searchFields["fields"]):

                #! Mungkin ada kasus dimana relation yang diubah butuh Value
                if (field!="" and relation!="" and synSet[field] not in attrs[relation]):
                        
                    relName = findRelation(field)

                    #! Ingat!!! Jangan lupa implementasi insertRelation nanti
                    #insertRelation(searchFields["idx"][index], relName)
                    result["fields"][idxRel] = "R: "+relName
                    result["fields"][idxField] = "F: "+synSet[field]

                    if (value):
                        result["fields"][idxVal] = "" 
                    if (times):
                        result["fields"][idxTime] = ""

                    #! SEMENTARA LANGSUNG TARO DI RELATION AJA
                    result["relation"] = appendUnique("relation", relName)

        else:

            for index, field in enumerate(searchFields["fields"]):

                if (field!="" and relation!="" and synSet[field] not in attrs[relation]):
                        
                    relName = findRelation(field)
                    result["fields"][searchFields["idx"][index]] = "F: "+synSet[field]
                    result["fields"][idxRel] = "R: "+relName
                    if (value):
                        result["fields"][idxVal] = "" 
                    if (times):
                        result["fields"][idxTime] = ""

                    #! SEMENTARA LANGSUNG TARO DI RELATION AJA
                    result["relation"] = appendUnique("relation", relName)


        # TAHAP 2: PEMBERSIHAN DAN DEFFERED EXECUTION
        delList = []
        for index, value in enumerate(result["fields"]):
            if (value == ""):
                delList.append(index)

        delList.reverse()

        for index in delList:
            del(result["fields"][index])

        counter = counter + 1
        idx = getNthStartingIdxCond(counter)
        
#fixResult()
#print(result["cond"])
#print(result["fields"]) 
#print(result["cond"])'''
'''idx = getIdxFromCode(idx, 'R: ')
field = getIdxFromCode(idx, 'F: ')
value = getIdxFromCode(idx,)'''

'''print(result["cond"])
print(result["fields"])
fixResult()
print(result["cond"])
print(result["fields"])'''
#print(result["fields"])
#fixResult(2)
#print(getNthStartingIdxField(1))
#print(getNthStartingIdxField(2))
#print(getNthStartingIdxField(3))

#print(getNthStartingIdxCond(1))
#print(getNthStartingIdxCond(2))
#print(getNthStartingIdxCond(3))
#print(getNthStartingIdxCond(4))

# Tunjukkan negara bernama Malaysia dan beribukota Jakarta


'''def getRecentRelation(index):

    for i in range(index, -1, -1):
        if (result["cond"][i].startswith("R: ")):
            return result["cond"][i]

    return '''''

#print(getRecentRelation(4))

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

query = ""
passing = 0
isAgg = False
for idx, elem in enumerate(result["fields"]):
    #print("elem", elem)
    if (not elem.startswith("V: ") and not elem.startswith("R: ") and not elem.startswith("G: ") and not elem.startswith("O: ") and not elem.startswith("A: ")):
        #print("fields")
        #print(result["fields"][index:])
        if (passing == 0):
            rel, val = extractFirstRelation(result["fields"][idx:])
            '''if (not elem in attrs[rel]):
                for i in rangeDestinationRel(connections[rel]):
                    if (elem in attrs[connections[rel][i]]):
                        rel = connections[rel][i]
                        val = ""
                        whereAppend = "r" + indices[rel+val] + "." '''
            val = val.replace(" ", "")
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

            print("rel2 rel3", rel2, val2, rel3, val3)
            print("fld2 fld3", fld2, fld3)

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

            print("tes")
            print("param1", param1)
            print("param2", param2)
            query = query + declareFunctions(elem, [param1, param2] )
            if (isAgg):
                query = query + "), "
                isAgg = False
            else:
                query = query + ", "
        else:
            passing = 1
            while (result["fields"][idx].startswith('O:')):
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
                query = query + ", "
        isFunction = True

query = query[:-2] + '\n'
print(query, "query")
#print(connections)

#! Mungkin bisa digabung atau dioptimasi
def isConnected(rel1, rel2):

    for i in rangeDestinationRel(connections[rel1]):
        if (connections[rel1][i]==rel2):
            return True

    return False

def addSeparator():

    idxList = []
    prevRel = ""
    for idx, rel in enumerate(result["relation"]):
        if (not isNonFieldinFields(rel)):
            if (prevRel!=""):
                if (not isConnected(prevRel, rel)):
                    idxList.append(idx)
            prevRel = rel

    idxList.reverse()
    for idx in idxList:
        print("idx", idx)
        result["relation"].insert(idx, '|')

addSeparator()
print(result["relation"])

def getIdxDestRel(rel1, rel2):

    for i in rangeDestinationRel(connections[rel1]):
        if (connections[rel1][i]==rel2):
            return i

    return -1

def getSrcRelation(idxTarget):

    currentRel = ""
    currentVal = ""
    subRelations = result["relation"][:idxTarget+1]
    subRelations.reverse()
    print("sub", subRelations)
    for i, rel in enumerate(subRelations):
        #print("rel", rel)
        
        if (rel=='|'):
            break
        '''if (rel.startswith("V:")):
            currentVal = rel'''
        #(i+1, result["relation"][i+1])
        #print("i", i)
        if (i+1 == len(subRelations)):
            print(rel, " ", subRelations[i-1])
            currentRel = rel
            currentVal = subRelations[i-1].replace("V: ", "")
            break
        if (subRelations[i+1]=='|'):
            print(rel, " ", subRelations[i-1])
            currentRel = rel
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
                    query = query + "r" + getIndexRelation(prevRel, prevVal, srcRel, srcVal)  + "."
                    query = query + connections[prevRel][idxPrevDestRel-1]
                    query = query + " = "
                    query = query + "r" + getIndexRelation(rel, val, srcRel, srcVal)  + "."
                    query = query + connections[prevRel][idxPrevDestRel+1] + " AND "
            
            prevRel = rel
            prevIdx = i

    query = query[:-5]
    return query

print(isConnected('wifi', 'posisi_wifi'))
print(isConnected('wifi', 'posisi'))
print(makeAppend())

activeRel = ""
activeVal = ""
query = "FROM "
counter = 1
for i, rel in enumerate(result["relation"]):
    '''if (rel == '|' and not i != len(result["relation"])):
        activeRel = ''
        if result["relation"][i+1].startswith("V:"):
            activeVal = result["relation"][i+1].replace("V: ", "")
    if (i == 0):
        activeRel = rel
        if result["relation"][i+1].startswith("V:"):
            activeVal = result["relation"][i+1].replace("V: ", "")'''
    if (not isNonFieldinFields(rel) and rel != '|'):
        query = query + rel + " r" + str(counter) + ", "
        counter = counter + 1

query = query[:-2]
print("QUERY", query)

'''Catat sekarang di posisi mana
# Terdapat 2 Fase:
# 1) Fase penambahan/pengurangan(?)
# 2) Fase eksekusi'''