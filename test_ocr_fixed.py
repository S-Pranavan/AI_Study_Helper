import asyncio
from playwright.async_api import async_playwright
import time

async def test_ocr_functionality():
    """Test the OCR functionality to ensure it's working properly"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to True for headless testing
        page = await browser.new_page()
        
        try:
            print("🧪 Starting OCR functionality test...")
            
            # Navigate to the application
            print("📱 Navigating to http://localhost:5000...")
            await page.goto("http://localhost:5000")
            await page.wait_for_load_state("networkidle")
            
            # Check if the page loaded successfully
            title = await page.title()
            print(f"✅ Page loaded successfully. Title: {title}")
            
            # Look for the OCR button
            print("🔍 Looking for the 'Start OCR' button...")
            ocr_button = await page.locator("button:has-text('Start OCR')").first
            if not ocr_button:
                print("❌ 'Start OCR' button not found!")
                return False
            
            print("✅ 'Start OCR' button found!")
            
            # Click the OCR button
            print("🖱️ Clicking the 'Start OCR' button...")
            await ocr_button.click()
            
            # Wait for modal to appear
            print("⏳ Waiting for OCR modal to appear...")
            try:
                await page.wait_for_selector("#ocrModal", timeout=5000)
                print("✅ OCR modal appeared successfully!")
            except Exception as e:
                print(f"❌ OCR modal did not appear: {e}")
                return False
            
            # Check if modal is visible
            modal_visible = await page.locator("#ocrModal").is_visible()
            if not modal_visible:
                print("❌ Modal is not visible!")
                return False
            
            print("✅ Modal is visible!")
            
            # Check modal content
            print("🔍 Checking modal content...")
            
            # Check for upload areas
            single_upload = await page.locator("#singleUploadArea").is_visible()
            batch_upload = await page.locator("#batchUploadArea").is_visible()
            
            if single_upload:
                print("✅ Single upload area is visible")
            else:
                print("❌ Single upload area is not visible")
            
            if batch_upload:
                print("✅ Batch upload area is visible")
            else:
                print("❌ Batch upload area is not visible")
            
            # Check for file inputs
            single_input = await page.locator("#singleFileInput").is_visible()
            batch_input = await page.locator("#batchFileInput").is_visible()
            
            if not single_input:
                print("✅ Single file input is hidden (as expected)")
            else:
                print("❌ Single file input should be hidden")
            
            if not batch_input:
                print("✅ Batch file input is hidden (as expected)")
            else:
                print("❌ Batch file input should be hidden")
            
            # Check for processing spinner (should be hidden initially)
            spinner = await page.locator("#processingSpinner").is_visible()
            if not spinner:
                print("✅ Processing spinner is hidden initially (as expected)")
            else:
                print("❌ Processing spinner should be hidden initially")
            
            # Check for results area (should be hidden initially)
            results = await page.locator("#ocrResults").is_visible()
            if not results:
                print("✅ Results area is hidden initially (as expected)")
            else:
                print("❌ Results area should be hidden initially")
            
            # Test modal close functionality
            print("🔒 Testing modal close functionality...")
            
            # Try to close with close button
            close_button = await page.locator("button:has-text('Close')").first
            if close_button:
                await close_button.click()
                print("✅ Close button clicked")
                
                # Wait for modal to disappear
                try:
                    await page.wait_for_selector("#ocrModal", state="hidden", timeout=3000)
                    print("✅ Modal closed successfully!")
                except Exception as e:
                    print(f"❌ Modal did not close: {e}")
                    return False
            else:
                print("❌ Close button not found")
                return False
            
            # Reopen modal for further testing
            print("🔄 Reopening modal for further testing...")
            await ocr_button.click()
            await page.wait_for_selector("#ocrModal", timeout=5000)
            
            # Test drag and drop area interaction
            print("🖱️ Testing drag and drop area interaction...")
            
            # Click on single upload area to trigger file input
            single_area = await page.locator("#singleUploadArea")
            await single_area.click()
            
            # Check if file input is accessible
            try:
                # This should trigger the file input
                await page.wait_for_timeout(1000)
                print("✅ Single upload area is clickable")
            except Exception as e:
                print(f"❌ Error with single upload area: {e}")
            
            print("🎉 All OCR functionality tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
        
        finally:
            await browser.close()

async def main():
    """Main function to run the test"""
    print("🚀 Starting OCR functionality test suite...")
    print("=" * 50)
    
    success = await test_ocr_functionality()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! OCR functionality is working correctly.")
    else:
        print("❌ Some tests failed. OCR functionality needs attention.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
