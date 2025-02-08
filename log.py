from datetime import datetime
from time import time
from termcolor import colored


def log(header: str, color: str, text: str):
    ts = time()
    timestamp = colored(
        datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
        "grey",
        attrs=["bold"],
    )
    header = colored(header, color, attrs=["bold"])
    print(f"{header}\t[{timestamp}] {text}")

def log_info(text: str):
    log("INFO", "cyan", text)

def log_warning(text: str):
    log("WARNING", "yellow", text)

def log_join(guild_name: str, member_name: str):
    log_info(f"In {guild_name}, {member_name} joined!")

def log_assign(guild_name: str, member_name: str, role_id: int):
    log_info(f"In {guild_name}, {member_name} got assigned {role_id}")

def log_remove(guild_name: str, member_name: str, role_id: int):
    log_info(f"In {guild_name}, {member_name} got unassigned {role_id}")

if __name__ == "__main__":
    log_warning("hi Lia")
    log_info("other colors")
