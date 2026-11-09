"""
Automated File Organizer Utility
================================

Sorts the files in a folder (for example, Downloads) into category
subfolders based on each file's extension:

    report.PDF  ->  Documents/report.PDF
    photo.jpg   ->  Images/photo.jpg
    movie.mkv   ->  Videos/movie.mkv

Safety rules this script follows:
    * It never deletes a file and never overwrites one.
    * It only moves files, never folders.
    * Files with an extension it doesn't recognize stay where they are.
    * It shows a preview and asks before it moves anything.
    * Running it again is safe: the category folders are directories, and
      directories are always ignored, so already-organized files stay put.

Usage:
    python3 organizer.py                 # asks which folder (default: ~/Downloads)
    python3 organizer.py /path/to/folder # organizes that folder

Modules used (all part of Python's standard library):
    os          - os.scandir() lists a folder's contents efficiently;
                  os.makedirs() creates folders.
    shutil      - shutil.move() moves a file to a new location.
    pathlib     - Path objects make joining paths and reading extensions easy.
    collections - Counter tallies how many files went to each category.
    argparse    - reads the optional folder path from the command line.
"""

import argparse
import os
import shutil
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Configuration: which extensions belong in which folder
# ---------------------------------------------------------------------------

# Readable form: category -> list of extensions. Add new types here.
CATEGORIES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".svg"],
    "Videos":    [".mp4", ".mkv", ".avi", ".mov"],
    "Archives":  [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code":      [".py", ".js", ".html", ".css", ".java", ".cpp"],
}

# Lookup form: extension -> category, e.g. {".pdf": "Documents", ...}.
# Built from CATEGORIES so the two can never disagree. Looking up a key in a
# dictionary is instant, which is why we flip the mapping around.
EXTENSION_MAP = {
    ext: category
    for category, extensions in CATEGORIES.items()
    for ext in extensions
}

DEFAULT_DIRECTORY = Path.home() / "Downloads"

# The script's own location, so it never moves itself if it's run from
# inside the folder being organized (it is a .py file, after all).
THIS_SCRIPT = Path(__file__).resolve()

LINE = "=" * 40


# ---------------------------------------------------------------------------
# 2. Extension identification
# ---------------------------------------------------------------------------

def get_category(filename):
    """Return the category for a filename, or None if the type is unknown.

    Path(filename).suffix gives the last extension (".PDF" for "Report.PDF").
    .lower() makes the check case-insensitive, so ".PDF", ".Pdf" and ".pdf"
    are all treated the same.
    """
    extension = Path(filename).suffix.lower()
    return EXTENSION_MAP.get(extension)  # .get() returns None if missing


# ---------------------------------------------------------------------------
# 3. Directory scanning
# ---------------------------------------------------------------------------

def scan_directory(directory):
    """Look at every item directly inside `directory` and sort it into a plan.

    Returns two lists:
        to_move - (source Path, category) pairs for files we can organize
        skipped - (filename, reason) pairs for files we'll leave alone

    os.scandir() is used instead of os.listdir() because each entry it
    returns already knows whether it is a file or a folder, so Python
    doesn't have to ask the operating system a second time.

    Only the top level is scanned. Subfolders (including the category
    folders this script creates) are ignored completely.
    """
    to_move = []
    skipped = []

    with os.scandir(directory) as entries:
        for entry in entries:
            # Folders are never moved or looked inside.
            # follow_symlinks=False means a shortcut pointing at a folder
            # is not mistaken for a real folder.
            if entry.is_dir(follow_symlinks=False):
                continue

            # Symbolic links (shortcuts) are left alone: moving one could
            # break whatever relies on it.
            if entry.is_symlink():
                skipped.append((entry.name, "symbolic link"))
                continue

            # Anything that isn't a regular file (sockets, pipes, ...).
            if not entry.is_file(follow_symlinks=False):
                skipped.append((entry.name, "not a regular file"))
                continue

            source = Path(entry.path)

            if source.resolve() == THIS_SCRIPT:
                skipped.append((entry.name, "this organizer script"))
                continue

            category = get_category(entry.name)
            if category is None:
                skipped.append((entry.name, "unrecognized extension"))
            else:
                to_move.append((source, category))

    # Sort so the preview and progress output are in a predictable order.
    to_move.sort(key=lambda item: item[0].name.lower())
    skipped.sort(key=lambda item: item[0].lower())
    return to_move, skipped


# ---------------------------------------------------------------------------
# 4. Folder creation
# ---------------------------------------------------------------------------

def ensure_folder(path):
    """Create the folder at `path` if it doesn't exist yet.

    This is called only right before a file is moved into the folder, so
    no empty category folders are ever created.

    exist_ok=True means "it's fine if the folder is already there".
    If a *file* with the same name exists (e.g. a file called "Documents"
    with no extension), we can't create the folder, so we raise
    FileExistsError and the caller reports it as a failed operation.
    """
    if path.exists() and not path.is_dir():
        raise FileExistsError(
            f"a file named '{path.name}' is blocking the category folder")
    os.makedirs(path, exist_ok=True)


# ---------------------------------------------------------------------------
# 5. Collision handling
# ---------------------------------------------------------------------------

def get_unique_destination(folder, filename):
    """Return a path inside `folder` that no existing file is using.

    If "report.pdf" is free, it is used as-is (original names are kept
    whenever possible). Otherwise we try "report_1.pdf", "report_2.pdf",
    and so on until we find a name that isn't taken.
    """
    destination = folder / filename
    if not destination.exists():
        return destination

    stem = destination.stem      # "report"  from "report.pdf"
    suffix = destination.suffix  # ".pdf"    from "report.pdf"
    counter = 1
    while True:
        candidate = folder / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


# ---------------------------------------------------------------------------
# 6. File movement
# ---------------------------------------------------------------------------

def move_file(source, destination):
    """Move `source` to `destination` without ever overwriting a file.

    shutil.move() would silently replace an existing file on some
    systems, so we check one last time immediately before moving. If
    something appeared at the destination in the meantime, we raise
    FileExistsError instead of overwriting it.
    """
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")
    shutil.move(str(source), str(destination))


def organize_files(directory, to_move):
    """Move every planned file into its category folder.

    Each file is handled inside its own try/except block, so one file
    failing (for example because it's open in another program or we lack
    permission) doesn't stop the rest from being organized.

    Returns:
        category_counts - Counter of how many files went to each category
        failures        - list of (filename, error message) pairs
    """
    category_counts = Counter()
    failures = []

    for source, category in to_move:
        folder = directory / category
        try:
            ensure_folder(folder)
            destination = get_unique_destination(folder, source.name)
            move_file(source, destination)
        except PermissionError:
            reason = "permission denied"
        except FileNotFoundError:
            reason = "file disappeared before it could be moved"
        except FileExistsError as error:
            reason = str(error)
        except (OSError, shutil.Error) as error:
            # OSError covers other filesystem problems: disk full,
            # file locked, read-only drive, and so on.
            reason = f"filesystem error ({error})"
        else:
            # The `else` block runs only if no exception was raised.
            category_counts[category] += 1
            renamed = "" if destination.name == source.name else \
                f" (renamed to {destination.name})"
            print(f"  [MOVED]  {source.name}  ->  {category}/{renamed}")
            continue

        failures.append((source.name, reason))
        print(f"  [FAILED] {source.name}: {reason}")

    return category_counts, failures


# ---------------------------------------------------------------------------
# 7. User interaction
# ---------------------------------------------------------------------------

def ask_for_directory(cli_path):
    """Work out which folder to organize and make sure it exists.

    Uses the path from the command line if one was given; otherwise asks
    the user, falling back to ~/Downloads when they just press Enter.
    Returns an absolute Path, or None if the folder is invalid.
    """
    if cli_path:
        raw = cli_path
    else:
        raw = input(f"Folder to organize [{DEFAULT_DIRECTORY}]: ").strip()
        raw = raw.strip("\"'")  # allow pasted paths wrapped in quotes
        if not raw:
            raw = str(DEFAULT_DIRECTORY)

    # expanduser turns "~" into the home folder; resolve makes it absolute.
    directory = Path(raw).expanduser().resolve()

    if not directory.exists():
        print(f"Error: '{directory}' does not exist.")
        return None
    if not directory.is_dir():
        print(f"Error: '{directory}' is a file, not a folder.")
        return None
    return directory


def show_preview(to_move, skipped):
    """Print what will happen before anything is moved."""
    planned = Counter(category for _, category in to_move)

    print(f"\nFound {len(to_move) + len(skipped)} file(s).")
    print(f"  {len(to_move)} will be organized:")
    for category in CATEGORIES:
        if planned[category]:
            print(f"    {category + ':':<14}{planned[category]:>4}")
    if skipped:
        print(f"  {len(skipped)} will be left where they are:")
        for name, reason in skipped:
            print(f"    - {name} ({reason})")


def confirm(prompt):
    """Ask a yes/no question. Anything other than 'y' or 'yes' means no."""
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer in ("y", "yes")


# ---------------------------------------------------------------------------
# 8. Summary reporting
# ---------------------------------------------------------------------------

def print_summary(directory, scanned, category_counts, skipped, failures):
    """Print the final report."""
    organized = sum(category_counts.values())

    print()
    print(LINE)
    print("       AUTOMATED FILE ORGANIZER")
    print(LINE)
    print()
    print(f"Target Directory: {directory}")
    print()
    print(f"{'Files Scanned:':<20}{scanned:>4}")
    print(f"{'Files Organized:':<20}{organized:>4}")
    print(f"{'Files Skipped:':<20}{len(skipped):>4}")
    print(f"{'Failed Operations:':<20}{len(failures):>4}")
    print()
    print("Category Breakdown:")
    for category in CATEGORIES:
        print(f"{category + ':':<20}{category_counts[category]:>4}")

    if failures:
        print()
        print("Files that could not be moved (left untouched):")
        for name, reason in failures:
            print(f"  - {name}: {reason}")

    print()
    print(LINE)
    print("Organization Completed!")
    print(LINE)


# ---------------------------------------------------------------------------
# 9. Main program
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Sort files into category folders by extension.")
    parser.add_argument(
        "directory", nargs="?",
        help=f"folder to organize (default: ask, suggesting {DEFAULT_DIRECTORY})")
    args = parser.parse_args()

    print(LINE)
    print("       AUTOMATED FILE ORGANIZER")
    print(LINE)

    directory = ask_for_directory(args.directory)
    if directory is None:
        return 1

    print(f"\nScanning {directory} ...")
    try:
        to_move, skipped = scan_directory(directory)
    except PermissionError:
        print(f"Error: no permission to read '{directory}'.")
        return 1
    except OSError as error:
        print(f"Error: could not read '{directory}': {error}")
        return 1

    scanned = len(to_move) + len(skipped)
    show_preview(to_move, skipped)

    if not to_move:
        print("\nNothing to organize.")
        print_summary(directory, scanned, Counter(), skipped, [])
        return 0

    print()
    if not confirm(f"Move {len(to_move)} file(s) into category folders?"):
        print("Cancelled. No files were moved.")
        return 0

    print("\nOrganizing...")
    category_counts, failures = organize_files(directory, to_move)
    print_summary(directory, scanned, category_counts, skipped, failures)
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or Ctrl+D at a prompt: exit cleanly instead of a traceback.
        # Any file already moved stays moved; nothing is half-done, because
        # each move is a single operation.
        print("\nInterrupted. Exiting.")
        raise SystemExit(130)
