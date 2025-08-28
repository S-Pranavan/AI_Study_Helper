from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Database initialization
def init_db():
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            duration_minutes INTEGER,
            notes TEXT,
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subjects')
def subjects():
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects)

@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO subjects (name, description) VALUES (?, ?)', (name, description))
            conn.commit()
            flash('Subject added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Subject with this name already exists!', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('subjects'))
    
    return render_template('add_subject.html')

@app.route('/study_session', methods=['GET', 'POST'])
def study_session():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        duration = request.form['duration']
        notes = request.form['notes']
        
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO study_sessions (subject_id, duration_minutes, notes) VALUES (?, ?, ?)', 
                      (subject_id, duration, notes))
        conn.commit()
        conn.close()
        
        flash('Study session recorded!', 'success')
        return redirect(url_for('study_session'))
    
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    
    return render_template('study_session.html', subjects=subjects)

@app.route('/flashcards')
def flashcards():
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, s.name as subject_name 
        FROM flashcards f 
        JOIN subjects s ON f.subject_id = s.id 
        ORDER BY s.name, f.created_at DESC
    ''')
    flashcards = cursor.fetchall()
    conn.close()
    return render_template('flashcards.html', flashcards=flashcards)

@app.route('/add_flashcard', methods=['GET', 'POST'])
def add_flashcard():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        question = request.form['question']
        answer = request.form['answer']
        difficulty = request.form['difficulty']
        
        conn = sqlite3.connect('study_helper.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO flashcards (subject_id, question, answer, difficulty) VALUES (?, ?, ?, ?)', 
                      (subject_id, question, answer, difficulty))
        conn.commit()
        conn.close()
        
        flash('Flashcard added successfully!', 'success')
        return redirect(url_for('flashcards'))
    
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    
    return render_template('add_flashcard.html', subjects=subjects)

@app.route('/api/subjects')
def api_subjects():
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    
    subjects_list = []
    for subject in subjects:
        subjects_list.append({
            'id': subject[0],
            'name': subject[1],
            'description': subject[2],
            'created_at': subject[3]
        })
    
    return jsonify(subjects_list)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
