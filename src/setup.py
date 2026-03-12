import configparser
import os
import random

from cohort import Cohort
from course import Course
from helpers import ask_or_generate, ask_or_default, parse_json_response, generate_students
from llm_client import LLMClient
from records import create_course_files, create_student_file
from school import School


def _load_conf():
    conf = configparser.ConfigParser()
    conf_path = os.path.join(os.path.dirname(__file__), "..", "school.conf")
    conf.read(conf_path)
    return conf


def run_setup(output_dir):
    conf = _load_conf()
    sim  = conf["simulation"] if "simulation" in conf else {}
    oll  = conf["ollama"]     if "ollama"     in conf else {}

    # PHASE 1 — IDENTITY + TECHNICAL
    city = input("\nWhat city is your school in? [Helsinki]: ").strip() or "Helsinki"

    print("\nLocal AI connection:")
    host = input(f"  Ollama address [{oll.get('host', 'localhost:11434')}]: ").strip() or oll.get("host", "localhost:11434")
    model = input(f"  Model [{oll.get('model', 'mistral')}]: ").strip() or oll.get("model", "mistral")
    llm = LLMClient(host, model)
    print(f"  Connected to {model} at {host}")

    subject = ask_or_generate(
        "What do you teach? (press Enter and the AI will decide)",
        "Invent a specific and credible field of study for a school. Reply with just the subject, nothing else.",
        llm
    )
    print(f"  Subject: {subject}")

    # PHASE 2 — MODE
    conf_mode = sim.get("mode", "").lower()
    if conf_mode == "auto":
        auto = True
        print("\nFull auto engaged. Sit back.")
    else:
        print("\nTime is money.")
        mode = input("Full auto or semi-auto? [auto/semi]: ").strip().lower()
        auto = mode != "semi"
        if auto:
            print("Full auto engaged. Sit back.")

    # PHASE 3 — STRUCTURE
    seats           = ask_or_default("Seats",                      int(sim.get("seats",           20)),  auto)
    num_courses     = ask_or_default("Number of courses",           int(sim.get("num_courses",      3)),  auto)
    courses_to_grad = ask_or_default("Courses needed to graduate", int(sim.get("courses_to_graduate", num_courses)), auto)
    min_weeks       = ask_or_default("Min weeks per course",        int(sim.get("min_weeks",         4)),  auto)
    max_weeks       = ask_or_default("Max weeks per course",        int(sim.get("max_weeks",        12)),  auto)
    intake_interval = ask_or_default("Intake interval (weeks)",    int(sim.get("intake_interval",  13)),  auto)
    total_weeks     = ask_or_default("Total weeks to simulate",    int(sim.get("total_weeks",     200)),  auto)

    if auto:
        print(f"\n  {seats} seats  |  {num_courses} courses  |  graduate after {courses_to_grad}"
              f"  |  {min_weeks}–{max_weeks} weeks/course  |  intake every {intake_interval} weeks"
              f"  |  {total_weeks} weeks total")

    # PHASE 4 — CONTENT
    default_name = f"{city} School of {subject}"
    if auto:
        school_name = default_name
    else:
        custom = input(f"\nSchool name [{default_name}]: ").strip()
        school_name = custom if custom else default_name
    print(f"\n{school_name} — established today.")

    school = School(school_name, subject, seats)

    # COURSES
    course_list_raw = ask_or_generate(
        f"What {num_courses} courses will you offer? (one per line — or press Enter and let AI name them)",
        f"Generate exactly {num_courses} course names for a school teaching {subject}. "
        f"One per line, no numbers, no bullet points, no prefixes. Nothing else.",
        llm, auto
    )
    course_names = [c.strip() for c in course_list_raw.strip().split("\n") if c.strip()][:num_courses]

    for name in course_names:
        course = Course(name, subject)
        course.required_passes = random.randint(min_weeks, max_weeks)
        school.courses.append(course)

    # COURSE MATERIAL
    for course in school.courses:
        course.material = ask_or_generate(
            f"Write the course material for '{course.subject}'. Cover key topics. (or press Enter)",
            f"Write actual study material for '{course.subject}' in the field of {subject}. "
            f"A student should be able to read this and pass an exam on it. "
            f"Explain 3-4 core concepts in full — include definitions, how they work, and a concrete example for each. "
            f"Do not write a course outline, syllabus, or list of topics. Write the content itself.",
            llm, auto
        )
        print(f"\n--- {course.subject} Material ---")
        print(course.material)
        print("─" * 40)

    # EXAM QUESTIONS
    for course in school.courses:
        raw = ask_or_generate(
            f"Write 2 MCQ exam questions for '{course.subject}' as a JSON array. (or press Enter)",
            f"Based on this course material:\n\n{course.material}\n\n"
            f"Generate 2 multiple choice questions. Reply with ONLY a JSON array, no explanation, no markdown, no backticks. "
            f'Format: [{{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A"}}]',
            llm, auto
        )
        course.exam = parse_json_response(raw)
        if course.exam:
            print(f"\n--- {course.subject} Exam ---")
            for i, q in enumerate(course.exam, 1):
                print(f"  Q{i}: {q.get('question', '?')}")
                for opt in q.get("options", []):
                    print(f"       {opt}")
            print("─" * 40)
        else:
            course.exam = []
            print(f"  Warning: could not parse exam for {course.subject}, skipping")
        create_course_files(course, output_dir)

    # FIRST COHORT
    intake_size = round(seats * 1.1)
    print(f"\nEnrolling first cohort ({intake_size} students)...")
    students = generate_students(school, llm, intake_size)
    first_cohort = Cohort(1, 1, students)
    for s in students:
        s.cohort = first_cohort
        school.students.append(s)
        if school.courses:
            school.courses[0].enrolled_students.append(s)
    school.cohorts.append(first_cohort)
    print(f"\n{first_cohort} enrolled.")
    print("Filing student records...")
    for s in students:
        create_student_file(s, output_dir)

    # SCHOOL PROFILE FILE
    with open(os.path.join(output_dir, "school_profile.txt"), "w") as f:
        f.write(f"{school.name}\n")
        f.write(f"Subject: {school.description}\n")
        f.write(f"Seats: {school.seats} | Courses to graduate: {courses_to_grad}\n")
        f.write(f"Intake every {intake_interval} weeks | Simulation: {total_weeks} weeks\n")
        f.write("═" * 55 + "\n\n")
        for course in school.courses:
            f.write(f"COURSE: {course.subject}\n")
            f.write(f"Required passes to complete: {course.required_passes} weeks\n")
            f.write("─" * 40 + "\n")
            f.write("MATERIAL:\n")
            f.write((course.material or "Not generated.") + "\n\n")
            f.write("EXAM QUESTIONS:\n")
            if course.exam:
                for i, q in enumerate(course.exam, 1):
                    f.write(f"  Q{i}: {q.get('question', '?')}\n")
                    for opt in q.get("options", []):
                        f.write(f"       {opt}\n")
                    f.write(f"  Answer: {q.get('answer', '?')}\n\n")
            else:
                f.write("  Not generated.\n\n")
            f.write("═" * 55 + "\n\n")
    print(f"Saved: {output_dir}/school_profile.txt")

    config = {
        "courses_to_graduate": courses_to_grad,
        "min_weeks": min_weeks,
        "max_weeks": max_weeks,
        "intake_interval": intake_interval,
        "total_weeks": total_weeks,
        "llm": llm,
        "auto": auto,
        "intake_size": intake_size,
        "output_dir": output_dir,
    }
    return school, config
