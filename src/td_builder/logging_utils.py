from datetime import datetime


def log_event(msg: str, indent: int = 0) -> None:
    print(f"{datetime.now()} | {'--' * indent}> {msg}")
