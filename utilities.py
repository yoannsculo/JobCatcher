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
import fnmatch
import importlib
import html2text
import sqlite3 as lite
import requests

# Class for terminal Color
class tcolor:
    DEFAULT = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[96m"
    ORANGE = "\033[93m"
    MAGENTA = "\033[95m"
    RESET = "\033[2J\033[H"
    BELL = "\a"

from collections import namedtuple
PageResult = namedtuple(
    'PageResult',
    [
        'version',
        'statuscode',
        'pageid',
        'url',
        'content'
    ]
)

DownloadResult = namedtuple('DownloadResult', ['url', 'statuscode', 'content'])
PAGEVERSION = '1.0'


def showMessage(text, level="info", section=""):
    messcolor = tcolor.GREEN
    if level.lower() == "error":
        messcolor = tcolor.RED
    elif level.lower() == "warn":
        messcolor = tcolor.ORANGE

    if section == "":
        title = tcolor.DEFAULT
    else:
        title = "%s[%s%s%s] " % (
            tcolor.DEFAULT,
            messcolor,
            section,
            tcolor.DEFAULT
        )

    print "%s%s" % (
        title,
        text
    )


def getEncodedURL(url, datas):
    datas = None
    if datas:
        urlid = "%s/%s" % (url, datas)
    else:
        urlid = "%s" % url

    urlid = "%s/%s" % (url, datas)
    pageid = md5(urlid)

    return pageid


def getFeedDestination(rootdir, jobboardname, url, datas):
    feedid = getEncodedURL(url, datas)
    saveto = "%s/%s/feeds/%s.feed" % (
        rootdir,
        jobboardname,
        feedid
    )

    return saveto


def getPageDestination(rootdir, jobboardname, feedid, url, datas):
    pageid = getEncodedURL(url, datas)
    saveto = "%s/%s/pages/%s/%s.page" % (
        rootdir,
        jobboardname,
        feedid,
        pageid,
    )

    return saveto


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


def findFiles(srcdir, pattern):
    """ Find files with the pattern"""
    matches = []
    for root, dirnames, filenames in os.walk(srcdir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches


def getNow():
    """Get now timestamp"""
    return time.time()


def openPage(filename):
    pageresult = None

    fd = open(filename, 'rb')
    version = fd.readline().strip()
    statuscode = fd.readline().strip()
    pageid = fd.readline().strip()
    url = fd.readline().strip()
    content = fd.read()
    fd.close()

    if version != PAGEVERSION:
        mess = "The %s has bad version, current=%s, needed=%s" % \
               ( 
                   filename,
                   version,
                   PAGEVERSION
               )
        showMessage(mess, "warn", "Utilities")
    else:
        pageresult = PageResult(
            version=version,
            statuscode=statuscode,
            pageid=pageid,
            url=url,
            content=content
        )

    return pageresult


def download(url, datas):
    headers = {
        'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
        'Referer': 'http://candidat.pole-emploi.fr/candidat/rechercheoffres/avancee',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #'Content-Type': 'application/json',
    }

    try:
        if datas:
            r = requests.post(url, data=datas, headers=headers)
        else:
            r = requests.get(url)
    except Exception, e:
        showMessage(e, 'error', 'Utilities')

    return DownloadResult(url=url, statuscode=r.status_code, content=r.content)


def downloadFile(
        filename, url, datas=None, withmeta=False,
        age=0, forcedownload=False):
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
        if not forcedownload and t + (age) > now:
            return

    destdir = os.path.dirname(filename)
    if (not os.path.isdir(destdir)):
        os.makedirs(destdir)

    # Download file
    showMessage("Download %s(%s%s%s)" %
                (
                    url,
                    tcolor.MAGENTA,
                    filename,
                    tcolor.DEFAULT
                ),
                'info',
                'Utilities',
            )
    r = download(url, datas)

    if r.statuscode in [200, 404, 410]:
        out = open(filename, 'wb')
        if withmeta:
            version = PAGEVERSION
            statuscode = r.statuscode
            pageid = getEncodedURL(url, datas)
            out.write("%s\n" % version)
            out.write("%s\n" % statuscode)
            out.write("%s\n" % pageid)
            out.write("%s\n" % url)
        out.write(r.content)
        out.close()

    return r


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
    conn = lite.connect(configs.globals['database'])
    cursor = conn.cursor()
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % tablename
    cursor.execute(sql)
    return len(cursor.fetchall()) == 1


def db_create(configs):
    """Create the offers table"""
    conn = None
    conn = lite.connect(configs.globals['database'])
    cursor = conn.cursor()

    # create a offers table
    cursor.execute("""CREATE TABLE offers( \
                        source TEXT, \
                        offerid TEXT, \
                        lastupdate INTEGER, \
                        ref TEXT, \
                        feedid TEXT, \
                        date_pub INTEGER, \
                        date_add INTEGER, \
                        title TEXT, \
                        company TEXT, \
                        contract TEXT, \
                        duration INTEGER, \
                        location TEXT, \
                        department TEXT, \
                        lat TEXT, \
                        lon TEXT, \
                        salary TEXT, \
                        salary_cleaned TEXT, \
                        salary_min FLOAT, \
                        salary_max FLOAT, \
                        salary_nbperiod INTEGER, \
                        salary_unit FLOAT, \
                        salary_bonus TEXT, \
                        salary_minbonus FLOAT, \
                        salary_maxbonus FLOAT, \
                        url TEXT, \
                        content TEXT, \
                        state TEXT, \
                        PRIMARY KEY(source, offerid))""")
    # create a offers table
    # cursor.execute("""CREATE TABLE feeds( \
    #                     feedid TEXT, \
    #                     ref TEXT, \
    #                     PRIMARY KEY(feedid, ref))""")
    cursor.execute("""CREATE TABLE blacklist(company TEXT, PRIMARY KEY(company))""")


def db_delete_jobboard_datas(configs, jobboardname):
    """Delete jobboard datas from offers table"""
    conn = None
    conn = lite.connect(configs.globals['database'])
    cursor = conn.cursor()

    # Delete jobbord datas in offers
    sql = "delete from offers where source='%s'" % jobboardname
    cursor.execute(sql)

    # # Delete jobbor datas on jobboard table
    # sql = "delete from jb_%s" % jobboardname
    # cursor.execute(sql)

    conn.commit()


def db_delete_offer(configs, source, offerid):
    """Delete offer"""
    conn = None
    conn = lite.connect(configs.globals['database'])
    cursor = conn.cursor()

    # create a table
    sql = "delete from offers where source='%s' and offerid='%s'" % \
          (
              source,
              offerid
          )
    cursor.execute(sql)
    conn.commit()


def db_add_offer(configs, offer):
    conn = lite.connect(configs.globals['database'])
    try:
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO offers VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                offer.src, offer.offerid, offer.lastupdate, offer.ref,
                offer.feedid, offer.date_pub, offer.date_add,
                offer.title, offer.company, offer.contract,
                offer.duration, offer.location, offer.department,
                offer.lat, offer.lon, offer.salary, offer.salary_cleaned,
                offer.salary_min, offer.salary_max, offer.salary_nbperiod,
                offer.salary_unit, offer.salary_bonus, offer.salary_minbonus,
                offer.salary_maxbonus, offer.url, offer.content, offer.state
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
        if (e.args[0] == "columns source, offerid are not unique"):
            return 0
        else:
            showMessage(e, 'error', 'Utilities')
            return 1
    finally:
        if conn:
            conn.close()


def blacklist_flush(configs):
    conn = lite.connect(configs.globals['database'])
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

    fp.close()
    conn = None

    try:
        conn = lite.connect(configs.globals['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO blacklist VALUES(?)", list)
        conn.commit()

    except lite.Error, e:
        showMessage("Error %s:" % e.args[0], 'error', 'Utilities')

    finally:
        if conn:
            conn.close()


def filter_contract_fr(contract):
    contract = re.sub(ur'Perm', "CDI", contract)
    contract = re.sub(ur'[0-9]+ en (.*)', "\\1", contract, flags=re.DOTALL)
    contract = re.sub(ur'.*CDI.*', "CDI", contract, flags=re.DOTALL)
    contract = re.sub(ur'Travail temporaire', "CDD", contract, flags=re.DOTALL)
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

def filter_company_fr(company):
    company = re.sub(ur'^\(confidentiel\)$', 'NA', company, flags=re.IGNORECASE)
    company = re.sub(ur'^confidentiel$', 'NA', company, flags=re.IGNORECASE)
    return company

def filter_location_fr(location):
    location = re.sub(ur'IDF', "Île-de-France", location, flags=re.IGNORECASE)
    location = re.sub(ur'Ile-de-France', "Île-de-France", location, flags=re.IGNORECASE)
    location = re.sub(ur'Ile de France', "Île-de-France", location, flags=re.IGNORECASE)
    return location

def filter_salary_fr(salary):
    # TODO : use regexp once whe have a better view of possible combinations
    # TODO : use something similar as ^...$
    # Selon profil
    salary = re.sub(ur'.*selon profil.*', "NA", salary, flags=re.DOTALL | re.IGNORECASE)
    salary = re.sub(ur'Selon diplôme et expérience', "NA", salary)
    #salary = re.sub(ur'fixe + variable selon profil', "NA", salary)
    #salary = re.sub(ur'Fixe+Variable selon profil', "NA", salary)
    #salary = re.sub(ur'Fixe + Variable selon profil', "NA", salary)
    #salary = re.sub(ur'A définir selon profil', "NA", salary)
    #salary = re.sub(ur'A DEFINIR SELON PROFIL', "NA", salary)
    #salary = re.sub(ur'à défninir selon profil', "NA", salary)
    #salary = re.sub(ur'à définir selon profils', "NA", salary)
    #salary = re.sub(ur'A négocier selon profil', "NA", salary)
    #salary = re.sub(ur'A NEGOCIER SELON PROFIL', "NA", salary)
    #salary = re.sub(ur'à négocier selon profil', "NA", salary)
    #salary = re.sub(ur'à négocier selon le profil', "NA", salary)
    #salary = re.sub(ur'à déterminer selon profil', "NA", salary)
    salary = re.sub(ur'à définir selon expérience', "NA", salary)
    salary = re.sub(ur'A négocier selon expérience.', "NA", salary)
    salary = re.sub(ur'A négocier selon expérience', "NA", salary)
    salary = re.sub(ur'à négocier selon expérience', "NA", salary)
    salary = re.sub(ur'à négocier selon exp', "NA", salary)
    salary = re.sub(ur'à negocier K€ brut/an', "NA", salary)
    #salary = re.sub(ur'A voir selon profil', "NA", salary)
    #salary = re.sub(ur'Attractive et selon profil', "NA", salary)
    salary = re.sub(ur'De débutant à confirmé', "NA", salary)
    salary = re.sub(ur'En fonction du profil', "NA", salary)
    salary = re.sub(ur'en fonction du profil', "NA", salary)
    salary = re.sub(ur'En fonction de votre profil', "NA", salary)
    salary = re.sub(ur'Fonction profil et expérience', "NA", salary)
    #salary = re.sub(ur'Selon profil/expérience', "NA", salary)
    salary = re.sub(ur'Package Attractif selon expéri', "NA", salary)
    salary = re.sub(ur'selon niveau d\'expérience', "NA", salary)
    salary = re.sub(ur'Selon formation et/ou exp.', "NA", salary)
    salary = re.sub(ur'selon votre profil', "NA", salary)
    salary = re.sub(ur'Selon votre profil.', "NA", salary)
    salary = re.sub(ur'Selon votre profil', "NA", salary)
    salary = re.sub(ur'selon le profil', "NA", salary)
    salary = re.sub(ur'Selon le profil', "NA", salary)
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
    salary = re.sub(ur'SELON EXP', "NA", salary)
    salary = re.sub(ur'Selon CCN 15/3/66', "NA", salary)
    salary = re.sub(ur'selon CCN51', "NA", salary)
    salary = re.sub(ur'selon grille FPH', "NA", salary)
    salary = re.sub(ur'selon grille', "NA", salary)
    salary = re.sub(ur'selon grilles', "NA", salary)
    salary = re.sub(ur'cf. annonce', "NA", salary)
    salary = re.sub(ur'Package attractif', "NA", salary)
    salary = re.sub(ur'suivant profil', "NA", salary)
    salary = re.sub(ur'fixe + variable', "NA", salary)
    salary = re.sub(ur'Fixe + variable', "NA", salary)
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
    salary = re.sub(ur'A négocier.', "NA", salary)
    salary = re.sub(ur'A négocier', "NA", salary)
    salary = re.sub(ur'A NEGOCIER', "NA", salary)
    salary = re.sub(ur'A negocier', "NA", salary)
    salary = re.sub(ur'a confirmer', "NA", salary)
    salary = re.sub(ur'à définir', "NA", salary)
    salary = re.sub(ur'à défiinir', "NA", salary)
    salary = re.sub(ur'À définir', "NA", salary)
    salary = re.sub(ur'A définir.', "NA", salary)
    salary = re.sub(ur'A définir', "NA", salary)
    salary = re.sub(ur'A Definir', "NA", salary)
    salary = re.sub(ur'A DEFINIR', "NA", salary)
    salary = re.sub(ur'A DETERMINER', "NA", salary)
    salary = re.sub(ur'à determiner', "NA", salary)
    salary = re.sub(ur'A determiner', "NA", salary)
    salary = re.sub(ur'A definir', "NA", salary)
    salary = re.sub(ur'À definir', "NA", salary)
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
    salary = re.sub(ur'Negociable', "NA", salary)
    salary = re.sub(ur'non indiqué', "NA", salary)
    salary = re.sub(ur'non communiqué', "NA", salary)
    salary = re.sub(ur'NON COMMUNIQUE', "NA", salary)
    salary = re.sub(ur'non précisé', "NA", salary)
    salary = re.sub(ur'Non précisé.', "NA", salary)
    salary = re.sub(ur'Non précisé', "NA", salary)
    salary = re.sub(ur'Motivant.', "NA", salary)
    salary = re.sub(ur'Motivant', "NA", salary)
    salary = re.sub(ur'Voir annonce', "NA", salary)
    salary = re.sub(ur'GRILLE DE LA FPT', "NA", salary)
    salary = re.sub(ur'Grille', "NA", salary)
    salary = re.sub(ur'variable', "NA", salary)
    salary = re.sub(ur'confidentiel', "NA", salary)
    salary = re.sub(ur'TBD', "NA", salary)
    salary = re.sub(ur'N.S.', "NA", salary)
    salary = re.sub(ur'ANNUEL', "NA", salary)
    salary = re.sub(ur'^euros$', "NA", salary)
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
