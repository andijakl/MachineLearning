"""1 - Reasoning: thinking is a dial, and there are two separate dials.

  1. the PROMPT dial - asking the model to work step by step (the 2022 trick)
  2. the MODEL dial  - reasoning_effort, a trained thinking mode

Careful: Ollama turns thinking ON by default for models that support it, so a
"fast" answer may quietly have been a thought-through one. Part 1 switches it
off explicitly, which is the only way to see the difference honestly.

Run:  python 01_reasoning.py
"""

import os

from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.environ.get("MODEL", "qwen3.5:4b")

# Several sequential updates, and no formula to recall: the model has to
# actually track the running total.
QUESTION = (
    "A workshop starts the week with 249 screws.\n"
    "Monday: 47 screws are used, then a delivery of 120 screws arrives.\n"
    "Tuesday: three times as many screws are used as on Monday.\n"
    "Wednesday: 18 are used, and 25 unused screws are put back into stock.\n"
    "Thursday: a quarter of the screws in stock are moved to another workshop.\n"
    "How many screws are in stock at the end of Thursday?"
)

ONLY_THE_NUMBER = "Reply with the number only. Do not explain."


def ask(instruction: str, effort: str):
    reply = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"{QUESTION}\n\n{instruction}"}],
        reasoning_effort=effort,
    )
    message = reply.choices[0].message
    thinking = getattr(message, "reasoning", None) or getattr(message, "reasoning_content", None)
    return message.content, thinking


print("=== 1. No thinking at all (reasoning_effort='none') ===")
answer, _ = ask(ONLY_THE_NUMBER, "none")
print(answer)

print("\n=== 2. Thinking asked for in the PROMPT (model dial still off) ===")
answer, _ = ask("Work through it step by step, then give the final number.", "none")
print(answer)

print("\n=== 3. Thinking done by the MODEL (reasoning_effort='high') ===")
answer, thinking = ask(ONLY_THE_NUMBER, "high")
if thinking:
    print(f"-- thought for {len(thinking)} characters before answering --")
    print(thinking[:300].strip() + " ...\n")
print(answer)

# The answer is 141:
#   249 - 47 + 120 = 322      Monday
#   322 - 141      = 181      Tuesday (three times Monday's 47)
#   181 - 18 + 25  = 188      Wednesday
#   188 - 47       = 141      Thursday (a quarter of 188 moved away)
#
# Between 1 and 2, only the instruction changed.
# Between 1 and 3, only a request parameter changed - the instruction was the
# same "number only". That is the difference between prompting a model to
# reason and a model that was trained to.
