def check_ethical_content(text: str) -> None:
    """Checks for offensive or unethical words."""
    blocklist = [
        "hate speech", 
        "racist", 
        "sexist",
        "violence",
        "abuse"
    ]
    text_lower = text.lower()
    for word in blocklist:
        if word in text_lower:
            raise ValueError(f"Ethical violation detected: contains inappropriate content ('{word}').")
