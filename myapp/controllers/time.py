import re


def gap_to_time(time: float, gap: str) -> float:
    print(time)
    print("gap: ", gap)
    """
    Adds a time gap to a given time.

    Parameters:
    - time: the initial time in seconds
    - gap: the gap to add in format "+mm:ss.msmsms" or "+ss.msmsms"

    Returns:
    - The total time in seconds
    """
    # Check if the gap string matches the provided format
    match = re.match(r"\+(([0-5]?[0-9]):)?([0-5]?[0-9])([.,][0-9]{1,3})?", gap)

    if match is None:
        raise ValueError(f"Invalid format for gap: {gap}")

    # Break the gap string down into minutes, seconds, and milliseconds
    groups = match.groups()
    minutes = int(groups[1]) if groups[1] else 0
    seconds = int(groups[2])
    milliseconds = float("0." + groups[3][1:]) if groups[3] else 0

    # Convert the gap into seconds
    gap_in_seconds = minutes * 60 + seconds + milliseconds

    # Add the gap to the initial time and return the result
    return time + gap_in_seconds


def time_to_seconds(time: str):
    parts = time.split(".")

    print(time)
    min, sec = map(int, parts[0].split(":"))

    ms = int(parts[1]) / 1000 if len(parts) > 1 else 0

    return min * 60 + sec + ms
