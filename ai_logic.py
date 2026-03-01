import random

def generate_question_paper(
    topics,
    paper_pattern,
    total_marks,
    difficulty,
    subject,
    total_sets=6
):
    question_sets = {}

    templates = {
        "easy": [
            "Define {}.",
            "What is {}?",
            "List the features of {}."
        ],
        "moderate": [
            "Explain {}.",
            "Write a short note on {}.",
            "Describe the working of {}."
        ],
        "hard": [
            "Analyze {}.",
            "Explain {} with examples.",
            "Compare {} with related concepts."
        ]
    }

    # Shuffle topics ONCE (global shuffle)
    random.shuffle(topics)

    # Calculate max questions needed per set
    if paper_pattern.isdigit():
        marks_per_q = int(paper_pattern)
        questions_per_set = total_marks // marks_per_q
    else:
        questions_per_set = 10  # safe default

    # Ensure enough topics
    required_topics = questions_per_set * total_sets
    extended_topics = topics * ((required_topics // len(topics)) + 1)

    pointer = 0  # global pointer (NO overlap)

    for s in range(1, total_sets + 1):
        questions = []
        remaining_marks = total_marks

        set_topics = extended_topics[pointer:pointer + questions_per_set]
        pointer += questions_per_set

        # -------- FIXED MARKS (5 / 10) --------
        if paper_pattern.isdigit():
            marks = int(paper_pattern)
            for topic in set_topics:
                template = random.choice(templates[difficulty])
                questions.append(f"{template.format(topic)} ({marks} Marks)")
                remaining_marks -= marks

        # -------- UNIVERSITY STANDARD --------
        elif paper_pattern == "STANDARD":
            structure = [(2, "easy"), (6, "moderate"), (10, "hard")]
            topic_index = 0

            for marks, level in structure:
                while remaining_marks >= marks and topic_index < len(set_topics):
                    template = random.choice(templates[level])
                    questions.append(
                        f"{template.format(set_topics[topic_index])} ({marks} Marks)"
                    )
                    remaining_marks -= marks
                    topic_index += 1

        # -------- CUSTOM --------
        elif paper_pattern == "CUSTOM":
            topic_index = 0
            while remaining_marks > 0 and topic_index < len(set_topics):
                marks = random.choice([2, 5, 10])
                if marks > remaining_marks:
                    continue
                level = random.choice(["easy", "moderate", "hard"])
                template = random.choice(templates[level])
                questions.append(
                    f"{template.format(set_topics[topic_index])} ({marks} Marks)"
                )
                remaining_marks -= marks
                topic_index += 1

        random.shuffle(questions)

        question_sets[f"Set {s}"] = {
            "subject": subject,
            "total_marks": total_marks,
            "difficulty": difficulty.capitalize(),
            "paper_pattern": paper_pattern,
            "questions": questions
        }

    return question_sets
