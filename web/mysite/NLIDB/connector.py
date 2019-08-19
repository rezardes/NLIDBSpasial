import psycopg2
import pickle
import copy

q_1 = 'SELECT column_name FROM information_schema.columns WHERE table_name = \'{}\' AND (data_type LIKE \'char%\' OR data_type LIKE \'text%\')'
q_2 = 'SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' AND table_name <> \'geography_columns\' AND table_name <> \'geometry_columns\' AND table_name <> \'spatial_ref_sys\' AND table_name <> \'raster_columns\' AND table_name <> \'raster_overviews\''
q_3 = 'SELECT column_name FROM information_schema.columns WHERE table_name = \'{}\''
q_4 = 'SELECT column_name FROM information_schema.columns WHERE table_name = \'{}\' AND data_type = \'USER-DEFINED\''
q_5 = 'SELECT DISTINCT {} FROM {}'
q_6 = '''SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = \'FOREIGN KEY\';'''
q_7 = 'SELECT DISTINCT ST_GeometryType({}) FROM {}'
q_8 = 'SELECT Find_SRID(\'public\', \'{}\', \'{}\')'

# geoms: column, type, SRID
def getRelations(conn):

    cur = conn.cursor()
    cur.execute(q_2)
    result = cur.fetchall()
    cur.close()

    for i in range(0, len(result)):
        result[i] = result[i][0].lower()

    return result

def getColumns(conn, relations):

    result = {}
    columns = []
    for table in relations:
        cur = conn.cursor()
        cur.execute(q_3.format(table))
        result[table] = cur.fetchall()
        for i in range(0, len(result[table])):
            result[table][i] = result[table][i][0].lower()
            columns.append(result[table][i])
        cur.close()

    return columns, result

def getValues(conn, relations):

    values = []
    manyValues = []
    for table in relations:
        #print(table)
        cur = conn.cursor()
        cur.execute(q_1.format(table))
        columns = cur.fetchall()
        #print(columns)
        for column in columns:
            #print(column)
            cur2 = conn.cursor()
            cur2.execute(q_5.format(column[0], table))
            temps = cur2.fetchall()
            for temp in temps:
                if (temp[0]!=None):
                    if (" " in temp[0]):
                        manyValues.append(temp[0].lower())
                    else:
                        values.append(temp[0].lower())
            cur2.close()
        cur.close()
    
    return values, manyValues

def getGeoms(conn, relations):

    result = {}
    geoColumns = []
    for table in relations:
        cur = conn.cursor()
        cur.execute(q_4.format(table))
        result[table] = cur.fetchall()
        for i in range(0, len(result[table])):
            geoColumns.append(result[table][i][0])
            cur2 = conn.cursor()
            cur2.execute(q_7.format(result[table][i][0], table))
            tipe = cur2.fetchall()
            cur2.close()
            cur2 = conn.cursor()
            cur2.execute(q_8.format(table, result[table][i][0]))
            srid = cur2.fetchall()[0][0]
            cur2.close()
            result[table][i] = result[table][i][0]
            if ("point" in tipe[0][0].lower()):
                result[table].append("point")
            elif ("polygon" in tipe[0][0].lower()):
                result[table].append("polygon")
            elif ("line" in tipe[0][0].lower()):
                result[table].append("line")
            result[table].append(srid)
        cur.close()

    return result, geoColumns

def getConnection(conn, relations):

    connection = {}
    for relation in relations:
        connection[relation] = []
    #print(connection)
    cur = conn.cursor()
    cur.execute(q_6)
    hasil = cur.fetchall()
    for temp in hasil:
        connection[temp[0]].append(temp[1])
        connection[temp[0]].append(temp[2])
        connection[temp[0]].append(temp[3])
        connection[temp[2]].append(temp[3])
        connection[temp[2]].append(temp[0])
        connection[temp[2]].append(temp[1])
    cur.close()

    return connection

'''def getSynonym(text):

    if (text=='waktu'):
        return ['jam']
    else:
        return []'''

def getSynSet(fields):

    synSet = {}

    anotherField = fields.copy()
    for field in fields:
        synonyms = []
        if (field=='waktu'):
            synonyms = ['jam']
        for syn in synonyms:
            anotherField.append(syn)
            synSet[syn] = field
        synSet[field] = field

    return synSet, anotherField

def getMetadata(database, isLoad):

    metadata = None

    if (isLoad):

        conn = psycopg2.connect(host="localhost", database=database, user="postgres", password="1234")
        relations = getRelations(conn)
        fields, attrs = getColumns(conn, relations)
        synSet, fields = getSynSet(fields)

        connection = getConnection(conn, relations)
        connection = getConnection(conn, relations)
        values, manyValues = getValues(conn, relations)
        geoms, geoColumns = getGeoms(conn, relations)

        filename = 'metadata'
        outfile = open(filename,'wb')

        metadata = { 'values': values, 'geoColumns': geoColumns, 'manyValues': manyValues, 'connection': connection, 'fields': fields, 'attrs': attrs, 'relations': relations, 'geoms': geoms }
        #print(metadata)

        pickle.dump(metadata, outfile)
        outfile.close()

        filename = 'synset'
        outfile = open(filename,'wb')
        pickle.dump(synSet, outfile)
        outfile.close()
    
    else:

        infile = open('metadata','rb')
        metadata = pickle.load(infile)
        infile.close()

        infile = open('synset', 'rb')
        synSet = pickle.load(infile)
        infile.close()

    return metadata, synSet    

metadata = []
synSet = {'nama': 'nama'}
#metadata, synSet = getMetadata('sample2', True)
#print(metadata['connection'])
'''
conn = psycopg2.connect(host="localhost", database="sample2", user="postgres", password="1234")
relations = getRelations(conn)
fields, result  = getColumns(conn, relations)
#print(fields)
#print(result)

#print(result)
#print(getValues(conn, relations))
'''
'''
cur = conn.cursor()
cur.execute(q_6)
hasil = cur.fetchall()
print(hasil)
cur.close()
'''

'''
connection = getConnection(conn, relations)connection = getConnection(conn, relations)
print(geoms)

connection = getConnection(conn, relations)
print(connection)

semantics = {}
semantics["wifijangkauan"] = "jari-jari lingkaran"
'''