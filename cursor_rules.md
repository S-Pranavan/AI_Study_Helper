# AI Study Helper - Cursor Rules & Best Practices

**Project:** AI Study Helper from Photos  
**Document Type:** Cursor Rules & Development Guidelines  
**Date:** August 28, 2025  
**Budget:** $0 (100% Free Resources Only)  

---

## 🎯 Project Overview

This document defines the coding standards, best practices, and development guidelines for the AI Study Helper project. All development must use only free, open-source tools and resources.

---

## 🚫 **STRICTLY FORBIDDEN (No Paid Services)**

### **❌ Never Use:**
- **Paid APIs:** OpenAI GPT, Claude, Cohere, etc.
- **Paid Services:** AWS, Google Cloud, Azure (paid tiers)
- **Paid Models:** Commercial AI models with usage fees
- **Paid Hosting:** Premium hosting services
- **Paid Databases:** Commercial database services
- **Paid Tools:** Premium development tools or software

### **✅ Always Use (Free Alternatives):**
- **AI Models:** Hugging Face (free), Local models
- **Hosting:** Vercel (free), Render (free), Hugging Face Spaces (free)
- **Database:** SQLite (local), Supabase (free tier)
- **Tools:** VS Code, GitHub, Git, Python, Node.js (all free)

---

## 🛠 **Technology Stack (Free Only)**

### **Frontend:**
- **Framework:** React.js (free)
- **Styling:** TailwindCSS (free)
- **Icons:** Font Awesome (free), Heroicons (free)
- **Charts:** Chart.js (free), D3.js (free)

### **Backend:**
- **Framework:** Flask (Python - free)
- **Language:** Python 3.8+ (free)
- **Virtual Environment:** venv (built-in Python)

### **AI & ML:**
- **OCR:** Tesseract OCR (free)
- **Image Processing:** OpenCV (free)
- **AI Models:** Hugging Face Transformers (free)
- **Local Inference:** ONNX Runtime (free)

### **Database:**
- **Local:** SQLite (built-in Python)
- **Cloud:** Supabase (free tier - 500MB)

### **Hosting:**
- **Frontend:** Vercel (free tier)
- **Backend:** Render (free tier)
- **AI Models:** Hugging Face Spaces (free)

---

## 📝 **Code Style & Standards**

### **Python (Flask Backend)**
```python
# ✅ GOOD - Follow PEP 8
def process_image(image_file):
    """Process uploaded image using OCR and AI."""
    try:
        # Image preprocessing
        processed_image = preprocess_image(image_file)
        
        # OCR processing
        text_content = extract_text(processed_image)
        
        return {
            'success': True,
            'text': text_content,
            'confidence': 0.85
        }
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        return {
            'success': False,
            'error': 'Image processing failed'
        }

# ❌ BAD - Poor formatting, no error handling
def process_image(image_file):
    processed_image=preprocess_image(image_file)
    text_content=extract_text(processed_image)
    return text_content
```

### **JavaScript/React (Frontend)**
```javascript
// ✅ GOOD - Clean, readable code
const ImageUpload = ({ onUpload, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onUpload(files[0]);
    }
  }, [onUpload]);

  return (
    <div className="upload-container">
      <input
        type="file"
        accept="image/*"
        onChange={(e) => onUpload(e.target.files[0])}
        disabled={isLoading}
      />
    </div>
  );
};

// ❌ BAD - Poor structure, no error handling
const ImageUpload=({onUpload,isLoading})=>{
  const [dragActive,setDragActive]=useState(false);
  return <div><input type="file" onChange={(e)=>onUpload(e.target.files[0])}/></div>
}
```

---

## 🔒 **Security Best Practices**

### **Input Validation**
```python
# ✅ GOOD - Validate all inputs
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    # Process file...
```

### **SQL Injection Prevention**
```python
# ✅ GOOD - Use parameterized queries
def get_user_subjects(user_id):
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    # Use parameterized query to prevent SQL injection
    cursor.execute(
        'SELECT * FROM subjects WHERE user_id = ? ORDER BY name',
        (user_id,)
    )
    
    subjects = cursor.fetchall()
    conn.close()
    return subjects

# ❌ BAD - Vulnerable to SQL injection
def get_user_subjects(user_id):
    conn = sqlite3.connect('study_helper.db')
    cursor = conn.cursor()
    
    # Vulnerable to SQL injection
    cursor.execute(f'SELECT * FROM subjects WHERE user_id = {user_id}')
    
    subjects = cursor.fetchall()
    conn.close()
    return subjects
```

---

## 🚀 **Performance Best Practices**

### **Image Processing Optimization**
```python
# ✅ GOOD - Optimize image processing
import cv2
import numpy as np
from PIL import Image

def optimize_image_for_ocr(image_path):
    """Optimize image for better OCR accuracy."""
    # Read image
    image = cv2.imread(image_path)
    
    # Resize if too large (max 2000px)
    height, width = image.shape[:2]
    if max(height, width) > 2000:
        scale = 2000 / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height))
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

# ❌ BAD - No optimization
def process_image(image_path):
    image = cv2.imread(image_path)
    return image
```

### **AI Model Caching**
```python
# ✅ GOOD - Implement caching for AI models
import hashlib
import json
from functools import lru_cache

class AIContentGenerator:
    def __init__(self):
        self.cache = {}
    
    @lru_cache(maxsize=100)
    def generate_summary(self, text_content):
        """Generate summary with caching."""
        # Generate content using Hugging Face models
        summary = self._call_huggingface_model(text_content)
        return summary
    
    def _call_huggingface_model(self, text):
        # Implementation using free Hugging Face models
        pass
```

---

## 📱 **Responsive Design Guidelines**

### **CSS Best Practices**
```css
/* ✅ GOOD - Mobile-first responsive design */
.upload-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.2s ease;
}

.upload-area:hover {
  border-color: #4299e1;
  background-color: #f7fafc;
}

/* Mobile-first breakpoints */
@media (min-width: 640px) {
  .upload-container {
    padding: 2rem;
  }
}

@media (min-width: 1024px) {
  .upload-container {
    max-width: 800px;
  }
}

/* ❌ BAD - Fixed widths, no responsiveness */
.upload-container {
  width: 800px;
  margin: 0 auto;
}
```

---

## 🧪 **Testing Guidelines**

### **Unit Testing (Free Tools)**
```python
# ✅ GOOD - Comprehensive testing
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

class TestImageProcessing(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.test_image_path = self.create_test_image()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
    
    def test_image_optimization(self):
        """Test image optimization for OCR."""
        result = optimize_image_for_ocr(self.test_image_path)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.shape), 2)  # Grayscale
    
    def test_ocr_accuracy(self):
        """Test OCR accuracy with known text."""
        with patch('pytesseract.image_to_string') as mock_ocr:
            mock_ocr.return_value = "Test Text"
            result = extract_text(self.test_image_path)
            self.assertEqual(result, "Test Text")
    
    def create_test_image(self):
        """Create a test image for testing."""
        # Implementation to create test image
        pass

if __name__ == '__main__':
    unittest.main()
```

### **Frontend Testing (Free Tools)**
```javascript
// ✅ GOOD - React component testing
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ImageUpload from './ImageUpload';

describe('ImageUpload Component', () => {
  test('renders upload input', () => {
    render(<ImageUpload onUpload={() => {}} />);
    expect(screen.getByRole('button', { name: /upload/i })).toBeInTheDocument();
  });

  test('handles file upload', () => {
    const mockOnUpload = jest.fn();
    render(<ImageUpload onUpload={mockOnUpload} />);
    
    const file = new File(['test'], 'test.png', { type: 'image/png' });
    const input = screen.getByRole('button', { name: /upload/i });
    
    fireEvent.click(input);
    // Test file upload logic
  });
});
```

---

## 🔧 **Development Workflow**

### **Git Best Practices**
```bash
# ✅ GOOD - Proper git workflow
# 1. Create feature branch
git checkout -b feature/ocr-integration

# 2. Make changes and commit
git add .
git commit -m "feat: integrate Tesseract OCR with image preprocessing

- Add OpenCV image optimization
- Implement OCR text extraction
- Add error handling for failed OCR
- Update requirements.txt with free dependencies"

# 3. Push and create pull request
git push origin feature/ocr-integration

# ❌ BAD - Poor commit messages
git commit -m "fix stuff"
git commit -m "update"
```

### **Environment Management**
```bash
# ✅ GOOD - Proper environment setup
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install free dependencies
pip install -r requirements.txt

# ❌ BAD - Global installations
pip install flask opencv-python pytesseract
```

---

## 📚 **Documentation Standards**

### **Code Documentation**
```python
# ✅ GOOD - Comprehensive docstrings
def generate_quiz_from_text(text_content, difficulty='medium', num_questions=5):
    """
    Generate quiz questions from text content using AI models.
    
    Args:
        text_content (str): The text content to generate questions from
        difficulty (str): Difficulty level ('easy', 'medium', 'hard')
        num_questions (int): Number of questions to generate (max 10)
    
    Returns:
        dict: Dictionary containing quiz questions and answers
        
    Raises:
        ValueError: If text_content is empty or too short
        RuntimeError: If AI model fails to generate questions
    
    Example:
        >>> text = "Photosynthesis is the process by which plants convert sunlight into energy."
        >>> quiz = generate_quiz_from_text(text, difficulty='easy', num_questions=3)
        >>> print(quiz['questions'][0]['question'])
        'What is photosynthesis?'
    """
    if not text_content or len(text_content.strip()) < 50:
        raise ValueError("Text content must be at least 50 characters long")
    
    if num_questions > 10:
        num_questions = 10
    
    # Implementation using free Hugging Face models
    pass
```

---

## 🚨 **Critical Rules Summary**

### **MUST FOLLOW:**
1. **Never use paid APIs or services**
2. **Always validate user inputs**
3. **Use parameterized queries for databases**
4. **Implement proper error handling**
5. **Write comprehensive tests**
6. **Follow coding standards**
7. **Use only free, open-source tools**

### **NEVER DO:**
1. **Hardcode API keys or secrets**
2. **Use paid services or APIs**
3. **Skip input validation**
4. **Ignore error handling**
5. **Write code without tests**
6. **Use deprecated or insecure methods**

---

## 📋 **Daily Development Checklist**

### **Before Starting:**
- [ ] Virtual environment activated
- [ ] Free dependencies installed
- [ ] Git branch created for feature
- [ ] Requirements reviewed

### **During Development:**
- [ ] Following coding standards
- [ ] Using only free resources
- [ ] Implementing error handling
- [ ] Writing tests for new code
- [ ] Validating all inputs

### **Before Committing:**
- [ ] Code reviewed for standards
- [ ] Tests passing
- [ ] No paid services used
- [ ] Proper commit message
- [ ] Documentation updated

---

**Document Version:** 1.0  
**Last Updated:** August 28, 2025  
**Next Review:** Weekly  

---

*These rules ensure the AI Study Helper project maintains high quality standards while using only free, open-source resources. Follow them strictly to deliver a competition-ready product.*




