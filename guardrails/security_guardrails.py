def check_security_content(text: str) -> None:
    """Checks for malicious payloads or dangerous commands in generated text."""
    blocklist = [
        "rm -rf", 
        "mkfs", 
        "drop table", 
        "<script>", 
        "nc -e", 
        "eval("
    ]
    text_lower = text.lower()
    for word in blocklist:
        if word in text_lower:
            raise ValueError(f"Security violation detected: contains potentially malicious payload ('{word}').")
