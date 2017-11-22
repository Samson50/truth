from congressScraper import CongressScraper
from dbManager import DBManager

manager = DBManager()
manager.recreateAll()
manager.close()
congress = CongressScraper()
congress.populateDB()
congress.close()