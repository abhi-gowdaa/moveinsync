from langchain_google_genai import ChatGoogleGenerativeAI
import logging
import base64
from pathlib import Path
from langchain_core.messages import HumanMessage


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize Gemini Vision for image extraction
vision_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)




PHOTO_EXTRACTION_PROMPT = """Extract all transportation-related information from this image.

Look for:
- Vehicle license plates (exact format)
- Trip IDs or codes
- Route names/numbers
- Driver names
- Stop names
- Any visible text or numbers

Provide a brief summary of what you see. Be precise and preserve exact formats (e.g., if you see "KA-01-AB-1234", write it exactly like that).

If multiple items are visible, list them all. If nothing relevant is found, say "No relevant information found in image."

Keep response concise and factual."""



async def extract_photo_summary(image_path: str) -> str:
    """
    Extract content from photo using Gemini Vision.
    Returns a text summary to append to user message.
    """
    logger.info(f"Extracting content from image: {image_path}")
    
    try:
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Determine image type
        file_extension = Path(image_path).suffix.lower()
        mime_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        mime_type = mime_type_map.get(file_extension, "image/jpeg")
        
        # Create message with image
        message = HumanMessage(
            content=[
                {"type": "text", "text": PHOTO_EXTRACTION_PROMPT},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image_data}"}
                }
            ]
        )
        
        # Call Gemini Vision
        response = vision_llm.invoke([message])
        photo_summary = response.content.strip()
        
        logger.info(f"Photo summary extracted: {photo_summary}")
        return photo_summary
        
    except Exception as e:
        logger.error(f"Error extracting photo content: {str(e)}")
        return ""  # Return empty if extraction fails