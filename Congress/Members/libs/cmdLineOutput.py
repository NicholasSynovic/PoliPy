import colorama
from colorama import Fore

colorama.init(autoreset=True)

Fore.GREEN


def positiveMessage(message: str = "Hello World"):
    return "✅\t" + Fore.GREEN + message


def neutralMessage(message: str = "Hello World"):
    return Fore.WHITE + "...\t" + message


def errorMessage(message: str = "Hello World"):
    return "🔥\t" + Fore.RED + message
