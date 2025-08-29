# AI Study Helper

A comprehensive Flask-based web application designed to help students and learners manage their studies effectively through subject organization, study session tracking, and flashcard management.

## Features

### 🎯 Subject Management
- Create and organize study subjects
- Add descriptions and track creation dates
- Easy navigation between subjects

### ⏱️ Study Session Tracking
- Record study sessions with duration and notes
- Built-in Pomodoro timer (25-minute focus sessions)
- Track study time per subject
- Session notes for progress tracking

### 📝 Flashcard System
- Create personalized flashcards by subject
- Difficulty level classification (Easy, Medium, Hard)
- Interactive show/hide answer functionality
- Statistics and progress tracking

### 🎨 Modern UI/UX
- Responsive Bootstrap 5 design
- Clean, intuitive interface
- Mobile-friendly navigation
- Beautiful card-based layouts

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (lightweight, file-based database)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Python Version**: 3.8+

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone or Download
```bash
# If using git
git clone <repository-url>
cd aiStudyHelper

# Or simply navigate to the project directory
cd aiStudyHelper
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
aiStudyHelper/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── venv/                 # Python virtual environment
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page
│   ├── subjects.html     # Subjects listing
│   ├── add_subject.html  # Add subject form
│   ├── study_session.html # Study session tracking
│   ├── flashcards.html   # Flashcards display
│   └── add_flashcard.html # Add flashcard form
└── study_helper.db       # SQLite database (created automatically)
```

## Database Schema

### Subjects Table
- `id`: Primary key
- `name`: Subject name (unique)
- `description`: Optional subject description
- `created_at`: Creation timestamp

### Study Sessions Table
- `id`: Primary key
- `subject_id`: Foreign key to subjects
- `duration_minutes`: Study session duration
- `notes`: Session notes
- `session_date`: Session timestamp

### Flashcards Table
- `id`: Primary key
- `subject_id`: Foreign key to subjects
- `question`: Flashcard question
- `answer`: Flashcard answer
- `difficulty`: Difficulty level (1-3)
- `created_at`: Creation timestamp

## Usage Guide

### Getting Started
1. **Add Subjects**: Start by adding your study subjects (e.g., "Mathematics", "Physics", "History")
2. **Record Study Sessions**: Track your study time and add notes about what you learned
3. **Create Flashcards**: Build a personalized flashcard deck for active recall practice

### Study Tips
- Use the Pomodoro timer for focused 25-minute study sessions
- Take 5-minute breaks between sessions
- Review your session notes regularly
- Practice with flashcards using spaced repetition

### Best Practices
- Be specific with subject names
- Add detailed descriptions to subjects
- Take comprehensive session notes
- Create clear, focused flashcards
- Review and update difficulty levels regularly

## API Endpoints

- `GET /` - Home page
- `GET /subjects` - List all subjects
- `GET /add_subject` - Add subject form
- `POST /add_subject` - Create new subject
- `GET /study_session` - Study session form
- `POST /study_session` - Record study session
- `GET /flashcards` - List all flashcards
- `GET /add_flashcard` - Add flashcard form
- `POST /add_flashcard` - Create new flashcard
- `GET /api/subjects` - JSON API for subjects

## Customization

### Styling
- Modify CSS in `templates/base.html`
- Update Bootstrap theme colors
- Customize card layouts and animations

### Features
- Add new study techniques
- Implement spaced repetition algorithms
- Add progress analytics and charts
- Include study reminders and notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Future Enhancements

- [ ] User authentication and profiles
- [ ] Study analytics and progress charts
- [ ] Spaced repetition algorithm implementation
- [ ] Study group collaboration features
- [ ] Mobile app version
- [ ] Export/import functionality
- [ ] Study streak tracking
- [ ] Integration with calendar apps

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions:
1. Check the documentation above
2. Review the code comments
3. Open an issue on the repository
4. Contact the development team

---

**Happy Studying! 🎓✨**



