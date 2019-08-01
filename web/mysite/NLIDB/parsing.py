import re

import nltk
from nltk.grammar import Nonterminal, Production, CFG

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

    extractor = re.compile(r'\(\s*\d+\s*,\s*\d+\s*\)')
    keepList = extractor.findall(sentence)
    for keep in keepList:
        temp = keep.replace(',', ':')
        sentence = sentence.replace(keep, temp)

    extractor = re.compile(r'(\d+[\.|\:]\d+)')
    timeList = extractor.findall(sentence)
    print("timeList", timeList)
    for keep in timeList:
        sentence = sentence.replace(keep, 'time')

    #print("pra-stem", sentence)

    sentence = sentence.replace(',', ' xyz')
    sentence = sentence.replace(' irisan', ' irisanabc')
    sentence = sentence.replace('jangkauan', 'jangkauanabc')
    sentence = sentence.replace('.', 'aziz')
    sentence = sentence.replace('bersebelahan', 'belah')
    sentence = sentence.replace('lingkaran', 'lingkaranxyz')

    # Proses stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    # Data pembantu stemmer
    #removeList = ['ada', 'masing', 'tiap', 'dengan', 'besar', 'hadap', 'milik', 'antara', 'meter', 'seluruh']
    prefixList = ['ber-']
    stemList = ['beribukota', 'ibukota']

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
    output = output.replace('irisanabc', 'irisan')
    output = output.replace('jangkauanabc', 'jangkauan')
    output = output.replace('aziz', '.')
    output = output.replace('lingkaranxyz', 'lingkaran')
    #print("Hasil remove: "+output)

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
    coordinates = set([match.group(0) for match in re.finditer(r"\(\d+,\d+\)", sentence)])
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
    temp = """
    ABSIS -> 'absis'
    ORDINAT -> 'ordinat'
    KOORDINAT -> 'koordinat'
    JARAK -> 'jarak'
    IN -> 'dalam' | 'pada' | 'ada' 'di'
    OUTSIDE -> 'luar'
    PANJANG -> 'panjang'
    LUAS -> 'luas'
    KELILING -> 'keliling'
    OVERLAPS -> 'iris' | 'singgung'
    OVERLAP -> 'irisan'
    MEETS -> 'di' 'samping' | 'belah'
    WITHIN -> 'jangkau'
    PART -> 'bagian' | 'daerah'
    """
    nodes = nodes + temp

    # Node Satuan
    temp = """
    KM -> 'kilometer' | 'km'
    M -> 'meter' | 'm'
    MIL -> 'mil'
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
    WORD -> MIL | M | KM | LESS | MORE | EQUAL | NOT | AND | OR | SEPARATOR | COMMA
    WORD -> ABSIS | ORDINAT | KOORDINAT | JARAK | IN | WITHIN | OUTSIDE | PANJANG | LUAS
    WORD -> KELILING | OVERLAP | OVERLAPS | MEETS | FIELD | RELATION | VALUE | NUMBER
    WORD -> TIME | COOR | COUNT | MAX | MIN | SUM | PART | REMOVES
    """

    print("\nPreprocessing kalimat...")
    sentence = preprocessing(sentence)
    #print("preprocessing", sentence)

    removes = set([match.group(0) for match in re.finditer(r"\w+", sentence)])
    #print(removes)

    # Penanganan Multi Value termasuk Value
    # Sebaiknya dimasukkan pada penanganan CFG ERROR
    # Tambahkan penanganan kata yang berperan sebagai value dan bukan value
    # Mungkin gunakan cara sentencenya katanya dihapus terus dimunculin lagi
    words = re.finditer(r"\w+", sentence)
    wordList = []
    for word in words:
        wordList.append(word.group(0))
    #print(wordList)

    for val in manyValues:
        if (sentence.find(val)!=-1):
            #print(val)
            splitter = val.split(' ')
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
                        removes.remove(split)
                    #for i in range(0, len(splitter)):
                        #counters.append(idx+i)

    '''i = 0
    temp = []
    for idx, match in enumerate(re.finditer(r"\w+", sentence)):
        if (idx == counters[0]):
            i = i + 1
        else:
            temp.append(match.group(0))'''

    #print("removes", removes)

    grammar = CFG.fromstring(temp+nodes)

    # Load grammar into a parser
    lgrammar, lproductions = addSuffixGrammar(grammar)
    parser = nltk.RecursiveDescentParser(lgrammar)

    tokens = sentence.split()
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

    if (parse_tree==None):
        #print("tes")
        lproductions.extend([literal_production("REMOVES", remove) for remove in removes])
        lgrammar = CFG(grammar.start(), lproductions)
        parser = nltk.RecursiveDescentParser(lgrammar)
        for t in parser.parse(tokens):
            parse_tree = t
            break
        print("=====")
        for t in parser.parse(tokens):
            print(t)
        #print(parse_tree)

    #print("temp parse tree",parse_tree)

    removeList = traverseRemoval(parse_tree, [])
    sentence = remove(sentence, removeList)
    print("Kalimat hasil preprocessing", sentence)

    rule = """
    S -> QUERIES
    QUERIES -> QUERY COMMA QUERIES | QUERY CONJ QUERIES | QUERY
    QUERY -> COMMAND CONDITION | COMMAND VALUE
    FIELDS -> FIELD | SPATIALOP FIELDS | FIELD FIELDS | FIELD CONJ FIELDS | FIELD COMMA CONJ FIELDS | FIELD COMMA FIELDS
    VALUES -> VALUE CONJ VALUE | VALUE COMMA VALUE | VALUE VALUES | VALUE
    CONDITION -> OVERLAP FIELD RELATION VALUE FIELD RELATION VALUE | AGGREGATE CONDITION | COND CONJ CONDITION | COND COMMA CONDITION | COND COMMA CONJ CONDITION | COND CONDITION | RELATION SEPARATOR CONDITION | FIELD SEPARATOR CONDITION | COND SEPARATOR CONDITION | SPATIALOP OPERATOR | SPATIALOP COND OPERATOR | COND SPATIALOP OPERATOR | SPATIALOP GEOCONDS | SPATIALOP COND COND | SPATIALOP COND CONJ COND | NOT SPATIALOP COND COND | SPATIALOP COND OPERATOR | SPATIALOP COND COND OPERATOR | SPATIALOP COND | NOT SPATIALOP COND | SPATIALOP VALUES | SPATIALOP VALUES CONDITION | SPATIALOPS CONDITION | COND
    GEOCONDS -> GEOCOND COMMA GEOCONDS | GEOCOND CONJ COMMA GEOCOND | GEOCOND
    GEOCOND -> GEOMETRY POINT COOR CONJ POINT COOR | GEOMETRY POINT COOR SIZE NUMBER | POINT COOR OPERATOR
    COND -> PART RELATION | PART IN RELATION | PART RELATION VALUE | PART FIELD RELATION VALUE | PART IN RELATION VALUE | PART IN FIELD RELATION VALUE | PART RELATION FIELD VALUE | PART IN RELATION FIELD VALUE | NOT FIELD VALUE | FIELDS RELATION | FIELDS OPERATOR | FIELDS RELATION VALUE | FIELDS RELATION NOT VALUE | FIELDS RELATION FIELDS VALUE | FIELDS RELATION NOT FIELDS VALUE | FIELDS VALUE | FIELDS TIME | RELATION FIELDS VALUE | FIELDS NOT VALUE | FIELDS NOT TIME | RELATION FIELDS NUMBER | RELATION NOT FIELDS NUMBER | RELATION FIELDS NOT VALUE | RELATION FIELDS | RELATION VALUE | RELATION NOT VALUE | SPATIALOP GEOCONDS | SPATIALOP OPERATOR | SPATIALOP OPERATOR RELATION VALUE
    OPERATOR -> OP NUMBER | OP NUMBER UNIT | NUMBER | NUMBER UNIT
    OP -> LESS | MORE | EQUAL
    UNIT -> KM | M | MIL
    GEOMETRY -> SQUARE | RECTANGLE
    POINT -> LU | RU | LB | RB | PUSAT | 'titik'
    SIZE -> SIDE | LENGTH | WIDTH
    CONJ -> AND | OR
    SPATIALOP -> PANJANG | LUAS | KELILING | IN | OUTSIDE | JARAK | OVERLAP | OVERLAPS | MEETS | ABSIS | ORDINAT | WITHIN | KOORDINAT
    SPATIALOPS -> SPATIALOP COMMA SPATIALOPS | SPATIALOP CONJ SPATIALOPS | SPATIALOP
    AGGREGATE -> COUNT | MAX | MIN | SUM
    """

    grammar = CFG.fromstring(rule+nodes)
    tokens = sentence.split()

    # Load grammar into a parser
    lgrammar, lproductions = addSuffixGrammar(grammar)
    parser = nltk.RecursiveDescentParser(lgrammar)

    for t in parser.parse(tokens):
        #print(t)
        parse_tree = t
        break
    
    print("=====")
    for t in parser.parse(tokens):
        print(t)

    return parse_tree