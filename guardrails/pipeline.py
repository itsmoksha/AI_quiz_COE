from guardrails.input_guardrails import validate_input
from guardrails.output_guardrails import validate_json
from guardrails.ethical_guardrails import check_ethical_content
from guardrails.security_guardrails import check_security_content
from guardrails.contextual_guardrails import check_grounding

def apply_input_guardrails(text: str) -> None:
    """Applies all input-stage guardrails."""
    validate_input(text)

def apply_output_guardrails(raw_response: str, context: str = None) -> dict:
    """
    Applies all output-stage guardrails to the LLM response.
    Returns the parsed JSON dictionary if all checks pass.
    """
    # 1. Check for ethical violations (raw text)
    check_ethical_content(raw_response)
    
    # 2. Check for security violations (raw text)
    check_security_content(raw_response)
    
    # 3. Format & Schema Validation (returns dict)
    parsed_json = validate_json(raw_response)
    
    # 4. Contextual Grounding (if context provided, like in RAG)
    if context:
        check_grounding(parsed_json, context)
        
    return parsed_json
