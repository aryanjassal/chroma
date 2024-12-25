import random
from pathlib import Path

CHARACTER_SET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQURSTUVWXYZ"

fixtures = Path(".")


def generate_name(n: int = 8, character_set=CHARACTER_SET) -> str:
    return "".join(random.choices(character_set, k=n))
