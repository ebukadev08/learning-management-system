"""
Auto-grading logic, separated from routes so it can be tested on its own.

Each question type is compared differently:
 - mcq: exact match against the correct option string (case-insensitive,
   trimmed, so " Paris " still matches "Paris")
 - true_false: normalised to "true"/"false" so "True", "TRUE", "true" all work
 - fill_blank: case-insensitive trimmed match. This is deliberately
   forgiving - a stricter version could allow multiple accepted answers
   separated by a delimiter, which is a good later upgrade.
"""

from app.models.quiz_question import QuestionType

def _normalise(text: str) -> str:
    return (text or "").strip().lower()


def is_answer_correct(question, submitted_answer: str) -> bool:
    submitted = _normalise(submitted_answer)
    correct = _normalise(question.correct_answer)

    if question.question_type == QuestionType.true_false:
        # Accept "true"/"false", "t"/"f", "yes"/"no"
        truthy = {"true", "t", "yes", "1"}
        falsy = {"false", "f", "no", "0"}

        def to_bool(value: str):
            if value in truthy:
                return True
            if value in falsy:
                return False
            return None

        return to_bool(submitted) is not None and to_bool(submitted) == to_bool(correct)

    # mcq and fill_blank both use normalised exact match
    return submitted == correct


def calculate_score(correct_count: int, total_questions: int) -> int:
    """Returns a 0-100 percentage, rounded to the nearest whole number."""
    if total_questions == 0:
        return 0
    return round((correct_count / total_questions) * 100)