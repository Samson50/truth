from congressScraper import CongressScraper
from dbManager import DBManager

manager = DBManager()
manager.recreateAll()
manager.close()
congress = CongressScraper()
congress.populateDB()
congress.close()
#mysqldump -u root -p --databases federal > fed_bu.sql
#mysql -u root -p  federal < fed_bu.sql

#run tests from C:\Users\Jacob\git\truth
#restore database from ADMIN C:\Program Files\MySQL\MySQL Server 5.7\bin