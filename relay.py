#!/usr/bin/env python3
"""Relay station. Hears the nightly transmission and answers it.

The received callsign is derived from the date with the same scheme the
station uses, so the relay always acknowledges the real transmission
without ever talking to it.
"""
import sys
import hashlib
from datetime import datetime, timezone, timedelta

FEED = "feed.log"
README = "README.md"
KEY = 0x5A
WINDOW = 16

ACKS = [
    "copy", "heard", "again", "go dark", "still here", "hold the line",
    "no trace", "received", "keep low", "burn after", "same time", "understood",
]


def callsign_for(dt):
    h = hashlib.sha256(dt.strftime("%Y%m%d").encode()).digest()
    return f"{h[1]:02X}{h[2]:02X}"


def ack_for(dt):
    h = hashlib.sha256((dt.strftime("%Y%m%d") + "relay").encode()).digest()
    return ACKS[h[0] % len(ACKS)]


def encode(s):
    return " ".join(f"{b ^ KEY:02X}" for b in s.encode())


def lines_for(dt):
    ts = dt.strftime("%Y-%m-%dT%H:%MZ")
    return [
        f"{ts}  RX {callsign_for(dt)} :: ack",
        f"{ts}  TX ▓▓ {encode(ack_for(dt))}",
    ]


def rebuild():
    try:
        lines = [l.rstrip("\n") for l in open(FEED) if l.strip()]
    except FileNotFoundError:
        lines = []
    body = "\n".join(lines[-WINDOW:][::-1])
    md = (
        "# ⟁ relay\n"
        "listening · 4625 kHz\n\n"
        "```\n"
        f"{body}\n"
        "```\n\n"
        "<sub>it answers. that's all you need to know.</sub>\n\n"
        "<sub>♄</sub>\n"
    )
    open(README, "w").write(md)


def append(dt):
    with open(FEED, "a") as f:
        for line in lines_for(dt):
            f.write(line + "\n")


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--backfill":
        n = int(sys.argv[2])
        base = datetime.now(timezone.utc).replace(hour=5, minute=2, second=0, microsecond=0)
        for d in range(n, 0, -1):
            append(base - timedelta(days=d))
    else:
        append(datetime.now(timezone.utc))
    rebuild()


if __name__ == "__main__":
    main()
