import mysql.connector
import sys
import exceptions

class DBPopulate:
    def __init__(self):
        self.cnx = mysql.connector.connect(user='bob', password='bobwhite', host='localhost', database='federal')
        self.cursor = self.cnx.cursor()
        
    def getLegID(self, fname, lname):
        try:
            argument = ("SELECT LegID FROM Legislator WHERE FirstName=\""+fname+"\" AND LastName LIKE \""+lname+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print fname+" "+lname+" "+str(e)
        except exceptions.IndexError as e:
            print fname+" "+lname+" "+str(e)
        except:
            print fname+" "+lname+" "+str(sys.exc_info()[0])
        
    def getComID(self, committee):
        try:
            argument = ("SELECT ComID FROM Committee WHERE ComName=\""+committee+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print committee+" "+e
        except exceptions.IndexError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])

    def insertLeg(self, fname, lname, party, state, SoH):
        try:
            argument =   ("INSERT INTO Legislator "
                                "(FirstName, LastName, Party, State, Job)"
                                "VALUES (\""+fname+"\", \""+lname+"\", \""+party+"\", \""+state+"\", \""+SoH+"\");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "Legislator: "+fname+" "+lname+" "+str(e)
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def insertBill(self, name, year, spon, summary):
        try:
            argument = ("INSERT INTO Bill "
                            "(Name, Year, Sonsor, Summary, Issue)"
                            "VALUES (\""+name+"\", "+str(year)+", "+str(spon)+", \""+summary+"\")")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def insertCombo(self, fname, lname, commName):
        LegID = self.getLegID(fname,lname)
        ComID = self.getComID(commName)
        try:
            argument =   ("INSERT INTO Combo "
                                "(LegID, ComID)"
                                "VALUES ("+str(LegID)+", "+str(ComID)+");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print fname+" "+lname+" Com: "+commName+" "+str(e)
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def deleteItem(self, table, cond, itemNo):
        try:
            argument = ("DELETE FROM "+table+" WHERE "+cond+"="+str(itemNo))
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def showTable(self, item):
        self.cursor.execute("select * from %s"%(item))
        for item in self.cursor.fetchall():
            print item
            
    def close(self):
        self.cursor.close()
        self.cnx.close()

#con = mysql.connector.connect(user='bob', password='bobwhite', host='localhost', database='federal')
#test = DBPopulate()
#test.deleteItem("legislator","LegID",1)
#print test.getCommittee("Veterans' Affairs")
#test.showTable('Legislator')
#test.close()

#test = DBManager()
#test.recreateAll()
#test.show('tables')
#test.close()