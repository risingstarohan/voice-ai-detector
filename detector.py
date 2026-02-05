# detector.py

import random

def detect_ai_voice(audio_path: str):
    """
    Dummy AI voice detection logic
    """
    ai_probability = random.uniform(0.6, 0.95)

    if ai_probability > 0.75:
        return "AI generated", round(ai_probability, 2)
    else:
        return "Human voice", round(1 - ai_probability, 2)
