import re
from src.config import Config

config = Config()
config.load_config()

def is_valid(text: str, href: str) -> bool:
    if href in {"/", "#"}:
        return False

    if re.fullmatch(r"[A-Z]", text):
        return False

    if re.fullmatch(r"\d+", text):
        return False

    if re.fullmatch(r"Tamil \d{4} Movies", text):
        return False
    
    if re.fullmatch(r"Tamil \d{4} Dubbed Movies", text):
        return False
    
    if text in config.junks:
        return False

    return True