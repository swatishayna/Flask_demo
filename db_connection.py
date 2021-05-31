from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from flask import Flask, request, jsonify
import mysql.connector as connection
#pip install xlrd==1.2.0
import xlrd
import csv
import ssl
import pymongo


class Connection:
    def __init__(self):
        self.database = request.json['database']
        if self.database == "cassandra" or self.database == "mysql":
            self.path = request.json['path']
            self.clientid = request.json['clientid']
            self.clientsecret = request.json['clientsecret']
            self.selectpath = self.path + "\\secure-connect-test1.zip"
        else:
            self.client = request.json['client']
            self.keyspace = request.json['keyspace']


    def cassandra(self):

        cloud_config = {
            'secure_connect_bundle': self.selectpath
        }
        auth_provider = PlainTextAuthProvider(self.clientid, self.clientsecret)
        cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        global session
        session = cluster.connect()
        return session

    def mysql(self):
        session = connection.connect(host=self.path, user=self.clientid, passwd=self.clientsecret, use_pure=True)
        return session
    def mongodb(self):
        client_cloud = pymongo.MongoClient(self.client, ssl_cert_reqs=ssl.CERT_NONE)
        self.db = client_cloud[self.keyspace]
        return self.db


class select:
    def select(tablename,operation,session,database):

        query = "select * from " + tablename
        if database == "cassandra":

            row = session.execute(query)
            if operation == "create":
                column = row.column_names
                return column
            else:
                column = row.all()
                return column

        elif database == "mysql":

            cur = session.cursor()
            cur.execute(query)
            rows = cur.fetchall()

            for i in rows:
                print(i)
            return rows




class query(Connection,select):
    def excutequery(self,command):
        self.keyspace = request.json['keyspace']
        self.tablename = request.json['tablename']

        self.command = command
        super(query, self).__init__()
        if self.command == "create" and self.database != "mongodb":
            self.columns = request.json['columns']
            self.query = "CREATE TABLE " + self.tablename + "(" + self.columns + ")"
        elif self.command=="insert" and self.database != "mongodb":
            self.columns = request.json['columns']
            self.values = request.json['values']
            self.query = "INSERT INTO " + self.tablename + "(" + self.columns + ")" + "values" + "(" + self.values + ")"
        elif self.command=="update" and self.database != "mongodb":
            self.column_value = request.json['column_value']
            self.where_col_val = request.json['where_col_val']
            self.query = "UPDATE " + self.tablename + " SET " + self.column_value + " WHERE " + self.where_col_val
        elif self.command=="truncate" and self.database != "mongodb":
            self.query = "Truncate " + self.tablename
        elif self.command == "bulkinsertion" and self.database != "mongodb":

            self.total_col = int(request.json['total_col'])
            self.columns = request.json['columns']
            self.file = request.json['file']

        self.database = request.json['database']

        if self.database=="cassandra":
            super().cassandra()
            session.execute("USE " + self.keyspace)
            if self.command != "bulkinsertion":
                try:
                    result = session.execute(self.query)
                    return result
                except:
                    return "Table Already exits"
                finally:
                    select_obj = select.select(self.tablename, self.command, session, "cassandra")
                    return select_obj
            elif self.command == "bulkinsertion":
                self.holder = ((self.total_col - 1) * "?,") + "?"
                #query_bulk = "INSERT INTO "+ self.tablename + "("+self.columns + ") VALUES (" + self.holder + ")"

                prepared = session.prepare("INSERT INTO "+ self.tablename + "("+self.columns + ") VALUES (" + self.holder + ")")


                with open(self.file, "r") as data:
                    data_csv = csv.reader(data, delimiter=",")
                    next(data_csv)
                    print(data_csv)
                    for count, row in enumerate(data_csv):
                        if count >= 14:
                            break

                        row[0] = int(row[0])
                        row[-1] = int(row[-1])
                        print(row)

                        try:
                            session.execute(prepared, row)
                        except Exception as e:
                            print("Values cant be inserted")

                select_obj = select.select(self.tablename, self.command, session, "cassandra")
                return select_obj
            else:
                pass

        elif self.database =="mysql":

            super(query, self).__init__()
            self.session = connection.connect(host=self.path, user=self.clientid,database = self.keyspace, passwd=self.clientsecret, use_pure=True)
            cur = self.session.cursor()
            if self.command != "bulkinsertion":
                try:
                    result = cur.execute(self.query)
                    if self.command != "create":
                        self.session.commit()
                except:
                    print("TABLE AlREADY EXISTS")
                finally:
                    select_obj = select.select(self.tablename, self.command,self.session,"mysql")
                    return select_obj
            elif self.command =="bulkinsertion":
                self.holder = ((self.total_col - 1) * "%s,") + "%s"
                self.query = "INSERT INTO " + self.tablename + " (" + self.columns + ")" + "values" + "(" + self.holder + ")"
                self.file = request.json['file']
                a = xlrd.open_workbook(self.file)
                l = []
                sheet = a.sheet_by_index(0)
                sheet.cell_value(0, 0)

                cur = self.session.cursor()
                for row, i in enumerate(range(1, 14)):
                    x = tuple(sheet.row_values(i))

                    try:
                        cur.execute(self.query, x)
                        print(row, "inserted")
                        self.session.commit()
                    except Exception as e:
                        l.append(row)
                select_obj = select.select(self.tablename, self.command, self.session, "mysql")
                return select_obj
            else:
                pass
        elif self.database=="mongodb":
            super(query, self).__init__()
            super().mongodb()
            if self.command=="create":
                # to create collection

                self.collection= self.db[self.tablename]
                return "Table Created"


