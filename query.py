import psycopg2

# q_1: query kolom string
# q_2: query tabel
# q_3: query semua kolom

q_1 = 'SELECT column_name FROM information_schema.columns WHERE table_name = \'{}\' AND data_type LIKE \'char%\' OR data_type LIKE \'text%\''
q_2 = 'SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\''
q_3 = 'SELECT column_name FROM information_schema.columns WHERE table_name = \'{}\''
q_4 = 'SELECT column_name FROM information_schema.columns WHERE table_name = \'{}\' AND data_type = \'USER-DEFINED\''
q_5 = 'SELECT DISTINCT {} FROM {}'

def getRelations(conn):

    cur = conn.cursor()
    cur.execute(q_2)
    result = cur.fetchall()
    cur.close()

    for i in range(0, len(result)):
        result[i] = result[i][0]

    return result

def getColumns(conn, relations):

    result = {}
    columns = []
    for table in relations:
        cur = conn.cursor()
        cur.execute(q_3.format(table))
        result[table] = cur.fetchall()
        for i in range(0, len(result[table])):
            result[table][i] = result[table][i][0]
            columns.append(result[table][i])
        cur.close()

    return columns, result

def getValues(conn, relations):

    values = []
    for table in relations:
        cur = conn.cursor()
        cur.execute(q_1.format(table))
        columns = cur.fetchall()
        for column in columns:
            cur2 = conn.cursor()
            cur2.execute(q_5.format(column[0], table))
            temps = cur2.fetchall()
            for temp in temps:
                values.append(temp[0])
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
            result[table][i] = result[table][i][0]
        cur.close()

    return result

conn = psycopg2.connect(host="localhost", database="geometry", user="postgres", password="1234")
relations = getRelations(conn)
#print(relations)
#fields, result  = getColumns(conn, relations)
#print(fields)
#print(result)
print(getValues(conn, relations))
#cur = conn.cursor()
#cur.execute("SELECT r1.id FROM restoran r1, restoran r2 WHERE ST_Distance(r1.geom, r2.geom) < 500 and r2.id = 1")
#hasil = cur.fetchall()
#print(hasil)
#cur.close()