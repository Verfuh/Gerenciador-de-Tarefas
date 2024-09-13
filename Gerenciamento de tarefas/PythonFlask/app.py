from os import abort
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from db import db
from models import *
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_session import Session



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dados.db"
db.init_app(app)
app.secret_key = "super secret key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


#ROUTES

#Rotas de usuário |CRIAÇÃO|EDIÇÃO|LOGIN|
@app.route('/')
def index():
    users = db.session.query(User).all()
    return render_template('index.html', users = users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/edit/<int:id>', methods = ['GET','POST'])
def editar(id):

    users = db.session.query(User).filter_by(id=id).first()
    if request.method == 'GET':
        return render_template('edit.html', users = users)
    
    elif request.method == 'POST':
        username = request.form['usernameForm']
        password = request.form['passwordForm']
        users.username = username
        users.password = password
        db.session.commit()
        return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('tasks'))
        
        else:
            print('Usuário ou senha inválidos')
            return redirect(url_for('tasks'))

    return render_template('login.html')


@app.route('/delete/<int:id>')
def deletar(id):

    users = db.session.query(User).filter_by(id=id).first()
    db.session.delete(users)
    db.session.commit()
    return redirect(url_for('index'))



#Rotas de tarefas |CRIAÇÃO|EDIÇÃO|

@app.route('/tasks', methods=['GET'])
@login_required
def tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=user_tasks)
    

@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')

        status = request.form.get('status', 'pending')
        new_task = Task(title=title, description=description, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template('create_task.html')


@app.route('/tasks/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        return redirect(url_for('tasks'))

    new_status = request.form['status']
    task.status = new_status
    db.session.commit()
    return redirect(url_for('tasks'))


@app.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':

        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form['status']

        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template('edit_task.html', task=task)


@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):

    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('tasks'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)
