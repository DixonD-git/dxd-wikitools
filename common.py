# -*- coding: utf-8 -*-
import wikipedia as pywikibot
from login import LoginManager

def getWikiSite(code = None, page = None):
    if not code is None:
        return pywikibot.Site(code = code)

    if not page is None:
        return page.site()

    return pywikibot.Site(code = 'uk')

def templateAliases(templateNames, getRedirectsFromWiki = False):
    templateNamespaces = {u'Шаблон:', u'шаблон:', u'Template:', u'template:'}

    # remove namespace from names
    aliases = set()
    for templateName in templateNames:
        for templateNamespace in templateNamespaces:
            if templateName.startswith(templateNamespace):
                templateName = templateName[len(templateNamespace):]
                break
        aliases.add(templateName)

    if getRedirectsFromWiki:
        templateNames = set(aliases)
        for templateName in templateNames:
            templatePage = pywikibot.Page(getWikiSite(), u'Шаблон:' + templateName)
            aliases.union(set(page.titleWithoutNamespace() for page in templatePage.getReferences(redirectsOnly=True)))

    templateNames = set(aliases)
    for templateName in templateNames:
        aliases.add(templateName[0].upper() + templateName[1:])
        aliases.add(templateName[0].lower() + templateName[1:])

    templateNames = set(aliases)
    for templateName in templateNames:
        for templateNamespace in templateNamespaces:
            aliases.add(templateNamespace + templateName)

    return aliases

def login(username, password = None):
    site = getWikiSite()
    loginManager = LoginManager(username=username, site=site, password=password)
    if site.loggedInAs() <> username:
        pywikibot.output("Logging in as " + username)
        loginManager.login()
    else:
        pywikibot.output("Already logged in as " + username)

def logout(username):
    pywikibot.output("Logging out...")
    site = getWikiSite()
    loginManager = LoginManager(username=username, site=site)
    loginManager.logout()