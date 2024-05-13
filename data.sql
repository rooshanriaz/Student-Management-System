-- Inserting dummy data into Credentials table
INSERT INTO Credentials (email, password, role)
VALUES 
('u2022428@giki.edu.pk', '0328', 'student'),
('u2022506@giki.edu.pk', 'rooshan', 'student'),
('u2022078@giki.edu.pk', 'aizaz', 'student'),
('qasim@giki.edu.pk', 'qasim', 'teacher'),
('admin@giki.edu.pk', 'admin', 'admin'),
('abbas@giki.edu.pk', 'abbas', 'teacher'),
('sabir@giki.edu.pk', 'sabir', 'teacher'),
('hamid@giki.edu.pk', 'hamid', 'teacher'),
('faheem@giki.edu.pk', 'faheem', 'teacher'),
('naveed@giki.edu.pk', 'naveed', 'teacher'),
('ali@giki.edu.pk', 'ali', 'teacher'),
('ahmed@giki.edu.pk', 'ahmed', 'teacher'),
('shakeel@giki.edu.pk', 'shakeel', 'teacher');


-- Inserting dummy data into Program table
INSERT INTO Program (program_id, program_name)
VALUES 
(1, 'BS in Cyber Security'),
(2, 'BS in Mechanical Engineering'),
(3, 'BS in Electrical Engineering');


-- Inserting dummy data into Teachers table
INSERT INTO Teachers (teacher_id, teacher_name, email, teacher_position, teacher_program_name)
VALUES 
(1, 'Qasim Riaz', 'qasim@giki.edu.pk', 'Lecturer', 'BS in Cyber Security'),
(2, 'Dr. Ghulam Abbas', 'abbas@giki.edu.pk', 'Professor', 'BS in Cyber Security'),
(3, 'Muhammad Naveed', 'naveed@giki.edu.pk', 'Assistant Professor', 'BS in Cyber Security'),
(4, 'Muhammad Sabir', 'sabir@giki.edu.pk', 'Lecturer', 'BS in Mechanical Engineering'),
(5, 'Muhammad Hamid', 'hamid@giki.edu.pk', 'Assistant Professor', 'BS in Mechanical Engineering'),
(6, 'Muhammad Faheem', 'faheem@giki.edu.pk', 'Professor','BS in Mechanical Engineering'),
(7, 'Muhammad Ali', 'ali@giki.edu.pk', 'Lecturer', 'BS in Electrical Engineering'),
(8, 'Muhammad Shakeel', 'shakeel@giki.edu.pk', 'Assistant Professor', 'BS in Electrical Engineering'),
(9, 'Muhammad Ahmed', 'ahmed@giki.edu.pk', 'Professor', 'BS in Electrical Engineering');


-- Inserting dummy data into Course table
INSERT INTO Course (course_id, course_name, teacher_name, program_name)
VALUES 
(1,'Introduction to Programming', 'Qasim Riaz', 'BS in Cyber Security'),
(2, 'Object Oriented Programming', 'Dr. Ghulam Abbas', 'BS in Cyber Security'),
(3, 'Discrete Math', 'Qasim Riaz','BS in Cyber Security'),
(4, 'Data Structures & Alogrithms', 'Muhammad Naveed', 'BS in Cyber Security'),
(5, 'Mechanics I', 'Muhammad Sabir', 'BS in Mechanical Engineering'),
(6, 'Mechanics of Solids', 'Muhammad Faheem', 'BS in Mechanical Engineering'),
(7, 'Thermodynamics', 'Muhammad Hamid', 'BS in Mechanical Engineering'),
(8, 'Electric Machines', 'Muhammad Ali', 'BS in Electrical Engineering'),
(9, 'Power Systems', 'Muhammad Ahmed', 'BS in Electrical Engineering'),
(10, 'Microcontrollers', 'Muhammad Shakeel', 'BS in Electrical Engineering');

--Inserting dummy data into Students table
INSERT INTO Students (
    registration_number, student_name, email, student_date_of_birth, student_cgpa, 
    student_enrollment_year, Father_name, student_cnic, student_address, student_program_name,
    student_attendance, student_scholarship, student_fee_status, 
    student_status
) 
VALUES 
('2022428', 'Shameer Awais', 'u2022428@giki.edu.pk', '2003-09-28', 2.9, 
 2022, 'Awais Mehmood', '3650277893491', 'Multan', 'BS in Cyber Security', 90.0, 'Normal Scholarship', 'Paid', 'Active'),
('2022506', 'Rooshan Riaz', 'u2022506@giki.edu.pk', '2000-02-01', 3.2,
 2022, 'Riaz', '2345678901234', 'DG Khan', 'BS in Cyber Security', 85.0, 'Normal Scholarship', 'Paid', 'Active'),
('2022078', 'Aizaz Khan', 'u2022078@giki.edu.pk', '2000-03-01', 3.8,
 2022, 'Mr Khan', '3456789012345', 'Mardan', 'BS in Cyber Security', 95.0, 'Merit Scholarship', 'Paid', 'Active');

insert into registrations(course_name, teacher_name)
values ('Introduction to Programming', 'Qasim Riaz'), ('Object Oriented Programming', 'Dr. Ghulam Abbas'),
('Data Structures & Alogrithms', 'Muhammad Naveed'), ('Mechanics I', 'Muhammad Sabir'), ('Mechanics of Solids', 'Muhammad Faheem'),
('Thermodynamics', 'Muhammad Hamid'), ('Electric Machines', 'Muhammad Ali'), ('Power Systems', 'Muhammad Ahmed'), ('Microcontrollers', 'Muhammad Shakeel');


insert into credentials(email, password, role)
values ('u2022598@giki.edu.pk', 'ubaid', 'student');
insert into students(email, registration_number, student_name, student_date_of_birth, student_cgpa, student_enrollment_year, father_name, student_cnic, student_address, student_program_name, student_attendance, student_scholarship, student_fee_status, student_status)
values('u2022598@giki.edu.pk',2022598, 'Ubaid Nasir', '2004-01-01' ,4.00, 2022, 'Nasir Sheikh', 3520246646249, 'Lahore', 'BS in Mechanical Engineering', 80, 'No Scholarship', 'Paid', 'Active');

ALTER TABLE Teachers ADD CONSTRAINT unique_email UNIQUE (email);


ALTER TABLE Course ADD COLUMN teacher_email VARCHAR (100);

ALTER TABLE Course
ADD FOREIGN KEY (teacher_email) REFERENCES Teachers(email);