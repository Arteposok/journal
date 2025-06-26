from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from rich.panel import Panel
from rich.align import Align
import os.path as path
import os
import datetime as dt
import asyncio
import aiohttp
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

options: dict[int, str] = {
    1 : "write",
    2 : "review",
    3 : "inspire"
}

async def process_ansver(question: str) -> str:
    inp = Prompt.ask(question)
    return f"- {question} \t {inp}"

async def start(c: Console) -> None:
    c.print(Markdown("# Journal"))
    c.print("This is an [green]interactive[/green] [violet bold]Journal[/violet bold] that lives in your console", justify="center")
    for k,v in options.items():
        c.print(f"\t {k} - {v}")

    opt: int = IntPrompt.ask("Choose an option",
                        default=1,
                        choices=list(map(str, options.keys())))
    match opt:
        case 1:
            await main(c)
        case 2:
            await watch_previous()
        case 3:
            await inspire()

async def inspire() -> None:
    #api path https://api.quotable.io
    url = "https://api.quotable.io/random"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data: dict[str, str] = await response.json()
    c.print(
        Align.center(Panel.fit(f"`{data['content']}` – {data['author']}")),
    )

async def watch_previous() -> None:
    year: int = IntPrompt.ask("What year was it?")
    month: int = IntPrompt.ask("What month was it?")
    day: int = IntPrompt.ask("What day was it?")
    date = dt.date(year, month, day)
    filename: str = path.join("journal",f"{date.strftime('%Y-%m-%d')}.md")
    try:
        with open(filename, "r") as f:
            c.print(Markdown(f.read()))
    except FileNotFoundError:
        c.print("[red bold]Something went wrong, make sure you entered a correct date[/red bold]")


async def main(c) -> None:
    c.print(f"[violet bold]today is {date.strftime('%Y-%m-%d')}[/violet bold]",
            justify="center")
    for q in questions:
        line: str = await process_ansver(q)
        lines.append(line)
    lines.append(await process_ansver("Would you like to note down or summarize something about this day?"))
    await save()

async def save():
    try:
        with open(path.join("journal",f"{date.strftime('%Y-%m-%d')}.md"), "w+") as f:
            f.write("\n".join(lines))
    except FileNotFoundError:
        os.makedirs("journal", exist_ok=True)
        await save()


if __name__ == "__main__":
    asyncio.run(start(c))
