#!/usr/bin/env python3
"""
Password Generator - Generates secure random passwords or memorable passphrases.

Usage:
    python generate_password.py [options]

Examples:
    python generate_password.py                     # 16-char random password
    python generate_password.py -l 24               # 24-char random password
    python generate_password.py --passphrase        # 4-word passphrase
    python generate_password.py --passphrase -w 6   # 6-word passphrase
    python generate_password.py -n 5                # Generate 5 passwords
"""

import argparse
import secrets
import string


# Common English words for passphrases (EFF short wordlist subset)
WORDLIST = [
    "acid", "acorn", "acre", "acts", "afar", "affix", "aged", "agent", "agile",
    "aging", "agony", "ahead", "aide", "aids", "aim", "ajar", "alarm", "alias",
    "alibi", "alien", "alike", "alive", "alley", "allot", "allow", "alloy",
    "almond", "almost", "aloft", "alone", "alpha", "already", "also", "altar",
    "alter", "amaze", "amber", "amend", "amid", "ample", "amuse", "anchor",
    "angel", "anger", "angle", "angry", "ankle", "annex", "anvil", "apart",
    "apex", "apple", "apply", "apron", "aqua", "arbor", "arena", "argue",
    "arise", "armor", "army", "aroma", "array", "arrow", "arson", "artsy",
    "ascot", "ashen", "aside", "asked", "asset", "atlas", "atom", "attic",
    "audio", "audit", "aunt", "avoid", "awake", "award", "awash", "awful",
    "axis", "bacon", "badge", "badly", "bagel", "baggy", "baker", "balmy",
    "banjo", "barge", "baron", "basic", "basin", "batch", "beach", "beast",
    "began", "begin", "being", "belly", "below", "bench", "berry", "birth",
    "bison", "black", "blade", "blame", "blast", "blaze", "bleak", "blend",
    "bless", "blimp", "blind", "bliss", "blitz", "block", "blond", "blood",
    "bloom", "blown", "blunt", "blurt", "blush", "board", "boast", "boat",
    "bogus", "boil", "bold", "bolt", "bonus", "book", "booth", "boots",
    "booze", "boss", "botch", "both", "boxer", "brace", "brain", "brake",
    "brand", "brass", "brave", "bravo", "bread", "break", "breed", "brick",
    "bride", "brief", "brim", "bring", "brink", "brisk", "broad", "broil",
    "broke", "brook", "broom", "brush", "brute", "buck", "buddy", "budget",
    "build", "built", "bulge", "bulk", "bully", "bunch", "bunny", "burden",
    "burn", "burst", "bury", "bush", "bust", "busy", "buyer", "cabin",
    "cable", "cache", "cadet", "cage", "cake", "calm", "camel", "camp",
    "canal", "candy", "cane", "canon", "cape", "car", "card", "care",
    "cargo", "carol", "carry", "carve", "case", "cash", "cast", "catch",
    "cause", "cave", "cease", "cedar", "chain", "chair", "champ", "chance",
    "chaos", "charm", "chart", "chase", "cheap", "check", "cheek", "cheer",
    "chess", "chest", "chew", "chief", "child", "chill", "chimp", "chip",
    "chomp", "chord", "chore", "chose", "chunk", "churn", "cider", "cigar",
    "cinch", "city", "civic", "civil", "clad", "claim", "clamp", "clap",
    "clash", "clasp", "class", "claw", "clay", "clean", "clear", "clerk",
    "click", "cliff", "climb", "cling", "clip", "cloak", "clock", "clone",
    "close", "cloth", "cloud", "clout", "clown", "club", "cluck", "clue",
    "clump", "clung", "coach", "coast", "coat", "cobra", "cocoa", "coil",
    "coin", "cola", "cold", "colon", "color", "comet", "comic", "comma",
    "conch", "condo", "cone", "cope", "coral", "cork", "corn", "cost",
    "couch", "cough", "could", "count", "couple", "court", "cover", "cozy",
    "crack", "craft", "cramp", "crane", "crank", "crash", "crate", "crater",
    "crawl", "crazy", "cream", "creek", "creep", "creme", "crepe", "crept",
    "crest", "crick", "crime", "crisp", "croak", "crock", "crop", "cross",
    "crowd", "crown", "crude", "cruel", "crush", "crust", "cube", "cult",
    "cupid", "curb", "cure", "curl", "curry", "curse", "curve", "cyber",
    "cycle", "dab", "daddy", "daily", "dairy", "daisy", "dance", "dandy",
    "darn", "dart", "dash", "data", "date", "dawn", "deal", "dean",
    "dear", "death", "debit", "debug", "decaf", "decay", "deck", "decor",
    "decoy", "decry", "deed", "deep", "deer", "delay", "delta", "deluxe",
    "demon", "denim", "dense", "depth", "derby", "desk", "dial", "diary",
    "dice", "dig", "dill", "dime", "dimly", "diner", "dingy", "disco",
    "dish", "disk", "ditch", "ditto", "ditty", "diver", "dizzy", "dock",
    "dodge", "doing", "doll", "dome", "donor", "donut", "doom", "door",
    "dope", "dot", "double", "doubt", "dough", "dove", "down", "dozen",
    "draft", "drain", "drake", "drama", "drank", "drape", "draw", "dread",
    "dream", "dress", "dried", "drift", "drill", "drink", "drive", "drone",
    "drool", "droop", "drop", "drown", "drum", "dry", "duck", "duct",
    "dude", "duel", "duet", "dug", "duke", "dull", "dummy", "dump",
    "dune", "dunce", "dunk", "duo", "dusk", "dust", "duty", "dwarf",
    "dwell", "eagle", "early", "earth", "easel", "east", "eaten", "eater",
    "ebony", "echo", "edge", "edgy", "edit", "eel", "eerie", "egret"
]


def generate_random_password(length: int = 16,
                             include_upper: bool = True,
                             include_lower: bool = True,
                             include_digits: bool = True,
                             include_symbols: bool = True,
                             exclude_ambiguous: bool = False) -> str:
    """Generate a cryptographically secure random password."""

    chars = ""
    required = []

    if include_lower:
        lower = string.ascii_lowercase
        if exclude_ambiguous:
            lower = lower.replace("l", "").replace("o", "")
        chars += lower
        required.append(secrets.choice(lower))

    if include_upper:
        upper = string.ascii_uppercase
        if exclude_ambiguous:
            upper = upper.replace("I", "").replace("O", "")
        chars += upper
        required.append(secrets.choice(upper))

    if include_digits:
        digits = string.digits
        if exclude_ambiguous:
            digits = digits.replace("0", "").replace("1", "")
        chars += digits
        required.append(secrets.choice(digits))

    if include_symbols:
        symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        chars += symbols
        required.append(secrets.choice(symbols))

    if not chars:
        raise ValueError("At least one character type must be included")

    # Generate remaining characters
    remaining_length = length - len(required)
    if remaining_length < 0:
        remaining_length = 0
        required = required[:length]

    password_chars = required + [secrets.choice(chars) for _ in range(remaining_length)]

    # Shuffle to avoid predictable positions
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def generate_passphrase(num_words: int = 4,
                        separator: str = "-",
                        capitalize: bool = False) -> str:
    """Generate a memorable passphrase from random words."""

    words = [secrets.choice(WORDLIST) for _ in range(num_words)]

    if capitalize:
        words = [word.capitalize() for word in words]

    return separator.join(words)


def main():
    parser = argparse.ArgumentParser(
        description="Generate secure passwords or passphrases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_password.py                     # 16-char random password
  python generate_password.py -l 24               # 24-char random password
  python generate_password.py --passphrase        # 4-word passphrase
  python generate_password.py --passphrase -w 6   # 6-word passphrase
  python generate_password.py -n 5                # Generate 5 passwords
  python generate_password.py --no-symbols        # No special characters
  python generate_password.py --exclude-ambiguous # No 0/O/l/1/I confusion
        """
    )

    # Mode selection
    parser.add_argument(
        "--passphrase", "-p",
        action="store_true",
        help="Generate a memorable passphrase instead of random password"
    )

    # Common options
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="Number of passwords to generate (default: 1)"
    )

    # Random password options
    parser.add_argument(
        "-l", "--length",
        type=int,
        default=16,
        help="Password length (default: 16)"
    )
    parser.add_argument(
        "--no-upper",
        action="store_true",
        help="Exclude uppercase letters"
    )
    parser.add_argument(
        "--no-lower",
        action="store_true",
        help="Exclude lowercase letters"
    )
    parser.add_argument(
        "--no-digits",
        action="store_true",
        help="Exclude digits"
    )
    parser.add_argument(
        "--no-symbols",
        action="store_true",
        help="Exclude symbols"
    )
    parser.add_argument(
        "--exclude-ambiguous",
        action="store_true",
        help="Exclude ambiguous characters (0, O, l, 1, I)"
    )

    # Passphrase options
    parser.add_argument(
        "-w", "--words",
        type=int,
        default=4,
        help="Number of words in passphrase (default: 4)"
    )
    parser.add_argument(
        "-s", "--separator",
        type=str,
        default="-",
        help="Word separator for passphrase (default: -)"
    )
    parser.add_argument(
        "--capitalize",
        action="store_true",
        help="Capitalize each word in passphrase"
    )

    args = parser.parse_args()

    for i in range(args.count):
        if args.passphrase:
            password = generate_passphrase(
                num_words=args.words,
                separator=args.separator,
                capitalize=args.capitalize
            )
        else:
            password = generate_random_password(
                length=args.length,
                include_upper=not args.no_upper,
                include_lower=not args.no_lower,
                include_digits=not args.no_digits,
                include_symbols=not args.no_symbols,
                exclude_ambiguous=args.exclude_ambiguous
            )

        print(password)


if __name__ == "__main__":
    main()
