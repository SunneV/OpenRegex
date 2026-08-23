"""Capture-group accounting for POSIX ARE patterns.

PostgreSQL exposes group offsets through the `subexpr` argument of
regexp_instr(), but there is no way to ask the server how many capture groups a
pattern declares - and passing a number that is too high raises an error. So the
pattern is scanned here, with the same rules the ARE parser uses: a bare '('
captures, '(?' introduces a non-capturing construct, and everything inside a
bracket expression is literal.
"""


def count_capture_groups(pattern: str) -> int:
    count = 0
    index = 0
    length = len(pattern)
    in_bracket = False

    while index < length:
        char = pattern[index]

        if char == "\\":
            index += 2
            continue

        if in_bracket:
            # [:alpha:], [=e=] and [.hyphen.] carry their own ']' terminator.
            if char == "[" and index + 1 < length and pattern[index + 1] in ":.=":
                marker = pattern[index + 1]
                closing = pattern.find(marker + "]", index + 2)
                index = length if closing == -1 else closing + 2
                continue
            if char == "]":
                in_bracket = False
            index += 1
            continue

        if char == "[":
            in_bracket = True
            index += 1
            if index < length and pattern[index] == "^":
                index += 1
            if index < length and pattern[index] == "]":
                index += 1
            continue

        if char == "(" and not pattern.startswith("(?", index):
            count += 1

        index += 1

    return count
