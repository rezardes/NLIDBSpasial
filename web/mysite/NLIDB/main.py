import re
import sys
import itertools
import psycopg2

import sys
sys.path.insert(0, "D:\\My Documents\\Kuliah\\Tugas Akhir\\Experiment\\NLIDBSpasial\\web\\mysite")

from NLIDB.connector import getMetadata
from NLIDB.parsing import parse
from NLIDB.translator import convertToSQL

# Tunjukkan posisi wifi Mifi M5 ketika jam 13:00!

# relation tidak apa-apa duplikat
print("Masukkan query: ", end='')
sentence = input()
metadata, synSet = getMetadata('sample2', True)
#parsing = parse('Tunjukkan', metadata)
#parsing = parse('Tunjukkan irisan jangkauan wifi Mifi M5 dan jangkauan wifi Huawei e5577 ketika jam 13:00!', metadata)
parsing = parse('Tunjukkan jarak antara wifi Mifi M5 dengan wifi Huawei e5577 ketika jam 13:00!', metadata)
#parsing = parse('Tampilkan luas area Yagami Ramen dalam satuan meter persegi!', metadata)
#parsing = parse('Tampilkan absis dan ordinat posisi wifi Mifi yang ada di area Mall Metropolitan ketika jam 13:00 M5 ketika jam 13:00!', metadata)
#parsing = parse('Tampilkan seluruh nama wifi yang ada di jalan Ir. H. Juanda ketika jam 14:00!', metadata)\
#parsing = parse('Tampilkan bagian area Yagami Ramen yang terkena jangkauan wifi Mifi M5 pada jam 13:00!')
# KENAPA ERROR? 'ada pada'
#parsing = parse('Tunjukkan seluruh posisi wifi yang ada di area Mall Metropolitan ketika jam 13:00!', metadata)
query, headers = convertToSQL(parsing, metadata, synSet)
print(query)