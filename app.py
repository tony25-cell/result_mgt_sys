from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='result_management',
            user='root',
            password=''  # Default XAMPP MySQL password is empty
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to display all students
@app.route('/students')
def students():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students")
        students_data = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('students.html', students=students_data)
    return "Database connection error"

# Route to add a new student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        class_name = request.form['class']
        section = request.form['section']
        dob = request.form['dob']
        
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """INSERT INTO students 
                          (roll_number, first_name, last_name, email, class, section, date_of_birth) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(query, (roll_number, first_name, last_name, email, class_name, section, dob))
                connection.commit()
                flash("Student added successfully!", "success")
            except Error as e:
                flash(f"Error: {e}", "error")
            finally:
                cursor.close()
                connection.close()
            return redirect(url_for('students'))
    return render_template('add_student.html')

# Route to view student results
@app.route('/results/<int:student_id>')
def view_results(student_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Get student details
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        # Get results with subject and exam details
        query = """
        SELECT r.*, s.subject_name, e.exam_name, e.exam_date, e.academic_year
        FROM results r
        JOIN subjects s ON r.subject_id = s.subject_id
        JOIN exams e ON r.exam_id = e.exam_id
        WHERE r.student_id = %s
        ORDER BY e.exam_date DESC, s.subject_name
        """
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('view_results.html', student=student, results=results)
    return "Database connection error"

# Route to add a new result
@app.route('/add_result', methods=['GET', 'POST'])
def add_result():
    connection = create_connection()
    if not connection:
        return "Database connection error"
    
    cursor = connection.cursor(dictionary=True)
    
    # Get all students, subjects and exams for dropdowns
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    
    cursor.execute("SELECT * FROM exams")
    exams = cursor.fetchall()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        exam_id = request.form['exam_id']
        subject_id = request.form['subject_id']
        marks = request.form['marks']
        grade = request.form['grade']
        remarks = request.form['remarks']
        
        try:
            insert_query = """
            INSERT INTO results (student_id, exam_id, subject_id, marks_obtained, grade, remarks)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (student_id, exam_id, subject_id, marks, grade, remarks))
            connection.commit()
            flash("Result added successfully!", "success")
            return redirect(url_for('students'))
        except Error as e:
            flash(f"Error: {e}", "error")
    
    cursor.close()
    connection.close()
    
    return render_template('add_result.html', students=students, subjects=subjects, exams=exams)

# Route to search for results
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Search in students table
            query = """
            SELECT * FROM students 
            WHERE roll_number LIKE %s 
            OR first_name LIKE %s 
            OR last_name LIKE %s
            OR email LIKE %s
            """
            search_param = f"%{search_term}%"
            cursor.execute(query, (search_param, search_param, search_param, search_param))
            students = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return render_template('search_results.html', students=students, search_term=search_term)
    
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)