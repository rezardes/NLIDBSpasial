import sys
sys.path.insert(0, "D:\\My Documents\\Kuliah\\Tugas Akhir\\Experiment\\NLIDBSpasial\\web\\mysite")
import re

SRID_Params = {'JARAK': "3857", 'PANJANG': "3857", 'LUAS': "3857", 'KELILING': "3857", 'ABSIS': "4326", 'ORDINAT': "4326"}
SRID_Result = {'OVERLAP': "4326"}

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

def isNonFieldinFields(temp):

    return temp.startswith("R: ") or temp.startswith("V: ") or temp.startswith("O: ") or temp.startswith("G: ")

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

def declareFunctions(keyword, params, types):

    function = mapToFunctions(keyword)
    query = ''
    geog1 = ''
    geog2 = ''

    if (keyword not in parameter):
        return ''
    elif (parameter[keyword]==1):
        if (types[0]=="geog"):
            query = function + '(' + params[0] + '::geometry' + ')'
            if (keyword in SRID_Params):
                print("tes")
                query = function + '(ST_Transform(' + params[0] + '::geometry, ' + SRID_Params[keyword] + '))'
        else:
            query = function + '(ST_Transform(' + params[0] + ', ' + SRID_Params[keyword] + '))'
    elif (parameter[keyword]==2):
        appendResult1 = ""
        appendResult2 = ""
        appendTransform1 = ""
        appendTransform2 = ""
        if (keyword in SRID_Result):
            appendResult1 = "ST_Transform("
            appendResult2 = ", " + SRID_Result[keyword] + ")"
        if (keyword in SRID_Params):
            appendTransform1 = "ST_Transform("
            appendTransform2 = ", " + SRID_Params[keyword] + ")"
            
        if (types[0]=='geog'):
            geog1 = "::geometry"
        if (types[1]=='geog'):
            geog2 = "::geometry"
        
        query = query + appendResult1 + function + '(' + appendTransform1 + params[0] + geog1 + appendTransform2 + ', ' + appendTransform1 + params[1] + geog2 + appendTransform2 + ')' + appendResult2

    #print("query", query)
    return query

# ["O: IN", "F: posisi", "R: posisi", "S: wifi", "SV: connex", ".", "F: geom", "R: area", "V: yagami ramen", 
 #               "C: AND", "O: JARAK", "F: posisi", "R: posisi", "S: wifi", "SV: connex", ".", "F: posisi", "R: posisi", "S: wifi", 
 #               "SV: yagami ramen", "M: <", "1000", "U: KM", "|"]

result = {}
#result["relation"] = ['wifi', 'V: connex', 'posisi', '|', 'area', 'V: yagami ramen', '|', 'wifi', 'V: yagami ramen', 'posisi', '|']
#result["relation"] = ['provinsi', '|', 'provinsi', 'V: jawa barat', '|']
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
locator = {}
result["cond"] = []
result["fields"] = []
result["relation"] = []
synSet = {'places_of_interest': 'places_of_interest', 'restoran': 'places_of_interest', 'wifi': 'wifi'}
connections = {'jalan': [], 'area': [], 'places_of_interest': [], 'wifi': ['id', 'posisi_wifi', 'id_wifi'], 'posisi_wifi': ['id_wifi', 'wifi', 'id'], 'kabupaten': ['id_provinsi', 'provinsi', 'gid'], 'provinsi': ['gid', 'kabupaten', 'id_provinsi'], '|': []}
#wordList = ['<FP>', 'O1: JARAK1', '<P>', 'R: provinsi', 'V: jawa barat', '</P>', '<P>', 'R: provinsi', 'V: jawa timur', '</P>', 'U: KM', '</FP>']
#wordList = ['<FP>', 'R: wifi', '</FP>', 'SEPARATOR', '<PP>', '<P>', 'O2: JARAK2', 'OP: <', 'N: 600', 'U: M', '<P>', 'R: jalan', 'V: ir. h. juanda', '</P>', '</P>', '</PP>']
#wordList = ['<FP>', 'R: kabupaten', '</FP>', 'SEPARATOR', '<PP>', '<P>', 'O3: OVERLAPS', '<P>', 'R: provinsi', 'V: jawa barat', '</P>', '</P>', '</PP>']
#wordList = ['<FP>', 'R: jalan', '</FP>', 'SEPARATOR', '<PP>', '<P>', 'O3: OVERLAPS', '<P>', 'R: provinsi', 'V: jawa barat', '</P>', '</P>', '</PP>']
wordList = ['<FP>', 'O1: PANJANG1', '<P>', 'R: jalan', 'V: ir. h. juanda', '</P>', 'U: MIL', '</FP>']
#wordList = ['<FP>', 'PART', 'R: places_of_interest', 'V: yagami ramen', '</FP>', 'SEPARATOR', '<PP>', '<P>', 'O3: OVERLAPS', '<P>', 'F: jangkauan', 'R: wifi', 'V: connex', '</P>', '</P>', '</PP>']
wordList = ['<FP>', '<F>', 'F: nama', '</F>', 'R: wifi', '</FP>', 'SEPARATOR', '<PP>', '<P>', 'O1: ABSIS1', 'COMMA', 'O1: ORDINAT1', 'G: (107,61;-6,88)', '</P>', '</PP>']
#wordList = ['<FP>', '<F>', 'F: nama', 'COMMA', '<F>', 'O1: ABSIS1', 'COMMA', 'O1: ORDINAT1', 'COMMA', 'C: AND', '<F>', 'O1: LUAS1', 'F: jangkauan', '</F>', '</F>', '</F>', 'R: wifi', '</FP>', 'SEPARATOR', '<PP>', '<P>', 'O3: OVERLAPS', '<P>', 'R: places_of_interest', 'V: metropolitan bekasi', '</P>', '</P>', '</PP>']
#wordList = ['<FP>', '<F>', 'F: nama', 'COMMA', '<F>', 'O: LUAS1', 'COMMA', 'C: AND', '<F>', 'F: ibukota', '</F>', '</F>', '</F>', 'R: provinsi', '</FP>', 'SEPARATOR', '<PP>', '<P>', 'O2: MEETS', '<P>', 'R: provinsi', 'V: jawa barat', '</P>', '</P>', 'C: AND', '<PP>', '<P>', 'O1: LUAS1', 'OP: <', 'N: 10000', 'U: KM2', '</P>', '</PP>', '</PP>']
#wordList = []
#wordList = ['R: provinsi', 'SEPARATOR', 'O:2 MEETS', '<p>', 'R: provinsi', 'V: jawa barat', '</p>', "C: AND", 'O:2 MEETS', '<p>', 'R: provinsi', 'V: jawa timur', '</p>', '|']
geoms = {'jalan': ['geom', 'line'], 'area': ['geom', 'polygon'], 'wifi': ['posisi', 'point', 'jangkauan', 'polygon'], 
        'posisi': ['posisi', 'point'], 'provinsi': ['geog', 'geog'], 'kabupaten': ['geog', 'geog'], 'places_of_interest': ['geom', 'polygon']}

#! Jangan lupa default geom
#S Sementara pake brute force
def getNthPhrase(n):

    counter = 0
    for idx, elem in enumerate(wordList):
        if (elem=='<P>'):
            counter = counter + 1
            if (counter==n):
                return idx

    return -1

def getFields(arrs):

    results = []
    for arr in arrs:
        if (arr.startswith("F:")):
            results.append(arr.replace("F: ", ""))

    return results

def getCodes(arrs, code):

    idxResults = []
    results = []
    for idx, arr in enumerate(arrs):
        if (arr.startswith(code)):
            idxResults.append(idx)
            results.append(arr.replace("code", ""))

    return idxResults, results

def getCodeInList(arrs, code):

    for idx, arr in enumerate(arrs):
        if (arr.startswith(code)):
            return arr.replace(code, ''), idx
    return '', ''

def addRightRelations():

    idxStarts, temp = getCodes(wordList, '<P>')
    idxEnds, temp = getCodes(wordList, '</P>')
    #print("fields")
    for idx, elem in enumerate(idxStarts):
        fields = getFields(wordList[elem:idxEnds[idx]])
        #print(fields)
    '''counter = 1
    iter = getNthPhrase(counter)
    while (iter != -1):
        fields = getFields(wordList[iter:])
        getCodeInList(wordList[iter:])

        counter = counter + 1'''

# Pengolah connections
def rangeDestinationId(connections):

    return range(2, len(connections), 3)

def rangeDestinationRel(connections):

    return range(1, len(connections), 3)

#! Mungkin bisa digabung atau dioptimasi
def isConnected(rel1, rel2):

    for i in rangeDestinationRel(connections[rel1]):
        if (connections[rel1][i]==rel2):
            return True

    return False

#! Bisa dioptimasi menjadi sudah ada silsilahnya terlebih dahulu
'''traversed = []
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

    return hasil'''

addRightRelations()

'''print("getPhases", getCodes(wordList, '<P>'))
print("getPhasesEnd", getCodes(wordList, '</P>'))'''

'''print("getNthPhrase", getNthPhrase(1))
print("getNthPhrase", getNthPhrase(2))
print("getNthPhrase", getNthPhrase(3))'''

def getIndexRelation(relation, value="", srcRelation="", srcValue=""):

    #print(relation, value, srcRelation, srcValue)

    counter = 0
    relActive = ""
    valActive = ""
    #print(result["relation"])
    for idx, val in enumerate(result["relation"]):

        if (idx==0):
            relActive = result["relation"][0]
            if (1 < len(result["relation"]) and result["relation"][1].startswith("V:")):
                valActive = result["relation"][1].replace("V: ", "")
        if (val=='|'):
            if (idx+1 < len(result["relation"])):
                relActive = result["relation"][idx+1]
                if (idx+2 < len(result["relation"]) and result["relation"][idx+2].startswith("V:")):
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



def getIndexTwoElmt(arrs, rel, code):

    for i in range(0, len(arrs)-1):

        if (arrs[i]==rel and arrs[i+1]==code):
            return i
    return -1

# rel non-code; val code
def addRelVal(rel, val):

    indices = getIndexRelation(rel, val)
    if (indices=="-1"):
        result["relation"].append(rel)
        result["relation"].append(val)
        result["relation"].append('|')

def addRelation(rel):

    indices = getIndexRelation(rel)
    if (indices=="-1"):
        result["relation"].append(rel)
        result["relation"].append('|')

# Sementara Relation dengan Value
def makeResultRelation():

    for idx, elem in enumerate(wordList):
        if (elem.startswith("R:")):
            if (wordList[idx+1].startswith("V:")):
                addRelVal(elem.replace("R: ", ""), wordList[idx+1])
            else:
                #print("tes")
                addRelation(elem.replace("R: ", ""))

makeResultRelation()
#print("relations", result["relation"])

# Bagaimana membuat srcRel dan srcVal?
'''def makeResultCond():

    isCond = False
    rel = ""
    fld = ""
    val = ""

    for idx, elem in enumerate(wordList):
        # Apakah mendingan diganti menjadi yang ada di FPHRASE?
        if (elem.startswith("R:")):
            if (isCond):
                result["cond"].append(elem)
            else:
                rel = elem.replace("R: ", "")
                fld = ""
                val = ""
        elif (elem.startswith("F:")):
            if (isCond):
                result["cond"].append(elem)
            else:
                fld = elem.replace("F: ", "")
        elif (elem.startswith("V:")):
            if (isCond):
                result["cond"].append(elem)
            else:
                val = elem.replace("V: ", "")
        elif (elem.startswith("<p>") or elem.startswith("</p>")):
            if (isCond):
                result["cond"].append(elem)
        elif (elem.startswith("O:")):
            if (isCond):
                op = elem.replace("2", "").replace("1", "")
                result["cond"].append(op)
                if (elem.startswith("O:2")):
                    result["cond"].append("<p>")
                    result["cond"].append("R: "+rel)
                    if (fld!=""):
                        result["cond"].append("F: "+fld)
                    if (val!=""):
                        result["cond"].append("V: "+val)
                    result["cond"].append("</p>")
        elif (elem=="SEPARATOR"):
            isCond = True
        elif (elem.startswith("C:")):
            result["cond"].append(elem)
        elif (elem == '|'):
            result["cond"].append('|')
            isCond = False

makeResultCond()'''

#! Ingat FIELD-VALUE MASIH BELUM KOMPLIT
#! Operator field biasa bagaimana?
#! Bagaimana kalo lebih dari satu DESCRIPTION
def makeResultCond():

    isCond = False
    isPhrase = False
    isPart = False
    isSpatialOp = False
    isFields = False
    isSelectPhrase = False
    temp = {}
    paramRel = ""
    paramVal = ""
    relation = ""
    value = ""

    for elem in wordList:

        if (isFields):

            if (not isSelectPhrase):
                if (elem.startswith("R:")):
                    relation = elem.replace("R: ", "")
                elif (elem.startswith("V:")):
                    value = elem.replace("V: ", "")

            if (elem == "PART"):
                isPart = True
            elif (elem == "<P>"):
                isSelectPhrase = True
            elif (elem == "</P>"):
                isSelectPhrase = False

        elif (isCond):
            if (isPhrase):
                if (elem.startswith("O2: ") or elem.startswith("O1: ") or (elem.startswith("O3: ") and not isPart)):
                    isSpatialOp = True

                    temp = {"sp": "", "params": [], "unit": "M", "types": []}

                    if (elem.startswith("O2:") or elem.startswith("O3: ")):
                        indeks = getIndexRelation(relation, value)
                        params = "r" + indeks + "." + geoms[relation][0]
                        temp["params"].append(params)
                        temp["types"].append(geoms[relation][1])

                    op = elem.replace("1", "").replace("2", "").replace("3", "").replace("O: ", "")
                    temp["sp"] = op

                    if (op == "LUAS"):
                        temp["unit"] = "M2"

                elif (elem.startswith("R: ")):

                    rel = elem.replace("R: ", "")
                    if (isSpatialOp):
                        paramRel = rel

                elif (elem.startswith("V: ")):

                    val = elem.replace("V: ", "")
                    if (isSpatialOp):
                        paramVal = val

                elif (elem.startswith("OP:")):

                    if (isSpatialOp):
                        temp["op"] = elem.replace("OP: ", "")
                elif (elem.startswith("N:")):

                    if (isSpatialOp):
                        temp["num"] = elem.replace("N: ", "")
                elif (elem.startswith("U:")):
                    temp["unit"] = elem.replace("U: ", "")

            if (elem.startswith("G:")):
                #! Tangani juga untuk koordinat yang ","
                coor = re.compile('/d+;/d+')
                points = coor.findall(elem)
                result["cond"][len(result["cond"])-1]["num"] = points[0]
                result["cond"][len(result["cond"])-1]["op"] = "="
                result["cond"][len(result["cond"])-2]["num"] = points[1]
                result["cond"][len(result["cond"])-2]["op"] = "="
            elif (elem=="<P>"):
                isPhrase = True
            elif (elem=="</P>"):
                #! Jangan lupa cek parameter!
                if (isSpatialOp):
                    indeks = getIndexRelation(paramRel, paramVal)
                    params = "r" + indeks + "." + geoms[paramRel][0]
                    temp["params"].append(params)
                    print("type", geoms[paramRel][1])
                    temp["types"].append(geoms[paramRel][1])
                    result["cond"].append(temp)
                isSpatialOp = False
                isPhrase = False

        if (elem=="<PP>"):
            isCond = True
        elif (elem=="</PP>"):
            isCond = False
        elif (elem=="<FP>"):
            isFields = True
            relation = ""
            value = ""
        elif (elem=="</FP>"):
            isFields = False

'''makeResultCond()
print("cond", result["cond"])'''

# Belum menangani field yang tidak ada di relation
# Apa yang terjadi kalo query berupa relation value di FPHRASE
# Bagaimana dengan field yang termasuk geometri?
def makeResultFields():

    isFields = False
    relation = ""
    field = ""
    value = ""
    isPart = False
    isParam = False
    isSpatialOp = False
    isCol = False
    paramRel = ""
    paramVal = ""
    isThereFields = False
    temp = {}
    isForOverlap = False
    prevNode = ""
    #print("wordList", wordList)
    for idx, elem in enumerate(wordList):

        if (elem == "<FP>"):
            isFields = True
            relation = ""
            value = ""
        elif (elem == "</FP>"):
            isFields = False

            # Pemasukan nilai relasi
            for idxFld, fld in enumerate(result["fields"]):
                if ("col" in fld):
                    isThereFields = True
                    indeks = getIndexRelation(relation, value)
                    result["fields"][idxFld]["col"] = "r" + indeks + "." + result["fields"][idxFld]["col"]
                elif ("sp" in fld):
                    indeks = getIndexRelation(relation, value)
                    if (len(result["fields"][idxFld]["params"])==0):
                        indeks = getIndexRelation(relation, value)
                        result["fields"][idxFld]["params"].append("r" + indeks + "." + geoms[relation][0])
                        result["fields"][idxFld]["types"].append(geoms[relation][1])
                    #! Bagaimana dengan kasus field ada di relasi lain?
                    elif (result["fields"][idxFld]["params"][0].startswith("XXX")):
                        indeks = getIndexRelation(relation, value)
                        geoms[relation]
                        fld = result["fields"][idxFld]["params"][0].replace("XXX ", "")
                        result["fields"][idxFld]["params"][0] = "r" + indeks + "." + fld
                        idxGeom = 0
                        for idx in range(0, len(geoms[relation]), 2):
                            if (geoms[relation][idx]==fld):
                                idxGeom = idx
                                break
                        result["fields"][idxFld]["types"].append(geoms[relation][idxGeom+1])
            
            if (not isThereFields and not isSpatialOp and not isPart):
                temp = {"geom": "", "type": ""}
                indeks = getIndexRelation(relation, value)
                #print("relation", relation)
                temp["type"] = geoms[relation][1]
                temp["geom"] = "r" + indeks + "." + geoms[relation][0]
                result["fields"].append(temp)

        elif (elem == "PART"):
            isPart = True

        elif (elem == '<F>'):
            isCol = True
        elif (elem == '</F>'):
            isCol = False

        if (isFields):
            if (elem == "<P>"):
                isParam = True
            elif (elem == "</P>"):
                isParam = False
                indeks = getIndexRelation(paramRel, paramVal)
                params = "r" + indeks + "." + geoms[paramRel][0]
                #print(result["fields"][len(result["fields"])-1])
                #print(result["fields"])
                result["fields"][len(result["fields"])-1]["params"].append(params)
                result["fields"][len(result["fields"])-1]["types"].append(geoms[paramRel][1])
                paramRel = ""
                paramVal = ""
            
                # Masih belum ada untuk srcRelation dan srcVal
                '''fld = geoms[paramRel][0]
                indeks = getIndexRelation(paramRel, paramVal)
                params = "r" + indeks + "." + fld
                temp["params"].append(params)
                temp["types"].append(geoms[paramRel][1])
                
                paramRel = ""
                paramVal = ""'''

        #print("bool", isFields, isParam)
        #print("elem", elem)
        if (isFields and not isParam):
            #print("test")
            if (elem.startswith("O1:")):
                isSpatialOp = True
                temp = {"sp" : "", "params": [], "types": [], "unit": "M"}

                spatialOp = elem.replace("1", "").replace("2", "").replace("3", "").replace("O: ", "")

                if (spatialOp=="LUAS"):
                    temp["unit"] = "M2"

                temp["sp"] = spatialOp
                result["fields"].append(temp)
            elif (elem.startswith("R:")):
                #print("relation")
                relation = elem.replace("R: ", "")
            elif (elem.startswith("U:")):
                temp["unit"] = elem.replace("U: ", "")
            elif (elem.startswith("V:")):
                value = elem.replace("V: ", "")
            elif (elem.startswith("F:")):
                if (prevNode.replace("1", "").replace("2", "").replace("3", "").startswith("O:")):
                    result["fields"][len(result["fields"])-1]["params"].append("XXX "+elem.replace("F: ", ""))
                elif (isCol):
                    temp = {"col" : "", "relation": ""}
                    temp["col"] = elem.replace("F: ", "")
                    result["fields"].append(temp)
        elif (isFields and isParam):
            if (elem.startswith("R:")):
                paramRel = elem.replace("R: ", "")
            elif (elem.startswith("V:")):
                paramVal = elem.replace("V: ", "")

        if (not isFields):
            if (elem == "<P>"):
                isParam = True
            elif (elem == "</P>"):
                isParam = False
                if (isPart):
                    #print("temp", temp)
                    indeks = getIndexRelation(relation, value)
                    temp["params"].append("r" + indeks + "." + geoms[relation][0])
                    temp["types"].append(geoms[relation][1])
                    result["fields"].append(temp)
                    isPart = False

            if (elem.startswith("O3:")):
                if (isPart):
                    temp = {"sp" : "", "params": [], "types": [], "unit": "M"}
                    temp["sp"] = "OVERLAP"
                    indeks = getIndexRelation(relation, value)
                    temp["params"].append("r" + indeks + "." + geoms[relation][0])
                    temp["types"].append(geoms[relation][1])
                    #result["fields"].append(temp)
                    
            # Diasumsikan relasi dan value
            elif (isParam and elem.startswith("R:")):
                relation = elem.replace("R: ", "")
            elif (isParam and elem.startswith("V:")):
                value = elem.replace("V: ", "")

        prevNode = elem

makeResultFields()
print("fields", result["fields"])
makeResultCond()
print("cond", result["cond"])


'''def makeResultFields():

    isFields = True
    isThereFields = False
    counter = 0
    idxList = []
    for idx, elem in enumerate(wordList):

        if (elem == "<FP>"):
        elif (elem == "</FP>"):
        elif (elem == "OVERLAPS"):

        if (elem=="SEPARATOR"):
            isFields = False
        elif (elem=="|"):
            isThereFields = False
            isFields = True

        if (isFields):
            if (elem.startswith("O:")):
                spatialOp = elem.replace("1", "").replace("2", "")
                result["fields"].append(spatialOp)
            elif (elem.startswith("F:")):
                isThereFields = True
                result["fields"].append(elem)
                idxList.append(counter)
            elif (elem.startswith("R:")):
                if (not isThereFields):
                    result["fields"].append("F: "+geoms[elem.replace("R: ", "")][0])
                    idxList.append(counter)
                #else:
                for idx in idxList:
                    locator[str(idx)] = elem
                idxList = []
                result["fields"].append(elem)
            elif (elem.startswith("V:")):
                locator[str(idx)] = '|'+elem
                result["fields"].append(elem)
            else:
                # Untuk kasus dimana tidak perlu membuat lebih dari 1 query SQL
                if (elem!='|'):
                    result["fields"].append(elem)
                else:
                    counter = counter - 1
            counter = counter + 1'''


#makeResultFields()
#print(result["fields"])
#print(locator)

#def traverseTree():



'''def makeSelectClause():
    
    query = "SELECT "
    for idx, elem in enumerate(result["fields"]):
        if (elem.startswith("F:")):
            words = locator[str(idx)].split('|')
            for word in words:
                rel = ""
                val = ""
                srcRel = ""
                srcVal = ""
                if (word.startswith("R: ")):
                    rel = word.replace("R: ", "")
                elif (word.startswith("V: ")):
                    val = word.replace("V: ", "")
                elif (word.startswith("SR: ")):
                    srcRel = word.replace("SR: ", "")
                elif (word.startswith("SV: ")):
                    srcVal = word.replace("SV: ", "")
            query = query + "r" + getIndexRelation(rel, val, srcRel, srcVal)
            query = query + "." + elem.replace("F: ", "") + ", "

    query = query[:-2]

    return query'''

#! Tes dari mil ke meter
def displacement(fromUnit, toUnit):

    basicUnit = ["KM", "HM", "DAM", "M", "DM", "CM", "MM"]
    otherUnit = {"MIL": 0.00062}
    areaUnit = ["KM2", "HM2", "DAM2", "M2", "DM2", "CM2", "MM2"]
    calc = 1

    if (fromUnit in basicUnit and toUnit in basicUnit):
        idxF = basicUnit.index(fromUnit)
        idxT = basicUnit.index(toUnit)
        calc = pow(10, idxT-idxF)
    elif (fromUnit in otherUnit):
        idxF = basicUnit.index("M")
        idxT = basicUnit.index(toUnit)
        calc = pow(10, idxT-idxF)*otherUnit[fromUnit]
    elif (toUnit in otherUnit):
        calc = otherUnit[toUnit]
    else:
        idxF = areaUnit.index(fromUnit)
        idxT = areaUnit.index(toUnit)
        calc = pow(10, (idxT-idxF)*2)

    return calc

def convert(value, fromUnit, toUnit):

    return str(value*displacement(fromUnit, toUnit))

def makeSelectClause():
    
    query = "SELECT "
    for elem in result["fields"]:
        if ('sp' in elem):
            #print(elem['types'])
            geoJson1 = "" 
            geoJson2 = ""
            if (elem['sp']=='OVERLAP'):
                geoJson1 = "ST_AsGeoJSON("
                geoJson2 = ")"
            if (elem["unit"]!="M" and elem["unit"]!="M2"):
                if (elem["unit"]):
                    query = query + declareFunctions(elem['sp'], elem['params'], elem['types']) + "*" + convert(1, "M", elem["unit"])
                elif ("2" in elem["unit"]):
                    query = query + declareFunctions(elem['sp'], elem['params'], elem['types']) + "*" + convert(1, "M2", elem["unit"])
            else:
                query = query + geoJson1 + declareFunctions(elem['sp'], elem['params'], elem['types']) + geoJson2
        elif ('geom' in elem):
            if (elem['type']=="geog"):
                query = query + 'ST_AsGeoJSON(' + elem['geom'] + ')'
            else:
                query = query + 'ST_AsGeoJSON(' + 'ST_Transform(' + elem['geom'] + ', 4326)' + ')'
        elif ('col' in elem):
            #indeks = getIndexRelation(elem['rel'])
            query = query + elem['col']

        query = query + ', '

    query = query[:-2]

    return query

query = makeSelectClause()
print("SELECT:", query)

def makeFromClause():
    counter = 1
    query = "FROM "
    for idx, elem in enumerate(result["relation"]):
        # Sementara hanya "yang bukan value" saja
        if (not elem.startswith("V:") and elem != '|'):
            query = query + elem.replace("V: ", "") + " r" + str(counter) + ", "
            counter = counter + 1

    query = query[:-2]
    return query

query = makeFromClause()
#print("FROM:", query)

def createResultIdentifier():

    whereAppend = "("
    for idx, elem in enumerate(result["relation"]):
        if (idx+1 < len(result["relation"]) and result["relation"][idx+1].startswith("V:")):
            whereAppend = whereAppend + "lower(r" + getIndexRelation(elem, result["relation"][idx+1].replace("V: ", ""))
            whereAppend = whereAppend + "." + defAttrs[elem] + ") = '" + result["relation"][idx+1].replace("V: ", "") + "'"
            whereAppend = whereAppend + " AND "
    whereAppend = whereAppend[:-5] + ")"
    return whereAppend

#print("FIELD-VALUE", createResultIdentifier())

'''elif (elem.startswith("R: ")):
            if (isFirst):
                #print("isFirst", isFirst)
                relation1 = elem.replace("R: ", "")
            else:
                relation2 = elem.replace("R: ", "")
        elif (elem.startswith("F: ")):
            if (isFirst):
                field1 = elem.replace("F: ", "")
            else:
                field2 = elem.replace("F: ", "")
        elif (elem.startswith("V: ")):
            if (isFirst):
                value1 = elem.replace("V: ", "")
            else:
                value2 = elem.replace("V: ", "")
        elif (elem.startswith("S: ")):
            if (relation2==""):
                con1 = elem.replace("S: ", "")
            else:
                con2 = elem.replace("S: ", "")
        elif (elem.startswith("SV: ")):
            if (relation2==""):
                conVal1 = elem.replace("SV: ", "")
            else:
                conVal2 = elem.replace("SV: ", "")'''

def createCondition():

    whereAppend = "("

    for idx, elem in enumerate(result["cond"]):

        if ("sp" in elem and "op" in elem):
            whereAppend = whereAppend + declareFunctions(elem["sp"], elem["params"], elem["types"])
            if ("2" in elem["unit"]):
                num = convert(int(elem["num"]), elem["unit"], "M2")
            else:
                num = convert(int(elem["num"]),  elem["unit"], "M")
            whereAppend = whereAppend + " " + elem["op"] + " " + num
        elif ("sp" in elem):
            whereAppend = whereAppend + declareFunctions(elem["sp"], elem["params"], elem["types"])

        whereAppend = whereAppend + " AND "

    whereAppend = whereAppend[:-5] + ")"
    return whereAppend

# Apakah isFoundPhrase ampuh?
'''def createCondition():

    whereAppend = "("
    objects = []
    isFirst = True
    relation1 = ""
    field1 = ""
    value1 = ""
    relation2 = ""
    field2 = ""
    value2 = ""
    con1 = ""
    con2 = ""
    conVal1 = ""
    conVal2 = ""
    op = ""
    spatialOp = ""
    isFoundPhrase = False
    for idx, elem in enumerate(result["cond"]):
        if (elem.startswith("O:")):
            spatialOp = elem.replace("O: ", "")
        elif (elem.startswith("M:")):
            op = elem.replace("M: ", "")
        elif (elem == "<p>"):
            counter = idx + 1
            while (counter < len(result["cond"])):
                node = result["cond"][counter]
                if (node == '</p>'):
                    break

                if (not isFoundPhrase):
                    if (node.startswith("R:")):
                        relation1 = node.replace("R: ", "")
                    elif (node.startswith("F:")):
                        field1 = node.replace("F: ", "")
                    elif (node.startswith("V:")):
                        value1 = node.replace("V: ", "")
                    elif (node.startswith("SR:")):
                        con1 = node.replace("SR: ", "")
                    elif (node.startswith("SV:")):
                        conVal1 = node.replace("SV: ", "")
                else:
                    if (node.startswith("R:")):
                        relation2 = node.replace("R: ", "")
                    elif (node.startswith("F:")):
                        field2 = node.replace("F: ", "")
                    elif (node.startswith("V:")):
                        value2 = node.replace("V: ", "")
                    elif (node.startswith("SR:")):
                        con2 = node.replace("SR: ", "")
                    elif (node.startswith("SV:")):
                        conVal2 = node.replace("SV: ", "")
                
                counter = counter + 1

            isFoundPhrase = True

        elif (elem == "."):
            isFirst = False
        elif (elem.startswith("C: ") or elem.startswith("COMMA")):
            #print("data1", relation1, "  ", field1, "  ", value1, "  ", con1, "  ", conVal1)
            #print("data2", relation2, "  ", field2, "  ", value2, "  ", con2, "  ", conVal2)
            r1 = getIndexRelation(relation1, value1, con1, conVal1)
            r2 = getIndexRelation(relation2, value2, con2, conVal2)
            if (field1==""):
                field1 = geoms[relation1][0]

            param1 = "r" + r1 + "." + field1
            param2 = ""
            if (relation2!=""):
                if (field2==""):
                    field2 = geoms[relation2][0]
                param2 = "r" + r2 + "." + field2
            #print("params", param1, param2)
            #print("function", declareFunctions(spatialOp, [param1, param2]))
            whereAppend = whereAppend + declareFunctions(spatialOp, [param1, param2], geoms[relation1][1], geoms[relation2][1]) + " "
            if (op!=""):
                whereAppend = whereAppend + op + " " + num + " "
            whereAppend = whereAppend + elem.replace("C: ", "") + " "
            isFirst = True
            relation1 = ""
            field1 = ""
            value1 = ""
            relation2 = ""
            field2 = ""
            value2 = ""
            con1 = ""
            con2 = ""
            conVal1 = ""
            conVal2 = ""
            op = ""
            isFoundPhrase = False
        elif (elem == '|'):
            #print("data1", relation1, "  ", field1, "  ", value1, "  ", con1, "  ", conVal1)
            #print("data2", relation2, "  ", field2, "  ", value2, "  ", con2, "  ", conVal2)
            r1 = getIndexRelation(relation1, value1, con1, conVal1)
            r2 = getIndexRelation(relation2, value2, con1, conVal2)
            if (field1==""):
                field1 = geoms[relation1][0]
            
            param1 = "r" + r1 + "." + field1
            param2 = ""
            if (relation2!=""):
                if (field2==""):
                    field2 = geoms[relation2][0]
                param2 = "r" + r2 + "." + field2
            #print("params", param1, param2)
            whereAppend = whereAppend + declareFunctions(spatialOp, [param1, param2], geoms[relation1][1], geoms[relation2][1]) + " "
            if (op!=""):
                whereAppend = whereAppend + op + " " + num + " "
            isFirst = True
            relation1 = ""
            field1 = ""
            value1 = ""
            relation2 = ""
            field2 = ""
            value2 = ""
            con1 = ""
            con2 = ""
            conVal1 = ""
            conVal2 = ""
            op = ""
            whereAppend = whereAppend + ") OR ("
            isFoundPhrase = False
        elif (elem.startswith("U: ")):
            print("-")
        else:
            num = elem

    whereAppend = whereAppend[:-7]
    whereAppend = whereAppend + ")"
    return whereAppend'''

#print(getConnection('kabupaten', 'provinsi'))

#! Kasus Kabupaten Provinsi Kabupaten Provinsi dan perhatikan kasus lainnya
def makeJoinCondition():

    prevRelation = ""
    relation = ""
    appendWhere = "("
    counter = 1
    for elem in result["relation"]:
        if (not elem.startswith("V:") and elem != '|'):
            prevRelation = relation
            relation = elem.replace("R: ", "")
            if (prevRelation != ''):
                if (isConnected(prevRelation, relation)):
                    appendWhere = appendWhere + "r" + str(counter-1) + "." + connections[prevRelation][0]
                    appendWhere = appendWhere + " = r" + str(counter) + "." + connections[relation][0]
                    appendWhere = appendWhere + " AND "
            counter = counter + 1

    appendWhere = appendWhere[:-5]
    appendWhere = appendWhere + ")"

    return appendWhere

#print("join", makeJoinCondition())

def makeWhereClause():

    query = "WHERE "
    query = query + createResultIdentifier()
    temp = makeJoinCondition()
    if (temp!=")"):
        query = query + " AND "
        query = query + temp
    temp = createCondition()
    if (temp!=")"):
        query = query + " AND "
        query = query + temp
    
    return query

query = makeWhereClause()
print("WHERE:", query)

#whereAppend = createResultIdentifier()
#print(whereAppend)