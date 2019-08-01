import psycopg2

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
    for table in relations:
        print(table)
        cur = conn.cursor()
        cur.execute(q_1.format(table))
        columns = cur.fetchall()
        print(columns)
        for column in columns:
            #print(column)
            cur2 = conn.cursor()
            cur2.execute(q_5.format(column[0], table))
            temps = cur2.fetchall()
            for temp in temps:
                if (temp[0]!=None):
                    values.append(temp[0].lower())
            cur2.close()
        cur.close()
    
    return values

def getGeoms(conn, relations):

    result = {}
    for table in relations:
        cur = conn.cursor()
        cur.execute(q_4.format(table))
        result[table] = cur.fetchall()
        for i in range(0, len(result[table])):
            cur2 = conn.cursor()
            cur2.execute(q_7.format(result[table][i][0], table))
            #print(q_7.format(result[table][i][0], table))
            tipe = cur2.fetchall()
            result[table][i] = result[table][i][0]
            if ("point" in tipe[0][0].lower()):
                result[table].append("point")
            elif ("polygon" in tipe[0][0].lower()):
                result[table].append("polygon")
            elif ("line" in tipe[0][0].lower()):
                result[table].append("line")
        cur.close()

    return result

def getConnection(conn, relations):

    connection = {}
    cur = conn.cursor()
    cur.execute(q_6)
    hasil = cur.fetchall()
    for temp in hasil:
        connection[temp[0]] = [temp[2], temp[3]]
        connection[temp[2]] = [temp[0], temp[1]]
    cur.close()

    return connection

def test():
    print('hello')

'''
conn = psycopg2.connect(host="localhost", database="sample2", user="postgres", password="1234")
relations = getRelations(conn)
fields, result  = getColumns(conn, relations)
#print(fields)
#print(result)

#print(result)
#print(getValues(conn, relations))
'''cur = conn.cursor()
cur.execute(q_6)
hasil = cur.fetchall()
print(hasil)
cur.close()'''

geoms = getGeoms(conn, relations)
print(geoms)

connection = getConnection(conn, relations)
print(connection)

semantics = {}
semantics["wifijangkauan"] = "jari-jari lingkaran"
'''