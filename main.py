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
    "How would you describe your day?",
    "How did you feel today?",
    "How would you rate your day, 1 to 10?",
    "What did you learn today?",
    "Who made your day?",
    "Is it better than yesterday?",
    "What did you think about today that you remembered?",
    "What do you think you're missing right now? (like an emotion)",
    "What would you say to your future self when you will look through the journal?"
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
    filename: str = path.join("journal",f"{past.strftime('%Y-%m-%d')}.md")
    try:
        with open(filename, "r") as f:
            c.print(Markdown(f.read()))
    except FileNotFoundError:
        c.print("Could not find an entry from a week ago :(")

@cli.command()
def inspire() -> None:
    url = "http://api.quotable.io/random"
    with c.status("Collecting data"):
        data = httpx.get(url).json()
    c.print(
        Align.center(Panel.fit(f"`{data['content']}` – {data['author']}")),
    )

@cli.command()
@click.argument("dates")
def review(dates: str) -> None:
    date = dt.datetime.strptime(dates, "%Y-%m-%d").date()
    filename: str = path.join("journal",f"{date.strftime('%Y-%m-%d')}.md")
    try:
        with open(filename, "r") as f:
            c.print(Markdown(f.read()))
    except FileNotFoundError:
        c.print("[red bold]Something went wrong, make sure you entered a correct date[/red bold]")

@cli.command()
def journal() -> None:
    try_to_review(c)
    c.print(f"[violet bold]today is {date.strftime('%Y-%m-%d')}[/violet bold]",
            justify="center")
    for q in questions:
        line: str = process_ansver(q)
        lines.append(line)
    lines.append(process_ansver("Would you like to note down or summarize something about this day?"))
    save()

def save():
    try:
        with open(path.join("journal",f"{date.strftime('%Y-%m-%d')}.md"), "w+") as f:
            f.write("\n".join(lines))
    except FileNotFoundError:
        os.makedirs("journal", exist_ok=True)
        save()


if __name__ == "__main__":
    try:
        cli()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    except Exception:
        c.print()
        c.log("Exited with an error")
        show_trace = Prompt.ask("Show error trace?",
                                default="n",
                                choices=["Y", "n"])
        if show_trace == "Y":
            c.print_exception()
        else:
            sys.exit(1)
