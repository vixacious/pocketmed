from flask import Flask,render_template, request,url_for,json, redirect
from flask_sqlalchemy import SQLAlchemy

#creamos la aplicacion Flask
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'kurama'

#Creamos la base de datos
db=SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(50))
    apellido=db.Column(db.String(50))
    email=db.Column(db.String(50))
    cedula=db.Column(db.Integer())
    seguro_medico=db.Column(db.String(50))
    password=db.Column(db.String(50))


    def __init__(self,nombre,apellido,email,cedula,seguro_medico,password):
    
        self.nombre=nombre
        self.apellido=apellido
        self.email=email
        self.cedula=cedula
        self.seguro_medico=seguro_medico
        self.password=password

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre= db.Column(db.String(50))
    apellido=db.Column(db.String(50))
    cedula=db.Column(db.Integer())
    especialidad=db.Column(db.String(50))
    seguro_medico=db.Column(db.String(50))
    hospital=db.Column(db.String(50))
    horario=db.Column(db.String(50))

    def __init__(self,nombre,apellido,cedula,especialidad,seguro_medico,hospital,horario):

        self.nombre=nombre
        self.apellido=apellido
        self.cedula=cedula
        self.especialidad=especialidad
        self.seguro_medico=seguro_medico
        self.hospital=hospital
        self.horario=horario 

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    id_usuario=db.Column(db.Integer,db.ForeignKey('user.id'))
    doctor = db.Column(db.String,db.ForeignKey('doctor.id'))
    reserva= db.Column(db.String)

    def __init__(self,id_usuario,doctor,turnos):
        self.id_usuario=id_usuario
        self.doctor=doctor
        self.reserva = turnos

#create all, base de datos
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup',methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        nombre_usuario= request.form['name']
        apellido_usuario=request.form['apellido']
        email_usuario=request.form['email']
        cedula_usuario=request.form['CI']
        seguro_usuario=request.form['seguro_medico']
        contrasenha=request.form['password']
        #creamos un objeto para estirar de la base de datos

        usuario = User(nombre_usuario, apellido_usuario, email_usuario, cedula_usuario, seguro_usuario, contrasenha)
        
        db.session.add(usuario)
        db.session.commit()

        global usuario_actual
        usuario_actual=usuario.id

        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        nombre_usuario= request.form['username'] 
        contrasenha=request.form['password']

       # buscar el usuario en la base de datos
        usuario_registrado = User.query.filter_by(nombre=nombre_usuario).first()
       
       #si el usuario existe
        if usuario_registrado is not None:
            #si la contrasenha es correcta

            if usuario_registrado.password == contrasenha:

                global usuario_actual
                usuario_actual= usuario_registrado.id

                return redirect(url_for('home'))
            else:
                return 'La contrasenha es incorrecta'
        else:
            return 'El ususario no existe'

    return render_template('iniciosesion.html')


@app.route('/especialidad', methods=['GET','POST'])
def especialidad():
    #Obtener las especialidades
    especialidades_query = Doctor.query.all()
    #creamos una lista para almacenar las especialidades
    especialidades = []
    #recorro los datos recibidos
    for i in especialidades_query:
        # si la especialidad ya se encuentra en la lista 
        if i.especialidad not in especialidades:
            especialidades.append(i.especialidad)

    #lo mandamos a jinja, html
    return render_template('especialidades.html',especialidades=especialidades)


@app.route('/doctores/<especialidad>', methods=['GET','POST'])
def doctores(especialidad):
    doctores_query = Doctor.query.filter_by(especialidad=especialidad).all()
    doctores = []

    for i in doctores_query:
        doctores.append(f'{i.nombre}')
    return render_template('doctores.html', doctores = doctores_query)


@app.route('/reserva/<id_doctor>',methods=['GET'])
def reserva(id_doctor):
    doctor_elegido = Doctor.query.filter_by(id=id_doctor).first()
    horarios_marcacados = json.loads(doctor_elegido.horario)
    print(horarios_marcacados)
    return render_template("horariosdoc.html", horarios = horarios_marcacados, id_doctor = id_doctor)


@app.route('/crear_reserva/<id_doctor>&<reserva>', methods = ['GET'])
def reservar(id_doctor, reserva):
    doctor_elegido = Doctor.query.filter_by(id=id_doctor).first()
    horarios_marcacados = json.loads(doctor_elegido.horario)
    id_usuario = usuario_actual
    horarios_marcacados[reserva]=1
    horarios_marcacados=json.dumps(horarios_marcacados)
    doctor_elegido.horario=horarios_marcacados
    reserva_db = Reserva(id_usuario,doctor_elegido.id,reserva)
    db.session.add(reserva_db)
    db.session.commit()
    return render_template('ok.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port= 8000)