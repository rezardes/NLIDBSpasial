from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from NLIDB import parsing, connector

from django.views.decorators.csrf import csrf_exempt

import psycopg2
import json

@csrf_exempt
def index(request):

    context = {}
    return render(request, 'index.html', context)

@csrf_exempt
def parse(request):

    metadata = None
    parse = ""
    if request.method == 'POST':
        #print("in")
        query = request.POST.get("query", "")
        database = request.POST.get("database", "")
        isLoad = request.POST.get("isLoad", False)
        '''if (isLoad):
            metadata = connector.getMetadata(database, True)
            parse = parsing.parse(query, metadata)
        else:
            metadata = connector.getMetadata(database, False)
            parse = parsing.parse(query, metadata)'''

    query = 'SELECT DISTINCT nama, ST_AsGeoJSON(geom) FROM area'
    conn = psycopg2.connect(host="localhost", database="sample2", user="postgres", password="1234")
    cur = conn.cursor()
    cur.execute(query)
    answers = cur.fetchall()
    print("answers", answers)

    data = {}
    data['data'] = []
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

        data['data'].append(temp)

    '''data = {}
    data['data'] = []
    for subhasil in hasil:'''
        
    
    #print(obj)
    #print(obj['coordinates'])
    print(data)
    cur.close()
    
    return JsonResponse(data)
    #return JsonResponse({'type': obj['type'], 'coordinates': obj['coordinates']})
    #return JsonResponse(data)