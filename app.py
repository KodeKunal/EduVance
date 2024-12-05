from datetime import timedelta
from flask import Flask, jsonify, request, render_template, session, redirect
from flask_cors import CORS
from langchain_groq import ChatGroq
import sqlite3
import logging
import secrets
import os
import requests
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config.update(
    SECRET_KEY='your-secret-key-here',
    SESSION_COOKIE_SECURE=False,  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

CORS(app, 
    origins=['http://127.0.0.1:5500', 'http://localhost:5500'],
    supports_credentials=True,
    allow_headers=['Content-Type'],
    expose_headers=['Content-Type', 'Set-Cookie'],
    methods=['GET', 'POST', 'OPTIONS'])

app.secret_key = secrets.token_hex(16)

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to initialize the database with tables and sample data
@app.route('/init_db')
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            progress INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS completed_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_name TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            instructor TEXT,
            difficulty_level INTEGER
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            class_name TEXT NOT NULL
        );
    ''')

    # Insert sample data into the courses table
    cursor.executemany(''' 
        INSERT INTO courses (name, difficulty_level, description, instructor) 
        VALUES (?, ?, ?, ?)
    ''', [
        ('Intro to Chemistry', 1, 'Basics of Chemistry.', 'Dr. Smith'),
        ('Advanced Physics', 3, 'Explore advanced topics in Physics.', 'Prof. Johnson'),
        ('Basic Biology', 1, 'Introduction to Biology concepts.', 'Dr. Green'),
        ('Organic Chemistry', 2, 'In-depth study of organic compounds.', 'Prof. Brown')
    ])

    conn.commit()
    conn.close()
    return jsonify({'message': 'Database initialized with sample data.'})

# Route to handle user login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        # Set session variables
        session['user_id'] = user[0]
        session['username'] = user['username']
        session['email'] = user['email']
        session['class_name'] = user['class_name']
        
        conn.close()
        # return jsonify({'message': 'Login successful', 'profile': {
        #     'username': user['username'],
        #     'email': user['email'],
        #     'class_name': user['class_name']
        # }}), 200
        return jsonify({'message': 'Login successful', 'user': {'id': user[0], 'username': user[1] , 'email': user[3], 'class_name': user[4]}}), 200

    conn.close()
    return jsonify({'message': 'Invalid credentials'}), 401



# Route to handle user registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    # Get data from the request body
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    class_name = data.get('className')

    # Log received data for debugging
    logging.debug(f"Received data: {data}")

    # Validate required fields
    if not username or not password or not email or not class_name:
        logging.error(f"Missing required fields: {data}")
        return jsonify({"message": "Missing required fields"}), 400

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert into users table with the new columns
        cursor.execute("INSERT INTO users (username, password, email, class_name) VALUES (?, ?, ?, ?)", 
                       (username, password, email, class_name))
        conn.commit()
        cursor.close()
        logging.info(f"User {username} registered successfully.")
        
    except sqlite3.IntegrityError as e:
        logging.error(f"SQLite error: {str(e)}")
        return jsonify({'message': 'Email already exists', 'error': str(e)}), 409
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'User registered successfully'}), 201


# Route to get all courses
@app.route('/api/courses', methods=['GET'])
def get_courses():
    # Get the language parameter from the request, default to 'en' (English)
    lang = request.args.get('lang', 'en')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Modify the query to fetch courses based on the selected language
    cursor.execute("""
        SELECT 
            course_id, 
            course_name, 
            description_english AS description,
            description_kannada AS description_kn 
        FROM courses
    """)
    
    courses = cursor.fetchall()
    
    # Check the language and format the response accordingly
    if lang == 'kn':
        # Return Kannada content
        courses_data = [
            {
                "course_id": course["course_id"],
                "course_name": course["course_name"],
                "description": course["description_kn"] if course["description_kn"] else course["description_english"]
            }
            for course in courses
        ]
    else:
        # Default to English
        courses_data = [
            {
                "course_id": course["course_id"],
                "course_name": course["course_name"],
                "description": course["description_english"]
            }
            for course in courses
        ]
    
    conn.close()
    return jsonify(courses_data), 200

# Route to recommend courses based on student's progress
@app.route('/recommend_courses/<int:student_id>', methods=['GET'])
def recommend_courses(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    student = cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({'error': 'Student not found'}), 404

    progress = student['progress']
    if progress < 50:
        recommended_courses = cursor.execute('SELECT * FROM courses WHERE difficulty_level = 1').fetchall()
    elif progress < 80:
        recommended_courses = cursor.execute('SELECT * FROM courses WHERE difficulty_level <= 2').fetchall()
    else:
        recommended_courses = cursor.execute('SELECT * FROM courses').fetchall()

    conn.close()
    return jsonify([dict(course) for course in recommended_courses]), 200

@app.route('/api/profile', methods=['POST'])
def get_profile():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        logger.debug(f"Profile request for username: {username}")

        if not username or not password:
            return jsonify({'message': 'Missing credentials'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, class_name FROM users WHERE username = ? AND password = ?", 
                      (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'class_name': user[3]
            }), 200

        return jsonify({'message': 'Invalid credentials'}), 401




@app.route('/')
def index():
    return render_template('index.html')

os.environ["GROQ_API_KEY"] = "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"

# Initialize ChatGroq
summarizer = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-70b-versatile"
)



@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        query = request.json.get("question")
        if not query:
            return jsonify({"error": "Question is required"}), 400

        # Use the ChatGroq instance and extract the content from the response
        response = summarizer.invoke(query)
        
        if response:
            # Extract the content from the AIMessage object
            response_content = response.content if hasattr(response, 'content') else str(response)
            return jsonify({"answer": response_content})
        else:
            return jsonify({"error": "No response from AI model"}), 500

    except Exception as e:
        app.logger.error(f"Error during request handling: {str(e)}")
        return jsonify({"error": str(e)}), 500



@app.route('/language-toggle')
def language_toggle():
    return render_template('page_name.html')

# Main entry point for the Flask app
if __name__ == '__main__':
    app.run(debug=True)
