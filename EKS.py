import json
import re
from bs4 import BeautifulSoup
from urllib import response, request
from pprint import pprint as pp
from configparser import ConfigParser

config = ConfigParser()
config.read("settings.ini")

def scrape(url_id):

    check_url = "https://portal.eks.sk/SpravaZakaziek/Zakazky/Detail/{}".format(url_id)
    read_url = request.urlopen(check_url)
    check_soup = BeautifulSoup(read_url.read(), "html.parser",from_encoding="utf-8")
    r = check_soup.find(id="KlucoveSlova").text
    test2 = check_soup.find(id="Zakazka_Nazov")
    zak_nazov = re.search("value=\"(.*)\s*\"",str(test2)).group(1)

    l = check_soup(id="txbPredpokladanaCenaPlnenia")
    zak_cena = re.search("value=\"([\d]*,\d*)",str(l)).group(1)

    m = check_soup(id="Zakazka_Identifikator")
    zak_id = re.search("value=\"(.*)\"",str(m)).group(1)

    n = check_soup(id="Zakazka_LehotaNaPredkladaniePonuk")
    zak_lehota_ponuky = re.search("value=\"(.*)\"",str(n)).group(1)

    cpv = check_soup(id="cpvData")
    zak_cpv = re.findall("kod\" \:\"(\d{8}-\d+)",str(cpv))

    dataset = {
               "url": check_url,
               "nazov": zak_nazov,
               "ID": zak_id,
               "CPV": zak_cpv,
               "vyska zdrojov": zak_cena,
               "termin ponuky": zak_lehota_ponuky
               }
    #
    with open("text.json","a+", encoding="utf-8") as f:
        json.dump(dataset, f, sort_keys=True, indent=1)

for x in range(49505,49511):
    try:
        scrape(x)
    except AttributeError:
        pass
# soup = BeautifulSoup(open("https://portal.eks.sk/SpravaZakaziek/Zakazky/Detail/49503"))
#print(check_soup.prettify())

