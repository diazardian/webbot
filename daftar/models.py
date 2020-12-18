from py2neo import Graph, Node, Relationship
from py2neo.matching import *
from passlib.hash import bcrypt
from datetime import datetime
from datetime import date as tgl
import os
import uuid
from googletrans import Translator
tr = Translator()

# url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474/')
# username = os.environ.get('neo4j')
# password = os.environ.get('secret')

# graph = Graph(url + '/db/data/', username=username, password=password)
uri = "bolt://127.0.0.1:7687"
user = "neo4j"
password = "secret"

graph = Graph(uri=uri, user=user, password=password)
nodes = NodeMatcher(graph)

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def find(self):
        user = nodes.match('User', username=self.username).first()
        return user
    
    def find_email(self):
        email = nodes.match('User', email=self.email).first()
        return email

    def register(self, namalengkap, password):
        if self.find() is None and self.find_email() is None:
            user = Node('User', username=self.username, email=self.email, namalengkap=(namalengkap), password=bcrypt.encrypt(password), status="unverified")
            graph.create(user)
            return True
        else:
            return False

class Login:
    def __init__(self, username):
        self.username = username
    
    def find(self):
        user = nodes.match('User', username=self.username).first()
        return user

    def verify_password(self, password):
        user = self.find()
        if user:
           return bcrypt.verify(password, user['password'])
        else:
            return False
        
def user_all():
    query = """
    MATCH (user:UserTele)
    WHERE NOT user.role = 'admin'
    RETURN user.userid as id, user.namalengkap as nama, user.prodi as prodi, user.angkatan as angkatan, user.email as email, user.role as role, user.pjkelas as pj
    ORDER BY nama
    """
    return graph.run(query)

def log():
    query = """
    MATCH (user:UserTele)-[:LOGIING]-(log:Log)
    RETURN user.userid as id, user.namalengkap as nama, log.query as query, log.timestamp as jam
    """
    return graph.run(query)

def localtime():
    today_ori = tgl.today()
    hariini = today_ori.strftime('%A')
    hariini = tr.translate(hariini, dest='id', src='en')
    today = today_ori.strftime('%d %B %Y')
    today = tr.translate(today, dest='id', src='en')
    local = hariini.text + ',' + today.text
    return local