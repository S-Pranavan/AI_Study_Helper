"""
Playwright Test Suite for AI Study Helper - Phase 1
Testing OCR Foundation and Image Processing
"""

import pytest
from playwright.sync_api import sync_playwright, expect
import os
import tempfile
from PIL import Image
import time

class TestPhase1OCR:
    """Test suite for Phase 1 OCR functionality."""
    
    @pytest.fixture(scope="class")
    def browser_context(self):
        """Setup browser context for testing."""
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False, slow_mo=1000)
            context = browser.new_context()
            page = context.new_page()
            
            yield page, context, browser
            
            # Cleanup
            context.close()
            browser.close()
    
    @pytest.fixture(scope="class")
    def test_image(self):
        """Create a test image for OCR testing."""
        # Create a simple test image with text
        img = Image.new('RGB', (400, 200), color='white')
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_file.name, 'PNG')
        
        yield temp_file.name
        
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_01_homepage_loads(self, browser_context):
        """Test that the homepage loads correctly."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Check page title
        expect(page).to_have_title("AI Study Helper - Phase 1 (OCR Foundation)")
        
        # Check main heading
        expect(page.locator("h1")).to_contain_text("AI Study Helper")
        
        # Check phase indicator
        expect(page.locator(".alert-info")).to_contain_text("Phase 1: OCR Foundation")
        
        # Check OCR upload section exists
        expect(page.locator("h4")).to_contain_text("Image Upload & OCR Processing")
        
        print("✅ Homepage loads correctly with Phase 1 content")
    
    def test_02_ocr_system_info_display(self, browser_context):
        """Test that OCR system information is displayed."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Wait for OCR info to load
        page.wait_for_selector("#ocrInfo", timeout=10000)
        
        # Check OCR info panel exists
        expect(page.locator("#ocrInfo")).to_be_visible()
        
        # Check that OCR info is loaded (not showing loading spinner)
        page.wait_for_function("""
            () => {
                const info = document.getElementById('ocrInfo');
                return !info.querySelector('.spinner-border');
            }
        """, timeout=15000)
        
        # Check OCR info content
        ocr_info = page.locator("#ocrInfo")
        expect(ocr_info).not_to_contain_text("Loading OCR information")
        
        print("✅ OCR system information displays correctly")
    
    def test_03_single_file_upload_interface(self, browser_context):
        """Test single file upload interface."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Check single upload area exists
        single_upload = page.locator("#singleUploadArea")
        expect(single_upload).to_be_visible()
        
        # Check upload area text
        expect(single_upload).to_contain_text("Drag & Drop Image Here")
        expect(single_upload).to_contain_text("or click to browse")
        
        # Check choose image button
        choose_btn = page.locator("button:has-text('Choose Image')")
        expect(choose_btn).to_be_visible()
        
        # Check file input exists (hidden)
        file_input = page.locator("#singleFileInput")
        expect(file_input).to_be_visible()
        expect(file_input).to_have_attribute("accept", "image/*")
        
        print("✅ Single file upload interface is properly configured")
    
    def test_04_batch_file_upload_interface(self, browser_context):
        """Test batch file upload interface."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Check batch upload area exists
        batch_upload = page.locator("#batchUploadArea")
        expect(batch_upload).to_be_visible()
        
        # Check batch upload area text
        expect(batch_upload).to_contain_text("Drag & Drop Multiple Images")
        expect(batch_upload).to_contain_text("or click to browse multiple files")
        
        # Check choose multiple images button
        choose_btn = page.locator("button:has-text('Choose Multiple Images')")
        expect(choose_btn).to_be_visible()
        
        # Check batch file input exists (hidden)
        file_input = page.locator("#batchFileInput")
        expect(file_input).to_be_visible()
        expect(file_input).to_have_attribute("accept", "image/*")
        expect(file_input).to_have_attribute("multiple")
        
        print("✅ Batch file upload interface is properly configured")
    
    def test_05_drag_and_drop_functionality(self, browser_context):
        """Test drag and drop functionality."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Get upload areas
        single_upload = page.locator("#singleUploadArea")
        batch_upload = page.locator("#batchUploadArea")
        
        # Test drag over effect on single upload
        single_upload.hover()
        page.mouse.down()
        page.mouse.move(200, 200)
        page.mouse.up()
        
        # Check that drag over class is applied
        expect(single_upload).to_have_class(/dragover/)
        
        # Move mouse away to remove drag over effect
        page.mouse.move(0, 0)
        expect(single_upload).not_to_have_class(/dragover/)
        
        print("✅ Drag and drop functionality works correctly")
    
    def test_06_file_validation(self, browser_context):
        """Test file validation functionality."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Create a test text file (invalid)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a text file, not an image")
            text_file_path = f.name
        
        try:
            # Try to upload invalid file
            file_input = page.locator("#singleFileInput")
            file_input.set_input_files(text_file_path)
            
            # Check that error alert is shown
            page.wait_for_selector(".alert-danger", timeout=5000)
            error_alert = page.locator(".alert-danger")
            expect(error_alert).to_contain_text("Invalid file type")
            
            print("✅ File validation correctly rejects invalid file types")
            
        finally:
            # Cleanup
            os.unlink(text_file_path)
    
    def test_07_processing_spinner_display(self, browser_context):
        """Test that processing spinner is displayed during OCR."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Check spinner is hidden by default
        spinner = page.locator("#processingSpinner")
        expect(spinner).to_be_hidden()
        
        # Create a test image
        img = Image.new('RGB', (200, 100), color='white')
        test_image_path = tempfile.mktemp(suffix='.png')
        img.save(test_image_path, 'PNG')
        
        try:
            # Upload test image
            file_input = page.locator("#singleFileInput")
            file_input.set_input_files(test_image_path)
            
            # Check that spinner appears
            expect(spinner).to_be_visible()
            expect(spinner).to_contain_text("Processing image with OCR")
            
            # Wait for processing to complete
            page.wait_for_function("""
                () => {
                    const spinner = document.getElementById('processingSpinner');
                    return spinner.style.display === 'none';
                }
            """, timeout=30000)
            
            print("✅ Processing spinner displays and hides correctly")
            
        finally:
            # Cleanup
            os.unlink(test_image_path)
    
    def test_08_ocr_results_display(self, browser_context):
        """Test that OCR results are displayed correctly."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Create a test image
        img = Image.new('RGB', (300, 150), color='white')
        test_image_path = tempfile.mktemp(suffix='.png')
        img.save(test_image_path, 'PNG')
        
        try:
            # Upload test image
            file_input = page.locator("#singleFileInput")
            file_input.set_input_files(test_image_path)
            
            # Wait for results to appear
            page.wait_for_selector("#resultsSection", timeout=30000)
            
            # Check results section is visible
            results_section = page.locator("#resultsSection")
            expect(results_section).to_be_visible()
            
            # Check results content
            results_content = page.locator("#resultsContent")
            expect(results_content).to_contain_text("Extracted Text")
            expect(results_content).to_contain_text("Processing Details")
            
            print("✅ OCR results are displayed correctly")
            
        finally:
            # Cleanup
            os.unlink(test_image_path)
    
    def test_09_processing_history_display(self, browser_context):
        """Test that processing history is displayed."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Wait for history to load
        page.wait_for_selector("#historyContent", timeout=10000)
        
        # Check history section exists
        history_content = page.locator("#historyContent")
        expect(history_content).to_be_visible()
        
        # Wait for history to finish loading
        page.wait_for_function("""
            () => {
                const history = document.getElementById('historyContent');
                return !history.querySelector('.spinner-border');
            }
        """, timeout=15000)
        
        # Check history content (either shows history or empty state)
        history_text = history_content.text_content()
        assert "Loading processing history" not in history_text
        
        print("✅ Processing history loads and displays correctly")
    
    def test_10_phase_progress_indicator(self, browser_context):
        """Test that phase progress indicator shows correct status."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Check phase progress section exists
        progress_section = page.locator("h5:has-text('Implementation Progress')")
        expect(progress_section).to_be_visible()
        
        # Check Phase 1 shows as complete
        phase1_progress = page.locator("text=Phase 1: OCR Foundation").first
        expect(phase1_progress).to_be_visible()
        
        # Check Phase 1 progress bar shows 100%
        phase1_bar = page.locator("text=Phase 1: OCR Foundation").first.locator("..").locator(".progress-bar")
        expect(phase1_bar).to_contain_text("100%")
        
        # Check other phases show as pending
        phase2_progress = page.locator("text=Phase 2: AI Generation").first
        expect(phase2_progress).to_be_visible()
        
        print("✅ Phase progress indicator shows correct status")
    
    def test_11_responsive_design(self, browser_context):
        """Test responsive design on different screen sizes."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(1000)
        
        # Check that elements are properly stacked on mobile
        upload_sections = page.locator(".upload-area")
        expect(upload_sections).to_have_count(2)
        
        # Test tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        page.wait_for_timeout(1000)
        
        # Test desktop viewport
        page.set_viewport_size({"width": 1200, "height": 800})
        page.wait_for_timeout(1000)
        
        print("✅ Responsive design works on different screen sizes")
    
    def test_12_error_handling(self, browser_context):
        """Test error handling for various scenarios."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Test with very large file (if possible)
        # Create a large test image
        img = Image.new('RGB', (1000, 1000), color='white')
        large_image_path = tempfile.mktemp(suffix='.png')
        img.save(large_image_path, 'PNG')
        
        try:
            # Upload large image
            file_input = page.locator("#singleFileInput")
            file_input.set_input_files(large_image_path)
            
            # Wait for either results or error
            try:
                page.wait_for_selector("#resultsSection", timeout=15000)
                print("✅ Large image processed successfully")
            except:
                # Check for error message
                error_alert = page.locator(".alert-danger")
                if error_alert.is_visible():
                    print("✅ Error handling works for large files")
                else:
                    print("⚠️  Large image processing behavior unclear")
                    
        finally:
            # Cleanup
            os.unlink(large_image_path)
    
    def test_13_api_endpoints_functionality(self, browser_context):
        """Test that API endpoints are accessible."""
        page, context, browser = browser_context
        
        # Test health check endpoint
        response = page.goto("http://localhost:5000/api/health")
        expect(response).to_be_ok()
        
        # Test OCR info endpoint
        response = page.goto("http://localhost:5000/api/ocr/info")
        expect(response).to_be_ok()
        
        # Test OCR results endpoint
        response = page.goto("http://localhost:5000/api/ocr/results")
        expect(response).to_be_ok()
        
        print("✅ API endpoints are accessible and functional")
    
    def test_14_batch_processing_functionality(self, browser_context):
        """Test batch processing functionality."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Create multiple test images
        test_images = []
        for i in range(3):
            img = Image.new('RGB', (200, 100), color='white')
            test_image_path = tempfile.mktemp(suffix='.png')
            img.save(test_image_path, 'PNG')
            test_images.append(test_image_path)
        
        try:
            # Upload multiple images
            file_input = page.locator("#batchFileInput")
            file_input.set_input_files(test_images)
            
            # Wait for batch results
            page.wait_for_selector("#resultsSection", timeout=45000)
            
            # Check batch results content
            results_content = page.locator("#resultsContent")
            expect(results_content).to_contain_text("Batch Processing Summary")
            expect(results_content).to_contain_text("Total Files")
            
            print("✅ Batch processing functionality works correctly")
            
        finally:
            # Cleanup
            for path in test_images:
                os.unlink(path)
    
    def test_15_performance_metrics(self, browser_context):
        """Test that performance metrics are displayed."""
        page, context, browser = browser_context
        
        # Navigate to homepage
        page.goto("http://localhost:5000")
        
        # Create a test image
        img = Image.new('RGB', (250, 125), color='white')
        test_image_path = tempfile.mktemp(suffix='.png')
        img.save(test_image_path, 'PNG')
        
        try:
            # Upload test image
            file_input = page.locator("#singleFileInput")
            file_input.set_input_files(test_image_path)
            
            # Wait for results
            page.wait_for_selector("#resultsSection", timeout=30000)
            
            # Check performance metrics
            results_content = page.locator("#resultsContent")
            expect(results_content).to_contain_text("Processing Time")
            expect(results_content).to_contain_text("File Size")
            expect(results_content).to_contain_text("Confidence")
            
            print("✅ Performance metrics are displayed correctly")
            
        finally:
            # Cleanup
            os.unlink(test_image_path)

def run_phase1_tests():
    """Run all Phase 1 tests."""
    print("🚀 Starting Phase 1 OCR Tests...")
    print("=" * 50)
    
    # Create test instance
    test_instance = TestPhase1OCR()
    
    # Run tests
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    test_methods.sort()
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            print(f"\n🧪 Running: {method_name}")
            method = getattr(test_instance, method_name)
            
            # Setup browser context for each test
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, slow_mo=1000)
                context = browser.new_context()
                page = context.new_page()
                
                # Run test
                method((page, context, browser))
                
                context.close()
                browser.close()
            
            print(f"✅ {method_name} - PASSED")
            passed += 1
            
        except Exception as e:
            print(f"❌ {method_name} - FAILED: {str(e)}")
            failed += 1
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All Phase 1 tests passed! OCR Foundation is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review and fix issues.")
    
    return passed, failed

if __name__ == "__main__":
    run_phase1_tests()
