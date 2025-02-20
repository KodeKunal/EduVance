from datetime import timedelta
from flask import Flask, jsonify, request, render_template, session, redirect
from flask_cors import CORS
import sqlite3
import logging
import secrets
import os
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config.update(
    SECRET_KEY='your-secret-key-here',
    SESSION_COOKIE_SECURE=False,  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',  # Changed from 'Lax' to 'None' for cross-origin
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

    try:
        # First drop existing tables if they exist
        cursor.executescript('''
            DROP TABLE IF EXISTS progress;
            DROP TABLE IF EXISTS completed_courses;
            DROP TABLE IF EXISTS course_videos;
            DROP TABLE IF EXISTS assignments;
            DROP TABLE IF EXISTS courses;
            DROP TABLE IF EXISTS students;
            DROP TABLE IF EXISTS users;
        ''')

        # Create tables
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                progress INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                instructor TEXT,
                difficulty_level INTEGER
            );

            CREATE TABLE IF NOT EXISTS course_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                video_id TEXT NOT NULL,
                title TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                video_id TEXT NOT NULL,
                progress_percentage INTEGER NOT NULL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS completed_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_name TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                class_name TEXT NOT NULL
            );
        ''')

        # Insert sample data
        cursor.executemany('''
            INSERT OR REPLACE INTO courses (name, difficulty_level, description, instructor) 
            VALUES (?, ?, ?, ?)
        ''', [
            ('Intro to Chemistry', 1, 'Basics of Chemistry', 'Dr. Smith'),
            ('Advanced Physics', 3, 'Advanced Physics concepts', 'Prof. Johnson'),
            ('Basic Biology', 1, 'Introduction to Biology', 'Dr. Green'),
            ('Organic Chemistry', 2, 'Organic Chemistry basics', 'Prof. Brown')
        ])

        # Get course IDs
        cursor.execute('SELECT id, name FROM courses')
        courses = {row['name']: row['id'] for row in cursor.fetchall()}

        # Insert sample videos
        cursor.executemany('''
            INSERT OR REPLACE INTO course_videos (course_id, video_id, title)
            VALUES (?, ?, ?)
        ''', [
            (courses['Intro to Chemistry'], 'video1', 'Chemistry Video 1'),
            (courses['Intro to Chemistry'], 'video2', 'Chemistry Video 2'),
            (courses['Advanced Physics'], 'video3', 'Physics Video 1'),
            (courses['Advanced Physics'], 'video4', 'Physics Video 2'),
            (courses['Basic Biology'], 'video5', 'Biology Video 1'),
            (courses['Basic Biology'], 'video6', 'Biology Video 2'),
            (courses['Organic Chemistry'], 'video7', 'Chemistry Video 3'),
            (courses['Organic Chemistry'], 'video8', 'Chemistry Video 4')
        ])

        # Insert demo user and student
        cursor.execute('''
            INSERT OR REPLACE INTO users (username, password, email, class_name)
            VALUES (?, ?, ?, ?)
        ''', ('demo_user', 'demo123', 'demo@example.com', 'Demo Class'))

        cursor.execute('''
            INSERT OR REPLACE INTO students (id, name, email)
            VALUES (1, 'Demo Student', 'demo@example.com')
        ''')

        conn.commit()
        return jsonify({'message': 'Database initialized successfully'}), 200

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Route to initialize another database with tables and sample data
@app.route('/init_another_db')
def init_another_db():
    conn = sqlite3.connect('another_database.db')
    cursor = conn.cursor()

    try:
        # First drop existing tables if they exist
        cursor.executescript('''
            DROP TABLE IF EXISTS progress;
            DROP TABLE IF EXISTS completed_courses;
            DROP TABLE IF EXISTS course_videos;
            DROP TABLE IF EXISTS assignments;
            DROP TABLE IF EXISTS courses;
            DROP TABLE IF EXISTS students;
            DROP TABLE IF EXISTS users;
        ''')

        # Create tables
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                progress INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                instructor TEXT,
                difficulty_level INTEGER
            );

            CREATE TABLE IF NOT EXISTS course_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                video_id TEXT NOT NULL,
                title TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username INTEGER NOT NULL,
                video_id TEXT NOT NULL,
                progress_percentage INTEGER NOT NULL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS completed_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_name TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                class_name TEXT NOT NULL
            );
        ''')

        # Insert sample data
        cursor.executemany('''
            INSERT OR REPLACE INTO courses (name, difficulty_level, description, instructor) 
            VALUES (?, ?, ?, ?)
        ''', [
            ('Intro to Chemistry', 1, 'Basics of Chemistry', 'Dr. Smith'),
            ('Advanced Physics', 3, 'Advanced Physics concepts', 'Prof. Johnson'),
            ('Basic Biology', 1, 'Introduction to Biology', 'Dr. Green'),
            ('Organic Chemistry', 2, 'Organic Chemistry basics', 'Prof. Brown')
        ])

        # Get course IDs
        cursor.execute('SELECT id, name FROM courses')
        courses = {row['name']: row['id'] for row in cursor.fetchall()}

        # Insert sample videos
        cursor.executemany('''
            INSERT OR REPLACE INTO course_videos (course_id, video_id, title)
            VALUES (?, ?, ?)
        ''', [
            (courses['Intro to Chemistry'], 'video1', 'Chemistry Video 1'),
            (courses['Intro to Chemistry'], 'video2', 'Chemistry Video 2'),
            (courses['Advanced Physics'], 'video3', 'Physics Video 1'),
            (courses['Advanced Physics'], 'video4', 'Physics Video 2'),
            (courses['Basic Biology'], 'video5', 'Biology Video 1'),
            (courses['Basic Biology'], 'video6', 'Biology Video 2'),
            (courses['Organic Chemistry'], 'video7', 'Chemistry Video 3'),
            (courses['Organic Chemistry'], 'video8', 'Chemistry Video 4')
        ])

        # Insert demo user and student
        cursor.execute('''
            INSERT OR REPLACE INTO users (username, password, email, class_name)
            VALUES (?, ?, ?, ?)
        ''', ('demo_user', 'demo123', 'demo@example.com', 'Demo Class'))

        cursor.execute('''
            INSERT OR REPLACE INTO students (id, name, email)
            VALUES (1, 'Demo Student', 'demo@example.com')
        ''')

        conn.commit()
        return jsonify({'message': 'Another database initialized successfully'}), 200

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Route to handle user login
@app.route('/api/login', methods=['POST'])
def login():
    try:
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
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['class_name'] = user['class_name']
            
            response = jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'class_name': user['class_name']
                }
            })
            return response, 200

        return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'message': 'Server error'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/check_session', methods=['GET'])
def check_session():
    try:
        if 'user_id' in session:
            return jsonify({
                'logged_in': True,
                'user': {
                    'id': session.get('user_id'),
                    'username': session.get('username'),
                    'email': session.get('email')
                }
            })
        # Return success with demo data for development
        return jsonify({
            'logged_in': True,
            'user': {
                'id': 1,
                'username': 'demo_user',
                'email': 'demo@example.com'
            }
        })
    except Exception as e:
        logger.error(f"Session check error: {e}")
        return jsonify({'logged_in': True, 'error': str(e)})

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

        # Get the newly created user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()['id']

        # Initialize progress for the new user
        cursor.execute("INSERT INTO students (id, name, email, progress) VALUES (?, ?, ?, ?)", 
                       (user_id, username, email, 0))
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


@app.route('/check-course-completion/<int:student_id>/<string:course_name>', methods=['GET'])
def check_course_completion(student_id, course_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch all videos related to the course
        cursor.execute('''
            SELECT v.id AS video_id
            FROM courses c
            JOIN course_videos v ON c.id = v.course_id
            WHERE c.name = ?
        ''', (course_name,))
        videos = cursor.fetchall()

        # Check progress for all videos
        for video in videos:
            video_id = video['video_id']
            cursor.execute('''
                SELECT progress_percentage 
                FROM progress 
                WHERE student_id = ? AND video_id = ?
            ''', (student_id, video_id))
            progress = cursor.fetchone()

            if not progress or progress['progress_percentage'] < 100:
                return jsonify({'completed': False}), 200

        # Mark the course as completed
        cursor.execute('''
            INSERT INTO completed_courses (student_id, course_name)
            VALUES (?, ?)
        ''', (student_id, course_name))
        conn.commit()

        return jsonify({'completed': True}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()


# Route to recommend courses based on student's progress
@app.route('/recommend_courses/<int:student_id>', methods=['GET'])
def recommend_courses(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Calculate average progress for the student
        cursor.execute('''
            SELECT AVG(progress_percentage) as avg_progress
            FROM progress 
            WHERE student_id = ?
        ''', (student_id,))
        avg_progress = cursor.fetchone()['avg_progress'] or 0

        # Recommend courses based on average progress
        if (avg_progress < 50):
            recommended_courses = cursor.execute('SELECT * FROM courses WHERE difficulty_level = 1').fetchall()
        elif avg_progress < 80:
            recommended_courses = cursor.execute('SELECT * FROM courses WHERE difficulty_level <= 2').fetchall()
        else:
            recommended_courses = cursor.execute('SELECT * FROM courses').fetchall()

        return jsonify([dict(course) for course in recommended_courses]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()


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

GEMINI_API_KEY = os.getenv("AIzaSyAOIO-yDhasKYEbvu-42r9sH4g5WAynjeg")

@app.route('/api/update-progress', methods=['POST'])
def update_progress():
    try:
        data = request.get_json()
        video_id = data['videoId']
        progress = min(100, max(0, int(data['progressPercentage'])))
        student_id = session.get('user_id')  # Use the logged-in user's ID

        conn = get_db_connection()
        cursor = conn.cursor()

        # First, ensure the student exists
        cursor.execute('''
            INSERT OR IGNORE INTO students (id, name, email, progress) 
            VALUES (?, ?, ?, ?)
        ''', (student_id, session.get('username'), session.get('email'), 0))

        # Update or insert progress
        cursor.execute('''
            INSERT OR REPLACE INTO progress 
            (student_id, video_id, progress_percentage, last_updated) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (student_id, video_id, progress))

        # Check if this completes a course
        cursor.execute('''
            SELECT c.name as course_name
            FROM courses c
            JOIN course_videos cv ON c.id = cv.course_id
            WHERE cv.video_id = ?
        ''', (video_id,))
        
        course = cursor.fetchone()
        if course and progress >= 100:
            # Add to completed courses if all videos are done
            cursor.execute('''
                INSERT OR IGNORE INTO completed_courses (student_id, course_name)
                VALUES (?, ?)
            ''', (student_id, course['course_name']))

        conn.commit()
        return jsonify({
            'success': True, 
            'progress': progress,
            'video_id': video_id,
            'student_id': student_id
        }), 200

    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/user_progress/<int:student_id>', methods=['GET'])
def get_user_progress(student_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get detailed progress for each course including video counts
        cursor.execute('''
            WITH VideoProgress AS (
                SELECT 
                    cv.course_id,
                    cv.video_id,
                    COALESCE(p.progress_percentage, 0) as progress,
                    CASE WHEN p.progress_percentage >= 100 THEN 1 ELSE 0 END as completed
                FROM course_videos cv
                LEFT JOIN progress p ON cv.video_id = p.video_id 
                    AND p.student_id = ?
            )
            SELECT 
                c.id as course_id,
                c.name as course_name,
                COUNT(vp.video_id) as total_videos,
                COALESCE(SUM(vp.completed), 0) as completed_videos,
                ROUND(AVG(vp.progress), 2) as progress_percentage,
                GROUP_CONCAT(vp.progress) as individual_progress
            FROM courses c
            LEFT JOIN VideoProgress vp ON c.id = vp.course_id
            GROUP BY c.id, c.name
            ORDER BY c.name
        ''', (student_id,))

        progress_data = []
        for row in cursor.fetchall():
            course_data = {
                'course_id': row['course_id'],
                'course_name': row['course_name'],
                'total_videos': row['total_videos'] or 0,
                'completed_videos': row['completed_videos'] or 0,
                'progress_percentage': row['progress_percentage'] or 0,
                'individual_progress': [
                    float(p) for p in row['individual_progress'].split(',')
                ] if row['individual_progress'] else []
            }
            progress_data.append(course_data)

        return jsonify(progress_data), 200

    except Exception as e:
        logger.error(f"Error fetching progress: {e}")
        return jsonify([]), 200  # Return empty array instead of error
    finally:
        if conn:
            conn.close()

# Add these routes
@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Missing request body'}), 400
        return login()
    return jsonify({'message': 'Please use POST method for login'}), 405

@app.route('/api/check_login', methods=['GET'])
def check_login():
    # Always return logged in for development
    return jsonify({
        'logged_in': True,
        'user_id': session.get('user_id', 1)
    })

# Add logout route
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    response = jsonify({'message': 'Logged out successfully'})
    response.delete_cookie('session_id')
    return response, 200

@app.route('/api/completed_courses/<student_id>', methods=['GET'])
def get_completed_courses(student_id):
    if student_id == 'null':
        return jsonify({'error': 'Invalid student ID'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT course_name 
            FROM completed_courses 
            WHERE student_id = ?
        ''', (student_id,))
        completed_courses = [row['course_name'] for row in cursor.fetchall()]
        return jsonify(completed_courses), 200
    except Exception as e:
        logger.error(f"Error fetching completed courses: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Main entry point for the Flask app
if __name__ == '__main__':
    app.run(debug=True)
