from .models import *
from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify

import requests
import re
# regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
regex = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

app = Flask(__name__)


# @app.errorhandler(Exception)
# def server_error(err):
#     app.logger.exception(err)
#     return render_template('error.html'), 500

@app.route('/')
def showIndex():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    local = localtime()
    return render_template('dashboard.html', local=local)

@app.route('/user')
def user():
    user = user_all()
    local = localtime()
    return render_template('user.html', user=user, local=local)

@app.route('/log')
def loging():
    log = log_query()
    local = localtime()
    return render_template('log.html', log=log, local=local)

@app.route('/ruangsidang')
def ruang_sidang():
    ruang = ruangsidang()
    local = localtime()
    return render_template('ruangsidang.html', ruang=ruang, local=local)

@app.route('/ruangkelas')
def ruang_kelas():
    ruang = kelaspengganti()
    local = localtime()
    return render_template('ruangkelas.html', ruang=ruang, local=local)

@app.route('/admin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['your_username']
        password = request.form['your_pass']

        if not Login(username).verify_password(password):
            flash('gagal masuk!', 'error')
        else:
            session['username'] = username
            flash('Berhasil Masuk', 'success')
            #send notif
            token = '898847072:AAG1ivqjsSfi-P-EAcfLmcbNLz84YE1wvY8'
            id = 1194303548
            nama = nodes.match('User', username=username).first()
            nama = nama['namalengkap']
            text = nama + ' baru saja login di webbot!'
            base_url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={id}&text={text}'
            requests.get(base_url)
            return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        namalengkap = request.form['namalengkap']
        username = request.form['username']
        email = request.form['email']
        password = request.form['pass']
        repassword = request.form['re_pass']

        if len (namalengkap) == 0:
            flash('Nama lengkap tidak boleh kosong!')
        elif len (username) == 0:
            flash('Username tidak boleh kosong!')
        elif len (username) < 6:
            flash('Username setidaknya 6 karakter')
        elif not (re.search(regex,email)):
            flash('format email salah!')
        elif len (password) < 6:
            flash('Password minimal 6 karakter!')
        elif not password == repassword:
            flash('Password tidak sama!')
        elif not User(username , email).register(namalengkap, password):
            flash('Username atau Email sudah digunakan!')
        else:
            session['username'] = username
            flash('Berhasil mendaftar')
            return redirect(url_for('showIndex'))
    
    return render_template('signup.html')

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/logout')
def logout():
    username = session.pop('username', None)
    flash('Logged out.')
    #send notif
    token = '898847072:AAG1ivqjsSfi-P-EAcfLmcbNLz84YE1wvY8'
    id = 1194303548
    nama = nodes.match('User', username=username).first()
    nama = nama['namalengkap']
    text = nama + ' baru saja keluar dari webbot!'
    base_url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={id}&text={text}'
    requests.get(base_url)
    return redirect(url_for('showIndex'))

@app.route('/user/delete_user', methods=['GET','POST'])
def delete_user():
    if request.method == 'POST':
        req = request.get_json()
        req = req.get('id')
        id = int(req)
        if deleteuser(id):
            flash('Berhasil dihapus')
        else:
            flash('Gagal')
            return redirect(url_for('user'))
        
    return render_template('dashboard.html')