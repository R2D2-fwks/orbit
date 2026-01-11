
from pathlib import Path
from src.actor_system import start_actor_system
from src.services.file import FileService
import json
import click
from colorama import Fore
from art import text2art


if __name__ == "__main__":
    Art = text2art("ORBIT !", font='big')
    print(Art)
    artl1 = text2art("Welcome...", font='small',)
    artl2 = text2art("To ORBIT", font='small')
    print(f"{Fore.BLUE}{artl1}")
    print(f"{Fore.BLUE}{artl2}")
    click.pause()
    click.clear()
    artl4 = text2art("Question?", font='bubble')
    print(f"{Fore.RED}{artl4}")
    query = click.prompt('What is your Query?', type=str, default='How can I use ORBIT framework ?', show_default=True, err=False, prompt_suffix='\n>> ')
    print(f"{Fore.GREEN}\nGreat! You asked: {query}\n")
    print(f"{Fore.YELLOW}Processing your query, please wait...\n")
    response = start_actor_system(query)
    print(f"{Fore.BLUE}Response from ORBIT:\n{response}\n")