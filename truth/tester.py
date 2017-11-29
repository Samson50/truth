#import requests

#from lxml import html
#from lxml import etree
#from fake_useragent import UserAgent

#ua = UserAgent()
#header = {"User-Agent": ua.random}

#page = requests.get("http://www.whatsmyuseragent.com/", headers=header)
#tree = html.fromstring(page.content)
#print(etree.tostring(tree, pretty_print=True))
#for x in tree.xpath('//div[@id="user-agent"]/div[1]'): print x.text 
from random import random, randint

def getOneMax(congNum, chamber, t):
    if chamber: chamber = 'House'
    else: chamber = 'Senate'
    search = 'https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%5B%22'+str(congNum)+'%22%5D%2C%22chamber%22%3A%22'+chamber+'%22%2C%22type%22%3A%22'+t+'%22%7D'
    print search
    #self.fetch(search)
    #num = int(self.findElements('xpath','//div[@id="main"]/ol/li/span/a')[0].text.split('.')[-1])


types = [
        ['bills','amendments','resolutions','concurrent-resolutions','joint-resolutions'],
        ['bills','amendments','resolutions','concurrent-resolutions','joint-resolutions']
        ]

vals = {i : list(types) for i in range(115,92,-1)}#range(93,116)}#

print vals

def getMaxes(vals):
    while len(vals) != 0:
        k = vals.keys()[randint(0,len(vals.keys())-1)]
        if len(vals[k]) == 2: c = randint(0,1)
        else: c = 0
        i = randint(0,len(vals[k][c])-1)
        getOneMax(k,c,vals[k][c][i])
        w = list(vals[k][c])
        del w[i]
        vals[k][c] = w
        if len(vals[k][c]) == 0:
            del vals[k][c]
            if len(vals[k]) == 0:
                del vals[k] 

getMaxes(vals)
#print getOneMax(114,'House','bills')
