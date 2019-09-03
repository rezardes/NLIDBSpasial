import sys
sys.path.insert(0, "D:\\My Documents\\Kuliah\\Tugas Akhir\\Experiment\\NLIDBSpasial\\web\\mysite")

SRID_Params = {'JARAK': 3857, 'PANJANG': 3857, 'LUAS': 3857, 'KELILING': 3857, 'ABSIS': 4326, 'ORDINAT': 4326}
SRID_Result = {'OVERLAP': 4326}

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

def declareFunctions(keyword, params, *types):

    function = mapToFunctions(keyword)
    query = ''
    geog = ''

    if (keyword not in parameter):
        return ''
    elif (parameter[keyword]==1):
        if (types[0]=="geog"):
            query = function + params[0] + '::geometry'
        else:
            query = function + 'ST_Transform(' + params[0] + '::geometry, ' + SRID_Params[params[0]] + ')'
    elif (parameter[keyword]==2):
        appendResult1 = ""
        appendResult2 = ""
        appendTransform1 = ""
        appendTransform2 = ""
        if (keyword in SRID_Result):
            appendResult1 = "ST_Transform("
            appendResult2 = ")"
        if (keyword in SRID_Params):
            appendTransform1 = "ST_Transform("
            appendTransform2 = ")"
            if (types[0]=='geog'):
                geog = "::geometry"
        
        query = query + appendResult1 + function + '(' + appendTransform1 + params[0] + geog + appendTransform2 + ', ' + appendTransform1 + params[1] + geog + appendTransform2 + ')' + appendResult2

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
connections = {'jalan': [], 'area': [], 'wifi': ['id', 'posisi_wifi', 'id_wifi'], 'posisi_wifi': ['id_wifi', 'wifi', 'id'], '|': []}
#wordList = ['O: JARAK1', '<P>', 'F: posisi', 'R: wifi', 'V: connex', '</P>', '<P>', 'F: posisi', 'R: wifi', 'V: yagami ramen', '</P>']
wordList = ['R: provinsi', 'SEPARATOR', 'O:2 MEETS', '<p>', 'R: provinsi', 'V: jawa barat', '</p>', "C: AND", 'O:2 MEETS', '<p>', 'R: provinsi', 'V: jawa timur', '</p>', '|']
geoms = {'jalan': ['geom', 'line', 4326], 'area': ['geom', 'polygon', 4326], 'wifi': ['jangkauan', 'polygon', 4326], 
        'posisi': ['posisi', 'point', 4326], 'provinsi': ['geog', 'geog']}

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
    print("fields")
    for idx, elem in enumerate(idxStarts):
        fields = getFields(wordList[elem:idxEnds[idx]])
        print(fields)
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

addRightRelations()

'''print("getPhases", getCodes(wordList, '<P>'))
print("getPhasesEnd", getCodes(wordList, '</P>'))'''

'''print("getNthPhrase", getNthPhrase(1))
print("getNthPhrase", getNthPhrase(2))
print("getNthPhrase", getNthPhrase(3))'''

'''def fixResult():
    for '''

def getIndexRelation(relation, value="", srcRelation="", srcValue=""):

    print(relation, value, srcRelation, srcValue)

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
                print("tes")
                addRelation(elem.replace("R: ", ""))

makeResultRelation()
print("relations", result["relation"])

# Bagaimana membuat srcRel dan srcVal?
def makeResultCond():

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

makeResultCond()
print("cond", result["cond"])

# Belum menangani field yang tidak ada di relation
# Apa yang terjadi kalo query berupa relation value di FPHRASE
def makeResultFields():

    isFields = True
    isThereFields = False
    counter = 0
    idxList = []
    for idx, elem in enumerate(wordList):

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
            counter = counter + 1


makeResultFields()
print(result["fields"])
print(locator)

def makeSelectClause():
    
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
print("FROM:", query)

def createResultIdentifier():

    whereAppend = "("
    for idx, elem in enumerate(result["relation"]):
        if (idx+1 < len(result["relation"]) and result["relation"][idx+1].startswith("V:")):
            whereAppend = whereAppend + "lower(r" + getIndexRelation(elem, result["relation"][idx+1].replace("V: ", ""))
            whereAppend = whereAppend + "." + defAttrs[elem] + ") = '" + result["relation"][idx+1].replace("V: ", "") + "'"
            whereAppend = whereAppend + " AND "
    whereAppend = whereAppend[:-5] + ")"
    return whereAppend

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

# Apakah isFoundPhrase ampuh?
def createCondition():

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
    return whereAppend

def makeWhereClause():

    query = "WHERE "
    query = query + createResultIdentifier() + " AND "
    query = query + createCondition()
    
    return query

query = makeWhereClause()
print("WHERE:", query)

#whereAppend = createResultIdentifier()
#print(whereAppend)