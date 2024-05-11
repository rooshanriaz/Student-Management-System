CREATE TABLE Credentials (
    email VARCHAR(100) PRIMARY KEY,
    password VARCHAR(100),
    role varchar(50)
);

-- Program table in 3NF
CREATE TABLE Program (
    program_id int,
    program_name VARCHAR(100) primary KEY
);

-- Teachers table in 3NF
CREATE TABLE Teachers (
    teacher_id INT,
    teacher_name VARCHAR(100) PRIMARY KEY,
    email VARCHAR(100),
    teacher_position VARCHAR(100),
    teacher_program_name varchar(100),
    FOREIGN KEY (teacher_program_name) REFERENCES Program(program_name),
    FOREIGN KEY (email) REFERENCES Credentials(email)
);

-- Students table in 3NF
CREATE TABLE Students (
    registration_number int PRIMARY KEY,
    student_name VARCHAR(100),
    email VARCHAR(100),
    student_date_of_birth DATE,
    student_cgpa DECIMAL(4,2),
    student_enrollment_year INT,
    Father_name VARCHAR(100),
    student_cnic VARCHAR(13),
    student_address VARCHAR(255),
    student_program_name varchar(100),
    student_attendance DECIMAL(5,2),
    student_scholarship VARCHAR(100),
    student_fee_status VARCHAR(50),
    student_status VARCHAR(20),
	--student_grades varchar(50),
    FOREIGN KEY (student_program_name) REFERENCES Program(program_name),
    FOREIGN KEY (email) REFERENCES Credentials(email)
);

-- Course table in 3NF
CREATE TABLE Course (
    course_id int,
    course_name VARCHAR(100) PRIMARY KEY,
    teacher_name name,
    students_enrolled INT,
	program_name varchar(100),
	registration_number int,
    FOREIGN KEY (teacher_name) REFERENCES Teachers(teacher_name),
	foreign key (program_name) references Program(program_name),
	foreign key (registration_number) references students(registration_number)
);

create table registrations(
    registration_id serial primary key,
    registration_number int,
    course_name varchar(100),
    teacher_name varchar(100),
    foreign key (registration_number) references students(registration_number),
    foreign key (course_name) references course(course_name),
    foreign key (teacher_name) references teachers(teacher_name)
);

CREATE TABLE Admin (
    admin_id int PRIMARY KEY,
    email VARCHAR(100),
    password VARCHAR(100),
    program_name VARCHAR(100),
    teacher_id INT,
    teacher_name VARCHAR(100),
    teacher_position VARCHAR(100),
    teacher_salary DECIMAL(10,2),
    teacher_program varchar(100),
    course_id INT,
    course_name VARCHAR(100),
    students_enrolled INT,
    registration_number int,
    student_name VARCHAR(100),
    student_date_of_birth DATE,
    student_cgpa DECIMAL(4,2),
    Father_name VARCHAR(100),
    student_cnic VARCHAR(13),
    student_enrollment_year INT,
    student_address VARCHAR(255),
    student_program_name varchar(100),
    student_attendance DECIMAL(5,2),
    student_scholarship VARCHAR(100),
    student_fee_status VARCHAR(50),
    student_emergency_contact_phone VARCHAR(20),
    student_year_of_completion INT,
    student_status VARCHAR(20),
    FOREIGN KEY (program_name) REFERENCES Program(program_name),
    FOREIGN KEY (teacher_name) REFERENCES Teachers(teacher_name),
    FOREIGN KEY (course_name) REFERENCES Course(course_name),
    FOREIGN KEY (registration_number) REFERENCES Students(registration_number),
    FOREIGN KEY (email) REFERENCES Credentials(email)
);

ALTER TABLE Teachers ADD CONSTRAINT unique_email UNIQUE (email);


ALTER TABLE Course ADD COLUMN teacher_email VARCHAR (100);

ALTER TABLE Course
ADD FOREIGN KEY (teacher_email) REFERENCES Teachers(email);
