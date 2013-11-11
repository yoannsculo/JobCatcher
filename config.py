#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__license__ = 'GPLv2'
__version__ = '0.1'

# TODO
# https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?lg=FR&isco=%25&multipleCountries=FR-R281&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=5&page=1&country=FR&totalCount=781&multipleRegions=R281
# http://www.jobijoba.com
# http://candidat.pole-emploi.fr/candidat/rechercheoffres/resultatsrechercheparparametres?lieux=34D,91R&grandDomaine=K&offresPartenaires=true

configs = {
    'global': {
        'debug': True,
        'rootdir': './dl',
        'wwwdir': './www',
        'database': 'jobs.db',
    },
    'PoleEmploi': {
        'feeds': [
            {
                'url': 'http://candidat.pole-emploi.fr/candidat/rechercheoffres/avancee.recherche',
                'datas': {
                    'domaineParTheme': u'',
                    'dureeEmission': u'',
                    'experience': u'EXPERIMENTE',
                    'fourchetteSalaire': u'',
                    'grandDomaine': u'',
                    'heureMax': u'',
                    'langues1': u'',
                    'langues2': u'',
                    'numeroOffre': u'',
                    'partenaires': u'on',
                    'radiogroup': u'MOTS_CLES',
                    'rechercher': u'',
                    'rechercher:hiddenelementSubmit': u'rechercher:hiddenelementSubmit',
                    'secteurActiviteEntreprise1': u'',
                    'secteurActiviteEntreprise2': u'',
                    'select_1': u'',
                    'select_2': u'',
                    'select_3': u'',
                    'set101': u'python',
                    'set201': u'',
                    'sousDomaine': u'',
                    'textfield': u'python',
                    'theme': u'',
                    'typeContrat': u'',
                    'uniteDuree': u'AN',
                    'valeurExperience': u'5',
                    't:formdata': u'H4sIAAAAAAAAALVYz2/cRBj9sqilZFtafkkICSQgvSEn67YQkqZlu9lWgNNEXcolBzTr/XYzxfaYmfGue4ETR5A4I3HiiCoB9x7oASkHDvwH/AGckDiBxIxnbSfbJu16TKREyvM3b957M54Zzw9/wonJKrzN0d9Drn7ZcMhRLLfHJPIR10gQIB8jFwEpSgQN44AOKaLgsDPkToxO6Ds+C8MkciSJUUh+16F7ocZiFmEkhePR6NNe0g+pbI/R77BIYipxaYczH4XInghBWXT7yx/vbTRff7UBjV142jd1El7Y9e6QMVkOSDRa3u7fQV+ue9DEAENFf5OEKOH5AyU9yWk0Wk85nNOgo0HHtIPyJ41jCa9lJj9WJj1yKzfZK0xOrsDlo+IpcGKAzK8gkXQ4GVA24iyJVUirjI8cEhNVWORzSYXDMaD9gyHd0q1u6FZLPZRJ/M3K/bd+fvavXxqwoMzqMDgLtNnP4HNopPrvUxIWy85qEHuxgtjWfrq//1Pv3/sNlWmmarIGq/MLEShbKy0l4tKxIvpEoNPuK5D48jrFYGDiOn/7QfOPl3795/i4TppeLBW251X40Ex/cG9wcfj3d7/ZZ+YqRZqhacy5FuZUW810dvIeXJmfYMRJNBiwkNAIc0WnM3DTgPa0Rt1N8OxolqYrh8iWJDWenWMXspCmNBJO1zQy69jDI/rtF199/f327u9q7fLglB9QVfv+IJt85Vqm/13I5+KhcOLJVdioMGosETOZNzWWR25LahJ/F96Zn0XuqbxyUSey/yyIjJAb0K3YfmbMNd2Luax40oH2/LzTiGLCD1k9O8V3CP8oM10HubFfaTSjJETOTHk+RQy2rTFrUoslI2QDvc1y9bIkmTZQW/LpHPUUWk2dvBtjtgMQWVjWWMdg1qTG8hZ8aMXy6Cl5UGg8uQxrFd5fRezLT1Zy76dywI7OuO5CZ36KIUs0LiUKEhBazsTnyic986SmDoxYG7+t2fhadnQWivYw4RiStFCUAVsktaMziiqdGjGNkastzjcjeVIdREvIllIzLk424dr8JGMSaHOH1anEzpkH3VJjLfQWCSYRlThQZIXGxQza1JAtpdHVhqsVNh7dHqeHmlzamQztTtEaiC1OckK9TWoQ1NmajpVftYByjDkVWLywr0xL2tOSbllSd5f/hw/38T7curu0Xy7d2eXStaOzV3RhVtEFOzoLRfoGIkFRbik5YEdn8ZpHdIwkMUSFrDMG9QxaA7F9ZO5sZBWnVd66psjcR0bm1kBsBG7AeoWzpfrCHOr7hlzcMwViSWhEefBBhful4upQcqqWn5BJ4Qfq03mq8eWioGcKtlRBRxXU251xcB7ePIpSf2lhlJ1Ni2+GA9gTNjXdLMEbj1XOBYfrT3qBeo0lkkVHXT2U16YLh69FZ24Ki67/A14oWbX6FQAA',
                }
            }
        ]
    },
    'Apec': {
        'feeds' : [
            { 'url': 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101833.xml'},
        ]
    },
    'cadresonline': {
        'feeds': [
            #{ 'url': 'http://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kw=developpeur&kt=1&jc=5t.0.1.2.3.4.5.6.7-10t.0.1.2.3.4.5.6.7.8&ct=0&dt=1374746615' }
        ]
    },
    'RegionJob': {
        'feeds': [
            {'url': 'http://www.centrejob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.nordjob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.pacajob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.rhonealpesjobs.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.estjob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.ouestjob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.sudouestjob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.parisjob.com/fr/rss/flux.aspx?&fonction=10'},
        ]
    },
    'Eures': {
        'feeds': [
            { 'url': 'https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?lg=FR&isco=%25&multipleCountries=FR-R281&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=5&page=1&country=FR&totalCount=781&multipleRegions=R281'}
        ]
    }
}

configstest = {
    'global': {
        'debug': True,
        'rootdir': '/tmp/dl',
        'wwwdir': '/tmp/www',
        'database': '/tmp/jobs.db',
    },
    'PoleEmploi': {
        'feeds': [
            {
                'url': 'http://candidat.pole-emploi.fr/candidat/rechercheoffres/avancee.recherche',
                'datas': {
                    'domaineParTheme': u'',
                    'dureeEmission': u'',
                    'experience': u'EXPERIMENTE',
                    'fourchetteSalaire': u'',
                    'grandDomaine': u'',
                    'heureMax': u'',
                    'langues1': u'',
                    'langues2': u'',
                    'numeroOffre': u'',
                    'partenaires': u'on',
                    'radiogroup': u'MOTS_CLES',
                    'rechercher': u'',
                    'rechercher:hiddenelementSubmit': u'rechercher:hiddenelementSubmit',
                    'secteurActiviteEntreprise1': u'',
                    'secteurActiviteEntreprise2': u'',
                    'select_1': u'',
                    'select_2': u'',
                    'select_3': u'',
                    'set101': u'python',
                    'set201': u'',
                    'sousDomaine': u'',
                    'textfield': u'python',
                    'theme': u'',
                    'typeContrat': u'',
                    'uniteDuree': u'AN',
                    'valeurExperience': u'5',
                    't:formdata': u'H4sIAAAAAAAAALVYz2/cRBj9sqilZFtafkkICSQgvSEn67YQkqZlu9lWgNNEXcolBzTr/XYzxfaYmfGue4ETR5A4I3HiiCoB9x7oASkHDvwH/AGckDiBxIxnbSfbJu16TKREyvM3b957M54Zzw9/wonJKrzN0d9Drn7ZcMhRLLfHJPIR10gQIB8jFwEpSgQN44AOKaLgsDPkToxO6Ds+C8MkciSJUUh+16F7ocZiFmEkhePR6NNe0g+pbI/R77BIYipxaYczH4XInghBWXT7yx/vbTRff7UBjV142jd1El7Y9e6QMVkOSDRa3u7fQV+ue9DEAENFf5OEKOH5AyU9yWk0Wk85nNOgo0HHtIPyJ41jCa9lJj9WJj1yKzfZK0xOrsDlo+IpcGKAzK8gkXQ4GVA24iyJVUirjI8cEhNVWORzSYXDMaD9gyHd0q1u6FZLPZRJ/M3K/bd+fvavXxqwoMzqMDgLtNnP4HNopPrvUxIWy85qEHuxgtjWfrq//1Pv3/sNlWmmarIGq/MLEShbKy0l4tKxIvpEoNPuK5D48jrFYGDiOn/7QfOPl3795/i4TppeLBW251X40Ex/cG9wcfj3d7/ZZ+YqRZqhacy5FuZUW810dvIeXJmfYMRJNBiwkNAIc0WnM3DTgPa0Rt1N8OxolqYrh8iWJDWenWMXspCmNBJO1zQy69jDI/rtF199/f327u9q7fLglB9QVfv+IJt85Vqm/13I5+KhcOLJVdioMGosETOZNzWWR25LahJ/F96Zn0XuqbxyUSey/yyIjJAb0K3YfmbMNd2Luax40oH2/LzTiGLCD1k9O8V3CP8oM10HubFfaTSjJETOTHk+RQy2rTFrUoslI2QDvc1y9bIkmTZQW/LpHPUUWk2dvBtjtgMQWVjWWMdg1qTG8hZ8aMXy6Cl5UGg8uQxrFd5fRezLT1Zy76dywI7OuO5CZ36KIUs0LiUKEhBazsTnyic986SmDoxYG7+t2fhadnQWivYw4RiStFCUAVsktaMziiqdGjGNkastzjcjeVIdREvIllIzLk424dr8JGMSaHOH1anEzpkH3VJjLfQWCSYRlThQZIXGxQza1JAtpdHVhqsVNh7dHqeHmlzamQztTtEaiC1OckK9TWoQ1NmajpVftYByjDkVWLywr0xL2tOSbllSd5f/hw/38T7curu0Xy7d2eXStaOzV3RhVtEFOzoLRfoGIkFRbik5YEdn8ZpHdIwkMUSFrDMG9QxaA7F9ZO5sZBWnVd66psjcR0bm1kBsBG7AeoWzpfrCHOr7hlzcMwViSWhEefBBhful4upQcqqWn5BJ4Qfq03mq8eWioGcKtlRBRxXU251xcB7ePIpSf2lhlJ1Ni2+GA9gTNjXdLMEbj1XOBYfrT3qBeo0lkkVHXT2U16YLh69FZ24Ki67/A14oWbX6FQAA',
                }
            }
        ]
    },
    'Apec': {
        'feeds' : [
            { 'url': 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101833.xml'},
        ]
    },
    'cadresonline': {
        'feeds': [
            #{ 'url': 'http://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kw=developpeur&kt=1&jc=5t.0.1.2.3.4.5.6.7-10t.0.1.2.3.4.5.6.7.8&ct=0&dt=1374746615' }
        ]
    },
    'RegionJob': {
        'feeds': [
            {'url': 'http://www.centrejob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.nordjob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.pacajob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.rhonealpesjobs.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.estjob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.ouestjob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.sudouestjob.com/fr/rss/flux.aspx?&fonction=10'},
            {'url': 'http://www.parisjob.com/fr/rss/flux.aspx?&fonction=10'},
        ]
    },
    'Eures': {
        'feeds': [
            { 'url': 'https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?lg=FR&isco=%25&multipleCountries=FR-R281&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=5&page=1&country=FR&totalCount=781&multipleRegions=R281'}
        ]
    }
}
