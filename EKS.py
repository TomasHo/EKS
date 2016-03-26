import json
import re
import os, sys, smtp

from datetime import datetime
from bs4 import BeautifulSoup
from urllib import request
from configparser import ConfigParser
from time import sleep

assert sys.version_info.major >= 3

config = ConfigParser()
config.read("settings.ini")

try:
    with open('list.json') as file:
        file_list = json.load(file)
except IOError:
    for (dirpath, dirnames, filenames) in os.walk('Data'):
        file_list = []
        file_list.extend(filenames)
        break


def scrape(url_id):

    check_url = "https://portal.eks.sk/SpravaZakaziek/Zakazky/Detail/{}".format(url_id)
    read_url = request.urlopen(check_url)
    check_soup = BeautifulSoup(read_url.read(), "html.parser", from_encoding="utf-8")
    test2 = check_soup.find(id="Zakazka_Nazov")
    zak_nazov = re.search("value=\"(.*)\s*\"", str(test2)).group(1)

    l = check_soup(id="txbPredpokladanaCenaPlnenia")
    zak_cena = re.search("value=\"([\d]+),\d{2}", str(l)).group(1)

    m = check_soup(id="Zakazka_Identifikator")
    zak_id = re.search("value=\"(.*)\"", str(m)).group(1)

    n = check_soup(id="Zakazka_LehotaNaPredkladaniePonuk")
    zak_lehota_ponuky = re.search("value=\"(.*)\"", str(n)).group(1)

    CPV = check_soup(id="cpvData")
    zak_CPV = re.findall("kod\" \:\"(\d{8}-\d+)", str(CPV))
    CPV_2digs = re.findall("kod\" \:\"(\d{2})", str(CPV))
    dataset = {url_id:{
               "Show": False,
               "details": {
                           "ID_zakazky": zak_id,
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

    if int(zak_cena) > int(config['DEFAULT']['zak_cena']) and len(intersect) > 0:
        dataset[url_id]['Show'] = True
        with open("Data/{}".format(url_id), "w+", encoding="utf-8") as f:
            json.dump(dataset, f, sort_keys=True, indent=0)


def run():
    log_file = open('eks.log', 'a+')
    for x in range(max(file_list)-2, max(file_list)+2):
        try:
            log_file.write(str(datetime.now()) + ' : ' + "Extracting data for ID: {}\n".format(x))
            if x not in file_list:
                scrape(x)
                file_list.insert(0, x)
                log_file.write(str(datetime.now()) + ' : ' + "Inserting data to list.json: {}\n".format(x))
            else:
                log_file.write(str(datetime.now()) + ' : ' + "{} uz spracovane\n".format(x))
        except AttributeError:
            log_file.write(str(datetime.now()) + ' : ' + "Funkcia pre ID {} zlyhala\n".format(x))
            pass
        with open("list.json", "w+") as y:
            json.dump(file_list, y)
        sleep(10)
    while os.listdir('Data'):
        #sleep(3)
        smtp.send_mail()
        item = min(os.listdir('Data'))
        os.rename('Data/'+item, 'Data_processed/'+item)
        log_file.write(str(datetime.now()) + ' : '+item+' processed\n')

    smtp.smtpserver.close()
    log_file.close()
