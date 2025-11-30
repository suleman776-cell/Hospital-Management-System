from flask import Flask, render_template, request, redirect, url_for, session, flash
from hospital_dsa import HospitalDSA, DISEASE_SPECIALIST # Import DISEASE_SPECIALIST for registration form

app = Flask(__name__)
app.secret_key = 'your-very-secure-random-key-here-12345' # MUST be changed in production!

ADMIN_EMAIL = 'doctor@gmail.com'
ADMIN_PASSWORD = '4321oladoc'

h = HospitalDSA()
h.generate_doctors(count=80, start_id=2000)

@app.route('/')
def index():
    # Pass all relevant counts to the dashboard template
    stats = {
        'patients': len(h.patients),
        'appointments': h.appointments.count(),
        'doctors': len(h.doctors),
        'emergency': h.emergency.count()
    }
    return render_template('index.html', stats=stats)

@app.route('/register', methods=['GET','POST'])
def register():
    pid = None
    doctors = []
    specialization = None
    
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        disease = request.form.get('disease')
        priority = int(request.form.get('priority', 5))
        emergency_flag = request.form.get('emergency') == 'on'

        if not name or not age or not disease:
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('register'))
        
        try:
            age = int(age)
        except ValueError:
            flash('Age must be a valid number.', 'danger')
            return redirect(url_for('register'))

        # Register patient and get suggestions in one go
        pid, specialization, doctors = h.register_patient_and_suggest_doctors(
            name, age, disease, priority=priority, emergency=emergency_flag
        )
        flash(f'Patient **{pid}** registered for {specialization} consultation.', 'success')
        
    # Pass the specialist map and current doctors for the GET request form
    return render_template(
        'register.html', 
        doctors=doctors, 
        spec=specialization, 
        pid=pid, 
        disease_map=DISEASE_SPECIALIST
    )

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    try:
        pid = int(request.form.get('pid'))
        doctor_id = int(request.form.get('doctor_id'))
    except ValueError:
        flash('Invalid Patient or Doctor ID.', 'danger')
        return redirect(url_for('register')) # Redirect back to where registration happened
        
    time_str = request.form.get('time') or 'ASAP'
    
    success, msg = h.book_specialist_appointment(pid, doctor_id, time_str)
    
    # Use category in flash message for better styling
    flash(msg, 'success' if success else 'danger')
    
    # Redirect to appointments page after successful booking
    return redirect(url_for('appointments'))


@app.route('/appointments')
def appointments():
    # List Appointments (Queue)
    return render_template('appointments.html', appointments=h.list_appointments())

@app.route('/doctors')
def doctors():
    # List Doctors (Hash Map)
    return render_template('doctors.html', doctors=h.doctors.values())

@app.route('/emergency')
def emergency():
    # List Emergency Patients (Priority Heap)
    return render_template('emergency.html', data=h.get_emergency_list())

@app.route('/billing', methods=['GET','POST'])
def billing():
    if request.method == 'POST':
        try:
            pid = int(request.form.get('pid'))
            amount = float(request.form.get('amount'))
        except ValueError:
            flash('Invalid Patient ID or Bill Amount.', 'danger')
            return redirect(url_for('billing'))
        
        ok = h.add_bill(pid, amount)
        if ok:
            flash(f'Bill of Rs{amount:,.2f} added for Patient ID {pid}.', 'success')
        else:
            flash(f'Patient ID {pid} not found in the system.', 'danger')
        return redirect(url_for('billing'))
        
    # Get Bills (Stack)
    return render_template('billing.html', bills=h.get_bills())

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Welcome Admin.', 'info')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Access Denied.', 'danger')
            return redirect(url_for('admin_login'))
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        flash('Please login to access the Admin Dashboard.', 'warning')
        return redirect(url_for('admin_login'))
        
    return render_template(
        'admin_dashboard.html', 
        patients=h.all_patients(), # Sorted patients from BST traversal
        appointments=h.list_appointments(),
        emergency=h.get_emergency_list(),
        bills=h.get_bills(),
        doctors=h.doctors.values()
    )

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Setting debug=True is good for development
    app.run(debug=True)