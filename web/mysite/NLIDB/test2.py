import psycopg2
import json

#query = 'SELECT ST_AsGeoJSON(geom) FROM area'
#query = "SELECT DISTINCT kelurahan, kecamatan FROM area"
#query = 'SELECT DISTINCT nama, ST_AsGeoJSON(geom) FROM area'
query = '''SELECT r1.jangkauan, ST_AsGeoJSON(r3.posisi)
FROM wifi r1, posisi_wifi r2, posisi r3
WHERE r1.id = r2.id_wifi AND r2.id_posisi = r3.id AND lower(r1.nama) = 'mifi m5' AND r2.waktu = '13:00'
'''

conn = psycopg2.connect(host="localhost", database="sample2", user="postgres", password="1234")
cur = conn.cursor()
cur.execute(query)
answers = cur.fetchall()

context = {}
context['data'] = []
#isGeom = 'st_asgeojson' in query.lower()
isCircle = True
headers = ['~radCircle', '~pointCircle']

#! Bagaimana dengan looping agar masing2 sinkron (coordinates tidak di indeks yang salah)
#! Jangan lupa bahwa menampilkan koordinat titik lingkarannya memperhatikan SRID
for answer in answers:

    temp = {}
    #if (isGeom):
    temp = {"type": [], "value": [], "coordinates": [], "headers": [] }
    temp["headers"] = headers
    #else:
    #    temp = {"type": "text", "text": [], "headers": [] }
    
    for index, ans in enumerate(answer):
        if (headers[index].startswith("~") and "Circle" in headers[index]):
            if (headers[index]=="~radCircle"):
                temp["type"].append("radCircle")
                temp["value"].append(ans)
                temp['coordinates'].append([])
            elif (headers[index]=="~pointCircle"):
                temp["type"].append("pointCircle")
                temp["value"].append("")
                print("ans", ans)
                ans = json.loads(ans)
                temp['coordinates'].append(ans['coordinates'])
            
        elif ("{\"type\":" in ans):
            ans = json.loads(ans)
            temp['type'].append(ans['type'])
            temp['coordinates'].append(ans['coordinates'])
            temp["value"].append("")
        else:
            temp["type"].append("text")
            temp["value"].append(ans)
            temp['coordinates'].append([])

    context['data'].append(temp)

print(context)
        

        

    

    
    
#print(context["data"])
'''json_string = hasil[0][0]
obj = json.loads(json_string)
print(obj['coordinates'])'''
cur.close()