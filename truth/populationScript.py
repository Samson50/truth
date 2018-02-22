import os

from congressScraper import CongressScraper
from dbManager import DBManager

def clean():
    manager = DBManager()
    manager.recreateAll()
    manager.close()

def fillCongress():
    congress = CongressScraper()
    congress.populateDB()
    congress.close()

def backupDB():
    DB_USER = raw_input("User Name: ")
    DB_PASSWORD = raw_input("Password: ")
    DB_NAME = raw_input("Database: ")
    BACKUPPATH = os.getcwd()
    BACKUP_NAME = raw_input("Backup Name: ")
    dumpcmd = "mysqldump -u "+DB_USER+" -p "+DB_PASSWORD+" "+DB_NAME+" > "+BACKUPPATH+"\\"+BACKUP_NAME+".sql"
    os.system(dumpcmd)

def restoreDB():
    DB_USER = raw_input("User Name: ")
    DB_PASSWORD = raw_input("Password: ")
    DB_NAME = raw_input("Database: ")
    BACKUPPATH = os.getcwd()
    BACKUP_NAME = raw_input("Backup Name: ")
    #os.chdir("C:\\Program Files\\MySQL\\MySQL Server 5.7\\bin")
    dumpcmd = "mysqldump -u "+DB_USER+" -p "+DB_PASSWORD+" "+DB_NAME+" < "+BACKUPPATH+"\\"+BACKUP_NAME+".sql"
    os.system(dumpcmd)

#mysqldump -u root -p --databases federal > fed_bu.sql
#mysql -u root -p  federal < fed_bu.sql

#run tests from C:\Users\Jacob\git\truth
#restore database from ADMIN C:\Program Files\MySQL\MySQL Server 5.7\bin

#import os
#dumpcmd = "mysqldump -u "+DB_USER+" -p "+DB_PASSWORD+" "+DB_NAME+" > "+BACKUPPATH+"/"+BACKUP_NAME+".sql"
#os.system(dumpcmd)
