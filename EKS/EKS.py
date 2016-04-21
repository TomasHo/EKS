import json
import re
import os, sys
import logging

os.chdir('/home/pi/Documents/PythonProjects/')

from EKS import smtp
from datetime import datetime
from bs4 import BeautifulSoup
from urllib import request
from configparser import ConfigParser
from time import sleep


assert sys.version_info.major >= 3
if not os.path.isdir('EKS/Data'): os.mkdir('EKS/Data')
if not os.path.isdir('EKS/Data_processed'): os.mkdir('EKS/Data_processed')
#logging.basicConfig(filename='EKS/eks.log', level=logging.DEBUG)
logging.info(str(datetime.now()) + ' : eks.log test write')
try:
    if os.stat('EKS/eks.log').st_size > 2000000: os.rename('EKS/eks.log', 'EKS/eks.old')
except FileNotFoundError:
    pass
config = ConfigParser()
config.read("EKS/settings.ini")

try:
    with open('EKS/list.json') as file:
        file_list = json.load(file)
except IOError:
    for (dirpath, dirnames, filenames) in os.walk('EKS/Data'):
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
        with open("EKS/Data/{}".format(url_id), "w+", encoding="utf-8") as f:
            json.dump(dataset, f, sort_keys=True, indent=0)


def run(num):
    for x in range(max(file_list)-10, max(file_list)+num):
        try:
            logging.info(str(datetime.now()) + ' : ' + "Extracting data for ID: {}\n".format(x))
            if x not in file_list:
                scrape(x)
                file_list.insert(0, x)
                logging.info(str(datetime.now()) + ' : ' + "Inserting data to list.json: {}\n".format(x))
            else:
                logging.info(str(datetime.now()) + ' : ' + "{} uz spracovane\n".format(x))
        except AttributeError:
            logging.info(str(datetime.now()) + ' : ' + "Funkcia pre ID {} zlyhala\n".format(x))
            pass
        with open("EKS/list.json", "w+") as y:
            json.dump(file_list, y)
            sleep(20)
    while os.listdir('EKS/Data'):
        sleep(3)
        item = min(os.listdir('EKS/Data'))
        logging.info(str(datetime.now()) + ' :  sending file(s)\n' + str(item))
        try:
            smtp.send_mail()
        except [TimeoutError, ConnectionError, ConnectionRefusedError]:
            logging.info(str(datetime.now()) + ' : something went wrong\n')
            break
        os.rename('EKS/Data/'+item, 'EKS/Data_processed/'+item)
        logging.info(str(datetime.now()) + ' : '+item+' processed\n')

run(int(sys.argv[1]))

