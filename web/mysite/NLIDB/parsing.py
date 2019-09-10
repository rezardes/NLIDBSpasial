import re

import nltk
from nltk.grammar import Nonterminal, Production, CFG

import sys
sys.path.insert(0, "D:\\My Documents\\Kuliah\\Tugas Akhir\\Experiment\\NLIDBSpasial\\web\\mysite")

#from NLIDB.connector import metadata

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

manyValues = {}
values = {}
relations = {}
fields = {}
connections = {}
attrs = {}
geoms = {}

def checkNode(node, *symbols):

    result = False
    for symbol in symbols:
        if (type(node)!=type("tes") and node != None):
            if (node.label()==symbol):
                result = True
                break
    return result

def addSuffixGrammar(grammar):

    productions = grammar.productions()
    lproductions = list(productions)

    key = "VALUE"
    lhs = Nonterminal(key)
    for value in manyValues:
        temp = []
        for val in value.split(" "):
            temp.append(val)
        lproductions.extend([Production(lhs, temp)])

    # Add a production for every words and number
    lproductions.extend([literal_production("NUMBER", number) for number in numbers])
    lproductions.extend([literal_production("RELATION", relation) for relation in relations])
    lproductions.extend([literal_production("VALUE", value) for value in values])
    lproductions.extend([literal_production("FIELD", field) for field in fields])
    lproductions.extend([literal_production("COOR", coor) for coor in coordinates])
    lproductions.extend([literal_production("TIME", time) for time in times])

    # Make a local copy of the grammar with extra productions
    lgrammar = CFG(grammar.start(), lproductions)

    return lgrammar, lproductions
    

def literal_production(key, rhs):
    lhs = Nonterminal(key)
    return Production(lhs, [rhs])

def preprocessing(sentence):
    
    # Ubah menjadi lowercase
    sentence = sentence.lower()

    extractor = re.compile(r"\(-?\d+,\d+ ?; ?\d+,\d+ ?\)|\(\d+ ?, ?\d+ ?\)")
    keepList = extractor.findall(sentence)
    
    for idx, keep in enumerate(keepList):
        sentence = sentence.replace(keep, "coor"+str(idx))
        keepList[idx] = keepList[idx].replace(" ", "")
    #print("keepList", keepList)
    '''for keep in keepList:
        temp = keep.replace(',', ':')
        sentence = sentence.replace(keep, temp)'''

    extractor = re.compile(r'(\d+[\.|\:]\d+)')
    timeList = extractor.findall(sentence)
    #print("timeList", timeList)
    for keep in timeList:
        sentence = sentence.replace(keep, 'time')

    #print("pra-stem", sentence)

    sentence = sentence.replace(',', ' xyz')
    sentence = sentence.replace('tersebut', 'tersebutxyz')
    sentence = sentence.replace('bekasi', 'bekasixyz')
    sentence = sentence.replace('berjarak', 'berjarakxyz')
    sentence = sentence.replace('jaraknya', 'jaraknyaxyz')
    #sentence = sentence.replace('bersebelahan', 'bersebelahanxyz')
    sentence = sentence.replace(' irisan', ' irisanabc')
    sentence = sentence.replace('jangkauan', 'jangkauanabc')
    sentence = sentence.replace('.', 'aziz')
    sentence = sentence.replace('bersebelahan', 'belah')
    sentence = sentence.replace('lingkaran', 'lingkaranxyz')
    sentence = sentence.replace('satuan', 'satuanxyz')
    sentence = sentence.replace('bagian', 'bagianxyz')

    # Proses stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    # Data pembantu stemmer
    #removeList = ['ada', 'masing', 'tiap', 'dengan', 'besar', 'hadap', 'milik', 'antara', 'meter', 'seluruh']
    prefixList = ['ber-']
    stemList = ['beribukota', 'ibukota']

    #print("sentence", sentence)

    output = stemmer.stem(sentence)
    output = output + " "
    for keep in keepList:
        spaces = re.compile(r'\s+')
        coor = spaces.sub('', keep)
        temp = coor.replace(',', ' ')
        temp = temp.replace('(', '')
        temp = temp.replace(')', '')
        output = output.replace(temp, coor)

    for time in timeList:
        output = output.replace('time', time)
    #print("Hasil stemmer: "+output)
    for elem in prefixList:
        output = output.replace(elem, '')
    for i in range(0, len(stemList), 2):
        output = output.replace(stemList[i], stemList[i+1])
    output = output.replace(' xyz', ' ,')
    output = output.replace('tersebutxyz', 'tersebut')
    output = output.replace('berjarakxyz', 'berjarak')
    output = output.replace('bekasixyz', 'bekasi')
    output = output.replace('jaraknyaxyz', 'jaraknya')
    #output = output.replace('bersebelahanxyz', 'bersebelahan')
    output = output.replace('irisanabc', 'irisan')
    output = output.replace('jangkauanabc', 'jangkauan')
    output = output.replace('aziz', '.')
    output = output.replace('lingkaranxyz', 'lingkaran')
    output = output.replace('satuanxyz', 'satuan')
    output = output.replace('bagianxyz', 'bagian')
    output = output.replace('ada di belah', 'di belah')
    #print("Hasil remove: "+output)

    for idx, keep in enumerate(keepList):
        output = output.replace("coor"+str(idx), keep)

    return output

def traverseRemoval(tree, result):

    if (checkNode(tree, "REMOVES")):
        result.append(tree[0])
    else:
        if (type(tree)!=type("tes")):
            for elmt in tree:
                result = traverseRemoval(elmt, result)

    return result

def remove(sentence, removeList):
    sentence = sentence + ' '
    for elem in removeList:
        sentence = sentence.replace(' '+elem+' ', ' ')
    return sentence

def parse(sentence, metadata):

    global numbers
    global coordinates
    global times
    global values
    global relations
    global fields
    global connections
    global attrs
    global manyValues

    relations = metadata["relations"]
    fields = metadata["fields"]
    values = metadata["values"]
    manyValues = metadata["manyValues"]
    connections = metadata["connection"]
    attrs = metadata["attrs"]

    numbers = set([match.group(0) for match in re.finditer(r"\d+", sentence)])
    times = set([match.group(0) for match in re.finditer(r"\d+(\.|\:)\d+", sentence)])

    # Node Operator
    nodes = """
    LESS -> 'kurang' 'dari'
    MORE -> 'lebih' 'dari'
    EQUAL -> 'sama' 'dengan' | 'besar'
    NOT -> 'tidak' | 'bukan'
    AND -> 'dan' | 'serta'
    OR -> 'atau'
    SEPARATOR -> 'yang' | 'jika' | 'ketika'
    COMMA -> ','
    DET -> 'tersebut'
    """

    # Node Agregat
    temp = """
    COUNT -> 'jumlah'
    SUM -> 'total'
    MAX -> 'maksimal'
    MIN -> 'minimal'
    """
    nodes = nodes + temp

    # Pikirkan pula untuk ganti 'ada' 'di' sebagai INTERSECTS
    # Node Spatial Operator
    # WITHIN -> 'jangkau'
    temp = """
    ABSIS -> 'absis'
    ORDINAT -> 'ordinat'
    KOORDINAT1 -> 'koordinat'
    KOORDINAT2 -> 'berkoordinat'
    JARAK1 -> 'jarak'
    JARAK2 -> 'berjarak' | 'jaraknya'
    OUTSIDE -> 'luar'
    PANJANG1 -> 'panjang'
    PANJANG2 -> 'panjangnya'
    LUAS1 -> 'luas'
    LUAS2 -> 'berluas' | 'luasnya'
    KELILING -> 'keliling'
    OVERLAPS -> 'iris' | 'singgung' | 'kena' | 'jangkau' | 'ada' 'di' | 'lewat' | 'ada' 'pada'
    OVERLAP -> 'irisan'
    MEETS -> 'di' 'samping' | 'belah' | 'di' 'belah'
    PART -> 'bagian' | 'daerah'
    """
    nodes = nodes + temp

    # Node Satuan
    temp = """
    KM -> 'kilometer' | 'km'
    M -> 'meter' | 'm'
    MIL -> 'mil'
    M2 -> 'meter' 'persegi'
    KM2 -> 'kilometer' 'persegi'
    """
    nodes = nodes + temp

    # Node Kata Kunci Perintah
    temp = """
    COMMAND ->  'tampil' | 'tunjuk' | 'lihat' | 'hitung' | 'kalkulasi' | 'cari'
    """
    nodes = nodes + temp

    # Node Kata Kunci Geometri
    temp = """
    SIDE -> 'sisi'
    LENGTH -> 'panjang'
    WIDTH -> 'lebar'
    LU -> 'titik' 'kiri' 'atas'
    RB -> 'titik' 'kanan' 'bawah'
    PUSAT -> 'titik' 'pusat'
    SQUARE -> 'persegi'
    RECTANGLE -> 'segiempat' | 'persegi' 'panjang' | 'kotak'
    """
    nodes = nodes + temp

    # Node sebagai tagger
    # Kalo sempet dilakukan secara otomatis
    temp = """
    S -> WORDS
    WORDS -> WORD WORDS | WORD  
    WORD -> SIDE | LENGTH | WIDTH | LU | RB | PUSAT | SQUARE | RECTANGLE | COMMAND
    WORD -> MIL | M | KM | M2 | KM2 | LESS | MORE | EQUAL | NOT | AND | OR | SEPARATOR 
    WORD -> ABSIS1 | ORDINAT | KOORDINAT1 | ABSIS2 | ORDINAT2 | KOORDINAT2 | JARAK1
    WORD -> WITHIN | OUTSIDE | PANJANG1 | PANJANG2 | COMMA | DET | JARAK2 | IN
    WORD -> LUAS1 | LUAS2 | KELILING | OVERLAP | OVERLAPS | MEETS | FIELD | RELATION | VALUE
    WORD -> NUMBER | TIME | COOR | COUNT | MAX | MIN | SUM | PART | UNITDESC | REMOVES
    """

    print("\nPreprocessing kalimat...")
    sentence = preprocessing(sentence)
    coordinates = set([match.group(0) for match in re.finditer(r"\(-?\d+,\d+ ?; ?\d+,\d+ ?\)|\(\d+ ?, ?\d+ ?\)", sentence)])
    print("preprocessing", sentence)

    removes = set([match.group(0) for match in re.finditer(r"\w+\.|\w+", sentence)])
    #print("removes", removes)

    # Penanganan Multi Value termasuk Value
    # Sebaiknya dimasukkan pada penanganan CFG ERROR
    # Tambahkan penanganan kata yang berperan sebagai value dan bukan value
    # Mungkin gunakan cara sentencenya katanya dihapus terus dimunculin lagi
    words = re.finditer(r"\w+\.|\w+", sentence)
    wordList = []
    for word in words:
        wordList.append(word.group(0))
    #print(wordList)

    #print("wordList", wordList)
    #print("manyValues", manyValues)
    for val in manyValues:
        if (sentence.find(val)!=-1):
            #print(val)
            splitter = val.split(' ')
            #print("splitter ", splitter)
            #found = False
            #for split in splitter:
            #    if (not split in removes):
            #        found = True
            #        break
            #if (found):
            #    continue
            found = False
            while (not found):
                
                idx = wordList.index(splitter[0])
                for i in range(1, len(splitter)):
                    if (not splitter[i] in wordList):
                        found = False
                        break
                    else:
                        found = True
                if (not found):
                    words.pop(idx)
                else:
                    for split in splitter:
                        if (split in removes):
                            removes.remove(split)
    #print("removes", removes)                        
    grammar = CFG.fromstring(temp+nodes)

    # Load grammar into a parser
    lgrammar, lproductions = addSuffixGrammar(grammar)
    parser = nltk.RecursiveDescentParser(lgrammar)
    tokens = sentence.split()
    #print("tokens", tokens)
    print("Menguraikan kalimat...")
    parse_tree = None
    try:
        for t in parser.parse(tokens):
            parse_tree = t
            break

    except:
        lproductions.extend([literal_production("REMOVES", remove) for remove in removes])
        lgrammar = CFG(grammar.start(), lproductions)
        parser = nltk.RecursiveDescentParser(lgrammar)
        for t in parser.parse(tokens):
            parse_tree = t
            break

    #print("tree", parse_tree)

    if (parse_tree==None):
        #print("tes")
        lproductions.extend([literal_production("REMOVES", remove) for remove in removes])
        lgrammar = CFG(grammar.start(), lproductions)
        parser = nltk.RecursiveDescentParser(lgrammar)
        for t in parser.parse(tokens):
            parse_tree = t
            break
        #print("=====")
        #for t in parser.parse(tokens):
        #    print(t)'''
        #print(parse_tree)

    #print("temp parse tree",parse_tree)

    removeList = traverseRemoval(parse_tree, [])
    sentence = sentence.replace("kurang dari", "kurang darixyz")
    sentence = sentence.replace("lebih dari", "lebih darixyz")
    sentence = sentence.replace("ada di dalam", "dalam")
    sentence = remove(sentence, removeList)
    sentence = sentence.replace("darixyz", "dari")
    print("Kalimat hasil preprocessing", sentence)

    # SPATIALOP FIELDS
    # QUERIES -> QUERY COMMA QUERIES | QUERY CONJ QUERIES | QUERY
    # FIELDS -> FIELD | FIELD FIELDS | FIELD CONJ FIELDS | FIELD COMMA CONJ FIELDS | FIELD COMMA FIELDS
    # SPATIALOPS -> SPATIALOP COMMA SPATIALOPS | SPATIALOP CONJ SPATIALOPS | SPATIALOP
    # CONDITION -> SPATIALOPS CONDITION | SPATIALOP COND | SPATIALOP OPERATOR
    # PHRASES -> OVERLAP FIELD RELATION VALUE FIELD RELATION VALUE | SPATIALOP PHRASE PHRASE | PART RELATION | PART IN RELATION | PART RELATION VALUE | PART FIELD RELATION VALUE | PART IN RELATION VALUE | PART IN FIELD RELATION VALUE | PART RELATION FIELD VALUE | PART IN RELATION FIELD VALUE
    # COND -> SPATIALOP OPERATOR RELATION VALUE | FIELD OPERATOR
    # PHRASE -> RELATION FIELDS
    rule = """
    S -> QUERY
    QUERY -> COMMAND DESCRIPTION
    DESCRIPTION -> FPHRASE SEPARATOR PHRASES COMMA DESCRIPTION | FPHRASE SEPARATOR PHRASES CONJ DESCRIPTION | FPHRASE SEPARATOR PHRASES COMMA CONJ DESCRIPTION | FPHRASE CONJ DESCRIPTION | FPHRASE COMMA DESCRIPTION | FPHRASE COMMA CONJ DESCRIPTION | FPHRASE SEPARATOR PHRASES | FPHRASE
    FIELDS -> FIELD | SPATIALOP1 | SPATIALOP1 FIELD | FIELD CONJ FIELDS | FIELD COMMA CONJ FIELDS | FIELD COMMA FIELDS | SPATIALOP1 CONJ FIELDS | SPATIALOP1 COMMA FIELDS | SPATIALOP1 COMMA CONJ FIELDS | SPATIALOP1 FIELD CONJ FIELDS | SPATIALOP1 FIELD COMMA FIELDS | SPATIALOP1 FIELD COMMA CONJ FIELDS
    VALUES -> VALUE CONJ VALUE | VALUE COMMA VALUE | VALUE VALUES | VALUE
    PHRASES -> PHRASE CONJ PHRASES | PHRASE COMMA PHRASES | PHRASE COMMA CONJ PHRASES | PHRASE
    GEOCONDS -> GEOCOND COMMA GEOCONDS | GEOCOND CONJ COMMA GEOCOND | GEOCOND
    GEOCOND -> GEOMETRY POINT COOR CONJ POINT COOR | GEOMETRY POINT COOR SIZE NUMBER | POINT COOR OPERATOR
    FPHRASE -> RELATION | PART RELATION | FIELDS RELATION | FIELDS RELATION VALUE | RELATION FIELD VALUE | RELATION VALUE | PART RELATION VALUE | SPATIALOP1 PHRASE PHRASE | SPATIALOP1 PHRASE PHRASE UNIT | SPATIALOP1 PHRASE | SPATIALOP1 PHRASE UNIT
    PHRASE ->  PART PHRASE | NOT FIELD VALUE | FIELD RELATION | FIELD RELATION VALUE | FIELD OPERATOR | FIELD RELATION DET OPERATOR | FIELDS RELATION NOT VALUE | FIELDS RELATION FIELDS VALUE | FIELDS RELATION NOT FIELDS VALUE | FIELDS VALUE | FIELDS TIME | RELATION FIELDS VALUE | FIELDS NOT VALUE | FIELDS NOT TIME | RELATION FIELDS NUMBER | RELATION NOT FIELDS NUMBER | RELATION FIELDS NOT VALUE | RELATION VALUE | RELATION NOT VALUE | SPATIALOP GEOCONDS | SPATIALOP OPERATOR | SPATIALOP PHRASE OPERATOR | SPATIALOP OPERATOR PHRASE | SPATIALOP PHRASE | SPATIALOP COOR
    OPERATOR -> OP NUMBER | OP NUMBER UNIT | NUMBER | NUMBER UNIT
    OP -> LESS | MORE | EQUAL
    UNITCOND -> UNITDESC UNIT
    UNIT -> KM | M | MIL | M2 | KM2
    GEOMETRY -> SQUARE | RECTANGLE
    POINT -> LU | RU | LB | RB | PUSAT | 'titik'
    SIZE -> SIDE | LENGTH | WIDTH
    CONJ -> AND | OR
    SPATIALOP -> SPATIALOP1 | SPATIALOP2 | SPATIALOP3
    SPATIALOP1 -> PANJANG1 | LUAS1 | KELILING | JARAK1 | OVERLAP | ABSIS1 | ORDINAT1 | WITHIN | KOORDINAT1
    SPATIALOP2 -> ABSIS2 | ORDINAT2 | KOORDINAT2 | LUAS2 | JARAK2 | PANJANG2 | MEETS
    SPATIALOP3 -> OVERLAPS
    AGGREGATE -> COUNT | MAX | MIN | SUM
    """

    grammar = CFG.fromstring(rule+nodes)
    tokens = sentence.split()

    # Load grammar into a parser
    lgrammar, lproductions = addSuffixGrammar(grammar)
    #print(lgrammar)
    parser = nltk.RecursiveDescentParser(lgrammar)

    #for t in parser.parse(tokens):
    #    #print(t)
    #    parse_tree = t
    #    break'''
    
    print("=====")
    counter = 0
    for t in parser.parse(tokens):
        if (counter==0):
            parse_tree = t
            counter = 1
        print(t)

    print(parse_tree)

    return parse_tree

#sentence = "Tunjukkan irisan jangkauan wifi Mifi M5 dan jangkauan wifi Huawei e5577 ketika jam 13:00!"
#sentence = "Tunjukkan jarak antara wifi Mifi M5 dengan wifi Huawei e5577 ketika jam 13:00!"
#meta = metadata
#parser = parse(sentence, meta)
#print(parser)