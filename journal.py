# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "rich",
#   "click",
#   "httpx",
# ]
# ///
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.panel import Panel
from rich.align import Align
import os.path as path
import os
import datetime as dt
import sys
import click
import httpx

c: Console = Console()

questions: list[str] = [
    "Rate your day 1 to 10?",
    "What did you learn today?",
    "How are you willing to use it?",
    "What emotion did you feel the most today?",
]
date = dt.datetime.today().date()
lines: list[str] = [
    f"# {date.strftime('%Y-%m-%d')}",
    "",
]


@click.group()
def cli():
    pass


def process_ansver(question: str) -> str:
    inp = Prompt.ask(question)
    return f"- {question} \t {inp}"


def try_to_review(c: Console):
    past = date - dt.timedelta(weeks=1)
    filename: str = path.join("journal", f"{past.strftime('%Y-%m-%d')}.md")
    try:
        with open(filename, "r") as f:
            c.print(Align.center(Panel.fit(Markdown(f.read()))))
    except FileNotFoundError:
        c.print("Could not find an entry from a week ago :(", style="red")


@cli.command()
def inspire() -> None:
    url = "http://api.quotable.io/random"
    with c.status("Collecting data"):
        data: dict[str, str] = httpx.get(url).json()
    c.print(
        Align.center(Panel.fit(f"\"{data['content']}\" – {data['author']}")),
    )


@cli.command()
@click.argument("dates")
def review(dates: str) -> None:
    date = dt.datetime.strptime(dates, "%Y-%m-%d").date()
    filename: str = path.join("journal", f"{date.strftime('%Y-%m-%d')}.md")
    try:
        with open(filename, "r") as f:
            c.print(Markdown(f.read()))
    except FileNotFoundError:
        c.print(
            "Something went wrong, make sure you entered a correct date",
            style="red bold",
        )


@cli.command()
def journal() -> None:
    try_to_review(c)
    c.print(
        f"today is {date.strftime('%Y-%m-%d')}",
        justify="center",
        style="magenta bold",
    )
    for q in questions:
        line: str = process_ansver(q)
        lines.append(line)
    lines.append(
        process_ansver(
            "Would you like to note down or summarize something about this day?"
        )
    )
    save()


def save():
    try:
        with open(path.join("journal", f"{date.strftime('%Y-%m-%d')}.md"), "w+") as f:
            _ = f.write("\n".join(lines))
    except FileNotFoundError:
        os.makedirs("journal", exist_ok=True)
        save()


if __name__ == "__main__":
    try:
        c.print(
            Align.center(
                Panel.fit(
                    """
This is a handy script for keeping track of yourself
                    """,
                    title="Welcome",
                    title_align="left",
                    padding=(0, 2),
                )
            )
        )
        cli()
    except (KeyboardInterrupt, EOFError):
        c.print("Terminated by user.", style="green")
        sys.exit(0)
    except Exception:
        c.print()
        c.log("Exited with an error")
        show_trace = Prompt.ask("Show error trace?", default="n", choices=["Y", "n"])
        if show_trace == "Y":
            c.print_exception()
        else:
            sys.exit(1)
