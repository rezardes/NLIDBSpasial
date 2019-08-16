import sys
sys.path.insert(0, "D:\\My Documents\\Kuliah\\Tugas Akhir\\Experiment\\NLIDBSpasial\\web\\mysite")

from NLIDB.connector import getMetadata

metadata, synSet = getMetadata('sample2', True)
geoms = metadata["geoms"]
print(geoms)

result = {}
result['cond'] = ['F: nama', 'R: wifi', 'V: mifi m5', 'AND', 'F: nama', 'R: wifi', 'V: huawei e5577', 'AND', 'R: posisi_wifi', 'F: waktu', 'T: 13:00']
result['relation'] = ['wifi', 'V: mifi m5', '|', 'wifi', 'V: huawei e5577']
result['fields'] = ['O: OVERLAP', 'jangkauan', 'R: wifi', 'V: mifi m5', 'jangkauan', 'R: wifi', 'V: huawei e5577']
semantics = {'jangkauan': 'circleRadius'}

def isNonFieldinFields(temp):

    return temp.startswith("R: ") or temp.startswith("V: ") or temp.startswith("O: ") or temp.startswith("G: ")

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
            if (not isNonFieldinFields(val)):
                counter = counter + 1
            if (val==relation and (srcRelation!="" or srcValue!="")):
                if (value!=""):
                    if (result["relation"][idx+1].startswith("V: ")):
                        if (result["relation"][idx+1].replace("V: ", "")==value):
                            if (srcValue!=""):
                                #print("tes1")
                                if (relActive==srcRelation):
                                    return counter
                            else:
                                #print("tes2")
                                print(relActive, srcRelation, valActive, srcValue)
                                if (relActive==srcRelation and valActive==srcValue):
                                    return counter
                else:
                    if (srcValue!=""):
                                #print("tes1")
                        if (relActive==srcRelation and valActive==srcValue):
                            return counter
                    else:
                        #print("tes2")
                        #print(relActive, srcRelation, valActive, srcValue)
                        if (relActive==srcRelation):
                            return counter

            if (val==relation and srcRelation=="" and srcValue==""):
                #print("tes")
                if (value!=""):
                    if (result["relation"][idx+1].replace("V: ", "")==value):
                        return counter
                else:
                    return counter
        
    counter = -1
    return counter    

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
                            if (i == len(result["relation"])-1):
                                idxInsertion = len(result["relation"])
                            elif (result["relation"][i]==insertion):
                                idxInsertion = -1
                                break
                            elif (result["relation"][i] == "|"):
                                idxInsertion = i
                                break
                else:
                    for i in range(i+1, len(result["relation"])):
                        if (i == len(result["relation"])-1):
                            idxInsertion = len(result["relation"])
                        elif (result["relation"][i]==insertion):
                            idxInsertion = -1
                            break
                        elif (result["relation"][i] == "|"):
                            idxInsertion = i
                            break

    #print("idxInsertion", idxInsertion)
    
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

insertConnectivity('wifi', 'wifi', 'V: mifi m5')
insertConnectivity('posisi_wifi', 'wifi', 'V: mifi m5')
insertConnectivity('posisi', 'wifi', 'V: mifi m5')
insertConnectivity('posisi_wifi', 'wifi', 'V: mifi m5')
insertConnectivity('posisi', 'wifi', 'V: mifi m5')
insertConnectivity('wifi', 'wifi', 'V: huawei e5577')
insertConnectivity('posisi_wifi', 'wifi', 'V: huawei e5577')
insertConnectivity('posisi', 'wifi', 'V: huawei e5577')
print(result['relation'])
indices = {'wifimifim5': '1', 'posisi_wifi': '6', 'wifihuaweie5577': '4'}

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

def getFromCodeField(idx, key, code):

    for i, arr in enumerate(result[key][idx:]):
        if (arr.startswith(code)):
            return arr.replace(code, ''), idx+i
        if (arr.startswith("V: ")):
            break

    return '', ''

query = ""
for idx, elem in enumerate(result["fields"]):
    print("elem", elem)
    if (not elem.startswith("V: ") and not elem.startswith("R: ") and not elem.startswith("G: ") and not elem.startswith("O: ") and not elem.startswith("A: ")):
        #print("fields")
        #print(result["fields"][index:])
        rel, val = extractFirstRelation(result["fields"][index:])
        '''if (not elem in attrs[rel]):
            for i in rangeDestinationRel(connections[rel]):
                if (elem in attrs[connections[rel][i]]):
                    rel = connections[rel][i]
                    val = ""
                    whereAppend = "r" + indices[rel+val] + "." '''
        val = val.replace(" ", "")
        if (elem in geoColumns):
            query = query + "ST_AsGeoJSON(r" + indices[rel+val] + "." + getSynonym(elem) + ")"
        else:
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
            print("foundlist", founds)
            if (len(founds)>=2):
                val = ""
                for i in range(1, len(founds)):
                    val = val + founds[i]
                print("founds", founds[0])
                print("val", val)
                print("geoms", geoms)
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
            while ( idxField < idx ):
                counter = counter + 1

            idxField2 = getNthStartingIdxField(counter+1)

            fld2 = result['fields'][idxField]
            fld3 = result['fields'][idxField2]
            rel2, idxTemp = getFromCodeField(idxField, 'fields', 'R: ')
            val2, idxTemp = getFromCodeField(idxField, 'fields', 'V: ')
            rel3, idxTemp = getFromCodeField(idxField2, 'fields', 'R: ')
            val3, idxTemp = getFromCodeField(idxField2, 'fields', 'V: ')

            print("rel2 rel3", rel2, val2, rel3, val3)
            print("fld2 fld3", fld2, fld3)

            val2 = val2.replace(" ", "")
            val3 = val3.replace(" ", "")

            param1 = ""
            param2 = ""
            if (fld2 in semantics):
                if (semantics[fld2]=="circleRadius"):
                    param1 = "ST_Buffer(r"
                    relAns, source = getConnectionHasGeom([], rel2)
                    param1 = param1 + getIndexRelation(relAns, "", rel2, val2)
                    param1 = param1 + "." + geoms[relAns][0]
                    param1 = param1 + ", r" + getIndexRelation(rel2, val2)
                    param1 = param1 + "." +  fld2 + ")"
            else:
                if (fld2 in semantics):
                    if (semantics[fld2]=="circleRadius"):
                        param2 = "ST_Buffer(r"
                        relAns, source = getConnectionHasGeom([], rel3)
                        param2 = param2 + getIndexRelation(relAns, "", rel3, val3)
                        param2 = param2 + "." + geoms[relAns][0]
                        param2 = param2 + ", r" + getIndexRelation(rel3, val3)
                        param2 = param2 + "." +  fld2 + ")"

            query = query + declareFunctions(elem, [param1, param2] )
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
            query = query + declareFunctions(elem, ["r"+indices[rel+val]+"."+geoms[rel][0]])
            if (isAgg):
                query = query + "), "
                isAgg = False
            else:
                query = query + ", "
        isFunction = True

    index = index + 1
query = query[:-2] + '\n'