# Author: Matheus Fillipe
# Date: 31/10/2022
# Description: Chinese Language Utils

import string

import requests
from urllib.parse import quote

from cloudbot import hook

API = "https://api.ctext.org/"

commands = {
    "char": "getcharacter?char={chinese_charater}",
    "search": "searchtexts?title={title}",
    "link": "getlink?search={search_term}&urn={urn}",
    "text": "gettext?urn={urn}",
    "textinfo": "gettextinfo?urn={urn}",
    "readlink": "readlink?url={ctext_url}"
}


def pretty_dict(dict):
    return str(dict).replace(', ', '\n').replace(': ', ':\t').replace('{', '').replace('}', '').replace("'", '')


@hook.command("chinese", autohelp=False)
def chinese(text):
    """chinese <command> <args> - Chinese lang tools"""
    # If no arguments are provided list commands
    if not text:
        return "Commands: " + ", ".join(commands.keys())

    # Check if the command is valid
    cmd = text.split()[0]
    if cmd not in ["help", *commands]:
        return "Invalid command. Use .chinese to list commands."

    if cmd == "help":
        if len(text.split()) == 1:
            return "Commands: " + ", ".join(commands.keys())
        else:
            cmd = text.split()[1]
            fmtstr = commands[cmd]
            field_names = [name for text, name, spec,
                           conv in string.Formatter().parse(fmtstr) if name is not None]
            return f"Usage: .chinese {cmd} " + " ".join(field_names)

    fmtstr = commands[cmd]
    field_names = [name for text, name, spec,
                   conv in string.Formatter().parse(fmtstr) if name is not None]

    named_fields = {k: quote(v) for k, v in zip(field_names, text.split()[1:])}
    url = API + fmtstr.format(**named_fields)
    r = requests.get(url)

    if r.status_code == 200:
        _list = pretty_dict(r.json()).split("\n")
        # Join every n elements
        n = 4
        return [";\t".join(_list[i:i + n]) for i in range(0, len(_list), n)][:8]
    else:
        return "Error: " + r.status_code
