from flask import Flask, render_template, redirect, request, session, jsonify, abort, make_response
from flask_bootstrap import Bootstrap
import sqlite3
from function import hash_code
from flask import flash



app = Flask(__name__)
app.config['SECRET_KEY'] = 'nemo'
bootstrap = Bootstrap(app)




@app.route('/')
def home ():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')






@app.route('/Characters/')
def Characterrs():
    return render_template('Characters.html')



@app.route('/Development/')
def  Development():
	return render_template('Development.html')




@app.errorhandler(404)
def page_not_found(error):
  return "Sorry, we couldn't find the page you requested.", 404


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = hash_code(request.form.get('password'))


        conn = sqlite3.connect('db.db')
        cur = conn.cursor()
        try:

            sql = 'SELECT 1 FROM USER WHERE USERNAME=? AND PASSWORD=?'
            is_valid_user = cur.execute(sql, (username, password)).fetchone()


        except:
            flash('Wrong user name or password！')
            return render_template('login.html')
        finally:
            conn.close()

        if is_valid_user:

            session['is_login'] = True
            session['name'] = username
            return redirect('/index')
        else:
            flash('Wrong user name or password！')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/monster')
def monster():
    return render_template('monster.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm')

        if username and password and confirm_password:
            if password != confirm_password:
                flash('Inconsistent password entered twice！')
                return render_template('register.html', username=username)

            conn = sqlite3.connect('db.db')
            cur = conn.cursor()

            sql_same_user = 'SELECT 1 FROM USER WHERE USERNAME=?'
            same_user = cur.execute(sql_same_user, (username,)).fetchone()
            if same_user:
                flash('Username already exists！')
                return render_template('register.html', username=username)

            sql_insert_user = 'INSERT INTO USER(USERNAME, PASSWORD) VALUES (?,?)'
            cur.execute(sql_insert_user, (username, hash_code(password)))
            conn.commit()
            conn.close()

            return redirect('/login')
        else:
            flash('All fields must be entered！')
            if username:
                return render_template('register.html', username=username)
            return render_template('register.html')
    return render_template('register.html')


@app.route('/logout')
def logout():

    if session.get('is_login'):
        session.clear()
        return redirect('/')
    return redirect('/')


@app.route('/video')
def video():
    return render_template('video.html')


@app.route('/api/adduser', methods=['GET', 'POST'])
def add_user():
    if request.json:
        username = request.json.get('username', '').strip()
        password = request.json.get('password')
        confirm_password = request.json.get('confirm')

        if username and password and confirm_password:
            if password != confirm_password:
                return jsonify({'code': '400', 'msg': 'The password does not match twice!'}), 400

            conn = sqlite3.connect('db.db')
            cur = conn.cursor()

            sql_same_user = 'SELECT 1 FROM USER WHERE USERNAME=?'
            same_user = cur.execute(sql_same_user, (username,)).fetchone()
            if same_user:
                return jsonify({'code': '400', 'msg': 'Username already exists'}), 400

            sql_insert_user = 'INSERT INTO USER(USERNAME, PASSWORD) VALUES (?,?)'
            cur.execute(sql_insert_user, (username, hash_code(password)))
            conn.commit()
            sql_new_user = 'SELECT id,username FROM USER WHERE USERNAME=?'
            user_id, user = cur.execute(sql_new_user, (username,)).fetchone()
            conn.close()
            return jsonify({'code': '200', 'msg': 'Account generation succeeded！', 'newUser': {'id': user_id, 'user': user}})
        else:

            return jsonify({'code': '404', 'msg': 'Incomplete request parameters!'})
    else:
        abort(400)


@app.route('/api/testjson', methods=['GET', 'POST'])
def test_json():
    if 'x' in request.json:
        print(request.json)
        return jsonify(request.json)
    else:
        abort(400)


@app.route('/api/mock', methods=['GET', 'POST'])
def mock():

    if request.method == 'GET':
        res = []
        for arg in request.args.items():
            res.append(arg)
        res = dict(res)
        return jsonify(res)
    elif request.method == 'POST':
        return jsonify(request.json)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
