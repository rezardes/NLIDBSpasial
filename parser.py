import re

import nltk
from nltk.grammar import Nonterminal, Production, CFG

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def checkNode(node, *symbols):

    result = False
    for symbol in symbols:
        if (type(node)!=type("tes")):
            if (node.label()==symbol):
                result = True
                break
    return result

def addSuffixGrammar(grammar):

    productions = grammar.productions()
    lproductions = list(productions)

    key = "VALUE"
    lhs = Nonterminal(key)
    lproductions.extend([Production(lhs, ["bengawan","solo"])])
    lproductions.extend([Production(lhs, ["us","route","1"])])
    lproductions.extend([Production(lhs, ["us","route","2"])])
    lproductions.extend([Production(lhs, ["state","route","2"])])
    lproductions.extend([Production(lhs, ["state","route","3"])])

    # Add a production for every words and number
    lproductions.extend([literal_production("NUMBER", number) for number in numbers])
    lproductions.extend([literal_production("RELATION", relation) for relation in relations])
    lproductions.extend([literal_production("VALUE", value) for value in values])
    lproductions.extend([literal_production("FIELD", field) for field in fields])
    lproductions.extend([literal_production("COOR", coor) for coor in coordinates])

    # Make a local copy of the grammar with extra productions
    lgrammar = CFG(grammar.start(), lproductions)

    return lgrammar, lproductions
    

def literal_production(key, rhs):
    """ Return a production <key> -> n 

    :param key: symbol for lhs:
    :param rhs: string literal:
    """
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

    sentence = sentence.replace(',', ' xyz')
    sentence = sentence.replace(' irisan', ' irisanabc')

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
    #print("Hasil stemmer: "+output)
    for elem in prefixList:
        output = output.replace(elem, '')
    for i in range(0, len(stemList), 2):
        output = output.replace(stemList[i], stemList[i+1])
    output = output.replace(' xyz', ' ,')
    output = output.replace('irisanabc', 'irisan')
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


# Node Operator
nodes = """
LESS -> 'kurang' 'dari'
MORE -> 'lebih' 'dari'
EQUAL -> 'sama' 'dengan' | 'besar'
NOT -> 'tidak' | 'bukan'
AND -> 'dan' | 'serta'
OR -> 'atau'
COMMA -> ','
"""

# Node Spatial Operator
temp = """
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
WORD -> MIL | M | KM | LESS | MORE | EQUAL | NOT | AND | OR | COMMA | ABSIS
WORD -> ORDINAT | JARAK | INSIDE | OUTSIDE | PANJANG | LUAS | KELILING | OVERLAP
WORD -> OVERLAPS | MEETS | FIELD | RELATION | VALUE | REMOVES
"""

sentence = input()
sentence = preprocessing(sentence)
print(sentence)

numbers = set([match.group(0) for match in re.finditer(r"\d+", sentence)])
coordinates = set([match.group(0) for match in re.finditer(r"\(\d+,\d+\)", sentence)])
removes = set([match.group(0) for match in re.finditer(r"\w+", sentence)])
relations = ["segitiga", "kotak", "titik", "garis", "poligon", "negara", "kota", "provinsi", "restoran", "jalan"]
fields = ["nama", "ibukota", "geom", "id", "id_ibukota", "alamat"]
values = ["jakarta", "indonesia", "india", "a", "b", "c", "Mexfield", "Exford"]

grammar = CFG.fromstring(temp+nodes)

# Load grammar into a parser
lgrammar, lproductions = addSuffixGrammar(grammar)
parser = nltk.RecursiveDescentParser(lgrammar)

tokens = sentence.split()
#print(lgrammar)
parse_tree = None
try:
    for t in parser.parse(tokens):
        print(t)
        parse_tree = t
        break
except:
    lproductions.extend([literal_production("REMOVES", remove) for remove in removes])
    lgrammar = CFG(grammar.start(), lproductions)
    parser = nltk.RecursiveDescentParser(lgrammar)
    for t in parser.parse(tokens):
        print(t)
        parse_tree = t
        break

removeList = traverseRemoval(parse_tree, [])
sentence = remove(sentence, removeList)
print(sentence)

rule = CFG.fromstring("""
S -> QUERIES | VALUES
QUERIES -> QUERY COMMA QUERIES | QUERY CONJ QUERIES | QUERY
QUERY -> COMMAND CONDITION
FIELDS -> FIELD | SPATIALOP FIELDS | FIELD FIELDS | FIELD CONJ FIELDS | FIELD COMMA CONJ FIELDS | FIELD COMMA FIELDS
VALUES -> VALUE CONJ VALUE | VALUE COMMA VALUE | VALUE VALUES | VALUE
CONDITION -> COND CONJ CONDITION | COND COMMA CONDITION | COND COMMA CONJ CONDITION | COND CONDITION | RELATION SEPARATOR CONDITION | COND SEPARATOR CONDITION | SPATIALOP OPERATOR | SPATIALOP COND OPERATOR | COND SPATIALOP OPERATOR | SPATIALOP GEOCONDS | SPATIALOP COND COND | SPATIALOP COND CONJ COND | NOT SPATIALOP COND COND | SPATIALOP COND COND OPERATOR | SPATIALOP COND | NOT SPATIALOP COND | SPATIALOP VALUES | SPATIALOP VALUES CONDITION | SPATIALOPS CONDITION | COND
GEOCONDS -> GEOCOND COMMA GEOCONDS | GEOCOND CONJ COMMA GEOCOND | GEOCOND
GEOCOND -> GEOMETRY POINT COOR CONJ POINT COOR | GEOMETRY POINT COOR SIZE NUMBER | POINT COOR OPERATOR
COND -> PART RELATION | PART RELATION VALUE | PART RELATION FIELD VALUE | FIELDS RELATION | FIELDS OPERATOR | FIELDS RELATION VALUE | FIELDS RELATION NOT VALUE | FIELDS RELATION FIELDS VALUE | FIELDS RELATION NOT FIELDS VALUE | RELATION FIELDS VALUE | RELATION FIELDS NUMBER | RELATION NOT FIELDS NUMBER | RELATION FIELDS NOT VALUE | FIELDS VALUE | FIELDS NOT VALUE | RELATION FIELDS | RELATION VALUE | RELATION NOT VALUE | SPATIALOP COND COND | SPATIALOP COND COND OPERATOR | SPATIALOP GEOCONDS | SPATIALOP OPERATOR | SPATIALOP OPERATOR RELATION VALUE | SPATIALOP
OPERATOR -> OP NUMBER | OP NUMBER UNIT | NUMBER | NUMBER UNIT
UNIT -> KM | M | MIL
GEOMETRY -> SQUARE | RECTANGLE
POINT -> LU | RU | LB | RB | PUSAT | 'titik'
SIZE -> SIDE | LENGTH | WIDTH
CONJ -> AND | OR
""")

parser = nltk.RecursiveDescentParser(rule+lgrammar)
for t in parser.parse(tokens):
    print(t)
    parse_tree = t
    break'''