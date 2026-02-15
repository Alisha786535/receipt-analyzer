import cv2
import numpy as np
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image preprocessing for better OCR results"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def preprocess(self, image_path):
        """
        Apply preprocessing techniques to enhance text visibility
        
        Steps:
        1. Convert to grayscale
        2. Noise reduction
        3. Contrast enhancement
        4. Thresholding
        5. Deskewing
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Noise reduction
            denoised = cv2.fastNlMeansDenoising(gray, h=30)
            
            # Contrast enhancement (CLAHE)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Adaptive thresholding
            binary = cv2.adaptiveThreshold(
                enhanced, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Deskew image
            deskewed = self._deskew(binary)
            
            # Additional sharpening
            kernel = np.array([[-1,-1,-1],
                               [-1, 9,-1],
                               [-1,-1,-1]])
            sharpened = cv2.filter2D(deskewed, -1, kernel)
            
            logger.info("Image preprocessing completed successfully")
            return sharpened
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {str(e)}")
            raise
    
    def _deskew(self, image):
        """Correct image skew"""
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
                                flags=cv2.INTER_CUBIC,
                                borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    def resize_if_needed(self, image, max_width=2000):
        """Resize large images to improve processing speed"""
        h, w = image.shape[:2]
        if w > max_width:
            scale = max_width / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            resized = cv2.resize(image, (new_w, new_h))
            logger.info(f"Image resized from {w}x{h} to {new_w}x{new_h}")
            return resized
        return image