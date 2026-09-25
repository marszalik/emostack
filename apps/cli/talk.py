"""Talk to a being in the terminal.

    python3 apps/cli/talk.py --config config.json --being Maya --person Eliza

Commands: /leave ends the conversation, /wait <hours> lets time pass, /tick runs the clock once,
/quit exits."""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from emostack.core.config import config
from emostack.runtime.engine import engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--being", default="Maya")
    parser.add_argument("--person", default="Guest")
    options = parser.parse_args()
    mind = engine(config.fromFile(options.config))
    conversation, outcome = mind.open(options.being, options.person)
    show(options.being, outcome)
    while True:
        try:
            line = input(f"{options.person}> ").strip()
        except EOFError:
            line = "/quit"
        if not line:
            continue
        if line in ("/leave", "/quit"):
            if not conversation.closed:
                show(options.being, mind.leave(conversation))
            if line == "/quit":
                break
            conversation, outcome = mind.open(options.being, options.person)
            show(options.being, outcome)
        elif line.startswith("/wait"):
            hours = float(line.split()[1]) if len(line.split()) > 1 else 1.0
            mind.time.advance(hours * 3600)
            print(f"({hours:g} h pass)")
        elif line == "/tick":
            mind.tick()
        else:
            show(options.being, mind.hear(conversation, line))
    mind.close()


def show(name, outcome):
    for construct in outcome.thoughts:
        print(f"  ({name} — {construct.statement()})")
    if outcome.failed:
        print(f"  ({name} could not answer)")
    elif outcome.words:
        print(f"{name}: {outcome.words}")


if __name__ == "__main__":
    main()
