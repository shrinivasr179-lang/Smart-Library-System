
from backend.database.db import get_connection
from datetime import date


# UNIT 1: LOGICAL PROPOSITIONS

def check_eligibility(student_id, book_id):

    conn = get_connection()
    cursor = conn.cursor()

    # P: Student exists
    cursor.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    )
    student = cursor.fetchone()

    P = student is not None

    if not P:
        conn.close()
        return {
            "eligible": False,
            "message": "Student does not exist",
            "propositions": {"P": False}
        }

    # Q: Student has not reached borrowing limit
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM issue_records
        WHERE student_id = ? AND status = 'ISSUED'
    """, (student_id,))

    issued_count = cursor.fetchone()["total"]
    Q = issued_count < student["max_books"]

    # R: Book is available
    cursor.execute(
        "SELECT * FROM books WHERE book_id = ?",
        (book_id,)
    )
    book = cursor.fetchone()

    R = book is not None and book["available_copies"] > 0

    # S: Student has no overdue books
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM issue_records
        WHERE student_id = ?
        AND status = 'ISSUED'
        AND due_date < ?
    """, (student_id, date.today().isoformat()))

    overdue_count = cursor.fetchone()["total"]
    S = overdue_count == 0

    # Final logical expression:
    # E = P AND Q AND R AND S

    eligible = P and Q and R and S

    conn.close()

    reasons = []

    if not Q:
        reasons.append("Borrowing limit reached")

    if not R:
        reasons.append("Book unavailable or not found")

    if not S:
        reasons.append("Student has overdue books")

    return {
        "eligible": eligible,
        "message": (
            "Student is eligible to borrow this book"
            if eligible
            else ", ".join(reasons)
        ),
        "propositions": {
            "P_student_exists": P,
            "Q_within_limit": Q,
            "R_book_available": R,
            "S_no_overdue": S
        }
    }


# UNIT 1: TRUTH TABLE

def generate_truth_table():

    results = []

    for P in [False, True]:
        for Q in [False, True]:
            for R in [False, True]:
                for S in [False, True]:

                    E = P and Q and R and S

                    results.append({
                        "P": int(P),
                        "Q": int(Q),
                        "R": int(R),
                        "S": int(S),
                        "E": int(E)
                    })

    return results


# UNIT 1: LOGICAL IMPLICATION

def implication(p, q):
    return (not p) or q


# UNIT 1: LOGICAL EQUIVALENCE

def logical_equivalence(p, q):
    return p == q


if __name__ == "__main__":

    print("\nINTELLIGENT LIBRARY")
    print("LOGIC-BASED ELIGIBILITY SYSTEM")

    print("\nTRUTH TABLE")
    print("P Q R S | E")

    for row in generate_truth_table():
        print(
            row["P"],
            row["Q"],
            row["R"],
            row["S"],
            "|",
            row["E"]
        )

    print("\nLogical implication: P -> Q")
    print(implication(True, True))

    print("\nLogical equivalence: P <-> Q")
    print(logical_equivalence(True, True))
