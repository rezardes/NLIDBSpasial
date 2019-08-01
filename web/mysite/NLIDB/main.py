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

metadata, synSet = getMetadata('sample2', True)
parsing = parse('Tunjukkan jangkauan wifi Mifi M5 ketika jam 13:00!', metadata)
query = convertToSQL(parsing, metadata, synSet)
print(query)