"""
StudySync -- Find a Study Spot (Ticket 3, Tinker 3B).
"""

import csv

NOISE_ORDER = {"quiet": 0, "moderate": 1, "loud": 2}


def load_study_spots(csv_path: str) -> list:
    """
    Load study spots from a CSV into a list of dicts, converting
    "distance_miles" to float and "seats_available" to int.
    """
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        spots = []
        for row in reader:
            row["distance_miles"] = float(row["distance_miles"])
            row["seats_available"] = int(row["seats_available"])
            spots.append(row)
    return spots


def score_study_spot(profile: dict, spot: dict) -> tuple:
    """
    Score one study spot against a student profile.

    profile example: {"max_noise": "moderate", "max_distance": 1.0, "min_seats": 4}

    Return (score, reasons) where reasons is a list of short strings
    explaining what contributed to the score, e.g. ["quiet enough", "close enough"].
    """
    score = 0.0
    reasons = []

    # Noise: weighted highest, since a too-loud spot is hard to study in.
    # Bonus of 0.5 per level quieter than the student's limit.
    quieter_by = NOISE_ORDER[profile["max_noise"]] - NOISE_ORDER[spot["noise_level"]]
    if quieter_by >= 0:
        score += 2.0 + 0.5 * quieter_by
        reasons.append("quieter than needed" if quieter_by > 0 else "quiet enough")
    else:
        score -= 2.0
        reasons.append("too noisy")

    # Distance: closer than the limit earns more.
    if spot["distance_miles"] <= profile["max_distance"]:
        score += 1.0 + (profile["max_distance"] - spot["distance_miles"])
        reasons.append("close enough")
    else:
        score -= 1.0
        reasons.append("too far")

    # Seats: 0.1 per extra seat, capped at 0.5.
    if spot["seats_available"] >= profile["min_seats"]:
        extra_seats = spot["seats_available"] - profile["min_seats"]
        score += 1.5 + min(0.1 * extra_seats, 0.5)
        reasons.append("enough seats")
    else:
        score -= 1.0
        reasons.append("not enough seats")

    # Scale so a perfect spot (quietest, 0 miles, 5+ extra seats) scores 5.0.
    max_score = (2.0 + 0.5 * NOISE_ORDER[profile["max_noise"]]) + (1.0 + profile["max_distance"]) + 2.0
    score = 5.0 * score / max_score

    return (score, reasons)


def rank_study_spots(profile: dict, spots: list, k: int = 3) -> list:
    """
    Score every study spot, then return the top k as (spot, score, reasons)
    tuples, sorted by score descending.
    """
    scored = []
    for spot in spots:
        score, reasons = score_study_spot(profile, spot)
        scored.append((spot, score, reasons))
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]


def format_results(ranked: list) -> None:
    """Print each ranked study spot with its score and reasons, one line each."""
    for i, (spot, score, reasons) in enumerate(ranked, start=1):
        print(f"{i}. {spot['name']} -- Score: {score:.1f} -- Because: {', '.join(reasons)}")


def render_study_spot_tab():
    import streamlit as st

    st.subheader("Find a Study Spot")
    max_noise = st.selectbox("Max noise level", ["quiet", "moderate", "loud"], index=1)
    max_distance = st.slider("Max distance (miles)", 0.0, 3.0, 1.0)
    min_seats = st.number_input("Minimum seats needed", min_value=1, value=4, step=1)

    if st.button("Find spots"):
        profile = {"max_noise": max_noise, "max_distance": max_distance, "min_seats": min_seats}
        try:
            spots = load_study_spots("data/study_spots.csv")
            ranked = rank_study_spots(profile, spots, k=3)
            for spot, score, reasons in ranked:
                st.write(f"**{spot['name']}** -- Score: {score:.1f} -- Because: {', '.join(reasons)}")
        except NotImplementedError:
            st.warning("🚧 Ranking isn't implemented yet -- that's Tinker 3B's ticket.")


if __name__ == "__main__":
    spots = load_study_spots("data/study_spots.csv")
    profile = {"max_noise": "moderate", "max_distance": 1.0, "min_seats": 4}
    ranked = rank_study_spots(profile, spots, k=3)
    format_results(ranked)
