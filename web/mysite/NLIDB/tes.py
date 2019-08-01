import psycopg2
import json

import sys
sys.path.insert(0, "D:\\My Documents\\Kuliah\\Tugas Akhir\\Experiment\\NLIDBSpasial\\web\\mysite")

from NLIDB.connector import getMetadata
from NLIDB.translator import defAttrs

metadata, synSet = getMetadata('sample2', True)
geoms = metadata["geoms"]
relations = metadata["relations"]
attrs = metadata["attrs"]
connections = metadata["connection"]
semantics = {'jangkauan': 'circleRadius'}

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

#result {'cond': ['R: wifi', 'V: mifi m5', 'AND', 'F: jam', 'T: 13:00'], 'relation': ['wifi', 'V: mifi m5'], 'fields': ['posisi', 'R: wifi', 'V: mifi m5']}

result = {} 
result["cond"] = ['R: wifi', 'V: mifi m5', 'AND', 'F: jam', 'T: 13:00']
result["relation"] = ['wifi', 'V: mifi m5']
result["fields"] = ['jangkauan', 'R: wifi', 'V: mifi m5']
whereList = []

def findElmtInArr(arrs, elmt):    

    for index, value in enumerate(arrs):
        if (value == elmt):
            return index

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

def rangeDestinationId(connections):

    return range(2, len(connections), 3)

def rangeDestinationRel(connections):

    return range(1, len(connections), 3)

def fixResult():

    global whereList

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

            print("relation", relName, relation)
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

    counter = 1
    idx = getNthStartingIdxField(1)
    key = "fields"
    while (idx != -1):

        relation, idxRel = getFromCode(idx, key, 'R: ')
        value, idxVal = getFromCode(idx, key, 'V: ')
        times, idxTime = getFromCode(idx, key, 'T: ')
        searchFields = getSearchFields(idx)

        # PERBAIKAN ASAL RELASI dan PENGECEKAN ANOTASI
        if (len(searchFields["fields"])-1 > 1):

            for index, field in enumerate(searchFields["fields"]):

                if (field in semantics):
                    print("Yes in semantics!")
                    if (semantics[field]=="circleRadius"):
                        idxInsert = getNthStartingIdxCond(counter+1)
                        if (getNthStartingIdxCond(counter+1)==-1):
                            result["fields"].append()
                        else:
                            result["relation"].insert(idxInsert, )

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
                    print("relation", relName, relation)
                    '''if (relName in connections[relation]):
                        index = findElmtInArr(connections[relation], relName)
                        whereList.append("R: "+relation+value)
                        whereList.append("F: "+connections[relation][index-1])
                        whereList.append("R: "+relName)
                        whereList.append("F: "+connections[relation][index+1])'''

        else:

            for index, field in enumerate(searchFields["fields"]):

                if (field!="" and relation!="" and synSet[field] not in attrs[relation]):
                        
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
                    '''if (relName in connections[relation]):
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
        whereList.append("R: "+rel1+val1)
        whereList.append("F: "+connections[rel1][index-1])
        whereList.append("R: "+rel2+val2)
        whereList.append("F: "+connections[rel1][index+1])
        counterRel = counterRel + 1
        j = traverseRelation(counterRel)
        k = traverseRelation(counterRel+1)

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

def isNonFieldinFields(temp):

    return temp.startswith("R: ") or temp.startswith("V: ") or temp.startswith("F: ")

def getNthStartingIdxField(N):

    key = "fields"

    if (N==1):
        return 0

    fieldPhase = True
    counter = 1
    turn = 0
    breakPhase = False
    for temp in result[key]:
        turn = turn + 1
        if (fieldPhase):
            #! Mungkin disini kurang "code"
            if (isNonFieldinFields(temp)):
                fieldPhase = False
        else:
            if (not isNonFieldinFields(temp)):
                fieldPhase = True
                counter = counter + 1
                if (counter==N):
                    breakPhase = True
                    turn = turn + 1
                    break
    
    if (breakPhase):
        turn = turn - 1
    else:
        turn = -1

    return turn

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

print(connections)
def getConnectionHasGeom(source, relation):

    relAns = ''
    for i in rangeDestinationRel(connections[relation]):
        print(source, connections[relation][i])
        if (source!=connections[relation][i]):
            if (hasGeom(connections[relation][i])):
                relAns = connections[relation][i]
                break
            else:
                relAns = getConnectionHasGeom(relation, connections[relation][i])

    return relAns

#print(getConnectionHasGeom('', 'wifi'))
#print(hasGeom('posisi'))

#! Jangan lupa implementasi delimiternya
def getSearchFields(idx):

    print(idx)
    searchFields = {}
    searchFields["fields"] = []
    searchFields["idx"] = []
    counter = 0
    for word in result["fields"][idx:]:
        if (not isNonFieldinFields(word)):
            searchFields["fields"].append(word)
            searchFields["idx"].append(idx+counter)
        counter = counter + 1

    searchFields["fields"].reverse()
    searchFields["idx"].reverse()

    return searchFields

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


# Catat sekarang di posisi mana
# Terdapat 2 Fase:
# 1) Fase penambahan/pengurangan(?)
# 2) Fase eksekusi