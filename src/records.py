import os
import re


def _safe_name(text):
    """Convert a name to a safe directory name."""
    return re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "_")


def create_course_files(course, output_dir):
    """Create a directory for a course with material.txt and exam.txt."""
    folder = os.path.join(output_dir, "courses", _safe_name(course.subject))
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, "material.txt"), "w") as f:
        f.write(f"COURSE: {course.subject}\n")
        f.write(f"Required passes to complete: {course.required_passes}\n")
        f.write("─" * 40 + "\n\n")
        f.write(course.material or "No material generated.")
        f.write("\n")

    with open(os.path.join(folder, "exam.txt"), "w") as f:
        f.write(f"EXAM: {course.subject}\n")
        f.write("─" * 40 + "\n\n")
        if course.exam:
            for i, q in enumerate(course.exam, 1):
                f.write(f"Q{i}: {q.get('question', '?')}\n")
                for opt in q.get("options", []):
                    f.write(f"  {opt}\n")
                f.write(f"Answer: {q.get('answer', '?')}\n\n")
        else:
            f.write("No exam generated.\n")

    print(f"  Filed: {output_dir}/courses/{_safe_name(course.subject)}/")


def create_student_file(student, output_dir):
    """Create a directory for a student with their profile."""
    cohort_num = student.cohort.number if student.cohort else 0
    cohort_folder = f"cohort_{cohort_num:02d}"
    student_folder = _safe_name(f"{student.first_name}_{student.last_name}")
    folder = os.path.join(output_dir, "students", cohort_folder, student_folder)
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, "profile.txt"), "w") as f:
        f.write(f"NAME:        {student.first_name} {student.last_name}\n")
        f.write(f"PRONOUNS:    {student.pronouns}\n")
        f.write(f"EMAIL:       {student.email}\n")
        f.write(f"COHORT:      {cohort_num}\n")
        f.write(f"ABILITY:     {student.ability}\n")
        f.write(f"ALLERGIES:   {student.allergies or 'None'}\n")
        f.write(f"NEXT OF KIN: {student.next_of_kin or 'Not listed'}\n")
