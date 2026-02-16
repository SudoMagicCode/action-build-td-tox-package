from datetime import datetime


def log_event(msg: str, indent: int = 0) -> None:
    output_msg = f"{datetime.now()} | {'--' * indent}> {msg}"
    print(output_msg)
