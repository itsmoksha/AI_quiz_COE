def check_input_length(text: str, max_length: int = 1000) -> None:
    if len(text) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters.")

def check_prompt_injection(text: str) -> None:
    injection_phrases = [
        "ignore previous instructions",
        "system prompt",
        "forget all instructions",
        "you are now",
        "bypass",
        "developer mode"
    ]
    text_lower = text.lower()
    for phrase in injection_phrases:
        if phrase in text_lower:
            raise ValueError(f"Potential prompt injection detected: {phrase}")

def validate_input(text: str, max_length: int = 1000) -> None:
    """Validates user input against length constraints and prompt injection."""
    check_input_length(text, max_length)
    check_prompt_injection(text)
