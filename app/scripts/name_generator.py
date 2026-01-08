import json
import re
import sys

from pluralizer import Pluralizer

pluralizer = Pluralizer()


def to_dashed(string):
    return re.sub(r"([A-Z])", r"-\1", string).lower().lstrip("-")


def to_lower(string):
    return string.lower()


def to_underscore(string):
    return re.sub(r"([A-Z])", r"_\1", string).lower().lstrip("_")


def to_upper_case_underscored(string):
    return re.sub(r"([A-Z])", r"_\1", string).upper().lstrip("_")


def to_capitalized(string):
    return string[0].upper() + string[1:]


def to_space_separated(string):
    result = re.sub(r"([A-Z])", r" \1", string)
    return result.capitalize()


name = sys.argv[1] if len(sys.argv) > 1 else None

if not name:
    print("Please provide a name as argument.")
    sys.exit(1)

plural = None
singular = None

EXCEPTIONS = ["todos"]

if name in EXCEPTIONS:
    singular = name
    plural = name
elif pluralizer.isSingular(name):
    singular = name
    plural = pluralizer.plural(name)
else:
    plural = name
    singular = pluralizer.singular(name)

singular_dashed = to_dashed(singular)
plural_dashed = to_dashed(plural)

singular_capitalized_dashed = singular_dashed.upper()
plural_capitalized_dashed = plural_dashed.upper()

singular_underscored = to_underscore(singular)
plural_underscored = to_underscore(plural)

singular_capitalized_underscored = to_upper_case_underscored(singular)
plural_capitalized_underscored = to_upper_case_underscored(plural)

singular_capitalized = to_capitalized(singular)
plural_capitalized = to_capitalized(plural)

singular_space_separated = to_space_separated(singular)
plural_space_separated = to_space_separated(plural)

singular_space_separated_lower_case = to_lower(to_space_separated(singular))
plural_space_separated_lower_case = to_lower(to_space_separated(plural))


data = {
    "singular": singular,
    "plural": plural,
    "singular_dashed": singular_dashed,
    "plural_dashed": plural_dashed,
    "singular_capitalized_dashed": singular_capitalized_dashed,
    "plural_capitalized_dashed": plural_capitalized_dashed,
    "singular_underscored": singular_underscored,
    "plural_underscored": plural_underscored,
    "singular_capitalized_underscored": singular_capitalized_underscored,
    "plural_capitalized_underscored": plural_capitalized_underscored,
    "singular_capitalized": singular_capitalized,
    "plural_capitalized": plural_capitalized,
    "singular_space_separated": singular_space_separated,
    "plural_space_separated": plural_space_separated,
    "singular_space_separated_lower_case": singular_space_separated_lower_case,
    "plural_space_separated_lower_case": plural_space_separated_lower_case,
}

print(json.dumps(data, indent=2))
