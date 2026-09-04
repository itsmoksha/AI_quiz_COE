def check_grounding(parsed_json: dict, context: str) -> None:
    """
    Checks if the generated text is grounded in the provided context.
    Uses a simple heuristic: the correct answer for each question must share 
    at least one significant word with the provided context.
    """
    if not context:
        return

    context_words = set(word.strip('.,!?()[]{}"\'').lower() for word in context.split())
    
    # Common words to ignore in grounding check
    stopwords = {"a", "an", "the", "is", "are", "and", "or", "to", "in", "of", "for", "with", "on", "as", "by"}
    
    questions = parsed_json.get("questions", [])
    for idx, q in enumerate(questions):
        correct_answer = q.get("correct_answer", "")
        answer_words = set(word.strip('.,!?()[]{}"\'').lower() for word in correct_answer.split())
        
        # Filter out stopwords
        significant_answer_words = answer_words - stopwords
        
        if not significant_answer_words:
            continue
            
        # Check if there is an intersection
        if not significant_answer_words.intersection(context_words):
            raise ValueError(f"Contextual violation detected (Hallucination): Question {idx+1} answer '{correct_answer}' does not appear to be grounded in the context.")
