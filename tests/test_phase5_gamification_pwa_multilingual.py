"""
Phase 5 Test Suite: Gamification, PWA Offline Support, and Multilingual Support
Tests the integrated features of Phase 5 including:
- Gamification system (XP, levels, badges, achievements)
- PWA and offline support
- Multilingual capabilities
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_phase5_features():
    """Test all Phase 5 features"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("Starting Phase 5 Tests...")
            
            # Test 1: Main Dashboard with Gamification
            print("\nTest 1: Main Dashboard with Gamification")
            await page.goto("http://localhost:5000/")
            await page.wait_for_load_state("networkidle")
            
            # Check if gamification elements are present
            gamification_section = await page.locator("text=Gamification Dashboard").first
            if await gamification_section.is_visible():
                print("✅ Gamification dashboard section found")
            else:
                print("❌ Gamification dashboard section not found")
            
            # Check for XP and level display
            xp_element = await page.locator("text=XP:").first
            if await xp_element.is_visible():
                print("✅ XP display found")
            else:
                print("❌ XP display not found")
            
            # Test 2: PWA and Offline Support
            print("\nTest 2: PWA and Offline Support")
            
            # Check for offline support section
            offline_section = await page.locator("text=Offline Support").first
            if await offline_section.is_visible():
                print("✅ Offline support section found")
            else:
                print("❌ Offline support section not found")
            
            # Check for cache statistics
            cache_stats = await page.locator("text=Cache Statistics").first
            if await cache_stats.is_visible():
                print("✅ Cache statistics found")
            else:
                print("❌ Cache statistics not found")
            
            # Test 3: Multilingual Support
            print("\nTest 3: Multilingual Support")
            
            # Check for multilingual section
            multilingual_section = await page.locator("text=Multilingual Support").first
            if await multilingual_section.is_visible():
                print("✅ Multilingual support section found")
            else:
                print("❌ Multilingual support section not found")
            
            # Check for language detection tool
            lang_detection = await page.locator("text=Language Detection").first
            if await lang_detection.is_visible():
                print("✅ Language detection tool found")
            else:
                print("❌ Language detection tool not found")
            
            # Test 4: OCR Integration
            print("\nTest 4: OCR Integration")
            await page.goto("http://localhost:5000/ocr")
            await page.wait_for_load_state("networkidle")
            
            # Check if OCR page loads
            ocr_title = await page.locator("text=OCR Image Processing").first
            if await ocr_title.is_visible():
                print("✅ OCR page loaded successfully")
            else:
                print("❌ OCR page failed to load")
            
            # Test 5: AI Generation
            print("\nTest 5: AI Generation")
            await page.goto("http://localhost:5000/ai_generate")
            await page.wait_for_load_state("networkidle")
            
            # Check if AI generation page loads
            ai_title = await page.locator("text=AI Content Generation").first
            if await ai_title.is_visible():
                print("✅ AI generation page loaded successfully")
            else:
                print("❌ AI generation page failed to load")
            
            # Test 6: Quiz System
            print("\nTest 6: Quiz System")
            await page.goto("http://localhost:5000/quiz")
            await page.wait_for_load_state("networkidle")
            
            # Check if quiz page loads
            quiz_title = await page.locator("text=Quiz Generator").first
            if await quiz_title.is_visible():
                print("✅ Quiz page loaded successfully")
            else:
                print("❌ Quiz page failed to load")
            
            # Test 7: Flashcards
            print("\nTest 7: Flashcards")
            await page.goto("http://localhost:5000/flashcards")
            await page.wait_for_load_state("networkidle")
            
            # Check if flashcards page loads
            flashcard_title = await page.locator("text=Flashcard System").first
            if await flashcard_title.is_visible():
                print("✅ Flashcards page loaded successfully")
            else:
                print("❌ Flashcards page failed to load")
            
            # Test 8: AI Tutor
            print("\nTest 8: AI Tutor")
            await page.goto("http://localhost:5000/ai_tutor")
            await page.wait_for_load_state("networkidle")
            
            # Check if AI tutor page loads
            tutor_title = await page.locator("text=AI Tutor").first
            if await tutor_title.is_visible():
                print("✅ AI Tutor page loaded successfully")
            else:
                print("❌ AI Tutor page failed to load")
            
            # Test 9: Mind Maps
            print("\nTest 9: Mind Maps")
            await page.goto("http://localhost:5000/mind_map")
            await page.wait_for_load_state("networkidle")
            
            # Check if mind map page loads
            mindmap_title = await page.locator("text=Mind Map Generator").first
            if await mindmap_title.is_visible():
                print("✅ Mind Map page loaded successfully")
            else:
                print("❌ Mind Map page failed to load")
            
            # Test 10: API Endpoints
            print("\nTest 10: API Endpoints")
            
            # Test gamification API
            response = await page.request.get("http://localhost:5000/api/gamification/progress")
            if response.status == 200:
                print("✅ Gamification API endpoint working")
            else:
                print("❌ Gamification API endpoint failed")
            
            # Test offline API
            response = await page.request.get("http://localhost:5000/api/offline/stats")
            if response.status == 200:
                print("✅ Offline API endpoint working")
            else:
                print("❌ Offline API endpoint failed")
            
            # Test multilingual API
            response = await page.request.get("http://localhost:5000/api/multilingual/languages")
            if response.status == 200:
                print("✅ Multilingual API endpoint working")
            else:
                print("❌ Multilingual API endpoint failed")
            
            print("\nPhase 5 Tests Completed!")
            
        except Exception as e:
            print(f"Test failed with error: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_phase5_features())
