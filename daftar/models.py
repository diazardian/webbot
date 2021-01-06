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

def log_query():
    query = """
    MATCH (n:Log)
    RETURN n.userid as userid , n.nama as nama, n.query as query, n.timestamp as jam
    ORDER BY jam DESC
    """
    return graph.run(query)

def ruangsidang():
    query = """
    MATCH (a:RuangSidang)-[r:BOOKING_AT]->(b:HistoryRuangSidang)<-[:DELETED_BY]-(u:UserTele)
    MATCH (b:HistoryRuangSidang)<-[:BOOKED_BY]-(us:UserTele)
    RETURN b.jam as jam, a.nama as namaruang, b.acara as acara, b.peserta as peserta, b.tanggal as tanggal, us.namalengkap as nama, b.updateat as timestamp, u.namalengkap as naleng, r.status as status
    """
    return graph.run(query)

def kelaspengganti():
    query = """
    MATCH (kelas:Kelas)<-[:PUNYA_KELAS]-(u:UserTele)<-[:BOOKED_BY]-(brk:BookRuangKelas)
    MATCH (kp:KelasPengganti)-[:BOOK_CLASS]-(brk)-[:CLASS_AT]-(ruang:Ruang)
    RETURN kelas.nama as kelas, kp.nama as matkul, ruang.nama as ruang, brk.hari as hari, brk.jam as jam, brk.status as status
    ORDER BY brk.timestamp
    """
    return graph.run(query)

def deleteuser(id):
    query = Node('UserTele', id=(id))
    return graph.delete(query)

def localtime():
    today_ori = tgl.today()
    hariini = today_ori.strftime('%A')
    hariini = tr.translate(hariini, dest='id', src='en')
    today = today_ori.strftime('%d %B %Y')
    today = tr.translate(today, dest='id', src='en')
    local = hariini.text + ', ' + today.text
    return local