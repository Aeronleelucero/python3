
import random
from pathlib import Path

MAX_MISTAKES = 6

HANGMAN_STAGES = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\  |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\  |
     /    |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\  |
     / \  |
          |
    =========
    """,
]


def load_words():
    words_file = Path(__file__).resolve().parent / "words.txt"

    try:
        with words_file.open("r", encoding="utf-8") as file:
            words = [
                line.strip().upper()
                for line in file
                if line.strip().isalpha()
            ]
    except FileNotFoundError:
        raise SystemExit("Error: words.txt was not found.")

    if not words:
        raise SystemExit("Error: words.txt contains no valid words.")

    return words


def display_game(word, guessed_letters, mistakes):
    print(HANGMAN_STAGES[mistakes])

    masked_word = " ".join(
        letter if letter in guessed_letters else "_"
        for letter in word
    )

    print("Word:", masked_word)
    print(f"Mistakes: {mistakes}/{MAX_MISTAKES}")
    print("Guessed letters:", " ".join(sorted(guessed_letters)) or "None")


def play_hangman(words):
    secret_word = random.choice(words)
    guessed_letters = set()
    mistakes = 0

    print("\n=== HANGMAN ===")
    print("Guess the secret word one letter at a time.")

    while mistakes < MAX_MISTAKES:
        display_game(secret_word, guessed_letters, mistakes)

        if set(secret_word) <= guessed_letters:
            print("\nCongratulations! You guessed the word!")
            return

        guess = input("\nEnter a letter: ").strip().upper()

        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input. Enter one letter.")
            continue

        if guess in guessed_letters:
            print(f"You already guessed '{guess}'. Try another letter.")
            continue

        guessed_letters.add(guess)

        if guess in secret_word:
            print(f"Correct! '{guess}' is in the word.")
        else:
            mistakes += 1
            print(f"Incorrect! '{guess}' is not in the word.")

    display_game(secret_word, guessed_letters, mistakes)
    print("\nGame over! You used all six mistakes.")
    print(f"The secret word was: {secret_word}")


def main():
    words = load_words()

    while True:
        play_hangman(words)

        play_again = input("\nPlay again? (y/n): ").strip().lower()

        if play_again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
