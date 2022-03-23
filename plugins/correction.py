import re

from cloudbot import hook
from cloudbot.util.formatting import ireplace

correction_re = re.compile(r"^[sS]/(?:(.*?)(?<!\\)/(.*?)(?:(?<!\\)/([igx]{,4}))?)\s*$")
unescape_re = re.compile(r"\\(.)")

REFLAGS = {
    "i": re.IGNORECASE,
    "g": re.MULTILINE,
    "x": re.VERBOSE,
}


@hook.regex(correction_re)
def correction(match, conn, nick, chan, message):
    # groups = [unescape_re.sub(r"\1", group or "") for group in match.groups()]
    groups = match.groups()
    find = groups[0]
    replace = groups[1] if groups[1] else ""
    flags = str(groups[2]) if groups[2] else ""
    re_flags = []
    for flag in flags:
        if flag not in "igx":
            message("Invalid regex flag: {}".format(flag))
            return
        re_flags.append(REFLAGS[flag])

    max_i = 1000
    i = 0

    for name, timestamp, msg in reversed(conn.history[chan]):
        if i >= max_i:
            break
        i += 1
        if correction_re.match(msg):
            # don't correct corrections, it gets really confusing
            continue

        if msg.startswith("\x01ACTION"):
            mod_msg = msg[7:].strip(" \x01")
            fmt = "* {} {}"
        else:
            mod_msg = msg
            fmt = "<{}> {}"

        new = re.sub(find, "\x02" + replace + "\x02", mod_msg,
                     count=re.MULTILINE not in re_flags, flags=sum(re_flags))
        if new != mod_msg:
            find_esc = re.escape(find)
            replace_esc = re.escape(new)
            mod_msg = unescape_re.sub(r"\1", new)
            message("Correction, {}".format(fmt.format(name, mod_msg)))
            if nick.lower() == name.lower():
                msg = ireplace(re.escape(msg), find_esc, replace_esc)
                msg = unescape_re.sub(r"\1", msg)
                conn.history[chan].append((name, timestamp, msg))

            break

    return None
