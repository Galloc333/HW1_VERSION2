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

    for label in chosen_labels:
        score = round(random.uniform(0.05, 1.0), 2)
        matches.append({"name": label, "score": score})

    return matches
