import mysql.connector
import sys
import exceptions

class DBPopulate:
    def __init__(self):
        self.cnx = mysql.connector.connect(user='bob', password='bobwhite', host='localhost', database='federal')
        self.cursor = self.cnx.cursor()
        
    def getFirstYear(self):
        try:
            argument = ("SELECT MIN(First) FROM LEGISLATOR; ")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print e
        except exceptions.IndexError as e:
            print e
        except:
            print sys.exc_info()[0]
        
    def getLegID(self, fname, lname):
        try:
            argument = ("SELECT LegID FROM Legislator WHERE FirstName=\""+fname+"\" AND LastName LIKE \""+lname+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print fname+" "+lname+" "+str(e)
        except exceptions.IndexError as e:
            print "getLegID Error: "+fname+" - "+lname+" "+str(e)
        except:
            print "getLegID Error: "+fname+" - "+lname+" "+str(sys.exc_info()[0])
        
    def getComID(self, committee):
        try:
            argument = ("SELECT ComID FROM Committee WHERE ComName=\""+committee+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print committee+" "+e
        except exceptions.IndexError as e:
            print "getComID Error for Com: "+committee+": "+str(e)
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def getBillID(self, billName, con):
        try:
            argument = ("SELECT BillID FROM Bill WHERE Name=\""+billName+"\" AND Congress="+str(con)+";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print "getBillID Error for: "+str(billName)+": "+str(e)
        except exceptions.IndexError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def getPolicyID(self, pname):
        try:
            argument = ("SELECT PolID FROM PolicyArea where PAName=\""+pname+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print "getPolicyID Error for: "+pname+": "+str(e)
        except exceptions.IndexError as e:
            print e
        except:
            print "idk "+str(sys.exc_info()[0])
        

    def insertLeg(self, fname, lname, party, state, SoH, year):
        try:
            argument =   ("INSERT INTO Legislator "
                                "(FirstName, LastName, Party, State, Job, First)"
                                "VALUES (\""+fname+"\", \""+lname+"\", \""+party+"\", \""+state+"\", \""+SoH+"\", "+str(year)+");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "Legislator: "+fname+" "+lname+" "+str(e)
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
            
    def insertBill(self, name, con, fname, lname, summary):
        spon = self.getLegID(fname,lname)
        #print spon
        try:
            argument = ("INSERT INTO Bill "
                            "(Name, Congress, Sponsor, Summary)"
                            "VALUES (\""+name+"\", "+str(con)+", "+str(spon)+", \""+summary+"\")")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertBill Error: "+fname+" - "+lname+" "+str(e)
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def insertCosponsor(self, fname, lname, BillID):
        LegID = self.getLegID(fname,lname)
        try:
            argument = ("INSERT INTO Cosponsor (BillID, LegID)"
                                "VALUES ("+str(BillID)+","+str(LegID)+");")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertCosponsor Error: "+fname+" - "+lname+" bnum: "+str(BillID)+" "+str(e)
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def insertAction(self, BillID, date, action, actBy):
        if len(action) > 255: action = action[0:255]
        actDate = date.split('/')[2]+'-'+date.split('/')[0]+'-'+date.split('/')[1]
        try:
            argument = ("INSERT INTO Action (ActionDate, ActionBy, BillID, ActionStr)"
                                "VALUES (\""+actDate+"\", \""+actBy+"\", "+str(BillID)+", \""+action+"\");")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "Action error for Bill: "+str(BillID)+" "+str(e)
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def insertComboBill(self, BillID, commName):
        ComID = self.getComID(commName)
        try:
            argument =   ("INSERT INTO Combo "
                                "(LegID, ComID)"
                                "VALUES ("+str(BillID)+", "+str(ComID)+");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print str(BillID)+" Com: "+commName+" "+str(e)
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def insertRelatedBill(self, BillID, RBName, con):
        try:
            argument =   ("INSERT INTO RelatedBill "
                                "(BillID, RBName)"
                                "VALUES ("+str(BillID)+", \""+RBName+"\");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print str(BillID)+" Related Bill: "+str(RBName)+" "+str(e)
        except:
            print "idk "+str(sys.exc_info()[0])
            
    def insertBillPolicy(self, billID, policy):
        policyID = self.getPolicyID(policy)
        try:
            argument =   ("INSERT INTO BillPolicy "
                                "(BillID, PolID)"
                                "VALUES ("+str(billID)+", "+str(policyID)+");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print str(billID)+" Policy Area: "+str(policy)+" "+str(e)
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
#print test.getFirstYear()
#test.deleteItem("legislator","LegID",1)
#print test.getCommittee("Veterans' Affairs")
#test.showTable('Legislator')
#test.close()

#test = DBManager()
#test.recreateAll()
#test.show('tables')
#test.close()