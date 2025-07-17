from rich.text import Text


def strip_markdown(text: str) -> str:
    return Text.from_markup(text).plain
