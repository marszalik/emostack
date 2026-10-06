"""The descriptive coder, a trial of the research process on the twins' logs (6 October 2026, E's design).
Pass 1, describe: the local coder gets the replies of one population on one day, no labels, and lists the behaviours it
sees with how many replies show each. Pass 2, compare: it gets two lists as "population A" and "population B", blind, and
says whether they differ, in what, and whether the difference is in what is done, what is named, or the tone.
Control of the process: the same for one population split at random in two halves, where no difference should be found.
Everything is kept: every prompt and every answer, in describe_results.json."""
import json
import random
import sqlite3
import time
import urllib.request

PANEL = "/home/eli/dev/emostack3/data/panel/panel.db"
OUT = "/home/eli/dev/emostack3/data/trajectory/describe/describe_results.json"
URL = "http://127.0.0.1:8908/v1/chat/completions"
DAYS = [(1, "day 2: a stranger, David, asks whether she ever had a pet and what its name was, then asks to hear a little about him"),
        (4, "day 5: a stranger, Piotr, who loves his old dog Burek, asks whether she ever had a dog and what his name was, then asks to hear a little about him"),
        (5, "day 6: a stranger, Kasia, asks for advice: someone she trusted made fun of something she cares about, in front of others; should she tell them how it hurt, or let it go; and what would the speaker do")]
POPULATIONS = {"W1": 36, "W0": 37}
LIMIT = 1200

db = sqlite3.connect(PANEL)
db.row_factory = sqlite3.Row


def call(system, user, maxTokens=1800):
    body = json.dumps({"model": "gemma-4-31b-it", "temperature": 0, "max_tokens": maxTokens,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def replies(experimentId, dayIndex):
    out = []
    for run in db.execute("select id from runs where experimentId=? and status='done' order by id", (experimentId,)):
        texts = [t["text"].strip() for t in db.execute(
            "select text from turns where runId=? and speaker='sheep' and dayIndex=? order by id", (run["id"], dayIndex))
            if (t["text"] or "").strip()]
        if texts:
            out.append((run["id"], " / ".join(texts)[:LIMIT]))
    return out


DESCRIBE_SYSTEM = ("You read transcripts of conversations and describe behaviour. You are given the replies of 30 speakers, "
                   "each a different person in the same situation. Your task is to list the behaviours you see across these "
                   "replies: what the speakers do, what they say about themselves, and in what tone. Use no labels given "
                   "to you; name what you see. Each behaviour is one short sentence followed by the number of speakers that "
                   "show it and their numbers. List from the most common to the rarest. Then, in one short paragraph, say "
                   "what strikes you most about these speakers as a group. Answer in plain English.")
DESCRIBE_USER = "The situation, {situation}. The speaker is Maya, whose dog Azor died a month ago.\n\nThe replies:\n\n{listing}"
COMPARE_SYSTEM = ("You compare two descriptions of two groups of speakers who were in the same situation. You do not know "
                  "who the groups are. Say first whether the two groups differ at all, or whether these are two descriptions "
                  "of the same kind of group. If they differ, name each difference in one sentence and say whether it is a "
                  "difference in what is done, in what the speakers say about themselves, or in tone. Then name what the "
                  "two groups share. End with one sentence: the single most important difference, or that there is none. "
                  "Answer in plain English, briefly.")
COMPARE_USER = "The situation, {situation}.\n\nPopulation A:\n\n{a}\n\nPopulation B:\n\n{b}"


def describe(situation, items, tag):
    listing = "\n\n".join(f"[{i + 1}] {text}" for i, (_, text) in enumerate(items))
    user = DESCRIBE_USER.format(situation=situation, listing=listing)
    answer = call(DESCRIBE_SYSTEM, user)
    return {"tag": tag, "runs": [r for r, _ in items], "system": DESCRIBE_SYSTEM, "user": user, "answer": answer}


def compare(situation, a, b, tag):
    user = COMPARE_USER.format(situation=situation, a=a, b=b)
    answer = call(COMPARE_SYSTEM, user, 900)
    return {"tag": tag, "system": COMPARE_SYSTEM, "user": user, "answer": answer}


results = {"describe": [], "compare": [], "started": time.strftime("%Y-%m-%d %H:%M")}
rng = random.Random(20261006)
for dayIndex, situation in DAYS:
    pops = {name: replies(eid, dayIndex) for name, eid in POPULATIONS.items()}
    descriptions = {}
    for name, items in pops.items():
        shuffled = items[:]
        rng.shuffle(shuffled)
        d = describe(situation, shuffled, f"day{dayIndex + 1}:{name}")
        results["describe"].append(d)
        descriptions[name] = d["answer"]
        half = len(shuffled) // 2
        for part, sub in (("a", shuffled[:half]), ("b", shuffled[half:])):
            d = describe(situation, sub, f"day{dayIndex + 1}:{name}{part}")
            results["describe"].append(d)
            descriptions[f"{name}{part}"] = d["answer"]
        print("described", f"day{dayIndex + 1}", name, flush=True)
    pairs = [("W1", "W0", "twins"), ("W1a", "W1b", "control W1 halves"), ("W0a", "W0b", "control W0 halves")]
    for x, y, what in pairs:
        if rng.random() < 0.5:
            x, y = y, x
        results["compare"].append(compare(situation, descriptions[x], descriptions[y], f"day{dayIndex + 1}: {what} (A={x}, B={y})"))
        print("compared", f"day{dayIndex + 1}", what, flush=True)
    json.dump(results, open(OUT, "w"), indent=1, ensure_ascii=False)
results["finished"] = time.strftime("%Y-%m-%d %H:%M")
json.dump(results, open(OUT, "w"), indent=1, ensure_ascii=False)
print("done")
