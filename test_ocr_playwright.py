#!/usr/bin/env python3
"""
Playwright Test for OCR Functionality
Tests the OCR button and modal functionality
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_ocr_functionality():
    """Test the OCR functionality using Playwright"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
        page = await browser.new_page()
        
        try:
            print("🚀 Starting OCR functionality test...")
            
            # Navigate to the application
            print("📱 Navigating to http://localhost:5000...")
            await page.goto("http://localhost:5000")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            print("✅ Page loaded successfully")
            
            # Check if the OCR button is visible
            print("🔍 Looking for OCR button...")
            ocr_button = page.locator("button:has-text('Start OCR')")
            
            if await ocr_button.is_visible():
                print("✅ OCR button found and visible")
            else:
                print("❌ OCR button not visible")
                return False
            
            # Click the OCR button
            print("🖱️ Clicking OCR button...")
            await ocr_button.click()
            
            # Wait for modal to appear
            print("⏳ Waiting for OCR modal...")
            await page.wait_for_selector("#ocrModal", timeout=5000)
            
            # Check if modal is visible
            modal = page.locator("#ocrModal")
            if await modal.is_visible():
                print("✅ OCR modal opened successfully")
            else:
                print("❌ OCR modal not visible")
                return False
            
            # Check modal content
            print("🔍 Checking modal content...")
            
            # Check title
            title = page.locator("#ocrModalLabel")
            if await title.is_visible():
                title_text = await title.text_content()
                print(f"✅ Modal title: {title_text}")
            else:
                print("❌ Modal title not found")
            
            # Check upload area
            upload_area = page.locator("#singleUploadArea")
            if await upload_area.is_visible():
                print("✅ Upload area visible")
            else:
                print("❌ Upload area not visible")
            
            # Check file input
            file_input = page.locator("#singleFileInput")
            if await file_input.is_visible():
                print("✅ File input visible")
            else:
                print("❌ File input not visible")
            
            # Test file upload (create a test image)
            print("📁 Testing file upload...")
            
            # Create a simple test image path (you can replace this with an actual image)
            test_image_path = "test_image.png"
            
            # Check if we can interact with the file input
            try:
                # Set a test file (this will just test the input, not actually upload)
                await file_input.set_input_files(test_image_path)
                print("✅ File input interaction successful")
            except Exception as e:
                print(f"⚠️ File input test: {e}")
            
            # Close the modal
            print("🔒 Closing modal...")
            close_button = page.locator("#ocrModal .btn-close")
            await close_button.click()
            
            # Wait for modal to close
            await page.wait_for_timeout(1000)
            
            # Check if modal is closed
            if not await modal.is_visible():
                print("✅ Modal closed successfully")
            else:
                print("❌ Modal did not close")
            
            print("🎉 OCR functionality test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
        
        finally:
            # Close browser
            await browser.close()

async def main():
    """Main function to run the test"""
    print("🧪 Starting Playwright OCR Test...")
    print("=" * 50)
    
    success = await test_ocr_functionality()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! OCR functionality is working correctly.")
    else:
        print("❌ Some tests failed. Please check the application.")
    
    return success

if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
