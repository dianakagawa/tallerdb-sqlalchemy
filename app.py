from flask import Flask, render_template, redirect, request, url_for # server for web app
from flask_sqlalchemy import SQLAlchemy # for database
from flask_wtf import FlaskForm # for forms
from wtforms import StringField, PasswordField, SubmitField, EmailField # for forms
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user # for login


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # database location
app.config['SECRET_KEY'] =  'mysecretkey' # secret key for session
db = SQLAlchemy(app) # database object

login_manager = LoginManager() # login manager config
login_manager.init_app(app)
login_manager.login_view = 'login' 

class LoginForm(FlaskForm): # login form
    email = EmailField('Correo electrónico')
    password = PasswordField('Contraseña')
    submit = SubmitField('Iniciar sesión')

class RegisterForm(FlaskForm): # register form. Vinculo entre la interfaz y la base de datos
    name = StringField('Nombre')
    email = StringField('Correo electrónico')
    password = PasswordField('Contraseña')
    submit = SubmitField('Registrarse')

class User(UserMixin, db.Model): # Modelo de usuario
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Todo(db.Model): # Modelo de tareas
    id = db.Column(db.Integer, primary_key=True)
    description=db.Column(db.String(200))
    is_completed=db.Column(db.Boolean)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id')) # Relación con el modelo de usuario


with app.app_context():
    db.create_all() # create database tables. Esto siempre tiene que estar debajo de los modelos.

@login_manager.user_loader # user loader function. It is used to reload the user object from the user ID stored in the session.
def load_user(user_id):
    return User.query.get(int(user_id)) 

@app.route('/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # desestructurado
        name = form.name.data
        email = form.email.data
        password = form.password.data

        user = User(name=name, email=email, password=password)
        db.session.add(user) # add new user to database
        db.session.commit() # commit changes
        return '<h1>success</h1>'
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                return redirect(url_for('todo'))
            return '<h1>Invalid password</h1>'
        return '<h1>Invalid email</h1>'
    return render_template('login.html', form=form)

@app.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    todos = Todo.query.filter_by(user_id=current_user.id)
    if request.method == 'POST': # add new todo
        description = request.form.get('description') # get todo description from form
        todo = Todo(description=description, is_completed=False, user_id=current_user.id) # create new todo that's false by default
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('todo'))
    return render_template('todo.html', todos=todos)

@app.route('/update/<int:todo_id>') # update todo
@login_required
def update_todo(todo_id):
    todo_to_be_updated = Todo.query.filter_by(id=todo_id).first()
    todo_to_be_updated.is_completed = not todo_to_be_updated.is_completed
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/delete/<int:todo_id>') # delete todo
@login_required
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/logout') # logout
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__': # run app
    app.run(debug=True)
