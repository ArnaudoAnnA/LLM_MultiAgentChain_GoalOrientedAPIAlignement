"""Named subsets of the ground-truth corpus and the helper that resolves a selection.

A selection is either the name of a set in SYSTEM_SETS or an explicit list of system
names (the "name" field of each ground-truth dictionary). Unknown names raise instead of
being skipped, so a typo cannot silently shrink an experiment.
"""
from groundtruth import ALL_GROUNDTRUTHS, GROUNDTRUTH_BY_NAME

# Systems used to iterate on improvements; every other system is held out for confirmation.
DEV_SYSTEMS = [
    "Genome Nexus",
    "Gestao Hospital",
    "London Ambulance Service",
    "SIA Project 25 26",
]

SYSTEM_SETS = {
    "all": [g["name"] for g in ALL_GROUNDTRUTHS],
    "dev": DEV_SYSTEMS,
    "holdout": [g["name"] for g in ALL_GROUNDTRUTHS if g["name"] not in DEV_SYSTEMS],
}


def resolve_systems(selection):
    """Return the ground-truth dictionaries for a set name or a list of system names."""
    if isinstance(selection, str):
        if selection not in SYSTEM_SETS:
            raise KeyError(f"Unknown system set '{selection}'. Available: {sorted(SYSTEM_SETS)}")
        names = SYSTEM_SETS[selection]
    else:
        names = list(selection)

    unknown = [n for n in names if n not in GROUNDTRUTH_BY_NAME]
    if unknown:
        raise KeyError(f"Unknown systems: {unknown}. Available: {sorted(GROUNDTRUTH_BY_NAME)}")
    duplicated = sorted({n for n in names if names.count(n) > 1})
    if duplicated:
        raise ValueError(f"Systems selected more than once: {duplicated}")
    if not names:
        raise ValueError("Empty system selection")

    return [GROUNDTRUTH_BY_NAME[n] for n in names]
