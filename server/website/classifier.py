import random

# You can expand this list
LABELS = [
    "cat", "dog", "carrot", "tomato", "lettuce", "airplane", "rabbit", "phone"
]

def classify_image(img):
    """
    Dummy classifier that randomly selects 2–3 labels with random scores.
    """
    num_matches = random.randint(2, 3)  # Return 2 or 3 matches

    chosen_labels = random.sample(LABELS, num_matches)
    matches = []
    # Generate random values that we'll normalize
    raw_scores = [random.uniform(0.05, 1.0) for _ in range(num_matches)]
    # Normalize scores so their sum is between 0 and 1
    # We'll use a random factor between 1 and the sum of raw scores to ensure sum is ≤ 1
    sum_raw = sum(raw_scores)
    divisor = random.uniform(sum_raw, max(sum_raw * 2, sum_raw + 0.1))  # Ensures sum < 1

    for i, label in enumerate(chosen_labels):
        # Normalize and round the score
        score = round(raw_scores[i] / divisor, 2)
        matches.append({"name": label, "score": score})

    return matches
