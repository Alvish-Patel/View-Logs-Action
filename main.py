import sys
import logging
import importlib
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

BASE_DIR = Path(__file__).resolve().parent
PLUGINS_PATH = BASE_DIR / "plugins"
LOGS_DIR = BASE_DIR / "logs"

if str(PLUGINS_PATH) not in sys.path:
    sys.path.insert(0, str(PLUGINS_PATH))

LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / f"jarvis_{datetime.now().strftime('%Y-%m-%d')}.log"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logging.info("SRE-Jarvis started")

console = Console()


def get_main_modules():
    return sorted([
        f.name for f in PLUGINS_PATH.iterdir()
        if f.is_dir() and not f.name.startswith("__") and not f.name.startswith(".")
    ])


def get_module_files(module_name):
    module_path = PLUGINS_PATH / module_name
    return sorted([
        f.stem for f in module_path.glob("*.py")
        if f.is_file() and f.name != "__init__.py"
    ])


def show_main_menu(modules):
    table = Table(title="🤖 SRE-Jarvis Main Menu", header_style="bold magenta")
    table.add_column("Option", justify="center")
    table.add_column("Module")

    for idx, name in enumerate(modules, start=1):
        table.add_row(str(idx), name.capitalize())
    table.add_row("0", "[red]Exit[/red]")

    console.clear()
    console.print(table)


def show_sub_menu(module_name, files):
    table = Table(title=f"🔧 {module_name.capitalize()} Submenu", header_style="bold cyan")
    table.add_column("Option", justify="center")
    table.add_column("Action")

    for idx, name in enumerate(files, start=1):
        table.add_row(str(idx), name)
    table.add_row("0", "[red]Back[/red]")

    console.print(table)


def load_and_run(module, file):
    try:
        logging.info(f"Executing {module} > {file}")
        imported = importlib.import_module(f"{module}.{file}")
        if hasattr(imported, "run"):
            imported.run()
        else:
            logging.warning(f"No 'run()' function in {module}.{file}")
            console.print(f"[yellow]⚠️ The file '{file}.py' does not contain a run() function.[/yellow]")
    except Exception as e:
        logging.error(f"Error in {module}.{file}: {e}")
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
    input("\nPress Enter to return to the submenu...")


def main():
    while True:
        modules = get_main_modules()
        show_main_menu(modules)
        choice = Prompt.ask("\nSelect a main module")

        if choice == "0":
            logging.info("User exited the program.")
            console.print("\n[green]👋 Exiting SRE-Jarvis. Have a nice day![/green]")
            break

        if choice.isdigit() and 1 <= int(choice) <= len(modules):
            module_name = modules[int(choice) - 1]
            logging.info(f"User selected main module: {module_name}")

            sub_files = get_module_files(module_name)
            if not sub_files:
                console.print("\n[bold yellow]⚠️ This feature is not yet implemented.[/bold yellow]")
                input("Press Enter to return to the main menu...")
                continue

            while True:
                console.clear()
                show_sub_menu(module_name, sub_files)
                sub_choice = Prompt.ask("\nSelect a sub-option")

                if sub_choice == "0":
                    break

                if sub_choice.isdigit() and 1 <= int(sub_choice) <= len(sub_files):
                    selected_file = sub_files[int(sub_choice) - 1]
                    logging.info(f"User selected sub-option: {selected_file}")
                    load_and_run(module_name, selected_file)
                else:
                    console.print("[red]Invalid sub-option. Try again.[/red]")
        else:
            console.print("[red]Invalid main option. Try again.[/red]")


if __name__ == "__main__":
    main()
