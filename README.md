# Python Internship Projects

![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/Core%20Dependencies-Standard%20Library%20Only-success)

This repository contains four command-line applications developed during a structured four-week Python internship program: a word-guessing game, a stock portfolio tracker, a file organization utility, and a rule-based customer support chatbot.

Each project addresses a distinct practical problem and demonstrates core software development skills, including input validation, data processing, safe file handling, text matching, and exception handling. All four core applications are built exclusively with the Python standard library. Third-party packages are used only for clearly identified optional features.

---

## Table of Contents

1. [Internship Program Overview](#internship-program-overview)
2. [Project Summary](#project-summary)
3. [Technologies and Python Modules](#technologies-and-python-modules)
4. [Repository Structure](#repository-structure)
5. [Installation](#installation)
6. [Projects](#projects)
   - [Task 1: Hangman Word Guessing Game](#task-1-hangman-word-guessing-game)
   - [Task 2: Stock Portfolio Performance Tracker](#task-2-stock-portfolio-performance-tracker)
   - [Task 3: Automated File Organizer and Cleanup Utility](#task-3-automated-file-organizer-and-cleanup-utility)
   - [Task 4: Rule-Based Interactive Terminal Assistant](#task-4-rule-based-interactive-terminal-assistant)
7. [Skills and Programming Concepts](#skills-and-programming-concepts)
8. [Testing and Implementation](#testing-and-implementation)
9. [Learning Objectives](#learning-objectives)
10. [Author](#author)
11. [Conclusion](#conclusion)

---

## Internship Program Overview

The internship was a four-week, project-based program in which each task required the delivery of a complete, functional application built to a written specification. The program emphasized the following professional practices:

- Writing clean, modular, and maintainable Python code
- Validating user input and handling errors without interrupting program execution
- Working with files, directories, and structured data formats (CSV and JSON)
- Designing clear and informative command-line interfaces
- Verifying application behavior against both standard scenarios and edge cases

---

## Project Summary

| Task | Project | Directory | Entry Point | Focus Areas |
|:---:|---|---|---|---|
| 1 | Hangman Word Guessing Game | `HangmanWordGuessingGame/` | `hangman_terminal.py` | Game loops, sets, string handling, file input |
| 2 | Stock Portfolio Performance Tracker | `StockPortfolioPerormanceTracker/` | `portfolio.py` | Dictionaries, financial calculations, CSV export |
| 3 | Automated File Organizer and Cleanup Utility | `AutomatedFileOrganizer&CleanupUtility/` | `organizer.py` | Directory scanning, safe file operations, exception handling |
| 4 | Rule-Based Interactive Terminal Assistant | `Rule-BaseInteractiveTerminalAssistandChatbot/` | `chatbot.py` | JSON processing, regular expressions, text similarity, conversational state |

---

## Technologies and Python Modules

**Language:** Python 3 (version 3.7 or later; developed with Python 3.14)

| Module | Category | Purpose | Project |
|---|---|---|---|
| `random` | Standard library | Random word selection | Task 1 |
| `pathlib` | Standard library | Cross-platform path handling | Tasks 1–4 |
| `argparse` | Standard library | Command-line argument parsing | Tasks 2, 3 |
| `csv` | Standard library | Portfolio summary export | Task 2 |
| `datetime` | Standard library | Timestamps for exported records | Task 2 |
| `math` | Standard library | Numeric input validation | Task 2 |
| `os` | Standard library | Directory scanning and folder creation | Task 3 |
| `shutil` | Standard library | File relocation | Task 3 |
| `collections` | Standard library | Per-category statistics (`Counter`) | Task 3 |
| `json` | Standard library | FAQ knowledge base loading | Task 4 |
| `re` | Standard library | Keyword and pattern matching | Task 4 |
| `string` | Standard library | Punctuation handling | Task 4 |
| `difflib` | Standard library | Text similarity and typo tolerance | Task 4 |
| `dataclasses` | Standard library | Conversation state and intent modeling | Task 4 |
| `yfinance` | Third-party (optional) | Live stock price retrieval | Task 2 |
| `pygame` | Third-party (optional) | Graphical version of Hangman | Task 1 |

---

## Repository Structure

```text
Python-Internship-Projects/
│
├── HangmanWordGuessingGame/
│   ├── hangman_terminal.py
│   ├── words.txt
│   ├── src/
│   │   └── main.py
│   ├── assets/
│   └── assets1/
│
├── StockPortfolioPerormanceTracker/
│   ├── portfolio.py
│   └── s&p500TickerDataset.csv
│
├── AutomatedFileOrganizer&CleanupUtility/
│   └── organizer.py
│
├── Rule-BaseInteractiveTerminalAssistandChatbot/
│   ├── chatbot.py
│   └── sample_faq.json
│
└── README.md
```

**Notes**

- `words.txt` contains the 9,894-word list used by the Hangman game.
- `src/main.py` and the image asset directories belong to the optional graphical version of Hangman.
- `s&p500TickerDataset.csv` is a reference list of S&P 500 companies. It is not currently read by `portfolio.py`.
- `portfolio_summary.csv` is generated by the portfolio tracker on its first export and is therefore not included in the repository.

---

## Installation

### Prerequisites

- Python 3.7 or later

Verify the installed version:

```bash
python3 --version
```

### Clone the Repository

```bash
git clone <repository-url>
cd Python-Internship-Projects
```

Replace `<repository-url>` with the URL of this repository.

### Optional Dependencies

The core applications require no third-party packages. The following packages are needed only for their respective optional features:

| Package | Feature | Installation |
|---|---|---|
| `yfinance` | Live stock prices in the portfolio tracker | `python3 -m pip install yfinance` |
| `pygame` | Graphical version of Hangman | `python3 -m pip install pygame` |

On Windows, use `python` or `py` in place of `python3`.

---

## Projects

### Task 1: Hangman Word Guessing Game

A terminal implementation of the classic word-guessing game. The player reveals a hidden word one letter at a time and loses after six incorrect guesses.

#### Features

- **Random word selection** from an external word list (`words.txt`)
- **Input validation** requiring exactly one alphabetic character per guess
- **Masked word display** that reveals correctly guessed letters and conceals the rest
- **Guess tracking** with previously guessed letters displayed in alphabetical order
- **Duplicate guess protection:** repeated letters do not count as incorrect attempts
- **ASCII graphics** illustrating seven stages, from an empty gallows to the completed figure
- **Attempt limit** of six incorrect guesses
- **Win and loss conditions,** with the secret word revealed after a loss
- **Replay option** at the end of each round
- **Error handling** for a missing or empty word list

#### Technologies

Python 3, `random`, `pathlib`

#### Usage

```bash
cd HangmanWordGuessingGame
python3 hangman_terminal.py
```

#### Implementation Notes

- Guessed letters are stored in a `set`, which simplifies duplicate detection and the win-condition check.
- The word list is resolved relative to the script's location, so the game runs correctly from any working directory.
- An optional graphical version is available at `src/main.py`. It requires `pygame` and is launched with `python3 src/main.py`.

---

### Task 2: Stock Portfolio Performance Tracker

A command-line application that evaluates investment portfolio performance from stock ticker symbols, purchase prices, and share quantities.

#### Features

- **Ticker entry** with validation (letters A–Z only); entering `DONE` completes input
- **Numeric validation** requiring purchase prices and share quantities to be positive, finite numbers
- **Dictionary-based portfolio** mapping each ticker to its purchase price and share quantity
- **Position consolidation:** repeated purchases of the same ticker are merged at a weighted-average purchase price
- **Two pricing modes:**
  - *Sample mode (default):* built-in prices for `AAPL`, `MSFT`, `NVDA`, `AMZN`, and `GOOGL`
  - *Live mode (optional):* the most recent closing price retrieved from Yahoo Finance through `yfinance`
- **Per-holding metrics:** invested capital, current market value, gain or loss, and percentage return
- **Portfolio totals:** total invested capital, total market value, overall gain or loss, and overall return
- **CSV export:** results are appended to `portfolio_summary.csv` with timezone-aware timestamps, preserving a history of previous runs
- **Error handling:** tickers without an available price are reported and excluded from the totals without interrupting execution

#### Technologies

Python 3, `csv`, `datetime`, `pathlib`, `argparse`, `math`, `yfinance` (optional)

#### Usage

```bash
cd StockPortfolioPerormanceTracker
python3 portfolio.py
```

To use live market prices (requires `yfinance` and an internet connection):

```bash
python3 portfolio.py --live
```

#### Sample Output

```text
Ticker        Shares    Buy Price      Current     Gain/Loss     Return
-----------------------------------------------------------------------
AAPL           20.00       250.00       250.00          0.00      0.00%
MSFT            2.00       500.00       510.00         20.00      2.00%
XYZ: No sample price available for XYZ.
-----------------------------------------------------------------------
Total invested:       6,000.00
Current market value: 6,020.00
Total gain/loss:      20.00
Overall return:       0.33%
```

In this example, AAPL was entered twice (10 shares at $200 and 10 shares at $300). The application consolidated both purchases into a single 20-share position at a weighted-average price of $250.

---

### Task 3: Automated File Organizer and Cleanup Utility

A file management utility that organizes cluttered directories, such as Downloads, by moving files into category subfolders according to their extensions. The utility is designed never to delete or overwrite existing files.

#### Features

- **Directory scanning** of top-level contents using `os.scandir()`
- **Case-insensitive extension matching** (`.PDF`, `.Pdf`, and `.pdf` are treated identically)
- **Five file categories:**

  | Category | Supported Extensions |
  |---|---|
  | Documents | `.pdf`, `.docx`, `.doc`, `.txt`, `.xlsx`, `.pptx` |
  | Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.svg` |
  | Videos | `.mp4`, `.mkv`, `.avi`, `.mov` |
  | Archives | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` |
  | Code | `.py`, `.js`, `.html`, `.css`, `.java`, `.cpp` |

- **On-demand folder creation:** category folders are created only when a file is about to be moved into them
- **Overwrite protection:** each destination is verified immediately before `shutil.move()` is called
- **Collision handling:** conflicting filenames receive a numeric suffix (`report_1.pdf`, `report_2.pdf`, and so on)
- **Per-file exception handling** for `PermissionError`, `FileNotFoundError`, `FileExistsError`, and other `OSError` conditions, so a single failure does not halt the process
- **Preview** of all planned moves and skipped files before any action is taken
- **Explicit confirmation:** no files are moved unless the user enters `y`
- **Execution summary** reporting files scanned, organized, skipped, and failed, with a per-category breakdown
- **Idempotent execution:** subdirectories are never processed, so the utility can be run repeatedly without affecting previously organized files
- **Excluded items:** unsupported extensions, directories, symbolic links, and the script itself remain untouched

#### Technologies

Python 3, `os`, `shutil`, `pathlib`, `collections.Counter`, `argparse`

#### Usage

```bash
cd "AutomatedFileOrganizer&CleanupUtility"
python3 organizer.py
```

The application prompts for a target directory; pressing Enter selects the default, `~/Downloads`. A directory may also be passed as an argument:

```bash
python3 organizer.py ~/Desktop
```

The quotation marks in the `cd` command are required because the directory name contains an ampersand (`&`).

#### Sample Summary

```text
========================================
       AUTOMATED FILE ORGANIZER
========================================

Target Directory: /home/user/Downloads

Files Scanned:        13
Files Organized:       6
Files Skipped:         5
Failed Operations:     2

Category Breakdown:
Documents:             2
Images:                2
Videos:                1
Archives:              1
Code:                  0

Files that could not be moved (left untouched):
  - app.py: a file named 'Code' is blocking the category folder
  - style.css: a file named 'Code' is blocking the category folder

========================================
Organization Completed!
========================================
```

---

### Task 4: Rule-Based Interactive Terminal Assistant

A terminal-based customer support chatbot that identifies user intent and responds using a JSON FAQ knowledge base. Intent recognition is entirely rule-based, combining keyword matching, regular expressions, and text similarity scoring; no external AI services or APIs are used.

#### Features

- **Greeting recognition** for `hello`, `hi`, `hey`, `good morning`, and `good afternoon`
- **External knowledge base:** questions and answers are loaded from `sample_faq.json`, allowing new FAQs to be added without code changes
- **Input normalization:** conversion to lowercase, whitespace trimming, and punctuation removal
- **Scored intent matching:** each FAQ is evaluated against the user's message as follows:

  | Criterion | Score |
  |---|---|
  | Regular-expression pattern match | +2.0 |
  | Each matching keyword | +1.0 |
  | Overall similarity to the FAQ question | +0.0 to +1.0 |

  The highest-scoring FAQ is selected when its score is at least 1.0.
- **Flexible phrasing:** alternative formulations of the same question are recognized
- **Typo tolerance:** minor misspellings (for example, `certifcate`) are matched to the intended keyword
- **Combined messages:** inputs such as "Hi, when are you open?" receive both a greeting and an answer
- **Clarification prompts:** uncertain matches trigger a "Did you mean...?" suggestion, which the user can confirm with `yes`
- **Progressive fallback:** an unrecognized question produces a list of supported topics; a second consecutive miss produces the full list of available questions
- **Help command** listing all questions the chatbot can answer
- **Exit commands:** `bye`, `goodbye`, `exit`, `quit`, and short phrases such as "ok bye"; longer sentences containing these words are not treated as exit requests
- **Error handling:**
  - A missing or invalid JSON file produces a descriptive warning (including the line and column for syntax errors), and the chatbot continues in a limited greetings-only mode
  - Malformed FAQ entries and invalid regular expressions are skipped individually
  - Empty input and keyboard interrupts (Ctrl+C, Ctrl+D) are handled gracefully

#### Technologies

Python 3, `json`, `re`, `string`, `difflib`, `dataclasses`, `pathlib`

#### Usage

```bash
cd Rule-BaseInteractiveTerminalAssistandChatbot
python3 chatbot.py
```

An alternative FAQ file may be supplied as an argument:

```bash
python3 chatbot.py path/to/other_faq.json
```

#### Sample Conversation

```text
========================================
       CUSTOMER SUPPORT CHATBOT
========================================

Bot: Hello! Welcome to Customer Support.
Bot: How can I assist you today?

You: hi
Bot: Hello! How may I help you?

You: when are you open?
Bot: We operate Monday through Friday from 9:00 AM to 6:00 PM IST.

You: when will i receive my results
Bot: I'm not sure I understood. Did you mean: "When will I receive my certificate?" (yes/no)

You: yes
Bot: Certificates are reviewed and issued within 3-5 business days after your code review.

You: bye
Bot: Thank you for contacting us. Have a great day!

Chatbot terminated.
```

#### Extending the Knowledge Base

New questions are added as entries in the `faqs` list of `sample_faq.json`. Only the `question` and `answer` fields are required; the optional `topic`, `keywords`, and `patterns` fields improve matching accuracy.

```json
{
  "question": "Is the internship paid?",
  "answer": "This is an unpaid internship.",
  "topic": "stipend",
  "keywords": ["paid", "stipend"],
  "patterns": ["\\b(paid|stipend|salary)\\b"]
}
```

---

## Skills and Programming Concepts

| Skill | Application |
|---|---|
| Python fundamentals | All four projects |
| Variables and data types | Strings, integers, floating-point numbers, booleans, and `None` |
| Control flow | Game loop, input validation loops, directory iteration, and conversation loop |
| Functions and modular design | Single-responsibility functions for scanning, moving, scoring, and reporting |
| Dictionaries and sets | Portfolio positions, extension mappings, FAQ data, and guessed letters |
| String manipulation | Word masking, ticker validation, filename generation, and text normalization |
| File and directory management | Word-list loading, directory scanning, folder creation, and file relocation |
| CSV and JSON processing | Portfolio export with `csv.DictWriter` and knowledge-base loading with `json` |
| Exception handling | Targeted handling of invalid input, missing files, permission errors, and malformed JSON |
| Regular expressions | Greeting detection, intent patterns, and word-boundary matching |
| Text similarity | Fuzzy matching with `difflib.SequenceMatcher` and `get_close_matches` |
| Data processing and calculations | Weighted-average cost, returns, portfolio totals, and operation statistics |
| Command-line interfaces | Interactive prompts, `argparse` options, and formatted reports |
| Testing and debugging | Scripted terminal testing covering standard and edge-case scenarios |

---

## Testing and Implementation

All applications were verified manually through scripted terminal sessions covering standard usage and edge cases. The repository does not currently include an automated test suite.

| Project | Scenarios Verified |
|---|---|
| Hangman | Invalid input, repeated guesses without penalty, win condition, loss condition with word reveal, and declining a replay |
| Portfolio Tracker | Rejection of invalid and negative numbers, weighted-average consolidation of repeated tickers, exclusion of tickers without prices, and CSV output with headers and timestamps |
| File Organizer | Mixed-case extensions, filename collisions, unsupported file types, ignored subdirectories, blocked category folders, invalid paths, cancellation, and repeated execution |
| Chatbot | Required example questions, alternative phrasing, misspellings, combined greetings and questions, clarification follow-ups, exit-command edge cases, missing and malformed JSON, invalid entries, and end-of-input handling |

### Design Principles

- **Fault tolerance:** invalid input is re-prompted, and a failure affecting one item does not interrupt the remainder of the process.
- **Data safety:** the file organizer only relocates files; it never deletes or overwrites them.
- **Separation of data and logic:** the chatbot knowledge base and the Hangman word list are maintained in external files.
- **Location-independent paths:** data files are resolved relative to each script rather than the current working directory.
- **Transparent feedback:** previews, progress messages, and formatted summaries keep the user informed throughout execution.

---

## Learning Objectives

The internship projects were designed to develop the ability to:

1. Translate written requirements into complete, functional software.
2. Write maintainable code using descriptive naming, focused functions, and consistent structure.
3. Handle invalid, missing, malformed, and unexpected input reliably.
4. Automate file system operations while protecting user data.
5. Process data and present results through calculations, CSV exports, and formatted reports.
6. Apply text-processing techniques, including normalization, regular expressions, and similarity scoring.
7. Verify software systematically against expected behavior and edge cases.
8. Use the Python standard library effectively and keep external dependencies optional.

---

## Author

**GitHub:** [Aeronleelucero](https://github.com/Aeronleelucero)

Developed as part of a four-week Python internship program.

---

## Conclusion

These four projects demonstrate a progression from Python fundamentals to complete, reliable command-line applications. Each addresses a distinct problem domain (entertainment, financial analysis, file management, and customer support) while applying consistent practices in input validation, error handling, data safety, and code organization.

Thank you for reviewing this portfolio. Feedback and suggestions are welcome.
