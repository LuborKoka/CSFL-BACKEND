import re


def gap_to_time(time: float, gap: str) -> float:
    """
    Adds a time gap to a given time.

    Parameters:
    - time: the initial time in seconds
    - gap: the gap to add in format "+mm:ss.msmsms" or "+ss.msmsms"

    Returns:
    - The total time in seconds
    """
    # Check if the gap string matches the provided format
    if gap.lower() == "dnf":
        return None

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

import re

def time_to_gap(leader_time: float | None, driver_time: float | None) -> str | None:
    """
    Converts the time difference between a leader time and a driver time into a gap string.

    Parameters:
    - leader_time: the leader's time in seconds
    - driver_time: the driver's time in seconds

    Returns:
    - A gap string in the format "+mm:ss.msmsms" or "+ss.msmsms"
      representing the time difference between leader and driver
    """
    if leader_time is None:
        return None

    if leader_time == driver_time:
        return seconds_to_time(leader_time)
    
    if driver_time is None:
        return 'DNF'

    time_diff = driver_time - leader_time

    minutes = int(time_diff // 60)
    seconds = int(time_diff % 60)
    milliseconds = int((time_diff - int(time_diff)) * 1000)

    gap_string = f"+{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    return gap_string




def time_to_seconds(time: str):
    parts = time.split(".")

    print(time)
    min, sec = map(int, parts[0].split(":"))

    ms = int(parts[1]) / 1000 if len(parts) > 1 else 0

    return min * 60 + sec + ms




def seconds_to_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    seconds_str = f"{int(remaining_seconds):02d}"

    milliseconds = int((remaining_seconds - int(remaining_seconds)) * 1000)
    milliseconds_str = f".{milliseconds:03d}" if milliseconds > 0 else ""

    time_string = f"{minutes}:{seconds_str}{milliseconds_str}"
    return time_string
