#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
]
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '1.0'

# System
import os
import re
import time
import glob
import hashlib
import importlib
import html2text
import sqlite3 as lite
import requests


from collections import namedtuple
PageResult = namedtuple('PageResult', ['url', 'page'])


def htmltotext(text):
    """Fix html2text"""
    html2text.BODY_WIDTH = 0
    return html2text.html2text(text)


def md5(datas):
    """Calc md5sum string datas"""
    return hashlib.md5(datas).hexdigest()


def getModificationFile(filename):
    """ Get a modification file (in timestamp)"""
    t = None

    try:
        t = os.path.getmtime(filename)
    except:
        pass

    return t


def getNow():
    """Get now timestamp"""
    return time.time()


def openPage(filename):
    fd = open(filename, 'rb')
    url = fd.readline()
    html = fd.read()
    fd.close()

    return PageResult(url=url, page=html)


def downloadFile(url, datas, filename, age=60, forcedownload=False):
    headers = {
        'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
        'Referer': 'http://candidat.pole-emploi.fr/candidat/rechercheoffres/avancee',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #'Content-Type': 'application/json',
    }

    # Check if i must download file
    if os.path.isfile(filename):
        now = getNow()
        t = getModificationFile(filename)
        if not forcedownload or t + (age) < now:
            return

    print "Download %s" % url
    destdir = os.path.dirname(filename)
    if (not os.path.isdir(destdir)):
        os.makedirs(destdir)

    if datas:
        r = requests.post(url, data=datas, headers=headers)
    else:
        r = requests.get(url)
    out = open(filename, 'wb')
    out.write("%s\n" % url)
    out.write(r.content)
    out.close()


def removeFiles(rep, patern):
    filelist = glob.glob("%s/%s" % (rep, patern))

    for f in filelist:
        os.remove(f)


def loadJobBoard(jobboardname, configs):
    """Load Jobboard plugin"""
    module = importlib.import_module(
        'jobboards.%s' % jobboardname
    )
    moduleClass = getattr(module, "JB%s" % jobboardname)
    return moduleClass(configs)


def db_checkandcreate(configs):
    """Check and create offers table"""
    if not db_istableexists(configs, 'offers'):
        db_create(configs)


def db_istableexists(configs, tablename):
    """Check if tablename exist"""
    conn = lite.connect(configs['global']['database'])
    cursor = conn.cursor()
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % tablename
    cursor.execute(sql)
    return len(cursor.fetchall()) == 1


def db_create(configs):
    """Create the offers table"""
    conn = None
    conn = lite.connect(configs['global']['database'])
    cursor = conn.cursor()

    # create a table
    cursor.execute("""CREATE TABLE offers( \
                        source TEXT, \
                        ref TEXT, \
                        date_pub INTEGER, \
                        date_add INTEGER, \
                        title TEXT, \
                        company TEXT, \
                        contract TEXT, \
                        location TEXT, \
                        lat TEXT, \
                        lon TEXT, \
                        salary TEXT, \
                        url TEXT, \
                        content TEXT, \
                        PRIMARY KEY(source, ref))""")
    cursor.execute("""CREATE TABLE blacklist(company TEXT, PRIMARY KEY(company))""")


def db_delete_jobboard_datas(configs, jobboardname):
    """Delete jobboard datas from offers table"""
    conn = None
    conn = lite.connect(configs['global']['database'])
    cursor = conn.cursor()

    # create a table
    sql = "delete from offers where source='%s'" % jobboardname
    print sql
    cursor.execute("delete from offers where source='%s'" % jobboardname)
    conn.commit()


def db_add_offer(configs, offer):
    conn = lite.connect(configs['global']['database'])
    try:
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute("INSERT INTO offers VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (
                           offer.src, offer.ref,
                           offer.date_pub, offer.date_add,
                           offer.title, offer.company, offer.contract,
                           offer.location, offer.lat, offer.lon,
                           offer.salary, offer.url, offer.content
                       )
        )
        conn.commit()
        return 0

    except lite.Error, e:
        """ TODO : Waiting for this ... http://bugs.python.org/issue16379
                lite.errorcode.get(e.sqlite_errorcode)
            USE pip
            In the meantime, let's do something realy dirty. let's catch errors
            by string ! ugh
        """
        if (e.args[0] == "columns source, ref are not unique"):
            return 0
        else:
            return 1
    finally:
        if conn:
            conn.close()


def blacklist_flush(configs):
    conn = lite.connect(configs['global']['database'])
    cursor = conn.cursor()
    sql = "DELETE FROM blacklist"
    cursor.execute(sql)
    conn.commit()
    conn.close()


def blocklist_load(configs):
    fp = open('blacklist_company.txt', 'r')
    list = []
    for line in fp:
        company = unicode(line.rstrip('\n'))
        list.append([company])

    try:
        conn = lite.connect(configs['global']['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO blacklist VALUES(?)", list)
        conn.commit()

    except lite.Error, e:
        print "Error %s:" % e.args[0]

    finally:
        if conn:
            conn.close()


def filter_contract_fr(contract):
    contract = re.sub(ur'Perm', "CDI", contract)
    contract = re.sub(ur'[0-9]+ en (.*)', "\\1", contract, flags=re.DOTALL)
    contract = re.sub(ur'.*CDI.*', "CDI", contract, flags=re.DOTALL)
    contract = re.sub(
        ur'.*CDD.*de (.*)',
        "CDD de \\1",
        contract, flags=re.DOTALL
    )

    # PoleEmploi
    contract = re.sub(ur'.*Contrat à durée indéterminée.*', "CDI", contract, flags=re.DOTALL)
    contract = re.sub(ur'.*Contrat à durée déterminée de.*', "CDD", contract, flags=re.DOTALL)
    contract = re.sub(ur'.*Contrat travail saisonnier de.*', "CDD", contract, flags=re.DOTALL)


    return contract


def filter_location_fr(location):
    location = re.sub(ur'IDF', "Île-de-France", location)
    return location


def filter_salary_fr(salary):
    # TODO : use regexp once whe have a better view of possible combinations
    # TODO : use something similar as ^...$
    salary = re.sub(ur'Selon diplôme et expérience', "NA", salary)
    salary = re.sub(ur'fixe + variable selon profil', "NA", salary)
    salary = re.sub(ur'Fixe+Variable selon profil', "NA", salary)
    salary = re.sub(ur'Fixe + Variable selon profil', "NA", salary)
    salary = re.sub(ur'A définir selon profil', "NA", salary)
    salary = re.sub(ur'A DEFINIR SELON PROFIL', "NA", salary)
    salary = re.sub(ur'à défninir selon profil', "NA", salary)
    salary = re.sub(ur'à définir selon profils', "NA", salary)
    salary = re.sub(ur'à définir selon expérience', "NA", salary)
    salary = re.sub(ur'A négocier selon profil', "NA", salary)
    salary = re.sub(ur'A NEGOCIER SELON PROFIL', "NA", salary)
    salary = re.sub(ur'à négocier selon profil', "NA", salary)
    salary = re.sub(ur'à négocier selon le profil', "NA", salary)
    salary = re.sub(ur'à déterminer selon profil', "NA", salary)
    salary = re.sub(ur'A négocier selon expérience', "NA", salary)
    salary = re.sub(ur'à négocier selon expérience', "NA", salary)
    salary = re.sub(ur'à négocier selon exp', "NA", salary)
    salary = re.sub(ur'à negocier K€ brut/an', "NA", salary)
    salary = re.sub(ur'A voir selon profil', "NA", salary)
    salary = re.sub(ur'Attractive et selon profil', "NA", salary)
    salary = re.sub(ur'De débutant à confirmé', "NA", salary)
    salary = re.sub(ur'En fonction du profil', "NA", salary)
    salary = re.sub(ur'en fonction du profil', "NA", salary)
    salary = re.sub(ur'En fonction de votre profil', "NA", salary)
    salary = re.sub(ur'Fonction profil et expérience', "NA", salary)
    salary = re.sub(ur'Selon profil/expérience', "NA", salary)
    salary = re.sub(ur'Selon profil et expériences', "NA", salary)
    salary = re.sub(ur'Selon profil et expérience', "NA", salary)
    salary = re.sub(ur'selon profil et expérience +', "NA", salary)
    salary = re.sub(ur'selon niveau d\'expérience', "NA", salary)
    salary = re.sub(ur'selon profil et expérience', "NA", salary)
    salary = re.sub(ur'selon profil et exp', "NA", salary)
    salary = re.sub(ur'selon profil et avantages', "NA", salary)
    salary = re.sub(ur'Selon formation et/ou exp.', "NA", salary)
    salary = re.sub(ur'selon votre profil', "NA", salary)
    salary = re.sub(ur'Selon votre profil', "NA", salary)
    salary = re.sub(ur'selon le profil', "NA", salary)
    salary = re.sub(ur'Selon le profil', "NA", salary)
    salary = re.sub(ur'Selon profils', "NA", salary)
    salary = re.sub(ur'Selon profile', "NA", salary)
    salary = re.sub(ur'Selon profil', "NA", salary)
    salary = re.sub(ur'selon profil', "NA", salary)
    salary = re.sub(ur'selon Profil', "NA", salary)
    salary = re.sub(ur'Selon Profil', "NA", salary)
    salary = re.sub(ur'SELON PROFILS', "NA", salary)
    salary = re.sub(ur'SELON PROFIL', "NA", salary)
    salary = re.sub(ur'selo profil', "NA", salary)
    salary = re.sub(ur'Suivant profil', "NA", salary)
    salary = re.sub(ur'selon l\'expérience', "NA", salary)
    salary = re.sub(ur'selon experience', "NA", salary)
    salary = re.sub(ur'selon expérience', "NA", salary)
    salary = re.sub(ur'Selon expérience', "NA", salary)
    salary = re.sub(ur'Selon expérince', "NA", salary)
    salary = re.sub(ur'Selon Expérience', "NA", salary)
    salary = re.sub(ur'Selon experience', "NA", salary)
    salary = re.sub(ur'SELON EXPERIENCE', "NA", salary)
    salary = re.sub(ur'Selon compétences', "NA", salary)
    salary = re.sub(ur'Selon compétence', "NA", salary)
    salary = re.sub(ur'selon exp.', "NA", salary)
    salary = re.sub(ur'Selon exp.', "NA", salary)
    salary = re.sub(ur'selon exp', "NA", salary)
    salary = re.sub(ur'selon grille', "NA", salary)
    salary = re.sub(ur'selon grilles', "NA", salary)
    salary = re.sub(ur'cf. annonce', "NA", salary)
    salary = re.sub(ur'suivant profil', "NA", salary)
    salary = re.sub(ur'fixe + variable', "NA", salary)
    salary = re.sub(ur'grille fonction publique', "NA", salary)
    salary = re.sub(ur'Contrat Apprentissage', "NA", salary)
    salary = re.sub(ur'Salaire Attractif', "NA", salary)
    salary = re.sub(ur'Salaire à négocier', "NA", salary)
    salary = re.sub(ur'à déterminer', "NA", salary)
    salary = re.sub(ur'A déterminer', "NA", salary)
    salary = re.sub(ur'à convenir', "NA", salary)
    salary = re.sub(ur'A convenir', "NA", salary)
    salary = re.sub(ur'à débattre', "NA", salary)
    salary = re.sub(ur'à négocier', "NA", salary)
    salary = re.sub(ur'a négocier', "NA", salary)
    salary = re.sub(ur'a negocier', "NA", salary)
    salary = re.sub(ur'à negocier', "NA", salary)
    salary = re.sub(ur'A négocier', "NA", salary)
    salary = re.sub(ur'A NEGOCIER', "NA", salary)
    salary = re.sub(ur'A negocier', "NA", salary)
    salary = re.sub(ur'à définir', "NA", salary)
    salary = re.sub(ur'à défiinir', "NA", salary)
    salary = re.sub(ur'À définir', "NA", salary)
    salary = re.sub(ur'A définir', "NA", salary)
    salary = re.sub(ur'A DEFINIR', "NA", salary)
    salary = re.sub(ur'A DETERMINER', "NA", salary)
    salary = re.sub(ur'à determiner', "NA", salary)
    salary = re.sub(ur'A definir', "NA", salary)
    salary = re.sub(ur'A défnir', "NA", salary)
    salary = re.sub(ur'A discuter', "NA", salary)
    salary = re.sub(ur'à préciser', "NA", salary)
    salary = re.sub(ur'en fonction exp.', "NA", salary)
    salary = re.sub(ur'Negotiable', "NA", salary)
    salary = re.sub(ur'negotiable', "NA", salary)
    salary = re.sub(ur'Négociable', "NA", salary)
    salary = re.sub(ur'négociable', "NA", salary)
    salary = re.sub(ur'negociable', "NA", salary)
    salary = re.sub(ur'NEGOCIABLE', "NA", salary)
    salary = re.sub(ur'non indiqué', "NA", salary)
    salary = re.sub(ur'non communiqué', "NA", salary)
    salary = re.sub(ur'NON COMMUNIQUE', "NA", salary)
    salary = re.sub(ur'non précisé', "NA", salary)
    salary = re.sub(ur'Non précisé', "NA", salary)
    salary = re.sub(ur'Voir annonce', "NA", salary)
    salary = re.sub(ur'GRILLE DE LA FPT', "NA", salary)
    salary = re.sub(ur'Grille', "NA", salary)
    salary = re.sub(ur'variable', "NA", salary)
    salary = re.sub(ur'confidentiel', "NA", salary)
    salary = re.sub(ur'TBD', "NA", salary)
    salary = re.sub(ur'N.S.', "NA", salary)
    salary = re.sub(ur'ANNUEL', "NA", salary)
    salary = re.sub(ur'NC K€ brut/an', "NA", salary)
    salary = re.sub(ur'xx K€ brut/an', "NA", salary)
    # salary = re.sub(ur'0K€ brut/an', "NA", salary)
    salary = re.sub(ur'--K€ brut/an', "NA", salary)
    salary = re.sub(ur'- K€ brut/an', "NA", salary)
    salary = re.sub(ur'-K€ brut/an', "NA", salary)
    salary = re.sub(ur'XK€ brut/an', "NA", salary)
    salary = re.sub(ur'N/C', "NA", salary)
    salary = re.sub(ur'N.C', "NA", salary)
    salary = re.sub(ur'NC', "NA", salary)
    salary = re.sub(ur'nc', "NA", salary)



    return salary
