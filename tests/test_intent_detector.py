from app.services.intent_detector import IntentDetector
from app.voice.intent_detector_voice import VoiceIntentDetector


def test_text_intent_detector_billing() -> None:
    result = IntentDetector().detect("I was charged twice.")

    assert result["intent"] == "refund_request"


def test_voice_intent_detector_removes_disfluencies() -> None:
    result = VoiceIntentDetector().detect("Um, I like need a person.")

    assert result["intent"] == "human_escalation"
    assert result["normalized_text"] == "i need a person."

