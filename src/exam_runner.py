def run_exam_for_user(school):
    print("\nThe simulation is complete. Would you like to sit one of the exams?")
    for i, c in enumerate(school.courses, 1):
        print(f"  {i}. {c.subject}")
    choice = input("Enter course number, or press Enter to skip: ").strip()
    if not choice:
        return

    try:
        course = school.courses[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    if not course.exam:
        print(f"No exam available for {course.subject}.")
        return

    print(f"\n=== Exam: {course.subject} ===")
    score = 0
    for i, q in enumerate(course.exam, 1):
        print(f"\nQ{i}: {q.get('question', '?')}")
        for opt in q.get("options", []):
            print(f"  {opt}")
        answer = input("Your answer (A/B/C/D): ").strip().upper()
        if answer == q.get("answer", "").upper():
            print("  Correct!")
            score += 1
        else:
            print(f"  Wrong. Answer was {q.get('answer', '?')}.")
    print(f"\nYou scored {score}/{len(course.exam)}.")
    print("─" * 40)
