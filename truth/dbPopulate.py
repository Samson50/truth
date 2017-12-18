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
            argument = ("SELECT LegID FROM Legislator WHERE FirstName LIKE \""+fname+"\" AND LastName LIKE \""+lname+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print fname+" "+lname+" "+str(e)
        except exceptions.IndexError as e:
            #print "getLegID Error: "+fname+" - "+lname+" "+str(e)
            return 0
        except:
            print "getLegID Error: "+fname+" - "+lname+" "+str(sys.exc_info()[0])
            
    def getLegIDCID(self, fname, lname, state, party):
        try:
            argument = ("SELECT LegID FROM Legislator WHERE "
                        "FirstName LIKE \""+fname+"\" AND "
                        "LastName LIKE \""+lname+"\" AND "
                        "State LIKE \""+state+"\" AND "
                        "Party LIKE \""+party+"\""
                        ";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print fname+" "+lname+" "+str(e)
        except exceptions.IndexError as e:
            #print "getLegIDCID Error: "+fname+" - "+lname+" "+str(e)
            return 0
        except:
            print "getLegIDCID Error: "+fname+" - "+lname+" "+str(sys.exc_info()[0])
            
    def getContInfo(self):
        try:
            argument = ("SELECT legID, CID FROM Legislator WHERE NOT isnull(cid);")
            self.cursor.execute(argument)
            return self.cursor.fetchall()#[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print "getContInfo Error: "+str(e)
        except exceptions.IndexError as e:
            print "getContInfo Error: "+str(e)
        except:
            print "getContInfo Error: "+str(e)
            
    def getContID(self, cname, t):
        try:
            argument = ("SELECT ContID FROM Contributor WHERE Name=\""+cname+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print cname+" "+str(e)
        except exceptions.IndexError as e:
            try:
                arg = ("INSERT INTO Contributor (Name, Type) VALUES (\""+cname+"\", "+str(t)+";")
                self.cursor.execute(arg)
                self.cnx.commit()
                arg = ("SELECT ContID FROM Contributor WHERE Name=\""+cname+"\";")
                self.cursor.execute(argument)
                return self.cursor.fetchall()[0][0]
            except:
                print "Good Luck - Error: "+cname+" "+str(sys.exc_info()[0])
        except:
            print "getContID Error: "+cname+" "+str(sys.exc_info()[0])


    def getComID(self, committee):
        try:
            argument = ("SELECT ComID FROM Committee WHERE ComName=\""+committee+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print committee+" "+e
        except exceptions.IndexError as e:
            print "getComID Error for Com: "+committee+": "+str(e)
            return 0
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
            print "getBillID Error: "+billName+" "+str(con)+" "+str(e)
            return 0
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

    def getLegIDVar(self, fname, lname, state, SoH):
        # Stupid special cases for legislators with mismatched names
        if fname == "E.": 
            fname = ''
            lname = "Bernice Johnson"
        if len(fname) > 0:
            #print fname, len(fname)
            if len(state) > 0:
                #print state, len(state)
                try:
                    argument = ("SELECT LegID FROM Legislator WHERE FirstName LIKE \""+fname+"\" AND LastName LIKE \"%"+lname+"\" AND State = \""+state+"\";")# AND Job=\""+SoH+"\";")
                    self.cursor.execute(argument)
                    return self.cursor.fetchall()[0][0]
                except mysql.connector.errors.ProgrammingError as e:
                    print "getLegIDVar Error: "+fname+" - "+lname+" :"+state+" "+str(e)
                except exceptions.IndexError as e:
                    return 0
                    #print "getLegIDVar Error: "+fname+" - "+lname+" :"+state+" "+str(e)
                except:
                    print "getLegIDVar Error: "+fname+" - "+lname+" :"+state+" "+str(sys.exc_info()[0])

            else:
                try:
                    argument = ("SELECT LegID FROM Legislator WHERE FirstName LIKE \""+fname+"\" AND LastName LIKE \""+lname+"\";")# AND Job=\""+SoH+"\";")
                    self.cursor.execute(argument)
                    return self.cursor.fetchall()[0][0]
                except mysql.connector.errors.ProgrammingError as e:
                    print "getLegIDVar Error: "+fname+" - "+lname+" :"+str(e)
                except exceptions.IndexError as e:
                    print "getLegIDVar Error: "+fname+" - "+lname+" :"+str(e)
                except:
                    print "getLegIDVar Error: "+fname+" - "+lname+" :"+str(sys.exc_info()[0])
        elif len(state) > 0:
            try:
                argument = ("SELECT LegID FROM Legislator WHERE LastName LIKE \"%"+lname+"\" AND State = \""+state+"\";")# AND Job=\""+SoH+"\";")
                self.cursor.execute(argument)
                return self.cursor.fetchall()[0][0]
            except mysql.connector.errors.ProgrammingError as e:
                print "getLegIDVar Error: "+lname+" :"+state+" "+str(e)
            except exceptions.IndexError as e:
                #print "getLegIDVar Error: "+lname+" :"+state+" "+str(e)
                return 0
            except:
                print "getLegIDVar Error: "+lname+" :"+state+" "+str(sys.exc_info()[0])

        else:
            try:
                argument = ("SELECT LegID FROM Legislator WHERE LastName LIKE \""+lname+"\";")# AND Job=\""+SoH+"\";")
                self.cursor.execute(argument)
                return self.cursor.fetchall()[0][0]
            except mysql.connector.errors.ProgrammingError as e:
                print "getLegIDVar Error: "+lname+" :"+str(e)
            except exceptions.IndexError as e:
                #print "getLegIDVar Error: "+lname+" :"+str(e)
                return 0
            except:
                print "getLegIDVar Error: "+lname+" :"+str(sys.exc_info()[0])
        return 0



    def insertLeg(self, fname, lname, party, state, SoH, year, website):
        try:
            argument =   ("INSERT INTO Legislator "
                                "(FirstName, LastName, Party, State, Job, First, Website)"
                                "VALUES (\""+fname+"\", \""+lname+"\", \""+party+"\", \""+state+"\", \""+SoH+"\", "+str(year)+", \""+website+"\");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertLeg Error: "+fname+" "+lname+" "+str(e)
        except:
            print "insertLeg Error: "+str(sys.exc_info()[0])
            
    def addCID(self, fname, lname, cid, state, party):
        if len(fname) == 1: fname = fname+'.'
        legID = self.getLegIDCID(fname, '%'+lname, state, party)
        if legID == 0:
            legID = self.getLegIDCID(fname, '%'+lname.split()[-1], state, party)
            if legID == 0: 
                legID = self.getLegIDCID("%", '%'+lname, state, party)
                if legID == 0: legID = self.getLegIDCID("%", '%'+lname.split()[-1], state, party)
        try:
            argument = ("UPDATE Legislator SET CID="+str(cid)+" WHERE LegID="+str(legID)+";")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "addCID Error: "+fname+" "+lname+" "+str(e)
        except:
            print "addCID Error: "+fname+" "+lname+": "+str(sys.exc_info()[0])
            
    def getContributor(self, name, t):
        try: 
            argument = ("SELECT ContID FROM Contributor WHERE NAME=\""+name+"\";")
            self.cursor.execute(argument)
            return self.cursor.fetchall()[0][0]
        except mysql.connector.errors.ProgrammingError as e:
            print "getContributor Error: - "+name+" - "+str(e)
        except exceptions.IndexError as e:
            self.insertContributor(name, t)
            return self.getContributor(name, t)
        except:
            print "getContributor Error: "+name+" "+str(sys.exc_info()[0])


    def insertContributor(self, name, t):
        try: 
            argument = ("INSERT INTO Contributor (Name, Type) VALUES (\""+name+"\", "+str(t)+");")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertContributor Error: "+name+": "+t+" "+str(e)
        except:
            print "insertContributor Error: "+str(sys.exc_info()[0])

            
    def insertContribution(self, legID, contID, amount, nature):
        try:
            argument =   ("INSERT INTO Money"
                                "(LegID, ContID, Amount, Nature)"
                                "VALUES ("+legID+", "+contID+", "+amount+", "+nature+");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "addCont Error: "+str(legID)+": "+str(contID)+" "+str(e)
        except:
            print "addCont Error: "+str(sys.exc_info()[0])


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
            print "insertBill Error: "+str(sys.exc_info()[0])

    def insertCosponsor(self, fname, lname, BillID):
        LegID = self.getLegID(fname,lname)
        if LegID == 0: return
        try:
            argument = ("INSERT INTO Cosponsor (BillID, LegID)"
                                "VALUES ("+str(BillID)+","+str(LegID)+");")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertCosponsor Error: "+fname+" - "+lname+" bnum: "+str(BillID)+" "+str(e)
        except:
            print "insertCosponsor Error: "+str(sys.exc_info()[0])

    def insertAction(self, BillID, date, action, actBy):
        if len(action) > 255: action = action[0:255]
        if '-' in date: date = date.split('-')[0]
        actDate = date.split('/')[2]+'-'+date.split('/')[0]+'-'+date.split('/')[1]
        try:
            argument = ("INSERT INTO Action (ActionDate, ActionBy, BillID, ActionStr)"
                                "VALUES (\""+actDate+"\", \""+actBy+"\", "+str(BillID)+", \""+action+"\");")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "Action error for Bill: "+str(BillID)+" "+str(e)
        except:
            print "Action error: "+str(sys.exc_info()[0])

    def insertComboBill(self, BillID, commName):
        ComID = self.getComID(commName)
        if ComID == 0: return
        try:
            argument =   ("INSERT INTO ComboBill "
                                "(BillID, ComID)"
                                "VALUES ("+str(BillID)+", "+str(ComID)+");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertComboBill Error: "+str(BillID)+" Com: "+commName+" "+str(e)
        except:
            print "insertComboBill Error: "+str(sys.exc_info()[0])

    def insertRelatedBill(self, BillID, RBName):
        try:
            argument =   ("INSERT INTO RelatedBill "
                                "(BillID, RBName)"
                                "VALUES ("+str(BillID)+", \""+RBName+"\");"
                        )
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertRelatedBill Error: "+str(BillID)+" Related Bill: "+str(RBName)+" "+str(e)
        except:
            print "insertRelatedBill Error: "+str(BillID)+" Related Bill: "+str(RBName)+" "+str(sys.exc_info()[0])

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
            print "insertBillPolicy Error: "+str(billID)+" Policy: "+str(policy)+" "+str(e)
        except:
            print "insertBillPolicy Error: "+str(sys.exc_info()[0])

    def insertRoll(self, voteID, question, issue):
        year = voteID/1000000
        con = year-1901 - ((year+1)%2)
        billID = self.getBillID(issue, con)
        if len(question) >= 255: question = question[:255]
        try:
            argument = ("INSERT INTO Roll"
                        "(VoteNum, Question, Issue)"
                        "VALUES ("+str(voteID)+", \""+question+"\", "+str(billID)+");")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertRoll Error for: "+str(voteID)+" - "+issue+": "+str(e)
        except exceptions.IndexError as e:
            print "insertRoll Error: "+str(e)
        except:
            print "insertRoll Error: "+str(sys.exc_info()[0])

    def insertVote(self, voteID, choice, fname, lname, state, SoH):
        legID = self.getLegIDVar(fname, lname, state, SoH)
        choice = choice[:3]
        if legID == 0: return
        try:
            argument = ("INSERT INTO Vote (VoteNum, Choice, LegID)"
                         "VALUES ("+str(voteID)+", \""+choice+"\", "+str(legID)+");")
            self.cursor.execute(argument)
            self.cnx.commit()
        except mysql.connector.errors.ProgrammingError as e:
            print "insertVote Error for: "+str(voteID)+" Name: "+fname+" - "+lname+": "+str(e)
        except exceptions.IndexError as e:
            print "insertVote Error: "+str(e)
        except:
            print "insertVote Error: "+str(sys.exc_info()[0])


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