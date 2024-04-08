from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración de la conexión a la base de datos MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Agrega la contraseña de tu base de datos
    database="aplicacionesweb"
)
cursor = db.cursor()

# Función para verificar las credenciales del usuario en la base de datos
def verificar_credenciales(usuario, contrasena):
    query = "SELECT * FROM login WHERE usuario = %s AND contrasena = %s"
    cursor.execute(query, (usuario, contrasena))
    usuario = cursor.fetchone()
    if usuario:
        return True
    else:
        return False

# Ruta para la página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if verificar_credenciales(usuario, contrasena):
            session['usuario'] = usuario
            return redirect(url_for('index'))
        else:
            return render_template('login.html', mensaje='Credenciales incorrectas')
    return render_template('login.html', mensaje='')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# Middleware para verificar si el usuario está autenticado
@app.before_request
def requerir_inicio_sesion():
    rutas_autenticadas = ['index', 'agregar', 'eliminar', 'editar']
    if request.endpoint in rutas_autenticadas and 'usuario' not in session:
        return redirect(url_for('login'))

# Ruta para mostrar todos los usuarios
@app.route('/')
def index():
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    return render_template('index.html', usuarios=usuarios)

# Ruta para agregar un nuevo usuario
@app.route('/agregar', methods=['POST'])
def agregar():
    if request.method == 'POST':
        cedula = request.form['cedula']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cursor.execute("INSERT INTO usuarios (cedula, nombre, apellido) VALUES (%s, %s, %s)", (cedula, nombre, apellido))
        db.commit()
        return redirect(url_for('index'))

# Ruta para eliminar un usuario
@app.route('/eliminar/<string:cedula>')
def eliminar(cedula):
    cursor.execute("DELETE FROM usuarios WHERE cedula = %s", (cedula,))
    db.commit()
    return redirect(url_for('index'))


@app.route('/editar/<string:cedula>', methods=['GET', 'POST'])
def editar(cedula):
    if request.method == 'GET':
       
        cursor.execute("SELECT * FROM usuarios WHERE cedula = %s", (cedula,))
        usuario = cursor.fetchone()
        return render_template('editar.html', usuario=usuario)
    elif request.method == 'POST':
   
        nuevo_nombre = request.form['nombre']
        nuevo_apellido = request.form['apellido']
        cursor.execute("UPDATE usuarios SET nombre = %s, apellido = %s WHERE cedula = %s", (nuevo_nombre, nuevo_apellido, cedula))
        db.commit()
        return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)