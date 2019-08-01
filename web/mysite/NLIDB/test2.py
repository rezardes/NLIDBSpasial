import psycopg2
import json

#query = 'SELECT ST_AsGeoJSON(geom) FROM area'
#query = "SELECT DISTINCT kelurahan, kecamatan FROM area"
#query = 'SELECT DISTINCT nama, ST_AsGeoJSON(geom) FROM area'
#query = 
conn = psycopg2.connect(host="localhost", database="sample2", user="postgres", password="1234")
cur = conn.cursor()
cur.execute(query)
answers = cur.fetchall()

context = {}
context['data'] = []
isGeom = 'st_asgeojson' in query.lower()

for answer in answers:

    temp = {}
    if (isGeom):
        temp = {"type": [], "text": [], "coordinates": [] }
    else:
        temp = {"type": "text", "text": [] }
    for ans in answer:
        if ("{\"type\":" in ans):
            ans = json.loads(ans)
            temp['type'].append(ans['type'])
            temp['coordinates'].append(ans['coordinates'])
        else:
            temp["text"].append(ans)

    context['data'].append(temp)

print(context)
        

        

    

    
    
#print(context["data"])
'''json_string = hasil[0][0]
obj = json.loads(json_string)
print(obj['coordinates'])'''
cur.close()