#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Yoann Sculo <yoann.sculo@gmail.com>'
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '0.1'

import os
import re
import time

from apecbot import ApecBot
from apecbot import Jobboard
from apecbot import Offer
from apecbot import Location

from utilities import *

from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

""" License : http://cadres.apec.fr/delia/core/common/site/ApecViewDetailConseil/currentArticle_ART_46448/Voir+les+conditions+g%C3%A9n%C3%A9rales+d+utilisation.html
"""

class Apec(Jobboard):

    def __init__(self):
        self.name = "APEC"
        self.url = "http://www.apec.fr"
        self.lastFetch = ""
        self.processingDir = self.dlDir + "/apec"
        self.lastFetchDate = 0

    def fetch_url(self, url):
        filename = url.split('/')[-1]
        download_file(url, self.processingDir)

        xmldoc = minidom.parse(os.path.join(self.processingDir, filename))

        MainPubDate = xmldoc.getElementsByTagName('pubDate')[0].firstChild.data
        epochPubDate = datetime.datetime.strptime(MainPubDate, "%a, %d %b %Y %H:%M:%S +0200").strftime('%s')

        # if (epochPubDate <= self.lastFetchDate):
        #     return 0

        itemlist = xmldoc.getElementsByTagName('item')

        for elt in itemlist :
            # TODO : Test object first
            title = elt.getElementsByTagName('title')[0].firstChild.data
            link = elt.getElementsByTagName('link')[0].firstChild.data.split("?")[0]
            pubDate = elt.getElementsByTagName('pubDate')[0].firstChild.data

            if (epochPubDate <= self.lastFetchDate):
                break

            if (not os.path.isfile(os.path.join(self.processingDir, link.split('/')[-1]))):
                print "Downloading %s" % (link)
                download_file(link, self.processingDir)


    def fetch(self):
        print "Fetching " + self.name

        feed_list = ['http://www.apec.fr/fluxRss/XML/OffresCadre_F101833.xml', # informatique
                     'http://www.apec.fr/fluxRss/XML/OffresCadre_F101810.xml', # informatique industrielle
                     'http://www.apec.fr/fluxRss/XML/OffresCadre_F101813.xml'] # système, réseaux, donnée

        for url in feed_list :
            self.fetch_url(url)

        if (not os.path.isdir(self.processingDir)):
                os.makedirs(self.processingDir)


        self.processOffers()

    def processOffers(self):
        for file in os.listdir(self.processingDir):
            if (not file.lower().endswith('.html')):
                    continue

            print "Processing %s" % (file)
            offer = ApecOffer()
            res = offer.loadFromHtml(os.path.join(self.processingDir, file))
            if (res != 0):
                continue
            offer.date_add = int(time.time())
            loc = Location()
            # loc.loadFromAddress(offer.location)
            offer.lat = loc.lat
            offer.lon = loc.lon
            if (offer.add_db() == 0):
                os.remove(os.path.join(self.processingDir,file))

    def setup(self):
        print "setup " + self.name

class ApecOffer(Offer):

    src     = 'APEC'
    license = ''

    def loadFromHtml(self, filename):
        fd = open(filename, 'rb')
        html = fd.read()
        fd.close()

        soup = BeautifulSoup(html, fromEncoding="UTF-8")

        # Offer still available ?
        res = soup.body.find('div', attrs={'class':'boxSingleMain box'})
        if (res != None):
            content = res.find('p')
            if (content.text == u'L\'offre que vous souhaitez afficher n\'est plus disponible.Cliquer sur le bouton ci-dessous pour revenir à l\'onglet Mes Offres'):
                return 1

        # Title
        res = soup.body.find('div', attrs={'class':'boxMain boxOffres box'})
        if (res == None):
            return -1
        res = res.find("h2", attrs={'class':'borderBottom0'})
        self.title = HTMLParser().unescape(res.text)
        matchObj = re.match( ur'Offre d\'emploi (.*)', self.title)
        if matchObj:
            self.title = matchObj.group(1)

        # Other information
        res = soup.body.find('div', attrs={'class':'content1_9ImbLeft'})
        res = res.findAll("tr")

        for elt in res:
            th = elt.find('th')
            td = elt.find('td')
            if (th.text == u'Référence Apec :'):
                self.ref = HTMLParser().unescape(td.text)
            if (th.text == u'Date de publication :'):
                apec_date = HTMLParser().unescape(td.text)
                self.date_pub = datetime.datetime.strptime(apec_date, "%d/%m/%Y").strftime('%s')
            if (th.text == u'Société :'):
                self.company = HTMLParser().unescape(td.text)
                matchObj = re.match( ur'(.*)Voir toutes les offres', self.company)
                if matchObj:
                    self.company = matchObj.group(1)
                matchObj = re.match( ur'(.*)Voir plus d\'infos sur la société', self.company)
                if matchObj:
                    self.company = matchObj.group(1)

            if (th.text == u'Type de contrat :'):
                self.contract = HTMLParser().unescape(td.text)
            if (th.text == u'Lieu :'):
                self.location = HTMLParser().unescape(td.text)
                self.location = re.sub(ur'IDF', "Île-de-France", self.location)
            if (th.text == u'Salaire :'):
                # TODO : use regexp once whe have a better view of possible combinations
                self.salary = HTMLParser().unescape(td.text)
                self.salary = re.sub(ur'Selon diplôme et expérience', "NA", self.salary)
                self.salary = re.sub(ur'fixe + variable selon profil', "NA", self.salary)
                self.salary = re.sub(ur'A définir selon profil', "NA", self.salary)
                self.salary = re.sub(ur'A DEFINIR SELON PROFIL', "NA", self.salary)
                self.salary = re.sub(ur'à défninir selon profil', "NA", self.salary)
                self.salary = re.sub(ur'à définir selon profils', "NA", self.salary)
                self.salary = re.sub(ur'à définir selon expérience', "NA", self.salary)
                self.salary = re.sub(ur'A négocier selon profil', "NA", self.salary)
                self.salary = re.sub(ur'A NEGOCIER SELON PROFIL', "NA", self.salary)
                self.salary = re.sub(ur'à négocier selon profil', "NA", self.salary)
                self.salary = re.sub(ur'A négocier selon expérience', "NA", self.salary)
                self.salary = re.sub(ur'A voir selon profil', "NA", self.salary)
                self.salary = re.sub(ur'En fonction du profil', "NA", self.salary)
                self.salary = re.sub(ur'Selon profil et expériences', "NA", self.salary)
                self.salary = re.sub(ur'Selon profil et expérience', "NA", self.salary)
                self.salary = re.sub(ur'selon profil et expérience +', "NA", self.salary)
                self.salary = re.sub(ur'selon profil et expérience', "NA", self.salary)
                self.salary = re.sub(ur'selon profil et exp', "NA", self.salary)
                self.salary = re.sub(ur'selon profil et avantages', "NA", self.salary)
                self.salary = re.sub(ur'selon votre profil', "NA", self.salary)
                self.salary = re.sub(ur'selon le profil', "NA", self.salary)
                self.salary = re.sub(ur'Selon le profil', "NA", self.salary)
                self.salary = re.sub(ur'Selon profils', "NA", self.salary)
                self.salary = re.sub(ur'Selon profil', "NA", self.salary)
                self.salary = re.sub(ur'selon profil', "NA", self.salary)
                self.salary = re.sub(ur'selon Profil', "NA", self.salary)
                self.salary = re.sub(ur'Selon Profil', "NA", self.salary)
                self.salary = re.sub(ur'SELON PROFIL', "NA", self.salary)
                self.salary = re.sub(ur'selo profil', "NA", self.salary)
                self.salary = re.sub(ur'selon l\'expérience', "NA", self.salary)
                self.salary = re.sub(ur'selon experience', "NA", self.salary)
                self.salary = re.sub(ur'selon expérience', "NA", self.salary)
                self.salary = re.sub(ur'Selon expérience', "NA", self.salary)
                self.salary = re.sub(ur'Selon expérince', "NA", self.salary)
                self.salary = re.sub(ur'Selon Expérience', "NA", self.salary)
                self.salary = re.sub(ur'SELON EXPERIENCE', "NA", self.salary)
                self.salary = re.sub(ur'Selon compétences', "NA", self.salary)
                self.salary = re.sub(ur'Selon compétence', "NA", self.salary)
                self.salary = re.sub(ur'selon exp.', "NA", self.salary)
                self.salary = re.sub(ur'suivant profil', "NA", self.salary)
                self.salary = re.sub(ur'à déterminer', "NA", self.salary)
                self.salary = re.sub(ur'à convenir', "NA", self.salary)
                self.salary = re.sub(ur'à négocier', "NA", self.salary)
                self.salary = re.sub(ur'a négocier', "NA", self.salary)
                self.salary = re.sub(ur'a negocier', "NA", self.salary)
                self.salary = re.sub(ur'à negocier', "NA", self.salary)
                self.salary = re.sub(ur'A négocier', "NA", self.salary)
                self.salary = re.sub(ur'A NEGOCIER', "NA", self.salary)
                self.salary = re.sub(ur'A negocier', "NA", self.salary)
                self.salary = re.sub(ur'à définir', "NA", self.salary)
                self.salary = re.sub(ur'À définir', "NA", self.salary)
                self.salary = re.sub(ur'A définir', "NA", self.salary)
                self.salary = re.sub(ur'A DEFINIR', "NA", self.salary)
                self.salary = re.sub(ur'A discuter', "NA", self.salary)
                self.salary = re.sub(ur'en fonction exp.', "NA", self.salary)
                self.salary = re.sub(ur'Négociable', "NA", self.salary)
                self.salary = re.sub(ur'négociable', "NA", self.salary)
                self.salary = re.sub(ur'negociable', "NA", self.salary)
                self.salary = re.sub(ur'NEGOCIABLE', "NA", self.salary)
                self.salary = re.sub(ur'non indiqué', "NA", self.salary)
                self.salary = re.sub(ur'non communiqué', "NA", self.salary)
                self.salary = re.sub(ur'NON COMMUNIQUE', "NA", self.salary)
                self.salary = re.sub(ur'non précisé', "NA", self.salary)
                self.salary = re.sub(ur'Non précisé', "NA", self.salary)
                self.salary = re.sub(ur'Voir annonce', "NA", self.salary)
                self.salary = re.sub(ur'GRILLE DE LA FPT', "NA", self.salary)
                self.salary = re.sub(ur'Grille', "NA", self.salary)
                self.salary = re.sub(ur'TBD', "NA", self.salary)
                self.salary = re.sub(ur'N.S.', "NA", self.salary)
                self.salary = re.sub(ur'ANNUEL', "NA", self.salary)
                self.salary = re.sub(ur'NC K€ brut/an', "NA", self.salary)
                self.salary = re.sub(ur'xx K€ brut/an', "NA", self.salary)
                # self.salary = re.sub(ur'0K€ brut/an', "NA", self.salary)
                self.salary = re.sub(ur'-K€ brut/an', "NA", self.salary)
            if (th.text == u'Expérience :'):
                self.experience = HTMLParser().unescape(td.text)

        # Content
        res = soup.body.find('div', attrs={'class':'contentWithDashedBorderTop marginTop boxContent'})
        res = res.find('div', attrs={'class':'boxContentInside'})
        self.content = HTMLParser().unescape(res.text);

        self.url = "http://cadres.apec.fr/offres-emploi-cadres/" + os.path.basename(filename)

        return 0
