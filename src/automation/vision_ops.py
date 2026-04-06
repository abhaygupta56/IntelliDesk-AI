"""
Vision Operations - The 'Eyes' of IntelliDesk
Handles screenshot capture, compression, and analysis using Groq Vision.
"""
import pyautogui
import base64
import io
from PIL import Image
from groq import Groq
from src.utils.logger import Logger
from config import Config

logger = Logger.get_logger("VisionOps")

def analyze_screen(prompt: str) -> dict:
    """
    Take a stealth screenshot, compress it, and analyze it using Groq Vision API.
    """
    try:
        logger.info(f"Taking stealth screenshot for vision analysis: '{prompt}'")
        
        # 1. Capture screen
        screenshot = pyautogui.screenshot()
        
        # 2. Compress and resize to save bandwidth/tokens
        # Maximum dimension is usually around 1080p for vision models
        max_size = (1920, 1080)
        screenshot.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 3. Convert to Base64 JPEG
        buffered = io.BytesIO()
        screenshot.save(buffered, format="JPEG", quality=70) # 70% quality compression
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        base64_image = f"data:image/jpeg;base64,{img_str}"
        
        logger.info("Image compressed and encoded. Sending to Groq Vision...")
        
        # 4. Call Groq Vector Vision Model
        client = Groq(api_key=Config.GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", # Powerful multimodal model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image
                            }
                        }
                    ]
                }
            ],
            temperature=0.4,
            max_tokens=1024
        )
        
        analysis = response.choices[0].message.content
        logger.info("Vision analysis complete.")
        
        return {
            "status": "success",
            "message": analysis,
            "data": {"prompt": prompt}
        }
        
    except Exception as e:
        logger.error(f"Vision analysis failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Could not analyze screen: {str(e)}"
        }
