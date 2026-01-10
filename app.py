from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date, time

app = Flask(__name__)
app.secret_key = "secretkey123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sep2.db'

db = SQLAlchemy(app)


# Relationships
#doctor patient relationship(many-to-many)
doc_pat_relation = db.Table('doc_pat_relation',
                    db.Column('doc_id', db.Integer, db.ForeignKey('doctor.doc_id'), primary_key = True),
                    db.Column('pat_id', db.Integer, db.ForeignKey('patient.pat_id'), primary_key = True))


# Models
# class User(db.Model):
#     user_id = db.Column(db.Integer, primary_key=True)
#     roles = db.Column(db.String(10), nullable=False)

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key = True)
    admin_name = db.Column(db.String(20), nullable = False)
    admin_phone_no = db.Column(db.Integer, nullable = False)
    admin_email = db.Column(db.String(20), nullable = False, unique = True)
    admin_password = db.Column(db.String(100), nullable = False)

class Doctor(db.Model):
    doc_id = db.Column(db.Integer, primary_key = True)
    doc_name = db.Column(db.String(20), nullable = False)
    doc_gender = db.Column(db.String(10), nullable = False)
    doc_phone_no = db.Column(db.Integer, nullable = False)
    doc_email = db.Column(db.String(20), nullable = False, unique = True)
    doc_special = db.Column(db.String(20), nullable = False)
    doc_exp = db.Column(db.Integer, nullable = False)
    doc_qual = db.Column(db.String(20))
    doc_password = db.Column(db.String(100), nullable = False)
    doc_blacklist = db.Column(db.Boolean, default = False)
    appointments = db.relationship('Appointment',  backref='doctor', lazy=True)
    patient_rel = db.relationship(
    'Patient',
    secondary='doc_pat_relation',
    backref=db.backref('doctor_rel', lazy=True)
    )
    availability = db.relationship('Availability', backref = 'doctor')
    specialization = db.relationship('Doctor_Specialization', backref='doctor')
    history = db.relationship('History', backref='doctor')
    # user = db.relationship('User', backref='doctor')
    # the relationship should be written in one part coz we are using one's primary key as foreignkey for many


class Patient(db.Model):
    pat_id = db.Column(db.Integer, primary_key = True)
    pat_name = db.Column(db.String(20), nullable = False)
    pat_phone_no = db.Column(db.Integer, nullable = False)
    pat_email = db.Column(db.String(20), nullable = False, unique = True)
    pat_password = db.Column(db.String(100), nullable = False)
    pat_blacklist = db.Column(db.Boolean, default = False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    history = db.relationship('History', backref='patient')
    # user = db.relationship('User', backref='patient')


class Appointment(db.Model):
    app_id = db.Column(db.Integer, primary_key = True)
    pat_app_id = db.Column(db.Integer, db.ForeignKey('patient.pat_id'))
    pat_name = db.Column(db.String(100))
    doc_app_id = db.Column(db.Integer, db.ForeignKey('doctor.doc_id'))
    doc_name = db.Column(db.String(100))
    dept_name = db.Column(db.String(100))
    app_time = db.Column(db.String(20))
    app_date = db.Column(db.String(20))
    app_status = db.Column(db.Boolean, default = False)
    app_action = db.Column(db.Boolean, default = False)
    app_cancel = db.Column(db.Boolean, default = False)



class Doctor_Specialization(db.Model):
    special_id = db.Column(db.Integer, primary_key = True)
    special_name = db.Column(db.String(50), nullable = False)
    special_doc_id = db.Column(db.Integer, db.ForeignKey('doctor.doc_id'))
    special_description = db.Column(db.String(200))


class Unique_Department(db.Model):
    __tablename__ = 'unique_department'

    unique_id = db.Column(db.Integer, primary_key = True)
    unique_dept = db.Column(db.String(50), unique = True)
    dept_overview = db.relationship(
        'Dept_Overview',
        backref='unique_department',
        uselist=False
    )
    # up_relation = db.relationship('Upcoming_Appointments', backref='unique_dept')
    # dept_overview = db.Column(db.String(500), unique = True)


class Dept_Overview(db.Model):
    __tablename__ = 'dept_overview'

    dept_overview_id = db.Column(db.Integer, primary_key = True)
    unique_dept_id = db.Column(
        db.Integer,
        db.ForeignKey('unique_department.unique_id'),
        unique=True
    )
    unique_dept_description = db.Column(db.String(300))


class Availability(db.Model):
    avail_id = db.Column(db.Integer, primary_key = True)
    avail_doc_id = db.Column(db.Integer, db.ForeignKey('doctor.doc_id'))
    avail_date = db.Column(db.String(15))
    morning_time = db.Column(db.String(20))
    morning_avail = db.Column(db.Boolean, default = False)
    evening_time = db.Column(db.String(20))
    evening_avail = db.Column(db.Boolean, default = False)
    # up_relation = db.relationship('Upcoming_Appointments', backref='availability')


class History(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.pat_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doc_id'))

    visit_no = db.Column(db.Integer)
    visit_type = db.Column(db.String(10))
    test_done = db.Column(db.String(100))
    diagnosis = db.Column(db.String(100))
    prescription = db.Column(db.String(100))
    medicine = db.Column(db.String(500))
    # up_relation = db.relationship('Upcoming_Appointments', backref='history')

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(30))
    user_role = db.Column(db.String(10))


# Flask code
@app.route('/', methods = ['GET', 'POST'])
def home():

    # return 'database'
    return render_template('home.html')

# only for patient
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('r_name')
        phone_num = request.form.get('r_phone#')
        email = request.form.get('r_e_mail')
        password = request.form.get('r_pass')

        new_patient = Patient(pat_name=name, pat_phone_no=phone_num, pat_email=email, pat_password=password)

        db.session.add(new_patient)
        db.session.commit()

        add_user = User(
        user_name=new_patient.pat_name,
        user_role="Patient")
        db.session.add(add_user)
        db.session.commit()


        return render_template('login.html')
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('a_name')
        password = request.form.get('a_pass')
        role = request.form.get('role')

        if role == 'admin':
            admin_check = Admin.query.filter_by(admin_name=name, admin_password=password).first()

            if admin_check:
                return redirect(url_for('admin'))
            else:
                return render_template('login.html')
        
        if role == 'doctor':
            doctor_check = Doctor.query.filter_by(doc_name=name, doc_password=password).first()
            
            if doctor_check:
                session['doctor_id'] = doctor_check.doc_id

                return redirect(url_for('doc_login'))
                # return render_template('doctor.html', doctor = doctor_check) #
            else:
                return render_template('login.html')

        if role == 'patient':
            patient_check = Patient.query.filter_by(pat_name=name, pat_password=password).first()

            if patient_check:
                session['patient_id'] = patient_check.pat_id

                return redirect(url_for('pat_login'))
                # return render_template('patient.html', patients = patient_check) # , patient_name = patient_check
            else:
                return render_template('login.html')
            
    return render_template('login.html')



@app.route('/doc_login')
def doc_login():
    doc_id = session.get('doctor_id')
    if not doc_id:
        return redirect(url_for('login'))

    return redirect(url_for('upcoming_appoint_doc'))


@app.route('/pat_login')
def pat_login():

    pat_id = session.get('patient_id')

    if not pat_id:
        return redirect(url_for('login'))
    
    patient = Patient.query.get(pat_id)
    
    return redirect(url_for('patient', pat_id = patient.pat_id))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    admin_detail = Admin.query.all()

    # Initialize variables so GET request won't break else they wont be sent to html
    results = None
    search_role = None
    search_val = None

    appoint = Appointment.query.all()

    if request.method == 'POST':

        search_val = request.form.get('search_value')
        search_role = request.form.get('value')

        if search_role == 'Doctor':
            results = Doctor.query.filter(Doctor.doc_name.ilike(f"%{search_val}%")).all()
        
        elif search_role == 'Patient':
            results = Patient.query.filter(Patient.pat_name.ilike(f"%{search_val}%")).all()
        
        elif search_role == 'Department':
            results = Doctor.query.filter(Doctor.doc_special.ilike(f"%{search_val}%")).all()
        
        else:
            return f"No data found"

    return render_template('admin.html', admins = admin_detail, 
                           results = results,
                           search_val = search_val,
                           search_role = search_role,
                           appoint = appoint)


# to display doctors in admin_doc
@app.route('/admin/doc' )
def admin_doc():
    all_doctors = Doctor.query.all()
   
    return render_template('admin_doc.html', doctors=all_doctors)

@app.route('/admin/pat')
def admin_pat():
    all_patients = Patient.query.all()

    return render_template('admin_pat.html', patients=all_patients)

# create operation by admin
# create doctor by admin
@app.route('/admin/doc/create', methods=['GET', 'POST'])
def create_doc():
    if request.method == 'POST':
        name = request.form.get('f_name')
        gender = request.form.get('gen')
        dept = request.form.get('dept')
        experience = request.form.get('experience')
        degree = request.form.get('degree')
        phone_no = request.form.get('phone#')
        email = request.form.get('email')
        password = request.form.get('pass')

        new_doctor = Doctor(doc_name=name, 
                            doc_gender=gender, 
                            doc_phone_no=phone_no, 
                            doc_email=email, 
                            doc_special=dept, 
                            doc_exp=experience, 
                            doc_qual = degree,
                            doc_password=password)

        db.session.add(new_doctor)
        db.session.commit()
        

        # Add user entry for doctor
        add_user = User(
            user_name = new_doctor.doc_name,
            user_role = "Doctor"
        )
        db.session.add(add_user)
        db.session.commit()


        if dept:
            spec = Doctor_Specialization(
                special_name=dept,
                special_doc_id=new_doctor.doc_id,
                special_description=f"{dept} specialization"
            )
            db.session.add(spec)
            db.session.commit()

        existing = Unique_Department.query.filter_by(unique_dept=dept).first()

        if not existing:
            add_dept = Unique_Department(unique_dept = dept)
            db.session.add(add_dept)
            db.session.commit()

        doctor = new_doctor
        if doctor:
            date1 = 21
            for _ in range(7):
                date1 += 1
                avail = Availability(avail_doc_id = doctor.doc_id, 
                                     avail_date = f"{date1}/1/2025", 
                                     morning_time = '08:00am to 12:00pm', 
                                     evening_time = '05:00pm to 09:00pm')
                
                db.session.add(avail)
                db.session.commit()
            

        return redirect(url_for('admin_doc'))
    return render_template('create_doc.html')

# update table by admin
# table_name.attributr_name=edit_name
@app.route('/update_doc/<int:doc_id>', methods=['GET', 'POST'])
def update_doc(doc_id):
    doctor = Doctor.query.get_or_404(doc_id)

    if request.method == 'POST':
        doctor.doc_name = request.form.get('f_name')
        doctor.doc_gender = request.form.get('gen')
        doctor.doc_phone_no = request.form.get('phone#')
        doctor.doc_email = request.form.get('email')
        doctor.doc_special = request.form.get('dept')
        doctor.doc_exp = request.form.get('experience')
        doctor.doc_password = request.form.get('pass')

        db.session.commit()

        return redirect(url_for('admin_doc'))
    
    return render_template('update_doc.html', doctor=doctor)

# delete doctor by admin
@app.route('/admin/doc/delete_doc/<int:doc_id>')
def delete_doc(doc_id):

    doctor = Doctor.query.get_or_404(doc_id)

    db.session.delete(doctor)
    db.session.commit()

    return redirect(url_for('admin_doc'))

# blacklist a doctor by admin
@app.route('/admin/doc/blacklist_doc/<int:doc_id>')
def blacklist_doc(doc_id):

    doctor = Doctor.query.get(doc_id)

    if doctor.doc_blacklist:
        doctor.doc_blacklist = False
    else:
        doctor.doc_blacklist = True

    db.session.commit()

    return redirect(url_for('admin_doc'))


@app.route('/provide_availability/<int:doc_id>')
def provide_availability(doc_id):
    doctor = Doctor.query.get_or_404(doc_id)

    # fetch ALL availability rows for this doctor
    availability_list = Availability.query.filter_by(avail_doc_id=doc_id).all()

    return render_template(
        'doc_availability.html',
        doctor=doctor,
        availability_list=availability_list
    )


@app.route('/check_mrng_avail/<int:avail_id>')
def check_mrng_avail(avail_id):
    availability = Availability.query.get_or_404(avail_id)
    availability.morning_avail = not availability.morning_avail
    db.session.commit()
    return redirect(url_for('provide_availability', doc_id=availability.avail_doc_id))


@app.route('/check_eve_avail/<int:avail_id>')
def check_eve_avail(avail_id):
    availability = Availability.query.get_or_404(avail_id)
    availability.evening_avail = not availability.evening_avail
    db.session.commit()
    return redirect(url_for('provide_availability', doc_id=availability.avail_doc_id))


# edit patient by admin
@app.route('/update_pat/<int:pat_id>', methods=['GET', 'POST'])
def update_pat(pat_id):
    patient = Patient.query.get_or_404(pat_id)
    print(patient)

    if request.method == 'POST':
        patient.pat_name = request.form.get('f_name')
        patient.pat_phone_no = request.form.get('phone#')
        patient.pat_email = request.form.get('email')
        patient.pat_pass = request.form.get('pass')

        db.session.commit()

        return redirect(url_for('admin_pat'))
    
    return render_template('update_pat.html', patient = patient)


# delete patient by admin
@app.route('/admin/pat/delete_pat/<int:pat_id>')
def delete_pat(pat_id):

    patient = Patient.query.get_or_404(pat_id)

    db.session.delete(patient)
    db.session.commit()

    return redirect(url_for('admin_pat'))

# blacklist a patient by admin
@app.route('/admin/pat/blacklist_pat/<int:pat_id>')
def blacklist_pat(pat_id):

    patient = Patient.query.get(pat_id)

    if patient.pat_blacklist:
        patient.pat_blacklist = False
    else:
        patient.pat_blacklist = True

    db.session.commit()

    return redirect(url_for('admin_pat'))


@app.route('/dept/<int:unique_dept_id>')
def dept_overview(unique_dept_id):
    department = Unique_Department.query.get_or_404(unique_dept_id)
 
    overview = department.dept_overview.unique_dept_description if department.dept_overview else "No overview available"

    # Doctors
    doctors = Doctor.query.filter_by(doc_special=department.unique_dept).all()

    return render_template(
        'dept_overview.html',
        department=department,
        overview=overview,
        doctors=doctors
        # availability = availability
    )


@app.route('/doc_profile/<int:doc_id>')
def doc_profile(doc_id):
    doctor = Doctor.query.get_or_404(doc_id)

    return render_template('doc_profile.html', doctor=doctor)


@app.route('/doc_dashboard/<int:doc_id>')
def doc_dashboard(doc_id):
    doctor = Doctor.query.get(doc_id)

    return render_template('doc_availibility', doctor = doctor)


# patient dashboard
@app.route('/patient/<int:pat_id>')
def patient(pat_id):
    patient = Patient.query.get_or_404(pat_id)
    # department = Doctor_Specialization.query.all()

    departments = Unique_Department.query.all()
    appoint = Appointment.query.filter_by(pat_app_id=pat_id).all()

    return render_template('patient.html', patient = patient, departments = departments, appoint=appoint) #


# view patient history
@app.route('/patient_history/<int:pat_id>')
def patient_history(pat_id):

    patient = Patient.query.get(pat_id)
    histories = History.query.filter_by(patient_id=pat_id).all()

    return render_template('patient_history.html', patient = patient, histories=histories)


# patient logout
@app.route('/patient_logout/<int:pat_id>')
def patient_logout(pat_id):
    # patient = Patient.query.get(pat_id)
    session.pop('patient_id', None)
    return render_template('home.html')


# edit patient profile by patient
@app.route('/edit_pat/<int:pat_id>', methods=['GET', 'POST'])
def edit_pat_profile(pat_id):
    patient = Patient.query.get_or_404(pat_id)

    if request.method == 'POST':
        patient.pat_name = request.form.get('f_name')
        patient.pat_phone_no = request.form.get('phone#')
        patient.pat_email = request.form.get('email')
        patient.pat_pass = request.form.get('pass')

        db.session.commit()

        return redirect(url_for('patient', pat_id=patient.pat_id))
        # return render_template('patient.html', patients = patient)

    return render_template('edit_profile_by_pat.html', patient = patient)



@app.route('/patient_history_update/<int:pat_id>', methods=['GET', 'POST'])
def patient_history_update(pat_id):

    # patient = Patient.query.filter_by(pat_id = Appointment.pat_app_id).first()
    # pat_id = session.get('patient_id')
    # doc_id = session.get('doctor_id')
    doctor = Doctor.query.get(session.get('doctor_id'))
    patient = Patient.query.get(pat_id)

    if request.method == 'POST':
        visit_no = request.form.get('visit_no')
        visit_type = request.form.get('visit_type')
        test = request.form.get('test')
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        medicines = request.form.get('medicines')

        add_details = History(visit_no = visit_no, 
                              patient_id = patient.pat_id,
                              doctor_id = doctor.doc_id,
                              visit_type = visit_type, 
                              test_done = test, 
                              diagnosis = diagnosis, 
                              prescription = prescription, 
                              medicine = medicines)

        db.session.add(add_details)
        db.session.commit()  

        return redirect(url_for('patient_history', pat_id=patient.pat_id))
    
    patient_history = History.query.filter_by(patient_id=patient.pat_id).all()

    return render_template('pat_history_update.html', patient = patient, histories = patient_history)


@app.route('/doc_actions/<int:app_id>')
def doc_actions(app_id):
    appointment = Appointment.query.get_or_404(app_id)

    appointment.app_status = not appointment.app_status
    db.session.commit()

    return redirect(url_for('upcoming_appoint_doc'))


@app.route('/book_appointment/<int:doc_id>')
def book_appointment(doc_id):
    book = Availability.query.filter_by(avail_doc_id = doc_id).all()


    return render_template('book_appoint.html', book=book)


@app.route('/book_slot/<int:avail_id>', methods=['GET', 'POST'])
def book_slot(avail_id):
    availability = Availability.query.get_or_404(avail_id)
    # appoint = Availability.query.filter_by(doc_app_id = avail_doc_id).first()
    pat_id = session.get('patient_id') 
    

    appointment = Appointment(
        pat_app_id = pat_id,
        doc_app_id = availability.avail_doc_id,   # doctor ID
        app_date   = availability.avail_date,
        app_time   = "Morning" if availability.morning_avail else "Evening",
        app_status = True
    )

    db.session.add(appointment)
    db.session.commit()

    return redirect(url_for('book_appointment', doc_id=availability.avail_doc_id))


@app.route('/cancel_app_doc/<int:app_id>')
def cancel_app_doc(app_id):
    appoint = Appointment.query.get(app_id)

    db.session.delete(appoint)
    db.session.commit()

    return redirect(url_for('upcoming_appoint_doc'))


@app.route('/cancel_app_pat/<int:app_id>')
def cancel_app_pat(app_id):

    appoint = Appointment.query.get(app_id)
    pat_id = appoint.pat_app_id

    db.session.delete(appoint)
    db.session.commit()

    return redirect(url_for('patient', pat_id = pat_id))


@app.route('/upcoming_appoint_admin')
def upcoming_appoint_sdmin():
    appoint = Appointment.query.all()

    return render_template('admin.html', appoint = appoint)


@app.route('/upcoming_appoint_doc')
def upcoming_appoint_doc():
    doc_id = session.get('doctor_id')
    if not doc_id:
        return redirect(url_for('login'))

    appoint = Appointment.query.filter_by(doc_app_id=doc_id).all()
    doctor = Doctor.query.get(doc_id)

    return render_template('doctor.html', doctor=doctor, appoint=appoint)


with app.app_context():
    db.drop_all()
    db.create_all()


    admin_info = Admin.query.get(1)
    if not admin_info:
        add = Admin(admin_id = 1,
               admin_name = "Aditya",
               admin_phone_no = 123654789,
               admin_email = 'arkulkarni85@gmail.com',
               admin_password = 123
        )
        db.session.add(add)
        db.session.commit()

        add_user = User(user_name = add.admin_name, user_role = 'Admin')
        db.session.add(add_user)
        db.session.commit()
    
    doc_info = Doctor.query.get(1)
    pat_info = Patient.query.get(1)


    # # #  # Step 1: Preload Unique_Department
    dept_names = ["Cardiologist", "Neurologist", "Urologist", "Dentist", "Dermatologist"]
    for name in dept_names:
        existing = Unique_Department.query.filter_by(unique_dept=name).first()
        if not existing:
            db.session.add(Unique_Department(unique_dept=name))
    db.session.commit()

    # Step 2: Preload Dept_Overview
    overviews = {
        "Cardiologist": "A cardiologist specializes in diagnosing and treating diseases related to the heart and blood vessels. They manage conditions such as hypertension, heart attacks, arrhythmias, and provide long-term cardiac care and preventive guidance.",

        "Neurologist": "A neurologist focuses on disorders of the brain, spinal cord, and nervous system. They diagnose and treat conditions like migraines, epilepsy, stroke, memory disorders, neuropathy, and movement disorders.",

        "Urologist": "A urologist specializes in the urinary tract and male reproductive system. They treat issues such as kidney stones, urinary infections, prostate problems, male infertility, and bladder disorders.",

        "Dentist": "A dentist provides oral health care including diagnosis, treatment, and prevention of issues related to teeth, gums, and mouth. They handle problems like cavities, gum disease, tooth extraction, root canals, and overall dental hygiene.",

        "Dermatologist": "A dermatologist specializes in skin, hair, and nail disorders. They diagnose and treat conditions such as acne, eczema, infections, allergies, hair fall, pigmentation issues, and perform cosmetic skin procedures."
    }

    for name, desc in overviews.items():
        dept = Unique_Department.query.filter_by(unique_dept=name).first()
        if dept and not dept.dept_overview:
            db.session.add(Dept_Overview(unique_dept_id=dept.unique_id, unique_dept_description=desc))
    db.session.commit()


    app.run(debug=True, use_reloader=False) #







