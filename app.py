from flask import Flask, render_template, request, redirect, url_for, session
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

    cur = db_connection.cursor()

    # Use SQL injection safe query
    query = sql.SQL("SELECT * FROM Credentials WHERE email=%s AND password=%s AND role=%s")
    cur.execute(query, (email, password, role))

    credentials = cur.fetchone()

    print("Credentials from DB:", credentials)  # Debugging output

    if credentials:
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
    
# Function to fetch student information from the database
def get_student_info(email):
    try:
        cursor = db_connection.cursor()

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

    except psycopg2.Error as e:
        # Handle any exceptions
        return {'error': str(e)}, 500

# Remaining functions and routes

def get_teacher_details(email):
    try:
        cursor = db_connection.cursor()

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

    except psycopg2.Error as e:
        print("Error fetching teacher details:", e)
        return {"error": str(e)}

def get_student_program(email):
    try:
        cursor = db_connection.cursor()

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

def get_courses_by_program(program):
    try:
        cursor = db_connection.cursor()

        # Query to fetch the courses available for the given program
        cursor.execute("SELECT course_name, teacher_name FROM Course WHERE program_name = %s", (program,))
        courses = cursor.fetchall()

        return courses

    except psycopg2.Error as e:
        print("Error fetching courses by program:", e)
        return []

def register_student_courses(email, selected_courses):
    try:
        cursor = db_connection.cursor()

        # Insert the selected courses into the StudentCourses table
        for course in selected_courses:
            # Get the registration number for the student
            cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
            registration_number = cursor.fetchone()[0]

            # Insert into registrations table
            cursor.execute("INSERT INTO registrations (course_name, teacher_name, registration_number) VALUES (%s, %s, %s)",
                           (course['course_name'], course['teacher_name'], registration_number))

        # Commit the transaction
        db_connection.commit()
        
        print("Courses registered successfully")

    except psycopg2.Error as e:
        # Rollback in case of any error
        db_connection.rollback()
        print("Error registering courses:", e)

def get_course_by_name(course_name):
    try:
        cursor = db_connection.cursor()

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

@app.route('/registration-confirmation')
def registration_confirmation():
    # Render the registration confirmation page
    return render_template('registration_confirmation.html')
@app.route('/register-courses', methods=['GET', 'POST'])
def register_courses():
    email = session.get('email')
    
    if not email:
        return "Email not found in session"

    if request.method == 'GET':
        cursor = db_connection.cursor()
        cursor.execute("SELECT student_program_name FROM Students WHERE email = %s", (email,))
        student_program = cursor.fetchone()
        
        if student_program:
            program_name = student_program[0]
            
            # Fetch all available courses for this program
            cursor.execute("SELECT course_name, teacher_name FROM Course WHERE program_name = %s", (program_name,))
            courses = cursor.fetchall()
            
            # Convert to a list of dictionaries
            courses_dict = [{'course_name': row[0], 'teacher_name': row[1]} for row in courses]
            
            # Render the `student.html` template with available courses
            return render_template('student.html', courses=courses_dict)
        else:
            return "Student program not found"
    
    elif request.method == 'POST':
        selected_course_names = request.form.getlist('course')
        
        # Fetch the student's registration number
        cursor = db_connection.cursor()
        cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
        registration_number = cursor.fetchone()[0]

        for course_name in selected_course_names:
            # Check if this course is already registered
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE registration_number = %s AND course_name = %s",
                (registration_number, course_name)
            )
            exists = cursor.fetchone()[0]

            if exists == 0:
                # Insert the course only if it's not already registered
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

    # Get the course name from the form data
    course_name = request.form['course_name']
    
    # Fetch the student's registration number
    cursor = db_connection.cursor()
    cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
    registration_number = cursor.fetchone()[0]

    # Delete the specified course from the registrations table
    cursor.execute(
        "DELETE FROM registrations WHERE registration_number = %s AND course_name = %s",
        (registration_number, course_name)
    )
    db_connection.commit()

    # Redirect back to the student page to view the updated list of courses
    return redirect(url_for('student'))


def get_registered_courses(email):
    try:
        cursor = db_connection.cursor()

        # Query to fetch the registration number of the student based on email
        cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
        result = cursor.fetchone()

        if not result:
            return []  # No registration number found for this email
        
        registration_number = result[0]

        # Query to fetch courses based on the student's registration number
        cursor.execute("SELECT course_name, teacher_name FROM registrations WHERE registration_number = %s", (registration_number,))
        courses = cursor.fetchall()

        # Convert the fetched data into a list of dictionaries
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
        
        # Fetch the student's registration number
        cursor.execute("SELECT registration_number FROM Students WHERE email = %s", (email,))
        registration_number = cursor.fetchone()
        
        if not registration_number:
            return "Student registration number not found"
        
        registration_number = registration_number[0]

        # Fetch courses from the registrations table
        cursor.execute(
            "SELECT course_name, teacher_name FROM registrations WHERE registration_number = %s",
            (registration_number,)
        )
        courses = cursor.fetchall()

        # Convert to a list of dictionaries
        registered_courses = [{'course_name': row[0], 'teacher_name': row[1]} for row in courses]

        return render_template('student.html', registered_courses=registered_courses)
    else:
        return "Email not found in session"
    
@app.route('/view-students')
def view_students():
    email = session.get('email')
    
    if email:
        cursor = db_connection.cursor()
        
        # Retrieve teacher details based on their email
        cursor.execute("SELECT teacher_name, email, teacher_position FROM Teachers WHERE email = %s", (email,))
        teacher_data = cursor.fetchone()
        
        if teacher_data:
            # Prepare the teacher details dictionary
            teacher_details = {
                'teacher_name': teacher_data[0],
                'email': teacher_data[1],
                'teacher_position': teacher_data[2]
            }
            
            # Fetch all courses taught by this teacher
            cursor.execute("SELECT course_name FROM Course WHERE teacher_name = %s", (teacher_data[0],))
            courses = [row[0] for row in cursor.fetchall()]
            
            # Prepare a mapping of courses to enrolled students
            enrolled_students = {}
            for course_name in courses:
                cursor.execute(
                    "SELECT s.student_name FROM registrations r "
                    "JOIN Students s ON r.registration_number = s.registration_number "
                    "WHERE r.course_name = %s AND r.teacher_name = %s",
                    (course_name, teacher_data[0])
                )
                enrolled_students[course_name] = [row[0] for row in cursor.fetchall()]
            
            # Pass the teacher details and enrolled students dictionary to the template
            return render_template('teacher.html', teacher_details=teacher_details, enrolled_students=enrolled_students)
        else:
            return "Teacher details not found."
    else:
        return "Email not found in session."


@app.route('/remove-student', methods=['POST'])
def remove_student():
    email = session.get('email')
    
    if not email:
        return "Email not found in session"

    # Extract data from the form
    course_name = request.form['course_name']
    student_name = request.form['student_name']
    
    cursor = db_connection.cursor()
    
    # Find the student's registration number
    cursor.execute("SELECT registration_number FROM Students WHERE student_name = %s", (student_name,))
    registration_number = cursor.fetchone()
    
    if registration_number:
        registration_number = registration_number[0]
        
        # Remove the student from the course in the registrations table
        cursor.execute(
            "DELETE FROM registrations WHERE registration_number = %s AND course_name = %s",
            (registration_number, course_name)
        )
        db_connection.commit()
    else:
        return f"Student '{student_name}' not found."

    # Redirect back to the students' list page
    return redirect(url_for('view_students'))


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
    email = session.get('email')
    
    if email:
        cursor = db_connection.cursor()
        
        # Retrieve the teacher's details based on their email
        cursor.execute("SELECT teacher_name, email, teacher_position FROM Teachers WHERE email = %s", (email,))
        teacher_data = cursor.fetchone()
        
        if teacher_data:
            # Create a dictionary to store the details
            teacher_details = {
                'teacher_name': teacher_data[0],
                'email': teacher_data[1],
                'teacher_position': teacher_data[2]
            }
            
            # Fetch the students enrolled in the teacher's courses if needed
            cursor.execute(
                "SELECT s.student_name, r.course_name FROM registrations r "
                "JOIN Students s ON r.registration_number = s.registration_number "
                "WHERE r.teacher_name = %s",
                (teacher_data[0],)
            )
            enrolled_students = [{'student_name': row[0], 'course_name': row[1]} for row in cursor.fetchall()]
            
            # Render the teacher.html template and include all necessary data
            return render_template('teacher.html', teacher_details=teacher_details, enrolled_students=enrolled_students)
        else:
            return "Teacher details not found."
    else:
        return "Email not found in session."


@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)