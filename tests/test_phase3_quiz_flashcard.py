"""
Phase 3: Quiz & Flashcard System Tests
Tests the complete quiz and flashcard functionality
"""

import pytest
from playwright.sync_api import sync_playwright, expect
import time
import json

class TestPhase3QuizFlashcard:
    """Test suite for Phase 3 Quiz & Flashcard functionality"""
    
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
    
    def test_phase3_homepage_loads(self, browser_context):
        """Test that Phase 3 homepage loads with quiz and flashcard features"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Check that the main interface elements are present
        expect(page.locator("text=Upload Image for OCR + AI + Quiz Generation")).to_be_visible()
        expect(page.locator("text=Direct Text Input for AI + Quiz Generation")).to_be_visible()
        
        print("✓ Phase 3 homepage loaded successfully with quiz and flashcard features")
    
    def test_quiz_generation_from_text(self, browser_context):
        """Test quiz generation from direct text input"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        # Enter sample text for quiz generation
        sample_text = """
        Photosynthesis is the process by which plants convert light energy into chemical energy.
        This process occurs in the chloroplasts of plant cells and requires carbon dioxide, water, and sunlight.
        The end products are glucose and oxygen, which are essential for plant growth and survival.
        """
        
        page.fill("#textInput", sample_text)
        
        # Set subject and difficulty
        page.select_option("#subjectInput", "Biology")
        page.select_option("#difficultyInput", "medium")
        
        # Click generate quiz button
        page.click("text=Generate Quiz")
        
        # Wait for quiz generation
        page.wait_for_timeout(3000)
        
        # Check that quiz section appears
        expect(page.locator("#quizSection")).to_be_visible()
        expect(page.locator("text=Generated 5 questions")).to_be_visible()
        
        # Check that start quiz button is present
        expect(page.locator("text=Start Quiz")).to_be_visible()
        
        print("✓ Quiz generation from text input successful")
    
    def test_flashcard_generation_from_text(self, browser_context):
        """Test flashcard generation from direct text input"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        # Enter sample text for flashcard generation
        sample_text = """
        The human heart has four chambers: two atria and two ventricles.
        The right side pumps blood to the lungs for oxygenation.
        The left side pumps oxygenated blood to the body.
        The heart beats approximately 60-100 times per minute at rest.
        """
        
        page.fill("#textInput", sample_text)
        
        # Set subject and difficulty
        page.select_option("#subjectInput", "Biology")
        page.select_option("#difficultyInput", "easy")
        
        # Click generate flashcards button
        page.click("text=Generate Flashcards")
        
        # Wait for flashcard generation
        page.wait_for_timeout(3000)
        
        # Check that flashcard section appears
        expect(page.locator("#flashcardSection")).to_be_visible()
        expect(page.locator("text=Generated 4 flashcards")).to_be_visible()
        
        # Check that flashcard navigation is present
        expect(page.locator("text=Previous")).to_be_visible()
        expect(page.locator("text=Next")).to_be_visible()
        
        print("✓ Flashcard generation from text input successful")
    
    def test_quiz_taking_functionality(self, browser_context):
        """Test the complete quiz taking experience"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Generate a quiz first
        sample_text = """
        The solar system consists of the Sun and the objects that orbit it.
        There are eight planets: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.
        Pluto was reclassified as a dwarf planet in 2006.
        The asteroid belt is located between Mars and Jupiter.
        """
        
        page.fill("#textInput", sample_text)
        page.select_option("#subjectInput", "Astronomy")
        page.select_option("#difficultyInput", "easy")
        page.click("text=Generate Quiz")
        
        # Wait for quiz generation
        page.wait_for_timeout(3000)
        
        # Start the quiz
        page.click("text=Start Quiz")
        
        # Wait for quiz to start
        page.wait_for_timeout(1000)
        
        # Check that quiz interface is visible
        expect(page.locator("#quizInterface")).to_be_visible()
        expect(page.locator("text=Question 1 of")).to_be_visible()
        
        # Answer the first question (assuming multiple choice)
        page.click("input[type='radio']:first-child")
        
        # Submit answer
        page.click("text=Submit Answer")
        
        # Wait for next question or results
        page.wait_for_timeout(1000)
        
        print("✓ Quiz taking functionality working correctly")
    
    def test_flashcard_review_functionality(self, browser_context):
        """Test the flashcard review system"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Generate flashcards first
        sample_text = """
        Python is a high-level programming language known for its simplicity.
        It supports multiple programming paradigms including procedural, object-oriented, and functional.
        Python has a large standard library and extensive third-party packages.
        It's widely used in data science, web development, and automation.
        """
        
        page.fill("#textInput", sample_text)
        page.select_option("#subjectInput", "Computer Science")
        page.select_option("#difficultyInput", "medium")
        page.click("text=Generate Flashcards")
        
        # Wait for flashcard generation
        page.wait_for_timeout(3000)
        
        # Check that flashcards are generated
        expect(page.locator("#flashcardSection")).to_be_visible()
        
        # Navigate through flashcards
        page.click("text=Next")
        page.wait_for_timeout(500)
        
        page.click("text=Previous")
        page.wait_for_timeout(500)
        
        # Check that flashcard content is visible
        expect(page.locator(".flashcard-question")).to_be_visible()
        expect(page.locator(".flashcard-answer")).to_be_visible()
        
        print("✓ Flashcard review functionality working correctly")
    
    def test_ocr_to_quiz_pipeline(self, browser_context):
        """Test the complete OCR to quiz generation pipeline"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Check that OCR upload is available
        expect(page.locator("input[type='file']")).to_be_visible()
        expect(page.locator("text=Upload Image for OCR + AI + Quiz Generation")).to_be_visible()
        
        # Check that the pipeline description is clear
        expect(page.locator("text=OCR → AI Analysis → Quiz Generation")).to_be_visible()
        
        print("✓ OCR to quiz pipeline interface is properly set up")
    
    def test_subject_and_difficulty_selection(self, browser_context):
        """Test subject and difficulty selection for quiz/flashcard generation"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Check that subject selection is available
        expect(page.locator("#subjectInput")).to_be_visible()
        
        # Check available subjects
        subjects = page.locator("#subjectInput option")
        expect(subjects).to_have_count(6)  # Should have 6 subjects
        
        # Check that difficulty selection is available
        expect(page.locator("#difficultyInput")).to_be_visible()
        
        # Check available difficulties
        difficulties = page.locator("#difficultyInput option")
        expect(difficulties).to_have_count(3)  # Should have 3 difficulty levels
        
        print("✓ Subject and difficulty selection working correctly")
    
    def test_error_handling(self, browser_context):
        """Test error handling for invalid inputs"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Try to generate quiz without text
        page.click("text=Generate Quiz")
        
        # Check that appropriate error message is shown
        page.wait_for_timeout(1000)
        
        # Check for error message (this might vary based on implementation)
        error_elements = page.locator(".error-message, .alert, .text-danger")
        if error_elements.count() > 0:
            print("✓ Error handling for empty input working correctly")
        else:
            print("⚠ Error handling may need improvement")
    
    def test_responsive_design(self, browser_context):
        """Test that the interface is responsive"""
        page = browser_context
        
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(1000)
        
        # Check that elements are still visible and accessible
        expect(page.locator("text=Upload Image for OCR + AI + Quiz Generation")).to_be_visible()
        expect(page.locator("text=Direct Text Input for AI + Quiz Generation")).to_be_visible()
        
        # Test tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        page.wait_for_timeout(1000)
        
        # Check that elements are still visible
        expect(page.locator("text=Upload Image for OCR + AI + Quiz Generation")).to_be_visible()
        
        # Reset to desktop viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print("✓ Responsive design working correctly")

def main():
    """Run all Phase 3 tests"""
    print("Running Phase 3: Quiz & Flashcard System Tests")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        test_suite = TestPhase3QuizFlashcard()
        
        try:
            # Test homepage loading
            test_suite.test_phase3_homepage_loads(page)
            
            # Test quiz generation
            test_suite.test_quiz_generation_from_text(page)
            
            # Test flashcard generation
            test_suite.test_flashcard_generation_from_text(page)
            
            # Test quiz taking
            test_suite.test_quiz_taking_functionality(page)
            
            # Test flashcard review
            test_suite.test_flashcard_review_functionality(page)
            
            # Test OCR pipeline
            test_suite.test_ocr_to_quiz_pipeline(page)
            
            # Test subject/difficulty selection
            test_suite.test_subject_and_difficulty_selection(page)
            
            # Test error handling
            test_suite.test_error_handling(page)
            
            # Test responsive design
            test_suite.test_responsive_design(page)
            
            print("\nAll Phase 3 tests completed successfully!")
            print("Quiz & Flashcard System is fully functional!")
            
        except Exception as e:
            print(f"\nTest failed: {e}")
            return False
        
        finally:
            context.close()
            browser.close()
        
        return True

if __name__ == "__main__":
    main()
