# quiz.py

import pathlib
import random
import os
from string import ascii_lowercase
import sqlite3 as sql3
import py_compile 

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib



NUM_QUESTIONS_PER_QUIZ = 2
#QUESTIONS_PATH = pathlib.Path(__file__).parent / "questions.toml"
QUESTIONS_PATH = pathlib.Path("d:/storage/education/cloud/pythonquiz/source_code_final/questions.toml")
user = os.environ.get("USERNAME")
sqlconn = sql3.connect(user + ".db")
c = sqlconn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS cloudassessment (
    user text,
    question text,
    choice text,
    timestamp text
)
""")
sqlconn.commit()


def run_quiz():
    questions = prepare_questions(
        QUESTIONS_PATH, num_questions=NUM_QUESTIONS_PER_QUIZ
    )

    num_correct = 0
    for num, question in enumerate(questions, start=1):
        print(f"\nQuestion {num}:")
        num_correct += ask_question(question)
    sqlconn.close()
    print(f"\nThank you for taking the assessment. It will be submitted for evaluation. Have a nice day !!")


def prepare_questions(path, num_questions):
    topic_info = tomllib.loads(path.read_text())
    topics = {
        topic["label"]: topic["questions"] for topic in topic_info.values()
    }
    topic_label = get_answers(
        question="Which topic do you want to be quizzed about",
        alternatives=sorted(topics),
    )[0]

    questions = topics[topic_label]
    num_questions = min(num_questions, len(questions))
    return random.sample(questions, k=num_questions)


def ask_question(question):
    alternatives =  question["alternatives"]
    ordered_alternatives = random.sample(alternatives, k=len(alternatives))

    answers = get_answers(
        question=question["question"],
        alternatives=ordered_alternatives,
        num_choices=1,
        hint=question.get("hint"),
    )
    qn = question["question"]
    insertstr = "INSERT OR REPLACE INTO cloudassessment (user, question ,choice, timestamp) VALUES('" + user + "','" + qn.replace("'","''") + "','" + ''.join(answers)  + "',STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))"
    print(insertstr)
    c.execute(insertstr)
    sqlconn.commit()
    c.execute("select * from cloudassessment")
    print(c.fetchall())
    if "explanation" in question:
        print(f"\nEXPLANATION:\n{question['explanation']}")

    return True


def get_answers(question, alternatives, num_choices=1, hint=None):
    print(f"{question}?")
    labeled_alternatives = dict(zip(ascii_lowercase, alternatives))
    if hint:
        labeled_alternatives["?"] = "Hint"

    for label, alternative in labeled_alternatives.items():
        print(f"  {label}) {alternative}")

    while True:
        plural_s = "" if num_choices == 1 else f"s (choose {num_choices})"
        answer = input(f"\nChoice{plural_s}? ")
        answers = set(answer.replace(",", " ").split())

        # Handle hints
        if hint and "?" in answers:
            print(f"\nHINT: {hint}")
            continue

        # Handle invalid answers
        if len(answers) != num_choices:
            plural_s = "" if num_choices == 1 else "s, separated by comma"
            print(f"Please answer {num_choices} alternative{plural_s}")
            continue

        if any(
            (invalid := answer) not in labeled_alternatives
            for answer in answers
        ):
            print(
                f"{invalid!r} is not a valid choice. "  # noqa
                f"Please use {', '.join(labeled_alternatives)}"
            )
            continue

        return [labeled_alternatives[answer] for answer in answers]


if __name__ == "__main__":
    run_quiz()
