"""Explicitly curated from Fifer's existing skill, usage, privacy and safety rules.

This tuple is the entire retrieval collection. No filesystem/web/private-record
search, embeddings, external service, or inferred history is involved.
"""
CONTENT = (
    {"id": "skill", "title": "Available grounding skill",
     "terms": ("skill", "try", "choose", "recommend", "ground", "54321", "5-4-3-2-1", "see", "feel", "hear", "smell", "taste", "picture"),
     "text": "Fifer offers one skill: 5-4-3-2-1 sensory grounding. The app controls See 5, Feel 4, an optional check-in, Hear 3, Smell 2 and Taste 1. Answers are optional and unscored; you can skip any category and choose Finish at the end."},
    {"id": "usage", "title": "Using Fifer",
     "terms": ("app", "fifer", "begin", "start", "use", "help", "finish", "complete", "how"),
     "text": "Choose Begin grounding to start. Each screen offers optional examples and text. Fifer does not sense your surroundings. No touching, eating, drinking, scent-finding or disclosure is required. Take your time; there is nothing to get right."},
    {"id": "controls", "title": "Pause, leave and resume",
     "terms": ("pause", "resume", "stop", "leave", "return", "refresh", "restart"),
     "text": "Pause keeps your place and requires explicit Resume. Stop/Leave exits immediately. Saved unfinished activity opens paused after refresh. The app never forces completion when time passes. Emergency Support remains available independently."},
    {"id": "privacy", "title": "History and privacy",
     "terms": ("save", "saving", "history", "delete", "clear", "privacy", "data", "context", "share", "sharing", "remember"),
     "text": "Fictional message saving is opt-in and OFF by default. Saved history remains until you Delete or Clear it. Turning saving OFF keeps existing messages. Context sharing is a separate choice and starts OFF. Sensory answers are not stored."},
    {"id": "safety", "title": "Coursework and safety boundaries",
     "terms": ("safety", "support", "emergency", "911", "therapy", "therapist", "diagnos", "treat", "suicid", "harm", "crisis"),
     "text": "Fifer is a coursework prototype for fictional, non-emergency use. It does not diagnose, provide therapy or monitor anyone. Please contact 911 for emergency support. Emergency Support is static app content; no calls or messages are sent."},
)


def retrieve(question):
    # Topic matching chooses app documentation, never assesses a person's safety.
    words = question.casefold()
    priority = {"safety": 5, "privacy": 4, "controls": 3, "skill": 2, "usage": 1}
    ranked = []
    for doc in CONTENT:
        hits = sum(term in words for term in doc["terms"])
        if hits:
            ranked.append((priority[doc["id"]], hits, doc))
    return [max(ranked, key=lambda item: item[:2])[2]] if ranked else []
