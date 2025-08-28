"""
OCR Pipeline Module for AI Study Helper
Phase 1 Implementation: Foundation & OCR Setup
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import logging
from typing import Dict, Tuple, Optional
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRPipeline:
    """
    OCR Pipeline for processing handwritten notes and textbook images.
    Implements image preprocessing and Tesseract OCR integration.
    """
    
    def __init__(self):
        """Initialize OCR pipeline with default settings."""
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        self.max_image_size = 2000  # Maximum dimension for optimization
        
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
        Preprocess image for better OCR accuracy.
        Implements deskewing, noise reduction, and contrast enhancement.
        
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
            
            # Resize if too large (max 2000px)
            height, width = image.shape[:2]
            if max(height, width) > self.max_image_size:
                scale = self.max_image_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply deskewing (rotation correction)
            coords = np.column_stack(np.where(gray > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = 90 + angle
            if angle != 0:
                (h, w) = gray.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                logger.info(f"Applied deskewing with angle: {angle:.2f} degrees")
            
            # Noise reduction using Gaussian blur
            denoised = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Contrast enhancement using adaptive histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Apply adaptive thresholding for better text extraction
            thresh = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            logger.info("Image preprocessing completed successfully")
            return cleaned
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {str(e)}")
            raise
    
    def extract_text(self, image_path: str, preprocess: bool = True) -> Dict[str, any]:
        """
        Extract text from image using Tesseract OCR.
        
        Args:
            image_path (str): Path to the input image
            preprocess (bool): Whether to apply image preprocessing
            
        Returns:
            Dict: Dictionary containing extracted text and metadata
        """
        try:
            # Validate image
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
                # Save processed image temporarily for OCR
                temp_path = tempfile.mktemp(suffix='.png')
                cv2.imwrite(temp_path, processed_image)
                ocr_image_path = temp_path
            else:
                ocr_image_path = image_path
            
            # Configure Tesseract parameters for better accuracy
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:()[]{}"\'-_+=/\\|@#$%^&*~`<>'
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                ocr_image_path, 
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Get confidence scores
            confidence_scores = text.get('conf', [])
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Clean extracted text
            extracted_text = text.get('text', '').strip()
            
            # Clean up temporary file if created
            if preprocess and os.path.exists(temp_path):
                os.remove(temp_path)
            
            logger.info(f"Text extraction completed. Confidence: {avg_confidence:.2f}%")
            
            return {
                'success': True,
                'text': extracted_text,
                'confidence': avg_confidence / 100.0,  # Convert to 0-1 scale
                'word_count': len(extracted_text.split()),
                'char_count': len(extracted_text),
                'preprocessed': preprocess
            }
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def batch_process(self, image_paths: list, preprocess: bool = True) -> list:
        """
        Process multiple images in batch.
        
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
            Dict: Information about Tesseract and supported languages
        """
        try:
            # Get Tesseract version
            version = pytesseract.get_tesseract_version()
            
            # Get available languages
            languages = pytesseract.get_languages()
            
            return {
                'tesseract_version': str(version),
                'available_languages': languages,
                'default_language': 'eng',
                'supported_formats': list(self.supported_formats)
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
    print("OCR System Information:")
    print(f"Tesseract Version: {info.get('tesseract_version', 'Unknown')}")
    print(f"Available Languages: {info.get('available_languages', [])}")
    print(f"Supported Formats: {info.get('supported_formats', [])}")
    
    # Test with a sample image (if available)
    test_image = "test_image.png"  # Replace with actual test image path
    if os.path.exists(test_image):
        print(f"\nTesting OCR with: {test_image}")
        result = ocr.extract_text(test_image)
        print(f"Success: {result['success']}")
        print(f"Text: {result['text'][:100]}...")
        print(f"Confidence: {result['confidence']:.2%}")
    else:
        print("\nNo test image found. OCR pipeline is ready for use.")
