"""
Enhanced OCR Pipeline Module for AI Study Helper
Phase 1 Implementation: Foundation & OCR Setup using EasyOCR
"""

import cv2
import numpy as np
from PIL import Image
import os
import logging
from typing import Dict, Tuple, Optional
import tempfile
import re

# Try to import EasyOCR, fallback to basic image processing if not available
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available, using basic image processing only")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRPipeline:
    """
    Enhanced OCR Pipeline for processing handwritten notes, textbook pages, and diagrams.
    Implements advanced image preprocessing and text extraction using free resources.
    """
    
    def __init__(self):
        """Initialize OCR pipeline with enhanced settings."""
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        self.max_image_size = 3000  # Increased for better quality
        
        # Initialize EasyOCR if available
        if EASYOCR_AVAILABLE:
            try:
                # Initialize with English and common languages
                self.reader = easyocr.Reader(['en'], gpu=False)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                EASYOCR_AVAILABLE = False
        
        # Enhanced preprocessing parameters
        self.preprocessing_config = {
            'deskew_threshold': 0.5,
            'noise_reduction': True,
            'contrast_enhancement': True,
            'sharpen': True,
            'adaptive_threshold': True
        }
        
    def validate_image(self, image_path: str) -> bool:
        """
        Validate if the image file is supported and exists.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            bool: True if image is valid, False otherwise
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return False
                
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in self.supported_formats:
                logger.error(f"Unsupported image format: {file_ext}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            return False
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Enhanced image preprocessing for better OCR accuracy.
        Handles various image types: handwritten notes, textbook pages, diagrams.
        
        Args:
            image_path (str): Path to the input image
            
        Returns:
            np.ndarray: Preprocessed image array
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Resize if too large (max 3000px)
            height, width = image.shape[:2]
            if max(height, width) > self.max_image_size:
                scale = self.max_image_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhanced deskewing for tilted images
            gray = self._apply_deskewing(gray)
            
            # Noise reduction for low-quality images
            if self.preprocessing_config['noise_reduction']:
                gray = self._reduce_noise(gray)
            
            # Contrast enhancement for low-light images
            if self.preprocessing_config['contrast_enhancement']:
                gray = self._enhance_contrast(gray)
            
            # Sharpening for blurry images
            if self.preprocessing_config['sharpen']:
                gray = self._sharpen_image(gray)
            
            # Adaptive thresholding for mixed quality images
            if self.preprocessing_config['adaptive_threshold']:
                gray = self._apply_adaptive_threshold(gray)
            
            logger.info("Image preprocessing completed successfully")
            return gray
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {str(e)}")
            # Return original grayscale if preprocessing fails
            return cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2GRAY)
    
    def _apply_deskewing(self, image: np.ndarray) -> np.ndarray:
        """Apply advanced deskewing for tilted images."""
        try:
            # Find text lines for better angle detection
            coords = np.column_stack(np.where(image > 0))
            if len(coords) > 0:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = 90 + angle
                
                # Only apply rotation if angle is significant
                if abs(angle) > self.preprocessing_config['deskew_threshold']:
                    (h, w) = image.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    image = cv2.warpAffine(image, M, (w, h), 
                                         flags=cv2.INTER_CUBIC, 
                                         borderMode=cv2.BORDER_REPLICATE)
                    logger.info(f"Applied deskewing with angle: {angle:.2f} degrees")
            
            return image
        except Exception as e:
            logger.warning(f"Deskewing failed: {e}")
            return image
    
    def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """Reduce noise in low-quality images."""
        # Bilateral filter for edge-preserving noise reduction
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        return denoised
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast for low-light images."""
        # CLAHE for adaptive contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        return enhanced
    
    def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """Sharpen blurry images."""
        # Unsharp masking
        gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
        sharpened = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        return sharpened
    
    def _apply_adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding for mixed quality images."""
        # Adaptive threshold for varying lighting conditions
        adaptive = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        return adaptive
    
    def extract_text(self, image_path: str, preprocess: bool = True) -> Dict:
        """
        Extract text from images with enhanced preprocessing.
        Handles handwritten notes, textbook pages, diagrams, and mixed quality images.
        
        Args:
            image_path (str): Path to the input image
            preprocess (bool): Whether to apply image preprocessing
            
        Returns:
            Dict: Extraction results with text, confidence, and metadata
        """
        try:
            if not self.validate_image(image_path):
                return {
                    'success': False,
                    'error': 'Invalid image file',
                    'text': '',
                    'confidence': 0.0
                }
            
            # Preprocess image if requested
            if preprocess:
                processed_image = self.preprocess_image(image_path)
                temp_path = tempfile.mktemp(suffix='.png')
                cv2.imwrite(temp_path, processed_image)
                image_to_process = temp_path
            else:
                image_to_process = image_path
                processed_image = None
            
            # Extract text using available OCR method
            if EASYOCR_AVAILABLE:
                result = self._extract_with_easyocr(image_to_process)
            else:
                result = self._extract_with_basic_processing(image_to_process)
            
            # Clean up temporary file if created
            if preprocess and os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Post-process extracted text
            if result['success']:
                result['text'] = self._post_process_text(result['text'])
                result['content_type'] = self._classify_content(result['text'])
                result['suggestions'] = self._generate_suggestions(result['text'], result['content_type'])
            
            logger.info(f"Text extraction completed. Confidence: {result.get('confidence', 0):.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def _extract_with_easyocr(self, image_path: str) -> Dict:
        """Extract text using EasyOCR."""
        try:
            results = self.reader.readtext(image_path)
            
            if not results:
                return {
                    'success': False,
                    'error': 'No text detected',
                    'text': '',
                    'confidence': 0.0
                }
            
            # Combine all detected text
            extracted_text = ' '.join([text[1] for text in results])
            confidences = [text[2] for text in results]
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                'success': True,
                'text': extracted_text,
                'confidence': avg_confidence,
                'word_count': len(extracted_text.split()),
                'char_count': len(extracted_text),
                'preprocessed': True
            }
            
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {e}")
            return self._extract_with_basic_processing(image_path)
    
    def _extract_with_basic_processing(self, image_path: str) -> Dict:
        """Fallback text extraction using basic image processing."""
        try:
            # Basic edge detection and contour analysis
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            
            # Apply edge detection
            edges = cv2.Canny(image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze image structure
            text_regions = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 10000:  # Typical text region size
                    text_regions += 1
            
            # Estimate text presence based on structure
            confidence = min(0.3, text_regions / 100.0) if text_regions > 0 else 0.0
            
            return {
                'success': True,
                'text': '[Text structure detected - OCR processing recommended]',
                'confidence': confidence,
                'word_count': text_regions,
                'char_count': text_regions * 5,  # Estimate
                'preprocessed': True,
                'note': 'Basic processing only - install EasyOCR for full text extraction'
            }
            
        except Exception as e:
            logger.error(f"Basic processing failed: {e}")
            return {
                'success': False,
                'error': 'Text extraction failed',
                'text': '',
                'confidence': 0.0
            }
    
    def _post_process_text(self, text: str) -> str:
        """Clean and format extracted text."""
        if not text:
            return text
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common OCR errors
        text = re.sub(r'[|]{2,}', 'l', text)  # Fix broken l's
        text = re.sub(r'[0]{2,}', 'o', text)  # Fix broken o's
        
        # Remove isolated characters that are likely noise
        text = re.sub(r'\b[a-zA-Z]\b', '', text)
        
        return text
    
    def _classify_content(self, text: str) -> str:
        """Classify the type of content extracted."""
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Check for mathematical content
        if any(char in text for char in '+-*/=()[]{}'):
            return 'mathematical'
        
        # Check for scientific content
        scientific_terms = ['equation', 'formula', 'theorem', 'hypothesis', 'experiment']
        if any(term in text_lower for term in scientific_terms):
            return 'scientific'
        
        # Check for handwritten notes
        if len(text.split()) < 20:  # Short text often indicates notes
            return 'handwritten_notes'
        
        # Check for textbook content
        if len(text.split()) > 50:  # Long text often indicates textbook
            return 'textbook'
        
        return 'general'
    
    def _generate_suggestions(self, text: str, content_type: str) -> Dict:
        """Generate study suggestions based on content type."""
        suggestions = {
            'summary': '',
            'explanation': '',
            'quiz_questions': []
        }
        
        if content_type == 'mathematical':
            suggestions['summary'] = 'Mathematical content detected. Consider breaking down into steps.'
            suggestions['explanation'] = 'Focus on understanding the mathematical concepts and formulas.'
            suggestions['quiz_questions'] = [
                'Can you solve this equation step by step?',
                'What mathematical principles are being applied here?'
            ]
        elif content_type == 'scientific':
            suggestions['summary'] = 'Scientific content detected. Focus on key concepts and definitions.'
            suggestions['explanation'] = 'Understand the scientific principles and their applications.'
            suggestions['quiz_questions'] = [
                'What are the main scientific concepts mentioned?',
                'How would you explain this to someone else?'
            ]
        elif content_type == 'handwritten_notes':
            suggestions['summary'] = 'Handwritten notes detected. Organize key points into structured format.'
            suggestions['explanation'] = 'Review and expand on your notes for better understanding.'
            suggestions['quiz_questions'] = [
                'What are the main points from these notes?',
                'How can you organize this information better?'
            ]
        else:
            suggestions['summary'] = 'General content detected. Extract key information and main ideas.'
            suggestions['explanation'] = 'Break down complex concepts into simpler terms.'
            suggestions['quiz_questions'] = [
                'What are the main ideas presented?',
                'How would you summarize this content?'
            ]
        
        return suggestions
    
    def batch_process(self, image_paths: list, preprocess: bool = True) -> list:
        """
        Process multiple images in batch with enhanced preprocessing.
        
        Args:
            image_paths (list): List of image file paths
            preprocess (bool): Whether to apply image preprocessing
            
        Returns:
            list: List of extraction results for each image
        """
        results = []
        total_images = len(image_paths)
        
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"Processing image {i}/{total_images}: {os.path.basename(image_path)}")
            result = self.extract_text(image_path, preprocess)
            result['image_path'] = image_path
            result['image_name'] = os.path.basename(image_path)
            results.append(result)
        
        return results
    
    def get_ocr_info(self) -> Dict[str, any]:
        """
        Get information about the OCR system.
        
        Returns:
            Dict: Information about OCR capabilities and supported features
        """
        try:
            return {
                'ocr_engine': 'EasyOCR' if EASYOCR_AVAILABLE else 'Basic Image Processing',
                'available': EASYOCR_AVAILABLE,
                'supported_formats': list(self.supported_formats),
                'max_image_size': self.max_image_size,
                'preprocessing_features': {
                    'deskewing': True,
                    'noise_reduction': True,
                    'contrast_enhancement': True,
                    'sharpening': True,
                    'adaptive_thresholding': True
                },
                'content_types_supported': [
                    'handwritten_notes',
                    'textbook_pages', 
                    'diagrams',
                    'mathematical_content',
                    'scientific_content',
                    'mixed_quality_images'
                ],
                'features': [
                    'Advanced image preprocessing',
                    'Content classification',
                    'Study suggestions generation',
                    'Batch processing',
                    'Free and open source'
                ]
            }
        except Exception as e:
            logger.error(f"Error getting OCR info: {str(e)}")
            return {
                'error': str(e),
                'supported_formats': list(self.supported_formats)
            }

# Example usage and testing
if __name__ == "__main__":
    # Initialize OCR pipeline
    ocr = OCRPipeline()
    
    # Get OCR system information
    info = ocr.get_ocr_info()
    print("Enhanced OCR System Information:")
    print(f"OCR Engine: {info.get('ocr_engine', 'Unknown')}")
    print(f"Available: {info.get('available', False)}")
    print(f"Supported Formats: {info.get('supported_formats', [])}")
    print(f"Content Types: {info.get('content_types_supported', [])}")
    print(f"Features: {info.get('features', [])}")
    
    # Test with a sample image (if available)
    test_image = "test_image.png"  # Replace with actual test image path
    if os.path.exists(test_image):
        print(f"\nTesting OCR with: {test_image}")
        result = ocr.extract_text(test_image)
        print(f"Success: {result['success']}")
        print(f"Text: {result['text'][:100]}...")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Content Type: {result.get('content_type', 'Unknown')}")
        if result.get('suggestions'):
            print(f"Suggestions: {result['suggestions']}")
    else:
        print("\nNo test image found. Enhanced OCR pipeline is ready for use.")
