# Handles all interaction with the Gemini API, including sending prompts, receiving responses, and returning a clean explanation string 
from google import Client
from dotenv import dotenv_values
from gemini_prompts import Prompt
import re


config = dotenv_values(".env")
api_key = config["GEMINI_API_KEY"]
model = config["MODEL_ID"]

try:
    client = Client(api_key)
except Exception as e:
    raise RuntimeError(f"ERROR: encountered {e} trying to initialize Gemini Client")

def close_client():
    """
    Closes connection with Client

    Returns:
        Boolean: sucess in clossing client

    """
    # Client used by module
    global client

    # Close a non empty client
    if(client != None):
        client.close()
        client = None

    return client == None
    
def parse_gemini_response(response_text):
    """
    Parse and clean Gemini response to extract just the explanation text.
    
    Args:
        response_text (str): Raw response from Gemini
        
    Returns:
        str: Cleaned explanation text
        
    Raises:
        ValueError: If response is empty, invalid, or contains error indicators
    """
    
    # Check for empty or None response
    if not response_text or not isinstance(response_text, str):
        raise ValueError("Gemini returned empty or invalid response")
    
    # Check for common error indicators
    error_indicators = [
        "error", "unavailable", "rate limit", "quota exceeded",
        "invalid request", "internal error", "can't", "cannot"
    ]
    
    response_lower = response_text.lower()
    for error in error_indicators:
        if error in response_lower and len(response_text) < 100:  # Short error messages
            raise ValueError(f"Gemini error response: {response_text[:200]}")
    
    # Remove markdown code blocks
    cleaned = re.sub(r"```.*?```", "", response_text, flags=re.DOTALL)
    
    # Remove inline code formatting
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    
    # Remove markdown formatting (bold, italic, headers)
    cleaned = re.sub(r"\*\*\*(.*?)\*\*\*", r"\1", cleaned)  # bold italic
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)      # bold
    cleaned = re.sub(r"\*(.*?)\*", r"\1", cleaned)          # italic
    cleaned = re.sub(r"__(.*?)__", r"\1", cleaned)          # bold alternate
    cleaned = re.sub(r"_(.*?)_", r"\1", cleaned)            # italic alternate
    cleaned = re.sub(r"^#{1,6}\s+", "", cleaned, flags=re.MULTILINE)  # headers
    
    # Remove HTML tags if any
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    
    # Remove excessive whitespace and newlines
    cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)  # Collapse multiple newlines
    cleaned = re.sub(r"[ \t]+", " ", cleaned)      # Collapse spaces
    cleaned = cleaned.strip()
    
    # Remove any leftover special characters or artifacts
    cleaned = re.sub(r"[ \t]+$", "", cleaned, flags=re.MULTILINE)
    
    # Validate we still have content
    if not cleaned or len(cleaned) < 10:
        raise ValueError(f"Parsing produced empty or insufficient content: {cleaned[:100]}")
    
    return cleaned

def gemini_response(query: dict) -> str:
    """
    Parse and clean Gemini response to extract just the explanation text.
    
    Args:
        query (dict): Raw response from Gemini
        
    Returns:
        str: Gemini's response
        
    Raises:
        RuntimeError: If a valid response could not be produced
    """
    # Specified client and model of module
    global client
    global model
    
    # Attempt to call Gemini with given prompt
    try: 
        # Parse query into a valid prompt
        prompt = Prompt(query)       
        model_response = client.model.generate_content(
            model = model,
            contents = prompt.contents,
            config = prompt.config
        )

        response = parse_gemini_response(model_response.text)
    # Error-handling
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")

    # Succesful response    
    return response
    
    




