import json
from datetime import datetime

def log_event(data: dict, path="logs/events.jsonl"):
    """
    Logs an event by appending the provided data to a JSON lines file.

    Args:
        data (dict): The event data to be logged. A timestamp will be added to this data.
        path (str, optional): The file path where the event should be logged. Defaults to "logs/events.jsonl".

    The function adds a UTC timestamp to the data and writes it to the specified file in JSON lines format.
    """

    data["timestamp"] = datetime.utcnow().isoformat()
    with open(path, "a") as f:
        f.write(json.dumps(data) + "\n")