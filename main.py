
import db_connection
from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


app = Flask(__name__)


@app.route('/connect', methods=['GET', 'POST']) # To render Homepage
def connect():
    database = request.json['database']
    conn_obj = db_connection.Connection()
    if database == "cassandra":
        session = conn_obj.cassandra()
    elif database =="mysql":
        session = conn_obj.mysql()
    elif database == "mongodb":
        session = conn_obj.mongodb()

    validation = {"connected" : str(session)}
    return jsonify(validation)


@app.route('/create', methods=['GET', 'POST'])
def create():
    query_obj  = db_connection.query()
    create_obj = query_obj.excutequery("create")
    return jsonify(create_obj)

@app.route('/insert', methods=['GET', 'POST']) # To render Homepage
def insert():
    query_obj = db_connection.query()
    insert_obj = query_obj.excutequery("insert")
    return jsonify(insert_obj)

@app.route('/update', methods=['GET', 'POST'])
def update():
    query_obj = db_connection.query()
    update_obj = query_obj.excutequery("update")
    return jsonify(update_obj)

@app.route('/truncate', methods=['GET', 'POST'])
def truncate():
    query_obj = db_connection.query()
    truncate_obj = query_obj.excutequery("truncate")
    return jsonify(truncate_obj)

@app.route('/bulkinsertion', methods=['GET', 'POST'])
def bulkinsertion_excel():
    query_obj = db_connection.query()
    bulkinsertion_obj = query_obj.excutequery("bulkinsertion")
    return jsonify(bulkinsertion_obj)







if __name__ == '__main__':
    app.run()


