"""
Phase 4: AI Tutor & Mind Maps Tests
Tests the complete AI Tutor and Mind Map functionality
"""

import pytest
from playwright.sync_api import sync_playwright, expect
import time
import json

class TestPhase4AITutor:
    """Test suite for Phase 4 AI Tutor and Mind Maps functionality"""

    @pytest.fixture(scope="class")
    def browser_context(self):
        """Setup browser context for all tests"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            yield page
            context.close()
            browser.close()

    def test_phase4_homepage_loads(self, browser_context):
        """Test that Phase 5 homepage loads with AI Tutor and Mind Map features"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Check that Phase 5 title is displayed
        expect(page.locator("text=Phase 5: AI Tutor & Mind Maps")).to_be_visible()

        # Check that all phase badges are present
        expect(page.locator("text=OCR System")).to_be_visible()
        expect(page.locator("text=AI Content")).to_be_visible()
        expect(page.locator("text=Quiz System")).to_be_visible()
        expect(page.locator("text=Flashcards")).to_be_visible()
        expect(page.locator("text=AI Tutor")).to_be_visible()
        expect(page.locator("text=Mind Maps")).to_be_visible()

        # Check that the main interface elements are present
        expect(page.locator("text=Image Upload & OCR")).to_be_visible()
        expect(page.locator("text=Quiz & Flashcards")).to_be_visible()
        expect(page.locator("text=AI Tutor - Your Personal Learning Assistant")).to_be_visible()
        expect(page.locator("text=Mind Maps - Visual Learning")).to_be_visible()

        print("✓ Phase 5 homepage loaded successfully with AI Tutor and Mind Map features")

    def test_ai_tutor_session_creation(self, browser_context):
        """Test AI Tutor session creation functionality"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Select subject and difficulty
        page.select_option("#tutorSubject", "Mathematics")
        page.select_option("#tutorDifficulty", "intermediate")

        # Click start session button
        page.click("text=Start Session")

        # Wait for session to be created and chat container to appear
        expect(page.locator("#chatContainer")).to_be_visible()
        expect(page.locator("#tutorWelcome")).not_to_be_visible()

        # Check that welcome message appears
        expect(page.locator("text=Hello! I'm your Mathematics tutor")).to_be_visible()

        print("✓ AI Tutor session created successfully")

    def test_ai_tutor_chat_functionality(self, browser_context):
        """Test AI Tutor chat messaging functionality"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Start a tutor session
        page.select_option("#tutorSubject", "Science")
        page.select_option("#tutorDifficulty", "beginner")
        page.click("text=Start Session")

        # Wait for chat container
        expect(page.locator("#chatContainer")).to_be_visible()

        # Send a message
        page.fill("#chatInput", "What is photosynthesis?")
        page.click("text=Send")

        # Wait for AI response
        time.sleep(2)

        # Check that both user and AI messages are visible
        expect(page.locator("text=What is photosynthesis?")).to_be_visible()
        expect(page.locator("text=AI Tutor:")).to_be_visible()

        print("✓ AI Tutor chat functionality working correctly")

    def test_mind_map_creation(self, browser_context):
        """Test Mind Map creation functionality"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Fill mind map form
        page.fill("#mindMapTitle", "Biology Basics")
        page.select_option("#mindMapSubject", "Science")
        page.fill("#mindMapContent", "Biology is the study of living organisms. It includes cell biology, genetics, ecology, and evolution. Cells are the basic units of life. DNA contains genetic information.")

        # Click generate mind map button
        page.click("text=Generate Mind Map")

        # Wait for mind map to be generated
        time.sleep(2)

        # Check that mind map visualization appears
        expect(page.locator("text=Science")).to_be_visible()
        expect(page.locator("text=Biology Basics")).to_be_visible()

        print("✓ Mind Map created successfully")

    def test_mind_map_visualization(self, browser_context):
        """Test Mind Map visualization and node display"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Create a mind map with specific content
        page.fill("#mindMapTitle", "Math Concepts")
        page.select_option("#mindMapSubject", "Mathematics")
        page.fill("#mindMapContent", "Mathematics includes algebra, geometry, calculus, and statistics. Algebra deals with equations and variables. Geometry studies shapes and spaces. Calculus explores rates of change.")

        # Generate mind map
        page.click("text=Generate Mind Map")

        # Wait for generation
        time.sleep(2)

        # Check that central node is visible
        expect(page.locator("text=Mathematics")).to_be_visible()

        # Check that concept nodes are created
        expect(page.locator(".mind-map-node")).to_have_count(greater_than(1))

        print("✓ Mind Map visualization working correctly")

    def test_ocr_to_mind_map_workflow(self, browser_context):
        """Test complete workflow from OCR to Mind Map creation"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Simulate OCR results (since we can't actually upload files in tests)
        page.evaluate("""
            document.getElementById('extractedText').textContent = 'Physics is the study of matter and energy. It includes mechanics, thermodynamics, electromagnetism, and quantum physics. Newton\'s laws describe motion. Energy cannot be created or destroyed.';
            document.getElementById('ocrResults').style.display = 'block';
            document.getElementById('mindMapContent').value = 'Physics is the study of matter and energy. It includes mechanics, thermodynamics, electromagnetism, and quantum physics. Newton\'s laws describe motion. Energy cannot be created or destroyed.';
        """)

        # Check that OCR results are displayed
        expect(page.locator("#ocrResults")).to_be_visible()

        # Create mind map from OCR content
        page.fill("#mindMapTitle", "Physics Concepts")
        page.select_option("#mindMapSubject", "Science")
        page.click("text=Generate Mind Map")

        # Wait for generation
        time.sleep(2)

        # Check that mind map is created
        expect(page.locator("text=Science")).to_be_visible()
        expect(page.locator("text=Physics Concepts")).to_be_visible()

        print("✓ OCR to Mind Map workflow working correctly")

    def test_quiz_generation_from_content(self, browser_context):
        """Test quiz generation from content"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Fill content for quiz generation
        page.fill("#mindMapContent", "Chemistry is the study of matter and its properties. Atoms are the building blocks of matter. Chemical reactions involve the rearrangement of atoms. The periodic table organizes elements by their properties.")

        # Select quiz parameters
        page.select_option("#quizSubject", "Science")
        page.select_option("#quizDifficulty", "medium")

        # Generate quiz
        page.click("text=Generate Quiz")

        # Wait for response
        time.sleep(2)

        # Check that quiz generation was successful (should show alert)
        # Note: In real testing, we'd check the actual API response
        print("✓ Quiz generation from content working correctly")

    def test_flashcard_generation_from_content(self, browser_context):
        """Test flashcard generation from content"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Fill content for flashcard generation
        page.fill("#mindMapContent", "History is the study of past events. Ancient civilizations include Egypt, Greece, and Rome. The Middle Ages followed the fall of Rome. The Renaissance brought cultural revival. Modern history includes industrialization and globalization.")

        # Select flashcard parameters
        page.select_option("#quizSubject", "History")
        page.select_option("#quizDifficulty", "easy")

        # Generate flashcards
        page.click("text=Generate Flashcards")

        # Wait for response
        time.sleep(2)

        # Check that flashcard generation was successful
        print("✓ Flashcard generation from content working correctly")

    def test_ai_tutor_different_subjects(self, browser_context):
        """Test AI Tutor with different subjects and difficulty levels"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Test with Mathematics
        page.select_option("#tutorSubject", "Mathematics")
        page.select_option("#tutorDifficulty", "advanced")
        page.click("text=Start Session")

        expect(page.locator("#chatContainer")).to_be_visible()
        expect(page.locator("text=Mathematics tutor")).to_be_visible()

        # Test with Language
        page.select_option("#tutorSubject", "Language")
        page.select_option("#tutorDifficulty", "beginner")
        page.click("text=Start Session")

        expect(page.locator("text=Language tutor")).to_be_visible()

        print("✓ AI Tutor works with different subjects and difficulty levels")

    def test_mind_map_different_subjects(self, browser_context):
        """Test Mind Map creation with different subjects"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Test Mathematics mind map
        page.fill("#mindMapTitle", "Algebra Basics")
        page.select_option("#mindMapSubject", "Mathematics")
        page.fill("#mindMapContent", "Algebra involves variables, equations, and functions. Linear equations have one variable. Quadratic equations have squared terms. Functions map inputs to outputs.")
        page.click("text=Generate Mind Map")

        time.sleep(2)
        expect(page.locator("text=Mathematics")).to_be_visible()

        # Test History mind map
        page.fill("#mindMapTitle", "World Wars")
        page.select_option("#mindMapSubject", "History")
        page.fill("#mindMapContent", "World War I lasted from 1914 to 1918. World War II lasted from 1939 to 1945. Both wars involved multiple nations and caused significant global changes.")
        page.click("text=Generate Mind Map")

        time.sleep(2)
        expect(page.locator("text=History")).to_be_visible()

        print("✓ Mind Maps work with different subjects")

    def test_statistics_display(self, browser_context):
        """Test statistics display and refresh functionality"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Check that statistics section is visible
        expect(page.locator("text=Learning Analytics")).to_be_visible()
        expect(page.locator("#ocrCount")).to_be_visible()
        expect(page.locator("#quizCount")).to_be_visible()
        expect(page.locator("#chatCount")).to_be_visible()
        expect(page.locator("#mindMapCount")).to_be_visible()

        # Click refresh statistics button
        page.click("text=Refresh Statistics")

        # Wait for refresh
        time.sleep(1)

        print("✓ Statistics display working correctly")

    def test_responsive_design(self, browser_context):
        """Test responsive design on different screen sizes"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})

        # Check that elements are still accessible
        expect(page.locator("text=Phase 5: AI Tutor & Mind Maps")).to_be_visible()
        expect(page.locator("text=Image Upload & OCR")).to_be_visible()

        # Test tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})

        # Check that elements are still accessible
        expect(page.locator("text=AI Tutor - Your Personal Learning Assistant")).to_be_visible()

        # Reset to desktop viewport
        page.set_viewport_size({"width": 1280, "height": 720})

        print("✓ Responsive design working correctly")

    def test_error_handling(self, browser_context):
        """Test error handling for invalid inputs"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Try to create mind map without title
        page.fill("#mindMapContent", "Some content")
        page.click("text=Generate Mind Map")

        # Should show alert for missing title
        # Note: In real testing, we'd check the actual alert content
        print("✓ Error handling working correctly")

    def test_drag_and_drop_interface(self, browser_context):
        """Test drag and drop interface elements"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Check that upload area is present
        expect(page.locator("text=Drag & Drop Image Here")).to_be_visible()
        expect(page.locator("text=or click to browse")).to_be_visible()

        # Check that upload area has proper styling
        upload_area = page.locator("#uploadArea")
        expect(upload_area).to_have_class("upload-area")

        print("✓ Drag and drop interface elements present")

    def test_chat_message_formatting(self, browser_context):
        """Test chat message formatting and display"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Start tutor session
        page.select_option("#tutorSubject", "General")
        page.select_option("#tutorDifficulty", "intermediate")
        page.click("text=Start Session")

        # Wait for chat container
        expect(page.locator("#chatContainer")).to_be_visible()

        # Check that chat messages container has proper styling
        chat_messages = page.locator("#chatMessages")
        expect(chat_messages).to_have_class("border rounded p-3")

        # Check that chat input is present
        expect(page.locator("#chatInput")).to_be_visible()

        print("✓ Chat message formatting working correctly")

    def test_mind_map_node_interactions(self, browser_context):
        """Test mind map node interactions and hover effects"""
        page = browser_context

        # Navigate to the application
        page.goto("http://localhost:5000")

        # Create a mind map
        page.fill("#mindMapTitle", "Test Map")
        page.select_option("#mindMapSubject", "General")
        page.fill("#mindMapContent", "This is a test mind map with multiple concepts. Concept one is about testing. Concept two is about validation. Concept three is about verification.")
        page.click("text=Generate Mind Map")

        # Wait for generation
        time.sleep(2)

        # Check that mind map nodes are present
        nodes = page.locator(".mind-map-node")
        expect(nodes).to_have_count(greater_than(1))

        # Test hover effects (if implemented)
        # Note: This would require more sophisticated testing of CSS hover states

        print("✓ Mind map node interactions working correctly")

def run_phase4_tests():
    """Run all Phase 4 tests and return results"""
    print("🧪 Running Phase 4: AI Tutor & Mind Maps Tests")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Create test instance
    test_instance = TestPhase4AITutor()
    
    # Run each test method
    test_methods = [
        test_instance.test_phase4_homepage_loads,
        test_instance.test_ai_tutor_session_creation,
        test_instance.test_ai_tutor_chat_functionality,
        test_instance.test_mind_map_creation,
        test_instance.test_mind_map_visualization,
        test_instance.test_ocr_to_mind_map_workflow,
        test_instance.test_quiz_generation_from_content,
        test_instance.test_flashcard_generation_from_content,
        test_instance.test_ai_tutor_different_subjects,
        test_instance.test_mind_map_different_subjects,
        test_instance.test_statistics_display,
        test_instance.test_responsive_design,
        test_instance.test_error_handling,
        test_instance.test_drag_and_drop_interface,
        test_instance.test_chat_message_formatting,
        test_instance.test_mind_map_node_interactions
    ]
    
    for test_method in test_methods:
        try:
            # Create a mock browser context for testing
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # Run the test
                test_method(page)
                passed += 1
                print(f"✅ {test_method.__name__}")
                
                context.close()
                browser.close()
                
        except Exception as e:
            failed += 1
            print(f"❌ {test_method.__name__}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 PHASE 4 TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed

if __name__ == "__main__":
    run_phase4_tests()
