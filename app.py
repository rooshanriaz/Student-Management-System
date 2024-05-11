import dbm
from flask import Flask, render_template, request, redirect, url_for, session, make_response
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

import firebase_admin
from firebase_admin import credentials

from firebase_admin import firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()


app.secret_key = '1PoepThNcgk6MiS1EM3wygyokLzjTNkY'

# Database setup
DB_NAME = 'project'
DB_USER = 'postgres'
DB_PASSWORD = 'pgadmin4'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Function to establish database connection
def create_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Global variable to hold the database connection
db_connection = create_connection()

# Function to add cache-control headers to all responses
def no_cache(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    cur = db_connection.cursor()
    query = sql.SQL("SELECT * FROM Credentials WHERE email=%s AND password=%s AND role=%s")
    cur.execute(query, (email, password, role))

    credentials = cur.fetchone()

    if credentials:
        session['email'] = email
        if role == 'student':
            return redirect(url_for('student'))
        elif role == 'teacher':
            return redirect(url_for('teacher'))
        elif role == 'admin':
            return redirect(url_for('admin'))
    else:
        return "Invalid credentials"

# Function to fetch student information from the database
def get_student_info(email):
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM Students WHERE email = %s", (email,))
        row = cursor.fetchone()

        if row:
            student_info = {
                "student_name": row[1],
                "email": row[2],
                "student_date_of_birth": row[3],
                "student_cgpa": row[4],
                "student_enrollment_year": row[5],
                "student_father_name": row[6],
                "student_cnic": row[7],
                "student_address": row[8],
                "student_program": row[9],
                "student_scholarship": row[11],
                "student_status": row[13]
            }
            return student_info
        else:
            return {'message': 'Email not found in credentials'}

    except psycopg2.Error as e:
        return {'error': str(e)}, 500

# Function to fetch teacher information from the database
def get_teacher_details(email):
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM Teachers WHERE email = %s", (email,))
        teacher_details = cursor.fetchone()

        if teacher_details:
            teacher_info = {
                "teacher_name": teacher_details[1],
                "email": teacher_details[2],
                "teacher_position": teacher_details[3]
            }
            return teacher_info
        else:
            return {"error": "Teacher not found"}

    except psycopg2.Error as e:
        print("Error fetching teacher details:", e)
        return {"error": str(e)}

# Function to get student's program
def get_student_program(email):
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT student_program_name FROM Students WHERE email = %s", (email,))
        program = cursor.fetchone()

        if program:
            return program[0]
        else:
            return None

    except psycopg2.Error as e:
        print("Error fetching student program:", e)
        return None

# Function to get courses by program
def get_courses_by_program(program):
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT course_name, teacher_name FROM Course WHERE program_name = %s", (program,))
        courses = cursor.fetchall()

        return courses

    except psycopg2.Error as e:
        print("Error fetching courses by program:", e)
        return []

# Function to register student courses
def register_student_courses(email, selected_courses):
    try:
        cursor = db_connection.cursor()

        for course in selected_courses:
            cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
            registration_number = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO registrations (course_name, teacher_name, registration_number) VALUES (%s, %s, %s)",
                (course['course_name'], course['teacher_name'], registration_number)
            )

        db_connection.commit()
        print("Courses registered successfully")

    except psycopg2.Error as e:
        db_connection.rollback()
        print("Error registering courses:", e)

# Function to get course details by name
def get_course_by_name(course_name):
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM Course WHERE course_name = %s", (course_name,))
        course = cursor.fetchone()

        if course:
            course_info = {
                "course_name": course[0],
                "teacher_name": course[1],
            }
            return course_info
        else:
            return None

    except psycopg2.Error as e:
        print("Error fetching course details by name:", e)
        return None

@app.route('/registration-confirmation')
def registration_confirmation():
    return render_template('registration_confirmation.html')

@app.route('/register-courses', methods=['GET', 'POST'])
def register_courses():
    email = session.get('email')
    
    if not email:
        return "Email not found in session"

    cursor = db_connection.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT student_program_name FROM Students WHERE email = %s", (email,))
        student_program = cursor.fetchone()

        if student_program:
            program_name = student_program[0]

            cursor.execute("SELECT course_name, teacher_name FROM Course WHERE program_name = %s", (program_name,))
            courses = cursor.fetchall()
            courses_dict = [{'course_name': row[0], 'teacher_name': row[1]} for row in courses]

            response = make_response(render_template('student.html', courses=courses_dict))
            return no_cache(response)
        else:
            return "Student program not found"

    elif request.method == 'POST':
        selected_course_names = request.form.getlist('course')
        cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
        registration_number = cursor.fetchone()[0]

        for course_name in selected_course_names:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE registration_number = %s AND course_name = %s",
                (registration_number, course_name)
            )
            exists = cursor.fetchone()[0]

            if exists == 0:
                cursor.execute(
                    "INSERT INTO registrations (registration_number, course_name, teacher_name) "
                    "VALUES (%s, %s, (SELECT teacher_name FROM Course WHERE course_name = %s))",
                    (registration_number, course_name, course_name)
                )
            else:
                print(f"Course '{course_name}' is already registered by this student.")

        db_connection.commit()
        return redirect(url_for('student'))

@app.route('/unregister-course', methods=['POST'])
def unregister_course():
    email = session.get('email')

    if not email:
        return "Email not found in session"

    course_name = request.form['course_name']
    cursor = db_connection.cursor()
    cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
    registration_number = cursor.fetchone()[0]

    cursor.execute(
        "DELETE FROM registrations WHERE registration_number = %s AND course_name = %s",
        (registration_number, course_name)
    )
    db_connection.commit()

    return redirect(url_for('student'))

# Function to get registered courses
def get_registered_courses(email):
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
        result = cursor.fetchone()

        if not result:
            return []

        registration_number = result[0]
        cursor.execute("SELECT course_name, teacher_name FROM registrations WHERE registration_number = %s", (registration_number,))
        courses = cursor.fetchall()

        registered_courses = [{'course_name': row[0], 'teacher_name': row[1]} for row in courses]
        return registered_courses

    except psycopg2.Error as e:
        print("Error fetching registered courses:", e)
        return []

@app.route('/view-courses')
def view_courses():
    email = session.get('email')
    
    if email:
        cursor = db_connection.cursor()
        cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
        registration_number = cursor.fetchone()

        if not registration_number:
            return "Student registration number not found"

        registration_number = registration_number[0]
        cursor.execute(
            "SELECT course_name, teacher_name FROM registrations WHERE registration_number = %s",
            (registration_number,)
        )
        courses = cursor.fetchall()

        registered_courses = [{'course_name': row[0], 'teacher_name': row[1]} for row in courses]

        response = make_response(render_template('student.html', registered_courses=registered_courses))
        return no_cache(response)
    else:
        return "Email not found in session"

@app.route('/view-students')
def view_students():
    email = session.get('email')
    
    if email:
        cursor = db_connection.cursor()
        cursor.execute("SELECT teacher_name, email, teacher_position FROM Teachers WHERE email = %s", (email,))
        teacher_data = cursor.fetchone()

        if teacher_data:
            teacher_details = {
                'teacher_name': teacher_data[0],
                'email': teacher_data[1],
                'teacher_position': teacher_data[2]
            }

            cursor.execute("SELECT course_name FROM Course WHERE teacher_name = %s", (teacher_data[0],))
            courses = [row[0] for row in cursor.fetchall()]

            enrolled_students = {}
            for course_name in courses:
                cursor.execute(
                    "SELECT s.student_name FROM registrations r "
                    "JOIN Students s ON r.registration_number = s.registration_number "
                    "WHERE r.course_name = %s AND r.teacher_name = %s",
                    (course_name, teacher_data[0])
                )
                enrolled_students[course_name] = [row[0] for row in cursor.fetchall()]

            response = make_response(render_template('teacher.html', teacher_details=teacher_details, enrolled_students=enrolled_students))
            return no_cache(response)
        else:
            return "Teacher details not found."
    else:
        return "Email not found in session."

@app.route('/remove-student', methods=['POST'])
def remove_student():
    course_name = request.form['course_name']
    student_name = request.form['student_name']

    try:
        cursor = db_connection.cursor()
        # Retrieve the registration number based on student name
        cursor.execute("SELECT registration_number FROM Students WHERE student_name = %s", (student_name,))
        registration_number = cursor.fetchone()[0]

        # Delete the registration entry
        cursor.execute("DELETE FROM Registrations WHERE registration_number = %s AND course_name = %s", (registration_number, course_name))
        db_connection.commit()
    except psycopg2.Error as e:
        db_connection.rollback()
        return f"Failed to remove student due to: {e}", 500

    return redirect(url_for('teacher'))  # Redirect back to the teacher view

@app.route('/student')
def student():
    email = session.get('email')

    if email:
        student_info = get_student_info(email)
        response = make_response(render_template('student.html', students=[student_info]))
        return no_cache(response)
    else:
        return "Email not found in session"

@app.route('/teacher')
def teacher():
    email = session.get('email')
    if not email:
        return "Email not found in session", 404
    
    cursor = db_connection.cursor()
    try:
        # Fetch teacher details
        cursor.execute("SELECT teacher_name, email, teacher_position FROM Teachers WHERE email = %s", (email,))
        teacher_details = cursor.fetchone()
        if not teacher_details:
            return "Teacher details not found.", 404
        
        # Fetch courses taught by this teacher along with enrolled students
        cursor.execute("""
            SELECT c.course_name, s.student_name, s.email
            FROM Course c
            LEFT JOIN Registrations r ON c.course_name = r.course_name
            LEFT JOIN Students s ON r.registration_number = s.registration_number
            WHERE c.teacher_email = %s
        """, (email,))
        course_details = cursor.fetchall()
        
        # Organize courses and enrolled students
        courses = {}
        for course_name, student_name, student_email in course_details:
            if course_name not in courses:
                courses[course_name] = []
            if student_name and student_email:  # Ensure that only valid student entries are added
                courses[course_name].append((student_name, student_email))
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return "Database error", 500
    
    # Render the teacher template with course and student details
    return render_template('teacher.html', teacher_details=teacher_details, courses=courses)

@app.route('/admin')
def admin():
    cursor = db_connection.cursor()
    try:
        # Fetch teachers
        cursor.execute("SELECT email, teacher_name FROM Teachers")
        teachers = cursor.fetchall()

        # Fetch courses
        cursor.execute("SELECT course_name FROM Course")
        courses = cursor.fetchall()

    except psycopg2.Error as e:
        print("Database error:", e)
        teachers = []
        courses = []

    # Pass the data to the template
    response = make_response(render_template('admin.html', teachers=teachers, courses=courses))
    return no_cache(response)

@app.route('/insert-teacher', methods=['POST'])
def insert_teacher():
    data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'position': request.form['position'],
        'program_name': request.form['program_name'],
        'password': request.form['password']
    }

    cursor = db_connection.cursor()
    try:
        # First, insert into Credentials
        cursor.execute(
            """INSERT INTO Credentials (email, password, role) VALUES (%s, %s, 'teacher')""",
            (data['email'], data['password'])
        )
        # Then, insert into Teachers
        cursor.execute(
            """INSERT INTO Teachers (teacher_name, email, teacher_position, teacher_program_name) 
            VALUES (%s, %s, %s, %s)""",
            (data['name'], data['email'], data['position'], data['program_name'])
        )
        db_connection.commit()
        return redirect(url_for('admin'))
    except psycopg2.Error as e:
        db_connection.rollback()
        print(f"Error inserting teacher: {e}")
        return "Error inserting teacher", 500

# Update teacher with program name
@app.route('/update-teacher', methods=['POST'])
def update_teacher():
    data = {
        'email': request.form['email'],
        'name': request.form['name'],
        'position': request.form['position'],
        'program_name': request.form['program_name']
    }
    try:
        cursor = db_connection.cursor()
        cursor.execute(
            """UPDATE Teachers SET teacher_name=%s, teacher_position=%s, teacher_program_name=%s 
            WHERE email=%s""",
            (data['name'], data['position'], data['program_name'], data['email'])
        )
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error updating teacher: {e}")
        db_connection.rollback()
        return "Error updating teacher"
    return redirect(url_for('admin'))

# Delete teacher
@app.route('/delete-teacher', methods=['POST'])
def delete_teacher():
    email = request.form['email']
    try:
        cursor = db_connection.cursor()
        # First, remove from Credentials
        cursor.execute("DELETE FROM Credentials WHERE email=%s AND role='teacher'", (email,))
        # Then, remove from Teachers
        cursor.execute("DELETE FROM Teachers WHERE email=%s", (email,))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"Error deleting teacher: {e}")
        db_connection.rollback()
        return "Error deleting teacher"
    return redirect(url_for('admin'))

# Insert student
@app.route('/insert-student', methods=['POST'])
def insert_student():
    data = {
        'registration_number': request.form['registration_number'],
        'name': request.form['name'],
        'email': request.form['email'],
        'dob': request.form['dob'],
        'cgpa': request.form['cgpa'],
        'enrollment_year': request.form['enrollment_year'],
        'father_name': request.form['father_name'],
        'cnic': request.form['cnic'],
        'address': request.form['address'],
        'program': request.form['program'],
        'scholarship': request.form['scholarship'],
        'status': request.form['status'],
        'password': request.form['password']
    }
    try:
        cursor = db_connection.cursor()
        # First, insert into Credentials
        cursor.execute(
            """INSERT INTO Credentials (email, password, role) VALUES (%s, %s, 'student')""",
            (data['email'], data['password'])
        )
        # Then, insert into Students
        cursor.execute(
            """INSERT INTO Students (registration_number, student_name, email, student_date_of_birth,
            student_cgpa, student_enrollment_year, Father_name, student_cnic, student_address,
            student_program_name, student_scholarship, student_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (data['registration_number'], data['name'], data['email'], data['dob'], data['cgpa'],
             data['enrollment_year'], data['father_name'], data['cnic'], data['address'], data['program'],
             data['scholarship'], data['status'])
        )
        db_connection.commit()
        db.collection('students').document(data['email']).set(data)
        return redirect(url_for('admin'))
    except psycopg2.Error as e:
        print(f"Error inserting student: {e}")
        db_connection.rollback()
        #return "Error inserting student"
    return redirect(url_for('admin'))

# Update student
@app.route('/update-student', methods=['POST'])
def update_student():
    email = request.form['email']  # Using email to identify the student
    # Define the updated_data dictionary using form data
    updated_data = {
        'name': request.form.get('name'),  # Using .get to avoid KeyError if key doesn't exist
        'dob': request.form.get('dob'),
        'cgpa': request.form.get('cgpa'),
        'enrollment_year': request.form.get('enrollment_year'),
        'father_name': request.form.get('father_name'),
        'cnic': request.form.get('cnic'),
        'address': request.form.get('address'),
        'program': request.form.get('program'),
        'scholarship': request.form.get('scholarship'),
        'status': request.form.get('status')
    }

    try:
        # Assuming 'db' is your Firestore client instance
        db.collection('students').document(email).update(updated_data)
        return redirect(url_for('admin'))  # Redirect to the 'admin' page or appropriate endpoint
    except Exception as e:
        print(f"Error updating student: {e}")
        return f"Error updating student: {e}", 500

@app.route('/delete-student', methods=['POST'])
def delete_student():
    email = request.form['email']
    cursor = None
    try:
        # Open a cursor to perform database operations
        cursor = db_connection.cursor()

        # Check if the student exists before attempting deletion
        cursor.execute("SELECT registration_number FROM Students WHERE email=%s", (email,))
        student = cursor.fetchone()
        if not student:
            return "Student record not found", 404

        registration_number = student[0]

        # Delete from Registrations table first to comply with foreign key constraints
        cursor.execute("DELETE FROM Registrations WHERE registration_number=%s", (registration_number,))
        
        # Delete from Students table
        cursor.execute("DELETE FROM Students WHERE email=%s", (email,))
        
        # Delete from Credentials table
        cursor.execute("DELETE FROM Credentials WHERE email=%s AND role='student'", (email,))

        # Commit all changes
        db_connection.commit()

        # After successfully deleting from the database, delete from Firestore
        db.collection('students').document(email).delete()

        # Redirect to admin page or wherever appropriate after successful deletion
        return redirect(url_for('admin'))  # Assuming 'admin' is the correct redirection target

    except psycopg2.Error as e:
        db_connection.rollback()  # Ensure database integrity by rolling back on error
        return f"Error deleting student in database: {str(e)}", 500
    except Exception as e:
        db_connection.rollback()
        return f"Error deleting student in Firestore: {str(e)}", 500
    finally:
        if cursor:
            cursor.close()




@app.route('/allocate-course', methods=['POST'])
def allocate_course():
    course_name = request.form['course_name']
    teacher_email = request.form['teacher_email']
    cursor = db_connection.cursor()
    try:
        # Update the course to allocate it to the selected teacher
        cursor.execute("UPDATE Course SET teacher_email = %s WHERE course_name = %s", (teacher_email, course_name))
        db_connection.commit()
        return redirect(url_for('admin'))
    except psycopg2.Error as e:
        db_connection.rollback()
        print(f"Error allocating course: {e}")
        return "Error allocating course"

    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('login'))
def setup_enrollment_trigger():
    """
    Sets up the UpdateEnrollment trigger in the PostgreSQL database.
    This trigger will automatically increment the students_enrolled count
    in the Course table whenever a new entry is made in the registrations table.
    """
    connection = create_connection()
    cursor = connection.cursor()
    
    # Define the function first before creating the trigger
    cursor.execute("""
    CREATE OR REPLACE FUNCTION update_enrollment()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE Course
        SET students_enrolled = students_enrolled + 1
        WHERE course_name = NEW.course_name;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Drop the existing trigger if it exists
    cursor.execute("""
    DROP TRIGGER IF EXISTS UpdateEnrollment ON registrations;
    """)
    
    # Create the trigger using the newly defined function
    cursor.execute("""
    CREATE TRIGGER UpdateEnrollment
    AFTER INSERT ON registrations
    FOR EACH ROW
    EXECUTE FUNCTION update_enrollment();
    """)
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Enrollment trigger has been set up successfully.")


def setup_delete_student_trigger():
    """
    Sets up the DeleteStudentRegistrations trigger in the PostgreSQL database.
    This trigger will automatically delete all registration entries for a student from the 
    registrations table when that student's record is removed from the Students table.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # Define the function that the trigger will execute
    cursor.execute("""
    CREATE OR REPLACE FUNCTION delete_student_registrations()
    RETURNS TRIGGER AS $$
    BEGIN
        DELETE FROM registrations
        WHERE registration_number = OLD.registration_number;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create the trigger that invokes the above function
    cursor.execute("""
    DROP TRIGGER IF EXISTS DeleteStudentRegistrations ON Students;
    CREATE TRIGGER DeleteStudentRegistrations
    AFTER DELETE ON Students
    FOR EACH ROW
    EXECUTE FUNCTION delete_student_registrations();
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("DeleteStudentRegistrations trigger has been set up successfully.")

if __name__ == '__main__':
    setup_enrollment_trigger()  # Set up the enrollment increment trigger
    setup_delete_student_trigger()  # Set up the delete student registrations trigger
    app.run(debug=True)