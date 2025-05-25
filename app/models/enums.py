from enum import Enum


class Intent(str, Enum):
    INQUIRY = "inquiry"
    OBJECTION = "objection"
    BUYING_SIGNAL = "buying_signal"
    CLARIFICATION = "clarification"
    OTHER = "other"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
