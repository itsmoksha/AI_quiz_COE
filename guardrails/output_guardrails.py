import json

def strip_markdown(text: str) -> str:
    """Strips markdown json wrappers if present."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def validate_json(text: str) -> dict:
    """Ensures the text is valid JSON."""
    clean_text = strip_markdown(text)
    
    start = clean_text.find("{")
    end = clean_text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No valid JSON object found in model output.")
        
    try:
        return json.loads(clean_text[start:end])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
