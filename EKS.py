import re
from bs4 import BeautifulSoup
from urllib import response, request

url_id = 49503

check_url = "https://portal.eks.sk/SpravaZakaziek/Zakazky/Detail/{}".format(url_id)

read_url = request.urlopen(check_url)

check_soup = BeautifulSoup(read_url.read(), "html.parser",from_encoding="utf-8")


r = check_soup.find(id="KlucoveSlova").text

test = "<input class=\"form-control\" id=\"Zakazka_Nazov\" name=\"Zakazka.Nazov\" value=\"toner Yellow do tlačiarne CLI 521 alebo ekvivalent \"/>"

test2 = check_soup.find(id="Zakazka_Nazov")

zak_nazov = re.search("value=\"(.*)\s\"",str(test2)).group(1)

l = check_soup(id="txbPredpokladanaCenaPlnenia")
zak_cena = re.search("value=\"([\d]*,\d*)",str(l)).group(1)

m = check_soup(id="Zakazka_Identifikator")
zak_id = re.search("value=\"(.*)\"",str(m)).group(1)

n = check_soup(id="Zakazka_LehotaNaPredkladaniePonuk")
zak_lehota_ponuky = re.search("value=\"(.*)\"",str(n)).group(1)


dataset = {
           "url": check_url,
           "nazov": zak_nazov,
           "ID": zak_id,
           "vyska zdrojov": zak_cena,
           "termin ponuky": zak_lehota_ponuky
           }
#
print(dataset)
# soup = BeautifulSoup(open("https://portal.eks.sk/SpravaZakaziek/Zakazky/Detail/49503"))
#print(check_soup.prettify())

