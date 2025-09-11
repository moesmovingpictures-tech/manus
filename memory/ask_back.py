from typing import Optional

def antecedent_resolver(text: str) -> bool:
    # Placeholder for a more sophisticated antecedent resolution
    # For now, a simple check if a pronoun has a clear preceding noun
    words = text.lower().split()
    if "it" in words or "they" in words or "them" in words:
        # Very basic: check if there's a noun before the pronoun
        # This needs a proper NLP library for real implementation
        return False # Assume no clear antecedent for now
    return True

def should_ask_back(turn: dict) -> Optional[str]:
    """Return a question if I am uncertain."""
    txt = turn["text"]

    # If the turn is very short and not a question
    if "?" not in txt and len(txt.split()) < 4:
        return "Could you tell me a bit more about that?"

    # If pronouns are used without clear antecedents
    if ("it" in txt.lower() or "they" in txt.lower() or "them" in txt.lower()) and not antecedent_resolver(txt):
        return "When you say ‘it’, what exactly do you mean?"

    return None


