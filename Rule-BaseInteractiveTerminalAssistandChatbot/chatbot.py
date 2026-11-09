"""
Rule-Based Customer Support Chatbot
===================================

A terminal chatbot that answers frequently asked questions. It doesn't use
any AI service: it understands questions by comparing the user's words with
rules stored in sample_faq.json.

How a message is understood (see identify_intent):
    1. The text is normalized: lowercase, no punctuation, single spaces.
    2. Special commands are checked first: exit words, greetings, "help".
    3. Every FAQ gets a score:
         +2.0  if one of its regex "patterns" matches the message
         +1.0  for each of its "keywords" found in the message
               (small typos are tolerated, e.g. "certifcate")
         +0-1  for how similar the message is to the FAQ's question text
    4. The highest-scoring FAQ wins if it scores at least 1.0.
       If none does, but one is fairly similar, the bot asks
       "Did you mean ...?"; otherwise it gives a polite fallback.

Conversation flow:
    Greeting -> Intent identification -> Resolution (or Fallback) -> ... -> Exit

To teach the bot a new question, add an entry to sample_faq.json. No
Python changes are needed. Only "question" and "answer" are required:
    {
      "question": "Is the internship paid?",
      "answer": "This is an unpaid internship.",
      "topic": "stipend",                     (optional: shown in fallback hints)
      "keywords": ["paid", "stipend"],        (optional: single words to look for)
      "patterns": ["\\\\bpaid\\\\b"]          (optional: regular expressions)
    }

Usage:
    python3 chatbot.py                  # uses sample_faq.json next to this file
    python3 chatbot.py other_faq.json   # uses a different dataset

Modules used (all part of Python's standard library):
    json    - reads the FAQ dataset.
    re      - regular expressions for matching patterns in messages.
    string  - string.punctuation lists the characters we strip out.
    difflib - measures how similar two pieces of text are (typo tolerance).
"""

import difflib
import json
import re
import string
import sys
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Look for the dataset next to this script, not in whatever folder the
# user happens to run it from.
DEFAULT_FAQ_FILE = Path(__file__).resolve().parent / "sample_faq.json"

# Used only if the JSON file has no "greetings" list.
DEFAULT_GREETINGS = ["hello", "hi", "hey", "good morning", "good afternoon"]

EXIT_COMMANDS = {"bye", "goodbye", "exit", "quit"}
YES_ANSWERS = {"yes", "y", "yeah", "yep", "yup", "sure", "correct", "yes please"}
NO_ANSWERS = {"no", "n", "nope", "nah", "not really", "no thanks"}

# Common words that say nothing about the topic. They are ignored when
# keywords are pulled out of an FAQ's question text automatically.
STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in",
    "is", "it", "me", "my", "of", "on", "or", "the", "to", "what", "when",
    "where", "which", "who", "why", "will", "with", "you", "your",
    # generic verbs that appear in all kinds of questions
    "get", "got", "have", "know", "need", "receive", "send", "want",
}

# Scoring rules (see the module docstring).
PATTERN_SCORE = 2.0
KEYWORD_SCORE = 1.0
MATCH_THRESHOLD = 1.0      # minimum score to answer with an FAQ
SUGGEST_THRESHOLD = 0.7    # minimum similarity to ask "Did you mean ...?"
TYPO_CUTOFF = 0.85         # how close a word must be to count as a typo
MIN_TYPO_LENGTH = 4        # don't typo-match short words ("hi" vs "hr")

THANKS_PATTERN = re.compile(r"^(ok(ay)? )?(thanks?|thank you|thx|ty)\b")
HELP_PATTERN = re.compile(
    r"^(help|menu|options|topics|faq|faqs|"
    r"what can (you|i) (do|ask|help( me)? with)|what do you know)$")

# A translation table that turns every punctuation character into a space.
PUNCTUATION_TO_SPACE = str.maketrans(
    {char: " " for char in string.punctuation})

LINE = "=" * 40


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Intent:
    """What the bot decided the user wants.

    name    - "faq", "greeting", "exit", "help", "thanks", "suggest",
              "confirm_yes", "confirm_no", "empty" or "fallback"
    faq     - the matching FAQ entry, for "faq" and "suggest"
    greeted - True if the message started with a greeting ("hi, ...")
    """
    name: str
    faq: dict = None
    greeted: bool = False


@dataclass
class ConversationState:
    """What the bot remembers between messages."""
    active: bool = True             # False once the user says goodbye
    fallback_streak: int = 0        # misunderstood messages in a row
    pending_suggestion: dict = None  # FAQ offered via "Did you mean ...?"


# ---------------------------------------------------------------------------
# 1. Loading the dataset
# ---------------------------------------------------------------------------

def load_faq(path=DEFAULT_FAQ_FILE):
    """Read the FAQ dataset and prepare it for matching.

    Returns (knowledge, warnings). `knowledge` is always usable, even when
    the file is missing or broken: in that case it holds the default
    greetings and no FAQs, and `warnings` explains what went wrong. This
    way a bad file gives the user a clear message instead of a crash.
    """
    warnings = []
    knowledge = {"faqs": [], "greeting_regex": build_greeting_regex(DEFAULT_GREETINGS)}

    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return knowledge, [f"FAQ file not found: {path}"]
    except json.JSONDecodeError as error:
        return knowledge, [
            f"FAQ file {path} is not valid JSON "
            f"(line {error.lineno}, column {error.colno}: {error.msg})"]
    except (OSError, UnicodeDecodeError) as error:
        return knowledge, [f"Could not read FAQ file {path}: {error}"]

    if not isinstance(data, dict):
        return knowledge, [f"FAQ file {path} must contain a JSON object at the top level"]

    greetings = data.get("greetings")
    if isinstance(greetings, list) and all(isinstance(g, str) for g in greetings) and greetings:
        knowledge["greeting_regex"] = build_greeting_regex(greetings)
    elif greetings is not None:
        warnings.append("'greetings' should be a list of strings; using defaults")

    raw_faqs = data.get("faqs", [])
    if not isinstance(raw_faqs, list):
        warnings.append("'faqs' should be a list; no FAQs loaded")
        raw_faqs = []

    for number, entry in enumerate(raw_faqs, start=1):
        faq = prepare_faq(entry, number, warnings)
        if faq is not None:
            knowledge["faqs"].append(faq)

    if not knowledge["faqs"]:
        warnings.append("No usable FAQs were found in the dataset")
    return knowledge, warnings


def prepare_faq(entry, number, warnings):
    """Check one FAQ entry and precompute what matching needs.

    Returns None (and adds a warning) if the entry is unusable, so one bad
    entry doesn't stop the rest of the dataset from loading.
    """
    if not isinstance(entry, dict):
        warnings.append(f"FAQ #{number} is not an object; skipped")
        return None

    question = entry.get("question")
    answer = entry.get("answer")
    if not (isinstance(question, str) and question.strip()
            and isinstance(answer, str) and answer.strip()):
        warnings.append(f"FAQ #{number} needs a non-empty 'question' and 'answer'; skipped")
        return None

    normalized_question = normalize_input(question)

    # Keywords = the important words of the question itself, plus any
    # extra keywords listed in the JSON.
    keywords = {word for word in normalized_question.split()
                if word not in STOPWORDS and len(word) > 2}
    for keyword in entry.get("keywords", []):
        if isinstance(keyword, str) and normalize_input(keyword):
            keywords.add(normalize_input(keyword))

    # Compile each regex once now, instead of on every message.
    patterns = []
    for pattern in entry.get("patterns", []):
        try:
            patterns.append(re.compile(pattern))
        except (re.error, TypeError) as error:
            warnings.append(f"FAQ #{number}: invalid pattern {pattern!r} ({error}); ignored")

    return {
        "question": question.strip(),
        "answer": answer.strip(),
        "topic": entry.get("topic") or question.strip(),
        "normalized_question": normalized_question,
        "keywords": keywords,
        "patterns": patterns,
    }


def build_greeting_regex(greetings):
    """Build one regex that matches a greeting at the start of a message.

    Longer greetings come first so "good morning" is tried before "good".
    The \\b ("word boundary") stops "hi" from matching the start of "hiring".
    Words like "there" are allowed after the greeting ("hi there").
    """
    options = sorted({normalize_input(g) for g in greetings if normalize_input(g)},
                     key=len, reverse=True)
    alternatives = "|".join(re.escape(option) for option in options)
    return re.compile(rf"^(?:{alternatives})(?: (?:there|everyone|team|all|bot))?\b")


# ---------------------------------------------------------------------------
# 2. Normalizing input
# ---------------------------------------------------------------------------

def normalize_input(text):
    """Clean a message so differently typed versions look the same.

    "  What's your HOURS?!  "  ->  "whats your hours"

    Apostrophes are removed (so "what's" becomes "whats", not "what s"),
    every other punctuation mark becomes a space, and runs of spaces are
    collapsed into one.
    """
    text = text.lower().strip()
    text = text.replace("'", "").replace("’", "")  # straight and curly
    text = text.translate(PUNCTUATION_TO_SPACE)
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# 3. Identifying the intent
# ---------------------------------------------------------------------------

def is_exit_command(text):
    """True for "bye", "quit", etc., and short goodbyes like "ok bye".

    Longer sentences such as "how do I exit the program" are *not*
    treated as exits, so the bot doesn't quit by accident.
    """
    if text in EXIT_COMMANDS:
        return True
    words = text.split()
    return len(words) <= 3 and any(word in ("bye", "goodbye") for word in words)


def count_keyword_hits(text, faq):
    """Count how many of an FAQ's keywords appear in the message.

    Close misspellings count too: difflib.get_close_matches compares a
    word against the keyword list and returns those that are at least
    TYPO_CUTOFF similar (1.0 would mean identical).
    """
    words = set(text.split())
    single_word_keywords = [kw for kw in faq["keywords"] if " " not in kw]
    matched = set()

    for word in words:
        if word in faq["keywords"]:
            matched.add(word)
        elif len(word) >= MIN_TYPO_LENGTH:
            close = difflib.get_close_matches(
                word, single_word_keywords, n=1, cutoff=TYPO_CUTOFF)
            if close:
                matched.add(close[0])

    # Keywords with spaces in them (e.g. "student workspace") are
    # matched as whole phrases.
    for keyword in faq["keywords"]:
        if " " in keyword and re.search(rf"\b{re.escape(keyword)}\b", text):
            matched.add(keyword)

    return len(matched)


def score_faq(text, faq):
    """Score how well a message matches one FAQ. Returns (score, similarity)."""
    score = 0.0
    if any(pattern.search(text) for pattern in faq["patterns"]):
        score += PATTERN_SCORE
    score += count_keyword_hits(text, faq) * KEYWORD_SCORE

    # SequenceMatcher.ratio() gives 0.0 (nothing alike) to 1.0 (identical).
    similarity = difflib.SequenceMatcher(None, text, faq["normalized_question"]).ratio()
    return score + similarity, similarity


def find_best_faq(text, faqs):
    """Return (best FAQ, its score, its similarity), or (None, 0, 0)."""
    best, best_score, best_similarity = None, 0.0, 0.0
    for faq in faqs:
        score, similarity = score_faq(text, faq)
        if score > best_score:
            best, best_score, best_similarity = faq, score, similarity
    return best, best_score, best_similarity


def identify_intent(text, knowledge, state):
    """Decide what a normalized message is asking for.

    The checks run in order, so for example "bye" always exits even if it
    looks a little like some FAQ.
    """
    if not text:
        return Intent("empty")

    # Answering a "Did you mean ...?" question from the previous turn.
    if state.pending_suggestion:
        if text in YES_ANSWERS:
            return Intent("confirm_yes", faq=state.pending_suggestion)
        if text in NO_ANSWERS:
            return Intent("confirm_no")

    if is_exit_command(text):
        return Intent("exit")

    # Strip a leading greeting so "hi, when are you open?" still gets
    # its question answered.
    greeted = False
    match = knowledge["greeting_regex"].match(text)
    if match:
        greeted = True
        text = text[match.end():].strip()
        if not text:
            return Intent("greeting")

    if HELP_PATTERN.match(text):
        return Intent("help", greeted=greeted)

    faq, score, similarity = find_best_faq(text, knowledge["faqs"])
    if faq and score >= MATCH_THRESHOLD:
        return Intent("faq", faq=faq, greeted=greeted)

    if THANKS_PATTERN.match(text):
        return Intent("thanks")

    if faq and similarity >= SUGGEST_THRESHOLD:
        return Intent("suggest", faq=faq, greeted=greeted)

    return Intent("fallback", greeted=greeted)


# ---------------------------------------------------------------------------
# 4. Building the response
# ---------------------------------------------------------------------------

def list_topics(faqs):
    """Join FAQ topics into readable text: "a, b, or c"."""
    topics = [faq["topic"] for faq in faqs]
    if len(topics) <= 2:
        return " or ".join(topics)
    return ", ".join(topics[:-1]) + ", or " + topics[-1]


def list_questions(faqs):
    """All FAQ questions as an indented bullet list."""
    return "\n".join(f"  - {faq['question']}" for faq in faqs)


def fallback_response(knowledge, state):
    """A polite "I don't understand" that gets more helpful if repeated."""
    faqs = knowledge["faqs"]
    if not faqs:
        return ("I'm sorry, my FAQ information isn't available right now, "
                "so I can only respond to greetings. Type 'bye' to exit.")
    if state.fallback_streak == 0:
        return ("I'm sorry, I don't quite understand that question. Could you "
                f"rephrase it or ask about our {list_topics(faqs)}?")
    return ("I still couldn't find an answer to that. Here are the questions "
            f"I can help with:\n{list_questions(faqs)}\n"
            "Type 'bye' when you're done.")


def get_response(intent, knowledge, state):
    """Turn an Intent into the bot's reply text."""
    faqs = knowledge["faqs"]
    hello = "Hello! " if intent.greeted else ""

    if intent.name == "empty":
        return "Please type a question, or type 'bye' to exit."
    if intent.name == "greeting":
        return "Hello! How may I help you?"
    if intent.name == "exit":
        return "Thank you for contacting us. Have a great day!"
    if intent.name == "thanks":
        return "You're welcome! Is there anything else I can help you with?"
    if intent.name in ("faq", "confirm_yes"):
        return hello + intent.faq["answer"]
    if intent.name == "suggest":
        return (f"{hello}I'm not sure I understood. Did you mean: "
                f"\"{intent.faq['question']}\" (yes/no)")
    if intent.name == "confirm_no":
        if not faqs:
            return "No problem. Could you rephrase your question?"
        return ("No problem. Could you rephrase your question? You can ask "
                f"about our {list_topics(faqs)}.")
    if intent.name == "help":
        if not faqs:
            return fallback_response(knowledge, state)
        return f"{hello}I can help with these questions:\n{list_questions(faqs)}"
    return hello + fallback_response(knowledge, state)


def update_state(state, intent):
    """Remember what matters for the next turn."""
    if intent.name == "exit":
        state.active = False

    # A "Did you mean" offer only lasts for the very next message.
    state.pending_suggestion = intent.faq if intent.name == "suggest" else None

    if intent.name == "fallback":
        state.fallback_streak += 1
    elif intent.name != "empty":
        state.fallback_streak = 0


# ---------------------------------------------------------------------------
# 5. Conversation loop
# ---------------------------------------------------------------------------

def bot_say(message):
    """Print a reply, indenting extra lines so they line up after "Bot: "."""
    for number, line in enumerate(message.splitlines()):
        print(("Bot: " if number == 0 else "     ") + line)


def chatbot(knowledge):
    """Run the conversation until the user exits."""
    print(LINE)
    print("       CUSTOMER SUPPORT CHATBOT")
    print(LINE)
    print()
    bot_say("Hello! Welcome to Customer Support.")
    bot_say("How can I assist you today?")

    state = ConversationState()
    while state.active:
        try:
            raw = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            # Ctrl+D / Ctrl+C: leave politely instead of showing a traceback.
            print()
            raw = "exit"

        try:
            intent = identify_intent(normalize_input(raw), knowledge, state)
            reply = get_response(intent, knowledge, state)
            update_state(state, intent)
        except Exception as error:  # last-resort guard: never crash mid-chat
            intent = Intent("fallback")
            reply = f"Sorry, something went wrong handling that message ({error})."
        bot_say(reply)

    print("\nChatbot terminated.")


def main():
    faq_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FAQ_FILE
    knowledge, warnings = load_faq(faq_path)
    for warning in warnings:
        print(f"Warning: {warning}")
    if warnings:
        print()
    chatbot(knowledge)


if __name__ == "__main__":
    main()
