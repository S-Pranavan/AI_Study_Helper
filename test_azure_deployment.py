import asyncio
from playwright.async_api import async_playwright
import time
import os

async def test_azure_deployment():
    """Test the AI Study Helper application deployed on Azure"""
    
    # Get the Azure URL from environment variable or use a default
    azure_url = os.environ.get('AZURE_APP_URL', 'https://ai-study-helper-app.azurewebsites.net')
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to True for headless testing
        page = await browser.new_page()
        
        try:
            print("🧪 Starting Azure deployment test...")
            print(f"🌐 Testing URL: {azure_url}")
            
            # Navigate to the Azure application
            print("📱 Navigating to Azure application...")
            await page.goto(azure_url)
            await page.wait_for_load_state("networkidle")
            
            # Check if the page loaded successfully
            title = await page.title()
            print(f"✅ Page loaded successfully. Title: {title}")
            
            # Test OCR functionality
            print("🔍 Testing OCR functionality...")
            
            # Look for the OCR button
            ocr_button = await page.locator("button:has-text('Start OCR')").first
            if not ocr_button:
                print("❌ 'Start OCR' button not found!")
                return False
            
            print("✅ 'Start OCR' button found!")
            
            # Click the OCR button
            print("🖱️ Clicking the 'Start OCR' button...")
            await ocr_button.click()
            
            # Wait for OCR interface to appear
            print("⏳ Waiting for OCR interface to appear...")
            try:
                await page.wait_for_selector("#ocrInterface", timeout=5000)
                print("✅ OCR interface appeared successfully!")
            except Exception as e:
                print(f"❌ OCR interface did not appear: {e}")
                return False
            
            # Check if interface is visible
            interface_visible = await page.locator("#ocrInterface").is_visible()
            if not interface_visible:
                print("❌ OCR interface is not visible!")
                return False
            
            print("✅ OCR interface is visible!")
            
            # Test file upload functionality
            print("📁 Testing file upload functionality...")
            
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
            
            # Test OCR interface close
            print("🔒 Testing OCR interface close functionality...")
            
            close_button = await page.locator("button:has-text('Close')").first
            if close_button:
                await close_button.click()
                print("✅ Close button clicked")
                
                # Wait for interface to disappear
                try:
                    await page.wait_for_selector("#ocrInterface", state="hidden", timeout=3000)
                    print("✅ OCR interface closed successfully!")
                except Exception as e:
                    print(f"❌ OCR interface did not close: {e}")
                    return False
            else:
                print("❌ Close button not found")
                return False
            
            # Test other navigation links
            print("🧭 Testing navigation functionality...")
            
            # Test Subjects link
            subjects_link = await page.locator("a:has-text('Subjects')").first
            if subjects_link:
                await subjects_link.click()
                await page.wait_for_load_state("networkidle")
                print("✅ Subjects page loaded successfully")
                
                # Go back to home
                await page.go_back()
                await page.wait_for_load_state("networkidle")
            else:
                print("❌ Subjects link not found")
            
            # Test Study Session link
            study_link = await page.locator("a:has-text('Study Session')").first
            if study_link:
                await study_link.click()
                await page.wait_for_load_state("networkidle")
                print("✅ Study Session page loaded successfully")
                
                # Go back to home
                await page.go_back()
                await page.wait_for_load_state("networkidle")
            else:
                print("❌ Study Session link not found")
            
            print("🎉 All Azure deployment tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
        
        finally:
            await browser.close()

async def main():
    """Main function to run the Azure deployment test"""
    print("🚀 Starting Azure deployment test suite...")
    print("=" * 60)
    
    success = await test_azure_deployment()
    
    print("=" * 60)
    if success:
        print("🎉 All tests passed! Azure deployment is working correctly.")
    else:
        print("❌ Some tests failed. Azure deployment needs attention.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
