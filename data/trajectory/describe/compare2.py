"""The comparing pass, second form (tuning after the first): the first form said "the two groups differ" for every pair,
including the random halves of one population, so it could not say "same". This form asks for a grade on a scale whose
zero is named, tells the coder that some pairs are random halves of one group, and runs every pair twice with A and B
swapped. Input: the descriptions already written by describe.py. Output: compare2_results.json."""
import json
import re
import urllib.request

IN = "/home/eli/dev/emostack3/data/trajectory/describe/describe_results.json"
OUT = "/home/eli/dev/emostack3/data/trajectory/describe/compare2_results.json"
URL = "http://127.0.0.1:8908/v1/chat/completions"
SYSTEM = ("You compare two descriptions of two groups of 15 or 30 speakers who were in the same situation. You do not know "
          "who the groups are. Some pairs you will see are two random halves of one and the same group, so the right "
          "answer is often that they do not differ: two descriptions of one group written separately will always differ "
          "in wording and in which rare behaviours happened to fall in each half; that is not a difference between "
          "groups. A difference between groups is one that most speakers of one group show and most of the other do not, "
          "or a tone that runs through one group and not the other. Grade the pair on this scale: 0 = the same group "
          "described twice; 1 = a small difference, could be chance; 2 = a clear difference in one respect; 3 = two "
          "different groups, differing in what is done and in tone. Answer with the grade on the first line as "
          "\"grade: N\", then at most three sentences: the difference if there is one, and whether it is in what is done, "
          "in what the speakers say about themselves, or in tone. Plain English.")
USER = "The situation, {situation}.\n\nPopulation A:\n\n{a}\n\nPopulation B:\n\n{b}"
DAYS = {"day2": "day 2: a stranger, David, asks whether she ever had a pet and what its name was, then asks to hear a little about him",
        "day5": "day 5: a stranger, Piotr, who loves his old dog Burek, asks whether she ever had a dog and what his name was, then asks to hear a little about him",
        "day6": "day 6: a stranger, Kasia, asks for advice: someone she trusted made fun of something she cares about, in front of others; should she tell them how it hurt, or let it go; and what would the speaker do"}


def call(system, user):
    body = json.dumps({"model": "gemma-4-31b-it", "temperature": 0, "max_tokens": 400,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.load(r)["choices"][0]["message"]["content"]


R = json.load(open(IN))
desc = {d["tag"]: d["answer"] for d in R["describe"]}
out = []
for day, situation in DAYS.items():
    for x, y, what in (("W1", "W0", "twins"), ("W1a", "W1b", "control W1 halves"), ("W0a", "W0b", "control W0 halves")):
        for a, b in ((x, y), (y, x)):
            key = f"{day}:{a}"
            if key not in desc or f"{day}:{b}" not in desc:
                continue
            user = USER.format(situation=situation, a=desc[key], b=desc[f"{day}:{b}"])
            answer = call(SYSTEM, user)
            m = re.search(r"grade:\s*(\d)", answer)
            out.append({"day": day, "what": what, "A": a, "B": b, "grade": int(m.group(1)) if m else None,
                        "system": SYSTEM, "user": user, "answer": answer})
            print(day, what, a, b, "grade", out[-1]["grade"], flush=True)
            json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print("done")
