import requests

from lxml import html
#from lxml import etree
from fake_useragent import UserAgent

ua = UserAgent()
header = {"User-Agent": ua.random}

page = requests.get("http://www.whatsmyuseragent.com/", headers=header)
tree = html.fromstring(page.content)
#print(etree.tostring(tree, pretty_print=True))
for x in tree.xpath('//div[@id="user-agent"]/div[1]'): print x.text 