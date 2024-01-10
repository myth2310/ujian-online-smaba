from application import app
from flask import Flask,render_template,request, redirect,url_for,flash,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib
import os
from datetime import datetime
from flask_mail import Mail, Message
# import requests
# from twilio.rest import Client

app.secret_key = 'your_secret_key'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'e-learning-smaba'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "achmadmiftahudin2310@gmail.com"
app.config['MAIL_PASSWORD'] = "usjdicuiisydiact"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'achmadmiftahudin2310@gmail.com'  
mail = Mail(app)

@app.route("/send_mail")
def send_mail():
    mail_message = Message(
        'Hi! Don’t forget to follow me for more articles!',
        recipients=['19090137.miftahudin@student.poltektegal.ac.id']
    )
    mail_message.body = "This is a test"
    mail.send(mail_message)
    return "Mail has been sent"

@app.route('/')
@app.route('/login')
def login():
    if 'islogin' in session:
         return redirect(url_for('home'))
    else:
        return render_template('login.html')

#Admin Page
@app.route('/home')
def home():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute('''
            SELECT users.*
            FROM users 
            WHERE users.id_user = %s
        ''',(session['id_user'],))
        data = curl.fetchone()

        curl.execute("SELECT COUNT(*) FROM users WHERE level='Siswa'")
        result_siswa = curl.fetchone()
        count_siswa = result_siswa['COUNT(*)']

        curl.execute("SELECT COUNT(*) FROM users WHERE level='Guru'")
        result_guru = curl.fetchone()
        count_guru = result_guru['COUNT(*)']

        curl.execute("SELECT COUNT(*) FROM kelas")
        result_kelas = curl.fetchone()
        count_kelas = result_kelas['COUNT(*)']

        curl.execute("SELECT COUNT(*) FROM mapel")
        result_mapel = curl.fetchone()
        count_mapel = result_mapel['COUNT(*)']

        return render_template('admin/index.html',data=data,count_siswa=count_siswa,count_guru=count_guru,count_kelas=count_kelas,count_mapel=count_mapel)
    else:
        return redirect(url_for('login'))

@app.route('/profil')
def profil():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute('''
            SELECT users.*, kelas.kelas,jurusan.jurusan
            FROM users 
            LEFT JOIN kelas ON kelas.id_kelas = users.id_kelas
            LEFT JOIN jurusan ON users.id_jurusan = jurusan.id_jurusan
            WHERE users.id_user = %s
        ''',(session['id_user'],))
        data = curl.fetchone() 
        return render_template('profil.html',data=data)
    else:
        return redirect(url_for('login'))

@app.route('/form-edit-profil/<int:id_user>', methods=['GET'])
def formEditProfil(id_user):
    if 'islogin' in session:
        curl = mysql.connection.cursor()
        curl.execute('''
                SELECT users.*, kelas.kelas,jurusan.jurusan
                FROM users 
                LEFT JOIN kelas ON kelas.id_kelas = users.id_kelas
                LEFT JOIN jurusan ON users.id_jurusan = jurusan.id_jurusan
                WHERE users.id_user = %s
        ''',(session['id_user'],))
        data = curl.fetchone() 
        return render_template('formProfil.html',data=data)
    else:
        return redirect(url_for('login'))

@app.route('/edit-profil/<int:id_user>', methods=['GET','POST'])
def updateProfil(id_user):
    nama_ortu = request.form['nama_ortu']
    email_ortu = request.form['email_ortu']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET nama_ortu = %s, email_ortu = %s WHERE id_user = %s", (nama_ortu,email_ortu, id_user))
    mysql.connection.commit()
    flash('Data Profil Berhasil diupdate')
    return redirect(url_for('profil'))

@app.route('/data-siswa')
def dataSiswa():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute('''
            SELECT users.*, kelas.kelas,jurusan.jurusan
            FROM users 
            LEFT JOIN kelas ON kelas.id_kelas = users.id_kelas
            LEFT JOIN jurusan ON users.id_jurusan = jurusan.id_jurusan
            WHERE users.level = 'Siswa'
        ''')
        siswa = curl.fetchall() 
        return render_template('admin/siswa.html',siswa=siswa)
    else:
        return redirect(url_for('login'))

@app.route('/data-guru')
def dataGuru():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute('''
                SELECT users.*, mapel.mapel
                FROM users 
                LEFT JOIN mapel ON mapel.id_mapel = users.id_mapel
                WHERE users.level = 'Guru'
            ''')
        guru = curl.fetchall() 
        return render_template('admin/guru.html',guru=guru)
    else:
        return redirect(url_for('login'))
    
@app.route('/data-admin')
def dataAdmin():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE level = 'Admin' ")
        admin = curl.fetchall()
        return render_template('admin/admin.html',admin=admin)
    else:
        return redirect(url_for('login'))
   
@app.route('/form-registrasi')
def formRegistrasi():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM mapel")
        mapel = curl.fetchall()

        curl.execute("SELECT * FROM kelas")
        kelas = curl.fetchall()

        curl.execute("SELECT * FROM jurusan")
        jurusan = curl.fetchall()
        return render_template('admin/formRegistrasi.html',kelas=kelas,mapel=mapel,jurusan=jurusan)
    else:
        return redirect(url_for('login'))
    
@app.route('/kelas')
def kelas():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute('''
                SELECT kelas.*, jurusan.jurusan
                FROM kelas 
                LEFT JOIN jurusan ON kelas.id_jurusan = jurusan.id_jurusan
            ''')
        kelas = curl.fetchall()

        curl.execute("SELECT * FROM jurusan")
        jurusan = curl.fetchall()
        return render_template('admin/kelas.html',kelas=kelas,jurusan=jurusan)
    else:
        return redirect(url_for('login'))
   
@app.route('/mapel')
def mapel():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute('''
                SELECT mapel.*, jurusan.jurusan
                FROM mapel
                LEFT JOIN jurusan ON mapel.id_jurusan = jurusan.id_jurusan
            ''')
        mapel = curl.fetchall()

        curl.execute("SELECT * FROM jurusan")
        jurusan = curl.fetchall()
        return render_template('admin/mapel.html',mapel=mapel,jurusan=jurusan)
    else:
        return redirect(url_for('login'))

@app.route('/jurusan')
def jurusan():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM jurusan")
        jurusan = curl.fetchall()
        return render_template('admin/jurusan.html',jurusan=jurusan)
    else:
        return redirect(url_for('login'))

#Page Guru
@app.route('/hasil')
def hasilUjian():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "SELECT hasil_ujian.*,users.nama,kelas.kelas FROM hasil_ujian \
         JOIN kategori ON hasil_ujian.id_kategori = kategori.id_kategori \
         JOIN users ON kategori.id_user = users.id_user \
         JOIN kelas ON users.id_kelas = users.id_kelas \
         WHERE kategori.id_user = %s"
        data = (session['id_user'],)
        curl.execute(query, data)
        hasil_ujian = curl.fetchall()
        print(hasil_ujian)
        return render_template('guru/hasilUjian.html',hasil_ujian=hasil_ujian)
    else:
        return redirect(url_for('login'))
    
@app.route('/tema-soal')
def temaSoal():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM kategori WHERE id_user = %s",(session['id_user'],))
        kategori = curl.fetchall()
      
        curl.execute('''
            SELECT users.*, mapel.mapel
            FROM users
            LEFT JOIN mapel ON mapel.id_mapel = users.id_mapel
            WHERE users.id_user = %s
        ''',(session['id_user'],))
        users = curl.fetchone()

        return render_template('guru/tema.html',kategori=kategori,users=users)
    else:
        return redirect(url_for('login'))

@app.route('/soal')
def soal():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        curl.execute('''
            SELECT soal.*,kategori.kategori,kategori.tanggal
            FROM soal
            LEFT JOIN kategori ON kategori.id_kategori = soal.id_kategori
            LEFT JOIN users ON users.id_user = kategori.id_user
            WHERE users.id_user = %s
        ''', (session['id_user'],))
        soal = curl.fetchall()

        return render_template('guru/soal.html',soal=soal)
    else:
        return redirect(url_for('login'))

@app.route('/view-ujian/<int:id_kategori>', methods=['GET'])
def viewUjian(id_kategori):
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = '''
                SELECT kategori.*
                FROM kategori 
                LEFT JOIN soal ON soal.id_kategori = kategori.id_kategori
                WHERE kategori.id_kategori = %s
            '''
        curl.execute(query, (id_kategori,))
        detail = curl.fetchone()

        return render_template('guru/tinjau.html', soal=soal,detail=detail,nomor_soal=nomor_soal,prev_data=prev_data, next_data=next_data)
    else:
        return redirect(url_for('login'))


@app.route('/form-soal')
def formSoal():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM kategori WHERE id_user = %s",(session['id_user'],))
        kategori = curl.fetchall()

        curl.execute("SELECT * FROM mapel")
        mapel = curl.fetchall()
        return render_template('guru/formSoal.html',kategori=kategori,mapel=mapel)
    else:
        return redirect(url_for('login'))
        
#Page Siswa
@app.route('/hasil-ujian')
def hasil():
    if 'islogin' in session:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = '''
                SELECT hasil_ujian.*,kategori.kategori,mapel.mapel
                FROM hasil_ujian 
                LEFT JOIN users ON hasil_ujian.id_user = users.id_user
                LEFT JOIN kategori ON hasil_ujian.id_kategori = kategori.id_kategori
                LEFT JOIN mapel ON mapel.id_mapel = kategori.id_mapel
                WHERE hasil_ujian.id_user = %s
            '''
        curl.execute(query,(session['id_user'],))
        data = curl.fetchall()
        return render_template('siswa/hasil.html',data=data)
    else:
        return redirect(url_for('login'))

@app.route('/ujian/<int:id_kategori>', methods=['GET','POST'])
def ujian(id_kategori):
    if 'islogin' in session:
        # Masukkan hasil ujian ke dalam database
        if request.method == 'GET':
            cur = mysql.connection.cursor()
            insert_query = "INSERT INTO hasil_ujian (id_user, id_kategori) VALUES (%s, %s)"
            cur.execute(insert_query, (session['id_user'], id_kategori))
            mysql.connection.commit()

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = '''
                SELECT kategori.*,mapel.mapel
                FROM kategori 
                LEFT JOIN soal ON soal.id_kategori = kategori.id_kategori
                LEFT JOIN mapel ON mapel.id_mapel = kategori.id_mapel
                WHERE kategori.id_kategori = %s
            '''
        curl.execute(query, (id_kategori,))
        detail = curl.fetchone()

        users_query = '''
            SELECT users.*, kelas.kelas
            FROM users 
            LEFT JOIN kelas ON kelas.id_kelas = users.id_kelas
            WHERE users.id_user = %s
        '''
        curl.execute(users_query, (session['id_user'],))
        data = curl.fetchone()

    
        curl.execute("SELECT * FROM soal WHERE id_kategori = %s ORDER BY RAND()", (id_kategori,))
        soal = curl.fetchall()

        return render_template('ujian.html', soal=soal,detail=detail,data=data,id_kategori=id_kategori)
    else:
        return redirect(url_for('login'))

@app.route('/daftar-ujian')
def listUjian():
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute('''
        SELECT kategori.*, mapel.mapel
        FROM kategori
        LEFT JOIN mapel ON mapel.id_mapel = kategori.id_mapel
        WHERE kategori.id_kategori IN (
            SELECT DISTINCT id_kategori
            FROM soal
        )
    ''')
    ujian = curl.fetchall()


    curl.execute('''
        SELECT users.*
        FROM users 
        WHERE users.id_user = %s
    ''',(session['id_user'],))
    data = curl.fetchone()

    if data['email_ortu'] is None:
        return redirect(url_for('profil'))

    curl.execute('''
                SELECT kategori.id_kategori
                FROM kategori
                JOIN hasil_ujian ON kategori.id_kategori = hasil_ujian.id_kategori 
                WHERE hasil_ujian.id_user = %s
            ''', (session['id_user'],))

    ujianSelesai = [item['id_kategori'] for item in curl.fetchall()]

    current_time = get_current_time()
    formatted_datetime = current_time.strftime("%H:%M")
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")

    return render_template('siswa/listUjian.html',ujian=ujian,ujianSelesai=ujianSelesai,formatted_date= formatted_date,formatted_datetime=formatted_datetime)

def get_current_time():
    return datetime.now()

#Action Guru
@app.route('/insert-jenis-ujian', methods=['POST'])
def insertKategori():
    id_user = session.get('id_user')
    id_mapel = request.form['id_mapel']
    kategori = request.form['kategori']
    tanggal = request.form['tanggal']
    time_start = request.form['time_start']
    time_done = request.form['time_done']
    # Convert strings to datetime objects
    format_str = '%H:%M'  # The format
    time_start_obj = datetime.strptime(time_start, format_str)
    time_done_obj = datetime.strptime(time_done, format_str)

    # Calculate the duration in minutes
    duration = (time_done_obj - time_start_obj).seconds // 60
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO kategori (id_user,id_mapel,kategori,tanggal,time_start,time_done,duration) VALUES (%s,%s,%s,%s,%s,%s,%s)",(id_user,id_mapel,kategori,tanggal,time_start,time_done,duration))
    mysql.connection.commit()
    return redirect(url_for('temaSoal'))

@app.route('/insert-soal', methods=['POST'])
def insertSoal():
    id_kategori = request.form['id_kategori']
    pertanyaan = request.form['pertanyaan']
    jawaban_a = request.form['jawaban_a']
    jawaban_b = request.form['jawaban_b']
    jawaban_c = request.form['jawaban_c']
    jawaban_d = request.form['jawaban_d']
    correct = request.form['correct']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO soal (id_kategori, pertanyaan, jawaban_a, jawaban_b, jawaban_c, jawaban_d, correct) VALUES (%s, %s, %s, %s, %s, %s, %s)", (id_kategori, pertanyaan, jawaban_a, jawaban_b, jawaban_c, jawaban_d, correct))
    mysql.connection.commit()
    flash('Soal Berhasil ditambahkan')
    return redirect(url_for('soal'))

@app.route('/update-soal/<int:id_soal>', methods=['POST'])
def updateSoal(id_soal):
    id_kategori = request.form['id_kategori']
    pertanyaan = request.form['pertanyaan']
    jawaban_a = request.form['jawaban_a']
    jawaban_b = request.form['jawaban_b']
    jawaban_c = request.form['jawaban_c']
    jawaban_d = request.form['jawaban_d']
    correct = request.form['correct']
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE soal SET id_kategori=%s, pertanyaan=%s, jawaban_a=%s, jawaban_b=%s, jawaban_c=%s, jawaban_d=%s, correct=%s WHERE id_soal=%s", (id_kategori, pertanyaan, jawaban_a, jawaban_b, jawaban_c, jawaban_d, correct, id_soal))
    mysql.connection.commit()
    flash('Soal Berhasil diperbarui')
    return redirect(url_for('soal'))


def generate_slug(text):
    text = text.lower()
    text = ''.join(e for e in text if (e.isalnum() or e == ' '))
    text = text.replace(' ', '-')
    return text

#Action Admin
@app.route('/insert-user', methods=['POST'])
def insertUser():
    nama = request.form['nama']
    email = request.form['email']
    status = request.form['status']
    level = request.form['level']
    id_mapel = request.form['id_mapel']
    id_jurusan = request.form['id_jurusan']
    id_kelas = request.form['id_kelas']
    password = request.form['password'] 
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (nama,email,status,level,id_mapel,id_jurusan,id_kelas,password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(nama,email,status,level,id_mapel,id_jurusan,id_kelas,hashed_password))
    mysql.connection.commit()
    return redirect(url_for('home'))

@app.route('/update-user/<int:id_user>', methods=['POST'])
def updateUser(id_user):
    nama = request.form['nama']
    email = request.form['email']
    status = request.form['status']
    level = request.form['level']
    id_mapel = request.form['id_mapel']
    id_jurusan = request.form['id_jurusan']
    id_kelas = request.form['id_kelas']
    password = request.form['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cur = mysql.connection.cursor()
    cur.execute('''
        UPDATE users 
        SET nama = %s, email = %s, status = %s, level = %s, id_mapel = %s, id_jurusan = %s, id_kelas = %s, password = %s 
        WHERE id_user = %s
    ''', (nama, email, status, level, id_mapel, id_jurusan, id_kelas, hashed_password, id_user))
    
    mysql.connection.commit()
    return redirect(url_for('home'))


@app.route('/insert-kelas',methods=['POST'])
def insertKelas():
    id_jurusan = request.form['id_jurusan']
    kelas = request.form['kelas']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO kelas (id_jurusan,kelas) VALUES (%s,%s)" ,(id_jurusan,kelas))  
    mysql.connection.commit()
    return redirect(url_for('kelas'))

@app.route('/insert-mapel',methods=['POST','GET'])
def insertMapel():
    mapel= request.form['mapel']
    id_jurusan = request.form['id_jurusan']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO mapel (mapel,id_jurusan) VALUES (%s,%s)", (mapel, id_jurusan))
    mysql.connection.commit()
    return redirect(url_for('mapel'))

@app.route('/insert-jurusan',methods=['POST','GET'])
def insertJurusan():
    jurusan= request.form['jurusan']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO jurusan (jurusan) VALUES (%s)", (jurusan,))
    mysql.connection.commit()
    return redirect(url_for('jurusan'))

@app.route('/view-users/<int:id_user>', methods=['GET'])
def viewUsers(id_user):
    curl = mysql.connection.cursor()
    query = '''
        SELECT users.*,mapel.mapel,jurusan.jurusan,kelas.kelas
        FROM users 
        LEFT JOIN mapel ON users.id_mapel = mapel.id_mapel
        LEFT JOIN jurusan ON users.id_jurusan = jurusan.id_jurusan
        LEFT JOIN kelas ON users.id_kelas = kelas.id_kelas
        WHERE users.id_user = %s
    '''
    curl.execute(query, (id_user,))
    data = curl.fetchone()

    curl.execute("SELECT * FROM mapel")
    mapel = curl.fetchall()

    curl.execute("SELECT * FROM jurusan")
    jurusan = curl.fetchall()

    curl.execute("SELECT * FROM kelas")
    kelas = curl.fetchall()

    return render_template('admin/formEdit.html', data=data,mapel=mapel,kelas=kelas,jurusan=jurusan)

@app.route('/delete-users/<int:id_user>', methods=['GET'])
def deleteUsers(id_user):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id_user = %s", (id_user,))
    mysql.connection.commit()
    flash('Data Berhasil dihapus')
    return redirect(url_for('home'))

@app.route('/update-jurusan/<int:id_jurusan>', methods=['POST', 'GET'])
def updateJurusan(id_jurusan):
    jurusan = request.form['jurusan']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE jurusan SET jurusan = %s WHERE id_jurusan = %s", (jurusan, id_jurusan))
    mysql.connection.commit()
    flash('Data Jurusan Berhasil diupdate')
    return redirect(url_for('jurusan'))

@app.route('/delete-jurusan/<int:id_jurusan>', methods=['GET'])
def deleteJurusan(id_jurusan):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM jurusan WHERE id_jurusan = %s", (id_jurusan,))
    cur.execute("DELETE FROM kelas WHERE id_jurusan = %s", (id_jurusan,))
    cur.execute("DELETE FROM mapel WHERE id_jurusan = %s", (id_jurusan,))
    cur.execute("DELETE FROM users WHERE id_jurusan = %s", (id_jurusan,))
    mysql.connection.commit()
    flash('Data Jurusan Berhasil dihapus')
    return redirect(url_for('jurusan'))

@app.route('/update-kelas/<int:id_kelas>', methods=['POST', 'GET'])
def updateKelas(id_kelas):
    id_jurusan = request.form['id_jurusan']
    kelas = request.form['kelas']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE kelas SET id_jurusan = %s ,kelas = %s WHERE id_kelas = %s", (id_jurusan,kelas, id_kelas))
    mysql.connection.commit()
    flash('Data Kelas Berhasil diupdate')
    return redirect(url_for('kelas'))

@app.route('/delete-kelas/<int:id_kelas>', methods=['GET'])
def deleteKelas(id_kelas):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM kelas WHERE id_kelas = %s", (id_kelas,))
    cur.execute("DELETE FROM users WHERE id_kelas = %s", (id_kelas,))
    mysql.connection.commit()
    flash('Data  Kelas Berhasil dihapus')
    return redirect(url_for('kelas'))

@app.route('/update-mapel/<int:id_mapel>', methods=['POST', 'GET'])
def updateMapel(id_mapel):
    id_jurusan = request.form['id_jurusan']
    mapel = request.form['mapel']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE mapel SET id_jurusan = %s ,mapel = %s WHERE id_mapel = %s", (id_jurusan,mapel, id_mapel))
    mysql.connection.commit()
    flash('Data Mapel Berhasil diupdate')
    return redirect(url_for('mapel'))

@app.route('/delete-mapel/<int:id_mapel>', methods=['GET'])
def deleteMapel(id_mapel):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM mapel WHERE id_mapel = %s", (id_mapel,))
    cur.execute("DELETE FROM users WHERE id_mapel = %s", (id_mapel,))
    mysql.connection.commit()
    flash('Data Mapel Berhasil dihapus')
    return redirect(url_for('mapel'))

@app.route('/delete-soal/<int:id_soal>', methods=['GET'])
def deleteSoal(id_soal):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM soal WHERE id_soal = %s", (id_soal,))
    mysql.connection.commit()
    flash('Data Soal Berhasil dihapus')
    return redirect(url_for('soal'))

@app.route('/delete-kategori/<int:id_kategori>', methods=['GET'])
def deleteKategori(id_kategori):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM kategori WHERE id_kategori = %s", (id_kategori,))
    cur.execute("DELETE FROM soal WHERE id_kategori = %s", (id_kategori,))
    cur.execute("DELETE FROM hasil_ujian WHERE id_kategori = %s", (id_kategori,))
    mysql.connection.commit()
    flash('Data Kategori Berhasil dihapus')
    return redirect(url_for('temaSoal'))

@app.route('/update-kategori/<int:id_kategori>', methods=['POST'])
def updateKategori(id_kategori):
    id_user = session.get('id_user')
    id_mapel = request.form['id_mapel']
    kategori = request.form['kategori']
    tanggal = request.form['tanggal']
    time_start = request.form['time_start']
    time_done = request.form['time_done']
    # Convert strings to datetime objects
    format_str = '%H:%M'  # The format
    time_start_obj = datetime.strptime(time_start, format_str)
    time_done_obj = datetime.strptime(time_done, format_str)

    # Calculate the duration in minutes
    duration = (time_done_obj - time_start_obj).seconds // 60
    cur = mysql.connection.cursor()
    cur.execute("UPDATE kategori SET id_user=%s, id_mapel=%s, kategori=%s, tanggal=%s, time_start=%s, time_done=%s, duration=%s WHERE id_kategori=%s", (id_user, id_mapel, kategori, tanggal, time_start, time_done, duration, id_kategori))
    mysql.connection.commit()
    return redirect(url_for('temaSoal'))

@app.route('/view-soal/<int:id_soal>', methods=['GET'])
def viewSoal(id_soal):
    curl = mysql.connection.cursor()
    query = '''
                SELECT soal.*, kategori.kategori, kategori.tanggal
                FROM soal 
                LEFT JOIN kategori ON soal.id_kategori = kategori.id_kategori
                WHERE soal.id_soal = %s
            '''
    curl.execute(query, (id_soal,))
    data = curl.fetchone()

    curl.execute("SELECT * FROM kategori WHERE id_user = %s",(session['id_user'],))
    kategori = curl.fetchall()
    return render_template('guru/editSoal.html', data=data,kategori=kategori)


#Auth/Login
@app.route('/action-login', methods=['GET', 'POST'])
def actionLogin():
    if 'islogin' in session:
        return redirect(url_for('home'))
    if request.method == 'POST' and 'nama' in request.form and 'password' in request.form:
        nama = request.form['nama']
        password = request.form['password'] 
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE nama = %s', (nama,))
        account = cursor.fetchone()
        if account and check_password(password, account['password']):
            session['islogin'] = True
            session['id_user'] = account['id_user']
            session['nama'] = account['nama']
            session['level'] = account['level']
           
            if account['level'] == 'Admin':
                return redirect(url_for('home'))
            elif account['level'] == 'Guru':
                return redirect(url_for('home'))
            elif account['level'] == 'Siswa':
                return redirect(url_for('home'))
        else:
            flash("User Tidak Ditemukan atau Password Salah")
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

def check_password(input_password, stored_password):
    hashed_input_password = hashlib.sha256(input_password.encode()).hexdigest()
    return hashed_input_password == stored_password

def get_correct_answers(id_kategori):
    correct_answers = {}
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_soal, correct FROM soal WHERE id_kategori = %s", (id_kategori,))
    rows = cur.fetchall()
    cur.close()
    print(rows)
    for row in rows:
        question_id = row['id_soal'] 
        correct_option = row['correct'] 
        print("Nilai id_soal:", question_id)
        print("Nilai correct:", correct_option)
        correct_answers[question_id] = correct_option 
    return correct_answers

def calculate_score(user_answers, correct_answers):
    correct_count = 0
    wrong_count = 0
    for question_id, user_choice in user_answers.items():
        if question_id.startswith('question_'):
            question_id = question_id[9:]
            correct_option = correct_answers.get(int(question_id), '')
            if correct_option and user_choice == correct_option:
                correct_count += 1
            else:
                wrong_count += 1
    return correct_count, wrong_count

# Fungsi pengiriman pesan WhatsApp
# def send_whatsapp_message(body,to_number):
#     account_sid = 'AC000d3808cdccad5d9f40263b14919d05'
#     auth_token = '2a215775b7305df78588878f710671d3'
#     client = Client(account_sid, auth_token)

#     message = client.messages.create(
#         from_='whatsapp:+14155238886',
#         body=body,
#         to=f'whatsapp:+{to_number}'
#     )
#     return message.sid

@app.route('/submit-quiz/<int:id_kategori>', methods=['POST'])
def submit_quiz(id_kategori):
    if request.method == 'POST':
        curl = mysql.connection.cursor()
        curl.execute('''
                SELECT users.*
                FROM users 
                WHERE users.id_user = %s
        ''',(session['id_user'],))
        data = curl.fetchone()
        email_ortu = data['email_ortu'] 
        nama_ortu = data['nama_ortu'] 
        nama = data['nama'] 

        user_answers = request.form
        correct_answers = get_correct_answers(id_kategori)
        print("Jawaban Pengguna:", user_answers)
        print("Jawaban yang Benar:", correct_answers)
        correct_count, wrong_count = calculate_score(user_answers, correct_answers)
        score = correct_count * 10
        total_questions = len(correct_answers)

        cur = mysql.connection.cursor()
        update_query = "UPDATE hasil_ujian SET hasil=%s, total_soal=%s, jumlah_betul=%s, jumlah_salah=%s WHERE id_user=%s AND id_kategori=%s"
        cur.execute(update_query, (score, total_questions,  correct_count, wrong_count, session['id_user'], id_kategori))
        mysql.connection.commit()

        # Kirim pesan WhatsApp
        mail_message = Message(
        f"Hasil Ujian {nama} | SMAN Balapulang 1",
        recipients=[email_ortu]
        )
        mail_message.body =  f"Assalamualaikum Wr. Wb Selamat Siang Ibu/Bapak {nama_ortu} \n\nSelaku orang tua/wali {nama}, kami sampaikan bahwa {nama} telah meneyelesaikan ujian dan mendapatkan Hasil ujian :  \n Score {score} dari {total_questions} soal. \n Jumlah jawaban benar: {correct_count}. \n Jumlah jawaban salah: {wrong_count}.\n\n  Terima kasih kami sampaikan, Wassalamualaikum Wr. Wb \n\n Ttd, Akademik SMAN Balapulang 1"
        mail.send(mail_message)
    
        return render_template('score.html', score=score, total=total_questions, wrong_count=wrong_count,correct_count=correct_count)

@app.route('/add_violation_data', methods=['POST'])
def add_violation_data():
    if request.method == 'POST':
        data = request.get_json()
        id_user = data.get('id_user')
        id_kategori = data.get('id_kategori')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE hasil_ujian SET pelanggaran = COALESCE(pelanggaran, 0) + 1 WHERE id_user = %s AND id_kategori = %s", (id_user, id_kategori))
        mysql.connection.commit()

        pelanggaran_query = 'SELECT pelanggaran FROM hasil_ujian WHERE id_user = %s AND id_kategori = %s'
        cur.execute(pelanggaran_query, (id_user, id_kategori))
        pelanggaran_result = cur.fetchone()
        pelanggaran = pelanggaran_result['pelanggaran'] if pelanggaran_result else 0

        return str(pelanggaran)  


@app.route('/score')
def score():
    return render_template('score.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



