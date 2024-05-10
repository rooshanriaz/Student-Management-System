from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

app.secret_key = '1PoepThNcgk6MiS1EM3wygyokLzjTNkY'
# Database setup
DB_NAME = 'project'
DB_USER = 'postgres'
DB_PASSWORD = 'pgadmin4'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Create a connection function to avoid repeating code
def create_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    print("Received:", email, password, role)  # Debugging output

    conn = create_connection()
    cur = conn.cursor()

    # Use SQL injection safe query
    query = sql.SQL("SELECT * FROM Credentials WHERE email=%s AND password=%s AND role=%s")
    cur.execute(query, (email, password, role))

    Credentials = cur.fetchone()
    conn.close()

    print("Credentials from DB:", Credentials)  # Debugging output

    if Credentials:
        # Store the email in the session
        session['email'] = email  # Add this line to store email in session

        if role == 'student':
            return redirect(url_for('student'))
        elif role == 'teacher':
            return redirect(url_for('teacher'))
        elif role == 'admin':
            return redirect(url_for('admin'))
    else:
        return "Invalid credentials"
    
from flask import jsonify


def get_student_info(email):
    try:
        # Establish a new connection to the database
        connection = psycopg2.connect(
            dbname="project",
            user="postgres",
            password="pgadmin4",
            host="localhost",
            port="5432"
        )

        cursor = connection.cursor()

        # Execute the SQL query to fetch student details based on email
        cursor.execute("SELECT * FROM Students WHERE email = %s", (email,))
        
        # Fetch the first row, if exists
        row = cursor.fetchone()
        
        if row:
            # Convert the fetched data into a dictionary for easy access
            student_info = {
                "student_name": row[1],
                "email": row[2],
                "student_date_of_birth": row[3],
                "student_cgpa": row[4],
                "student_enrollment_year": row[5],
                "student_father_name": row[6],
                "student_cnic": row[7],
                "student_address": row[8],
                "student_program":row[9],
                "student_scholarship": row[11],
                "student_status": row[13]
            }
            return student_info
        else:
            # If no row exists, it means the email doesn't match any credentials
            return {'message': 'Email not found in credentials'}

    except Error as e:
        # Handle any exceptions
        return {'error': str(e)}, 500

    finally:
        # Ensure cursor and connection are closed
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

import psycopg2
from psycopg2 import Error

def get_teacher_details(email):
    try:
        # Establish connection to the database
        connection = psycopg2.connect(
            user="postgres",
            password="pgadmin4",
            host="localhost",
            port="5432",
            database="project"
        )

        cursor = connection.cursor()

        # Query to fetch details of the teacher with the given email
        cursor.execute("SELECT * FROM Teachers WHERE email = %s", (email,))
        teacher_details = cursor.fetchone()

        if teacher_details:
            # Convert the fetched data into a dictionary for easy access
            teacher_info = {
                "teacher_name": teacher_details[1],
                "email": teacher_details[2],
                "teacher_position": teacher_details[3]
            }
            return teacher_info
        else:
            return {"error": "Teacher not found"}

    except Error as e:
        print("Error fetching teacher details:", e)
        return {"error": str(e)}

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

@app.route('/registration-confirmation')
def registration_confirmation():
    # Render the registration confirmation page
    return render_template('registration_confirmation.html')

def get_student_program(email):
    try:
        # Establish connection to the database
        connection = psycopg2.connect(
            user="postgres",
            password="pgadmin4",
            host="localhost",
            port="5432",
            database="project"
        )

        cursor = connection.cursor()

        # Query to fetch the program of the student with the given email
        cursor.execute("SELECT student_program_name FROM Students WHERE email = %s", (email,))
        program = cursor.fetchone()

        if program:
            return program[0]
        else:
            return None

    except psycopg2.Error as e:
        print("Error fetching student program:", e)
        return None

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def get_courses_by_program(program):
    try:
        # Establish connection to the database
        connection = psycopg2.connect(
            user="postgres",
            password="pgadmin4",
            host="localhost",
            port="5432",
            database="project"
        )

        cursor = connection.cursor()

        # Query to fetch the courses available for the given program
        cursor.execute("SELECT course_name, teacher_name FROM Course WHERE program_name = %s", (program,))
        courses = cursor.fetchall()

        return courses

    except psycopg2.Error as e:
        print("Error fetching courses by program:", e)
        return []

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

def register_student_courses(email, selected_courses):
    try:
        # Establish connection to the database
        connection = psycopg2.connect(
            user="postgres",
            password="pgadmin4",
            host="localhost",
            port="5432",
            database="project"
        )

        cursor = connection.cursor()

        # Insert the selected courses into the StudentCourses table
        for course in selected_courses:
            # Get the registration number for the student
            cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
            registration_number = cursor.fetchone()[0]

            # Insert into registrations table
            cursor.execute("INSERT INTO registrations (course_name, teacher_name, registration_number) VALUES (%s, %s, %s)",
                           (course.course_name, course.teacher_name, registration_number))

        # Commit the transaction
        connection.commit()
        
        print("Courses registered successfully")

    except psycopg2.Error as e:
        # Rollback in case of any error
        connection.rollback()
        print("Error registering courses:", e)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

def get_course_by_name(course_name):
    try:
        # Establish connection to the database
        connection = psycopg2.connect(
            user="postgres",
            password="pgadmin4",
            host="localhost",
            port="5432",
            database="project"
        )

        cursor = connection.cursor()

        # Query to fetch the course details by name
        cursor.execute("SELECT * FROM Course WHERE course_name = %s", (course_name,))
        course = cursor.fetchone()

        if course:
            # Convert the fetched data into a dictionary for easy access
            course_info = {
                "course_name": course[0],
                "teacher_name": course[1],
                # Add more attributes here if needed
            }
            return course_info
        else:
            return None

    except psycopg2.Error as e:
        print("Error fetching course details by name:", e)
        return None

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

@app.route('/register-courses', methods=['GET', 'POST'])
def register_courses():
    # Retrieve the email of the student from the session or any other source
    email = session.get('email')
    
    if email:
        if request.method == 'GET':
            # Fetch the program of the student based on their email
            student_program = get_student_program(email)
            
            if student_program:
                # Fetch the courses available for the student's program
                courses = get_courses_by_program(student_program)
                
                if courses:
                    # Render the register-courses.html template with the available courses
                    return render_template('student.html', courses=courses)
                else:
                    return "No courses available for the student's program"
            else:
                return "Student program not found for the provided email"
        elif request.method == 'POST':
            # Get the selected courses from the form submission
            selected_course_names = request.form.getlist('course')
            selected_courses = []
            
            # Fetch course objects based on the selected course names
            for course_name in selected_course_names:
                course = get_course_by_name(course_name)
                if course:
                    selected_courses.append(course)
            
            # Register the selected courses for the student
            register_student_courses(email, selected_courses)
            
            # Optionally, redirect the student to a confirmation page
            return redirect(url_for('registration_confirmation'))
    else:
        return "Email not found in session"

def get_registered_courses(email):
    try:
        # Establish connection to the database
        connection = psycopg2.connect(
            dbname="project",
            user="postgres",
            password="pgadmin4",
            host="localhost",
            port="5432"
        )

        cursor = connection.cursor()

        # Query to fetch the registered courses for the student
        cursor.execute("SELECT course_name, teacher_name FROM registrations WHERE registration_number = (SELECT registration_number FROM Students WHERE email = %s)", (email,))
        registered_courses = cursor.fetchall()

        return registered_courses

    except psycopg2.Error as e:
        print("Error fetching registered courses:", e)
        return []

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

@app.route('/view-courses')
def view_courses():
    # Retrieve the email from the session
    email = session.get('email')
    if email:
        # Fetch student's registered courses
        registered_courses = get_registered_courses(email)
        # Render the student.html template with the registered courses data
        return render_template('student.html', registered_courses=registered_courses)
    else:
        return "Email not found in session"

@app.route('/')
def home():
    return render_template('index.html')



@app.route('/student')
def student():
    # Retrieve the email from the session
    email = session.get('email')
    
    if email:
        # Fetch student information based on the provided email
        student_info = get_student_info(email)
        
        # Render the student.html template with the retrieved student information
        return render_template('student.html', students=[student_info])
    else:
        # Handle the case where the email is not found in the session
        return "Email not found in session"

@app.route('/teacher')
def teacher():
    # Retrieve the email from the session or any other source where it's stored
    email = session.get('email')
    
    if email:
        # Fetch teacher details based on the provided email
        teacher_details = get_teacher_details(email)
        
        # Render the teacher.html template with the retrieved teacher details
        return render_template('teacher.html', teacher_details=teacher_details)
    else:
        # Handle the case where the email is not found
        return "Email not found"

@app.route('/admin')
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
