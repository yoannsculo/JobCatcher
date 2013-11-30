#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
    'Yankel Scialom <yankel.scialom@mail.com>'
]
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '1.0'

# System
import sys

# Third party
from optparse import OptionParser

# Jobcatcher
import utilities
from jc.page import Pages
from jc.config import Config
from jc.p2p import P2PDownloader
from jc.report import ReportGenerator

reload(sys)
sys.setdefaultencoding("utf-8")


def executeall(conf, selecteduser):
    utilities.showMessage('Init blacklist', 'info', '###')
    initblacklist(conf)

    utilities.showMessage('Download feeds', 'info', '###')
    downloadfeeds(conf, selecteduser)

    utilities.showMessage('Download pages', 'info', '###')
    downloadpages(conf)

    utilities.showMessage('Insert pages to jobboard', 'info', '###')
    insertpages(conf, selecteduser)

    utilities.showMessage('Move datas to offers', 'info', '###')
    movepages(conf, selecteduser)

    utilities.showMessage('Generate reports', 'info', '###')
    generatereport(conf, selecteduser)


def generatereport(conf, selecteduser):
    r = ReportGenerator(conf)
    r.generate(selecteduser)


def initblacklist(conf):
    utilities.db_checkandcreate(conf)
    utilities.blacklist_flush(conf)
    utilities.blocklist_load(conf)


def downloadfeeds(conf, selecteduser):
    """Download all jobboard feeds"""

    # Get all users feeds
    feedsinfo = conf.getFeedsInfo(selecteduser)

    for jobboardname, jobboardfeeds in feedsinfo.iteritems():
        for feedid, feedinfo in jobboardfeeds.iteritems():
            plugin = utilities.loadJobBoard(jobboardname, conf)
            plugin.downloadFeed(feedinfo)


def downloadpages(conf):
    pages = Pages(conf)
    pages.downloadPagesFromJobboards()
    # """Download all jobboard pages"""
    # jobboardlist = conf.getJobboardList()
    # for jobboardname in jobboardlist:
    #     downloadpage(conf, jobboardname)


def redownload(conf):
    pages = Pages(conf)
    pages.redownloadFromOffers()


def insertpage(conf, jobboardname):
    # Search page for jobboard
    pages = Pages(conf)
    pages.searchPagesForJobboard(jobboardname)
    plugin = utilities.loadJobBoard(jobboardname, conf)

    for page in pages.pages:
        # Load page content if needed
        if not page.downloaded:
            page.load()

        # Analyse page
        if page.downloaded:
            error = plugin.analyzePage(page)
            if error:
                mess = "Analyse error page %s(%s)" % (page.url, error)
                utilities.showMessage(mess, "warn", "JobCatcher")
            else:
                mess = "%s analyzed" % page.url
                if conf.globals['debug']:
                    utilities.showMessage(mess, "info", "JobCatcher")


def insertpages(conf, selecteduser):
    """Insert all pages from all jobboard"""
    utilities.db_checkandcreate(conf)

    jobboardlist = conf.getJobboardList()

    for jobboardname in jobboardlist:
        insertpage(conf, jobboardname)


def movepage(conf, jobboardname):
    """Move jobboard pages to offers"""
    utilities.db_checkandcreate(conf)

    plugin = utilities.loadJobBoard(jobboardname, conf)
    plugin.moveToOffers()


def movepages(conf, selecteduser):
    """Move all pages from all jobboard"""
    jobboardlist = conf.getJobboardList()

    for jobboardname in jobboardlist:
        movepage(conf, jobboardname)


def clean(conf, jobboardname):
    utilities.db_checkandcreate(conf)
    utilities.db_delete_jobboard_datas(conf, jobboardname)


# def importjobboard(conf, jobboardname):
#     utilities.db_checkandcreate(conf)
#     pagesinsert(conf)
#     pagesmove(conf)


# def imports(conf):
#     jobboardlist = getjobboardlist(conf)
#     for jobboardname in jobboardlist:
#         importjobboard(conf, jobboardname)


# def reimports(conf, jobboardname):
#     clean(conf, jobboardname)
#     imports(conf)

if __name__ == '__main__':

    # Load configs
    from config import configs as globalconfig
    configs = Config()
    configs.addGlobalconfig(globalconfig)
    configs.loadUsersConfig()

    parser = OptionParser(usage='syntax: %prog [options] <from> [to]')
    args = sys.argv[1:]
    selecteduser = None

    parser.set_defaults(version=False)
    parser.add_option('--user',
                      action='store',
                      metavar='USERNAME',
                      dest='user',
                      help='download feed only for the USERNAME'
    )

    parser.add_option('--all',
                      action='store_true',
                      dest='all',
                      help='sync the blacklist, fetch the offers and generates reports.'
    )

    parser.add_option('--feeds',
                      action='store_true',
                      dest='feeds',
                      help='download the all feeds in the config'
    )

    # parser.add_option('--feed',
    #                   action='store',
    #                   metavar='JOBBOARD',
    #                   dest='feed',
    #                   help='download only the feed from JOBBOARD in the config',
    # )

    parser.add_option('--pages',
                      action='store_true',
                      dest='pages',
                      help='download the all pages in the config'
    )

    parser.add_option('--redownload',
                      action='store_true',
                      dest='redownload',
                      help='Redownload all web pages from url field offers table'
    )

    parser.add_option('--inserts',
                      action='store_true',
                      dest='inserts',
                      help='inserts all pages to offers'
    )

    parser.add_option('--insert',
                      action='store',
                      metavar='JOBBOARD',
                      dest='insert',
                      help='insert JOBBOARD pages to offers'
    )

    parser.add_option('--moves',
                      action='store_true',
                      dest='moves',
                      help='move datas to offer'
    )

    parser.add_option('--move',
                      action='store',
                      metavar='JOBBOARD',
                      dest='move',
                      help='move JOBBOARD datas to offer'
    )

    parser.add_option('--clean',
                      action='store',
                      metavar='JOBBOARD',
                      dest='clean',
                      help='clean offers from JOBBOARD source'
    )

    parser.add_option('--report',
                      action='store_true',
                      dest='report',
                      help='generate a full report'
    )

    parser.add_option('--blocklist',
                      action='store_true',
                      dest='blocklist',
                      help='update blocklist'
    )

    parser.add_option('--flush',
                      action='store_true',
                      dest='flush',
                      help = 'flush the blacklist and update it.'
    )

    parser.add_option('--p2psync',
                      action='store_true',
                      dest='p2psync',
                      help = 'sync by P2P'
    )

    parser.add_option('--version',
                      action='store_true',
                      dest='version',
                      help='output version information and exit'
    )
    # parser.add_option('-u', '--url',
    #                       action = 'store_true', dest = 'url',
    #                       help = 'analyse an url')
    # parser.add_option('-f', '--flush',
    #                       action = 'store_true', dest = 'flush',
    #                       help = 'flush the blacklist and update it.')

    (options, args) = parser.parse_args(args)

    # Clean
    if options.clean:
        clean(configs, options.clean)

    if options.version:
        print 'jobcatcher version %s - %s (%s)' % (
            __version__,
            __copyright__,
            __license__
        )
        sys.exit(0)

    if options.user:
        selecteduser = [options.user]

    if options.report:
        print "Report generation..."
        generatereport(configs, selecteduser)
        print "Done."
        sys.exit(0)

    if options.all:
        executeall(configs, selecteduser)
        sys.exit(0)

    #Feeds
    if options.feeds:
        downloadfeeds(configs, selecteduser)
        sys.exit(0)

    # if options.feed:
    #     downloadfeed(configs, options.feed)
    #     sys.exit(0)

    # Pages
    if options.pages:
        downloadpages(configs)
        sys.exit(0)

    if options.redownload:
        redownload(configs)
        sys.exit(0)

    # Inserts
    if options.inserts:
        insertpages(configs, selecteduser)

    if options.insert:
        insertpage(configs, options.insert)

    # Moves
    if options.moves:
        movepages(configs, selecteduser)

    if options.move:
        movepage(configs, options.move)

    if options.blocklist:
        utilities.blocklist_load(configs)
        sys.exit(0)

    if options.flush:
        initblacklist(configs)
        sys.exit(0)

    if options.p2psync:
        # Donwload feeds
        downloadfeeds(configs, selecteduser)

        # Sync p2p
        p = P2PDownloader(configs)
        p.initLocalCache()
        p.sync()
