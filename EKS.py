import json
import re
import os

from bs4 import BeautifulSoup
from urllib import response, request
from pprint import pprint as pp
from configparser import ConfigParser
from time import sleep

config = ConfigParser()
config.read("settings.ini")

try:
    with open('list.json') as f:
        file_list = json.load(f)
except IOError:
    for (dirpath, dirnames, filenames) in os.walk('/home/th/projects/EKS/Data'):
        file_list = []
        file_list.extend(filenames)
        break


def scrape(url_id):

    check_url = "https://portal.eks.sk/SpravaZakaziek/Zakazky/Detail/{}".format(url_id)
    read_url = request.urlopen(check_url)
    check_soup = BeautifulSoup(read_url.read(), "html.parser",from_encoding="utf-8")
    r = check_soup.find(id="KlucoveSlova").text
    test2 = check_soup.find(id="Zakazka_Nazov")
    zak_nazov = re.search("value=\"(.*)\s*\"",str(test2)).group(1)

    l = check_soup(id="txbPredpokladanaCenaPlnenia")
    zak_cena = re.search("value=\"([\d]+),\d{2}",str(l)).group(1)

    m = check_soup(id="Zakazka_Identifikator")
    zak_id = re.search("value=\"(.*)\"",str(m)).group(1)

    n = check_soup(id="Zakazka_LehotaNaPredkladaniePonuk")
    zak_lehota_ponuky = re.search("value=\"(.*)\"",str(n)).group(1)

    CPV = check_soup(id="cpvData")
    zak_CPV = re.findall("kod\" \:\"(\d{8}-\d+)",str(CPV))
    CPV_2digs = re.findall("kod\" \:\"(\d{2})",str(CPV))
    dataset = {url_id:{
               "Show": False,
               "details": {
                           "url": check_url,
                           "nazov": zak_nazov,
                           "CPV": zak_CPV,
                           "vyska zdrojov": zak_cena,
                           "termin ponuky": zak_lehota_ponuky
                           }}}

    intersect = []
    for item in config['DEFAULT']['CPV_starts_with'].split(','):        # match CPV
        for member in CPV_2digs:
            if item == member:
                intersect.append(item)
    # print(int(zak_cena), int(config['DEFAULT']['zak_cena']),(int(zak_cena) > int(config['DEFAULT']['zak_cena'])))
    # print(intersect)
    if int(zak_cena) > int(config['DEFAULT']['zak_cena']) and len(intersect)>0:
        dataset[url_id]['Show'] = True
        with open("Data/{}".format(url_id), "w+", encoding="utf-8") as f:
            json.dump(dataset, f, sort_keys=True, indent=0)



for x in range(max(file_list)+1, max(file_list)+10):
    try:
        print("Extracting data for ID: {}".format(x))
        scrape(x)
        sleep(10)
        file_list.insert(0, x)
    except AttributeError:
        print("Funkcia pre ID {} zlyhala".format(x))
        pass
        sleep(10)
    with open("list.json", "w+") as y:
        json.dump(file_list, y)
# soup = BeautifulSoup(open("https://portal.eks.sk/SpravaZakaziek/Zakazky/Detail/49503"))

