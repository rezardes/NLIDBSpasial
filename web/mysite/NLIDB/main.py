import re
import sys
import itertools
import psycopg2

import sys
sys.path.insert(0, "D:\\My Documents\\Kuliah\\Tugas Akhir\\Experiment\\NLIDBSpasial\\web\\mysite")
#sys.path.insert(0, "/home/rezardes/Documents/Programming/Python/NLIDBSpasial/web/mysite")

#print(sys.path)

from NLIDB.connector import getMetadata
from NLIDB.parsing import parse
from NLIDB.translator import convertToSQL

# Tunjukkan posisi wifi Mifi M5 ketika jam 13:00!

# relation tidak apa-apa duplikat
#print("Masukkan query: ", end='')
#sentence = input()
metadata, synSet = getMetadata('pemda', True)
#metadata = []
#synSet = {'nama': 'nama', 'alamat':'alamat', 'kota': 'kota', 'posisi': 'posisi', 'populasi': 'populasi'}
#parsing = parse('Tampilkan jarak posisi wifi Connex!', metadata)
#parsing = parse('Tampilkan jarak posisi wifi Connex dengan posisi wifi Yagami Ramen!', metadata)
#parsing = parse('Tunjukkan seluruh kota yang jaraknya dengan kota Bandung kurang dari 1000 kilometer!', metadata)
parsing = parse('Tampilkan nama dan luas setiap provinsi yang bersebelahan dengan provinsi Jawa Barat atau bersebelahan dengan provinsi Jawa Timur!', metadata)
#parsing = parse('Tampilkan koordinat posisi wifi Connex!', metadata)
#parsing = parse('Tampilkan irisan jangkauan wifi Connex dengan jangkauan wifi Yagami Ramen!', metadata)
#parsing = parse('Tampilkan panjang jalan Ir. H. Juanda!', metadata)
#parsing = parse('Tampilkan area yang beririsan dengan jangkauan wifi Connex!', metadata)
#parsing = parse('Tampilkan luas area Yagami Ramen!', metadata)
#parsing = parse('Tampilkan keliling area Yagami Ramen!', metadata)
#parsing = parse('Tampilkan seluruh posisi wifi yang ada di dalam area Mall Metropolitan!', metadata)
#parsing = parse('Tampilkan provinsi yang bersebelahan dengan provinsi Jawa Barat dan Jawa Timur!', metadata)
#parsing = parse('Tampilkan area Yagami Ramen dan area Dago Butik!', metadata)
#parsing = parse('Tampilkan area Yagami Ramen, area Dago Butik, dan area Mall Metropolitan!', metadata)
#parsing = parse('Tunjukkan area Yagami Ramen, area yang terjangkau wifi Connex, dan area Mall Metropolitan!', metadata)
print(metadata)
#parsing = parse('Tunjukkan provinsi yang ada di sebelah provinsi Jawa Barat dan di sebelah provinsi Jawa Timur!', metadata)

#parsing = parse('Tunjukkan', metadata)
#parsing = parse('Tunjukkan irisan jangkauan wifi Mifi M5 dan jangkauan wifi Huawei e5577 ketika jam 13:00!', metadata)
#parsing = parse('Tunjukkan jarak antara wifi Mifi M5 dengan wifi Huawei e5577 ketika jam 13:00!', metadata)
#parsing = parse('Tampilkan luas area Yagami Ramen dalam satuan meter persegi!', metadata)
#parsing = parse('Tampilkan absis dan ordinat posisi wifi Mifi yang ada di area Mall Metropolitan ketika jam 13:00 M5 ketika jam 13:00!', metadata)
#parsing = parse('Tampilkan seluruh nama wifi yang ada di jalan Ir. H. Juanda ketika jam 14:00!', metadata)\
#parsing = parse('Tampilkan bagian area Yagami Ramen yang terkena jangkauan wifi Mifi M5 pada jam 13:00!')
# KENAPA ERROR? 'ada pada'
#parsing = parse('Tunjukkan seluruh posisi wifi yang ada di area Mall Metropolitan ketika jam 13:00!', metadata)
query, headers = convertToSQL(parsing, metadata, synSet)
print(query)