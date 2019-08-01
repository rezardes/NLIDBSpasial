'''from bs4 import BeautifulSoup

import requests

url = "https://kamuslengkap.com/kamus/sinonim/arti-kata/waktu"

r  = requests.get(url)

data = r.text

soup = BeautifulSoup(data, features="html.parser")

divs = soup.find('div', {'class': 'entry-content'})
children = divs.findChildren("dd" , recursive=True)
#print(divs)
print(children[0])
#for child in children:
#    print(child)

#mydivs = soup.findAll("div", {"class": "entry-content"})
#children = mydivs.findChildren("dd" , recursive=False)
#print(children)'''

sinonim = "1 n durasi, era, jangka, janji, kala, kali, kurun, masa, periode, saat, sangkala, tempo, tenggat, termin, zaman; 2 n ajal, batas, batas hidup, giliran, had, keadaan, kejadian, kelapangan, kesempatan, peluang, suasana;"
for syn in sinonim.split(','):
    print(syn)

# Yang pertama selalu yang ketiga
