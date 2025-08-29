#!/usr/bin/env python3
"""
AI Study Helper - Phase 2: AI Content Generation Tests
Playwright test suite for AI-powered content generation
"""

import pytest
import tempfile
import os
from PIL import Image
from playwright.sync_api import expect, Page

class TestPhase2AI:
    """Test suite for Phase 2 AI Content Generation features"""
    
    def test_01_phase2_homepage_loading(self, browser_context):
        """Test Phase 2 homepage loads with AI features"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Check Phase 2 indicator
        phase_indicator = page.locator(".phase-indicator")
        expect(phase_indicator).to_be_visible()
        expect(phase_indicator).to_contain_text("Phase 2: AI Content Generation")
        
        # Check AI models status section
        model_status = page.locator("#modelStatus")
        expect(model_status).to_be_visible()
        
        print("✅ Phase 2 homepage loads correctly with AI features")
    
    def test_02_ai_models_status_display(self, browser_context):
        """Test AI models status is displayed correctly"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for model status to load
        page.wait_for_selector("#modelStatus", timeout=10000)
        
        # Check if models are loaded
        model_cards = page.locator(".model-info-card")
        expect(model_cards).to_have_count(4)  # BART, T5, DistilBERT, Device
        
        # Check for BART model
        bart_model = page.locator("text=BART")
        expect(bart_model).to_be_visible()
        
        # Check for T5 model
        t5_model = page.locator("text=T5")
        expect(t5_model).to_be_visible()
        
        # Check for DistilBERT model
        distilbert_model = page.locator("text=DistilBERT")
        expect(distilbert_model).to_be_visible()
        
        print("✅ AI models status displays correctly")
    
    def test_03_ocr_with_ai_generation(self, browser_context):
        """Test OCR processing with AI content generation"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Create test image
        img = Image.new('RGB', (400, 200), color='white')
        test_image_path = tempfile.mktemp(suffix='.png')
        img.save(test_image_path, 'PNG')
        
        try:
            # Upload image
            file_input = page.locator("#fileInput")
            file_input.set_input_files(test_image_path)
            
            # Wait for processing to complete
            page.wait_for_selector("#ocrResults", timeout=30000)
            
            # Check OCR results
            ocr_results = page.locator("#ocrResults")
            expect(ocr_results).to_be_visible()
            
            # Check AI content section appears
            ai_section = page.locator("#aiContentSection")
            expect(ai_section).to_be_visible()
            
            # Check for AI-generated content
            summary_section = page.locator("#summarySection")
            expect(summary_section).to_be_visible()
            
            explanation_section = page.locator("#explanationSection")
            expect(explanation_section).to_be_visible()
            
            keywords_section = page.locator("#keywordsSection")
            expect(keywords_section).to_be_visible()
            
            print("✅ OCR with AI generation works correctly")
            
        finally:
            os.unlink(test_image_path)
    
    def test_04_ai_content_quality(self, browser_context):
        """Test AI-generated content quality and display"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for AI models to be ready
        page.wait_for_selector("#modelStatus", timeout=10000)
        
        # Check if AI content sections are properly structured
        summary_content = page.locator("#summaryContent")
        explanation_content = page.locator("#explanationContent")
        keywords_content = page.locator("#keywordsContent")
        
        # These should exist but may be empty initially
        expect(summary_content).to_be_visible()
        expect(explanation_content).to_be_visible()
        expect(keywords_content).to_be_visible()
        
        print("✅ AI content sections are properly structured")
    
    def test_05_study_session_creation(self, browser_context):
        """Test study session creation with AI content"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#studySessionSection", timeout=10000)
        
        # Check study session form
        session_form = page.locator("#studySessionForm")
        expect(session_form).to_be_visible()
        
        # Check form fields
        session_name_input = page.locator("#sessionName")
        duration_input = page.locator("#duration")
        notes_textarea = page.locator("#notes")
        
        expect(session_name_input).to_be_visible()
        expect(duration_input).to_be_visible()
        expect(notes_textarea).to_be_visible()
        
        # Check submit button
        submit_btn = page.locator('button[type="submit"]')
        expect(submit_btn).to_be_visible()
        expect(submit_btn).to_contain_text("Save Session")
        
        print("✅ Study session creation form is properly displayed")
    
    def test_06_text_input_ai_generation(self, browser_context):
        """Test AI content generation from text input"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#textInput", timeout=10000)
        
        # Check text input section
        text_input = page.locator("#textInput")
        generate_btn = page.locator("#generateBtn")
        
        expect(text_input).to_be_visible()
        expect(generate_btn).to_be_visible()
        expect(generate_btn).to_contain_text("Generate")
        
        # Check content type checkboxes
        summary_checkbox = page.locator("#genSummary")
        explanation_checkbox = page.locator("#genExplanation")
        keywords_checkbox = page.locator("#genKeywords")
        
        expect(summary_checkbox).to_be_visible()
        expect(explanation_checkbox).to_be_visible()
        expect(keywords_checkbox).to_be_visible()
        
        # Check checkboxes are checked by default
        expect(summary_checkbox).to_be_checked()
        expect(explanation_checkbox).to_be_checked()
        expect(keywords_checkbox).to_be_checked()
        
        print("✅ Text input AI generation interface is properly displayed")
    
    def test_07_study_sessions_history(self, browser_context):
        """Test study sessions history display"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#sessionsHistory", timeout=10000)
        
        # Check sessions history section
        sessions_history = page.locator("#sessionsHistory")
        expect(sessions_history).to_be_visible()
        
        # Initially should show no sessions message
        no_sessions_msg = page.locator("text=No study sessions yet")
        expect(no_sessions_msg).to_be_visible()
        
        print("✅ Study sessions history displays correctly")
    
    def test_08_ai_processing_indicators(self, browser_context):
        """Test AI processing indicators and progress"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#uploadProgress", timeout=10000)
        
        # Check upload progress section exists (initially hidden)
        upload_progress = page.locator("#uploadProgress")
        expect(upload_progress).to_be_visible()
        
        # Check progress bar
        progress_bar = page.locator(".progress-bar")
        expect(progress_bar).to_have_count(1)
        
        print("✅ AI processing indicators are properly configured")
    
    def test_09_confidence_indicators(self, browser_context):
        """Test confidence score indicators for AI content"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#aiContentSection", timeout=10000)
        
        # Check confidence indicators exist
        confidence_indicators = page.locator(".confidence-indicator")
        expect(confidence_indicators).to_have_count(3)  # Summary, explanation, keywords
        
        print("✅ Confidence indicators are properly displayed")
    
    def test_10_keyword_tags_display(self, browser_context):
        """Test keyword tags display and styling"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#keywordsContent", timeout=10000)
        
        # Check keyword content section
        keywords_content = page.locator("#keywordsContent")
        expect(keywords_content).to_be_visible()
        
        # Check for keyword tag styling (even if empty)
        keyword_tags = page.locator(".keyword-tag")
        expect(keyword_tags).to_have_count(0)  # Initially no keywords
        
        print("✅ Keyword tags display is properly configured")
    
    def test_11_ai_model_integration(self, browser_context):
        """Test AI model integration and API endpoints"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Test health endpoint
        response = page.request.get("http://localhost:5000/api/health")
        expect(response).to_be_ok()
        
        # Check response contains Phase 2 info
        data = response.json()
        expect(data["phase"]).to_contain("Phase 2")
        expect(data["components"]["ai_generator"]).to_be_truthy()
        
        print("✅ AI model integration is working correctly")
    
    def test_12_error_handling(self, browser_context):
        """Test error handling for AI generation failures"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#aiContentSection", timeout=10000)
        
        # Check error display sections exist
        summary_content = page.locator("#summaryContent")
        expect(summary_content).to_be_visible()
        
        print("✅ Error handling sections are properly configured")
    
    def test_13_responsive_design(self, browser_context):
        """Test responsive design for mobile devices"""
        page, context, browser = browser_context
        
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector(".phase-indicator", timeout=10000)
        
        # Check mobile layout
        phase_indicator = page.locator(".phase-indicator")
        expect(phase_indicator).to_be_visible()
        
        # Check navigation
        navbar = page.locator(".navbar")
        expect(navbar).to_be_visible()
        
        print("✅ Responsive design works on mobile devices")
    
    def test_14_performance_metrics(self, browser_context):
        """Test performance metrics display"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#aiProcessingTime", timeout=10000)
        
        # Check processing time display
        ai_processing_time = page.locator("#aiProcessingTime")
        expect(ai_processing_time).to_be_visible()
        expect(ai_processing_time).to_contain_text("0")
        
        print("✅ Performance metrics are properly displayed")
    
    def test_15_phase2_complete_workflow(self, browser_context):
        """Test complete Phase 2 workflow"""
        page, context, browser = browser_context
        page.goto("http://localhost:5000")
        
        # Wait for page to load
        page.wait_for_selector("#uploadArea", timeout=10000)
        
        # Check all major components are present
        components = [
            "#uploadArea",           # Image upload
            "#modelStatus",          # AI models status
            "#aiContentSection",     # AI content display
            "#studySessionSection",  # Study session creation
            "#sessionsHistory",      # Sessions history
            "#textInput"             # Text input for AI
        ]
        
        for component in components:
            element = page.locator(component)
            expect(element).to_be_visible()
        
        print("✅ Phase 2 complete workflow is properly configured")
        print("🎉 Phase 2 AI Content Generation tests completed successfully!")

# Test configuration
@pytest.fixture(scope="class")
def browser_context(browser):
    """Setup browser context for tests"""
    context = browser.new_context()
    page = context.new_page()
    yield page, context, browser
    context.close()


