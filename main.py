import json
import math
import os
import random
import datetime

from cohort import Cohort
from course import Course
from exam_result import ExamResult
from llm_client import LLMClient
from newsletter import Newsletter
from school import School
from student import Student


# ── helpers ──────────────────────────────────────────────────────────────────

def ask_or_generate(question, prompt, llm, auto=False):
    if not auto:
        print(f"\n{question}")
        user_input = input("Type your answer or press Enter to let AI decide: ")
        if user_input.strip():
            return user_input
    print("Asking AI...")
    return llm.generate(prompt)


def parse_json_response(response):
    """Strip markdown wrappers, fix None→null, return parsed JSON or None."""
    response = response.strip()
    response = response.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    response = response.replace(": None", ": null").replace(":None", ":null")
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            return json.loads(response + "]")
        except json.JSONDecodeError:
            return None


def get_int(prompt_text):
    while True:
        try:
            return int(input(prompt_text))
        except ValueError:
            print("Please enter a number.")


# ── student generation ────────────────────────────────────────────────────────

def generate_students(school, llm, count, auto):
    students = []
    batches = math.ceil(count / 10)

    if not auto:
        print(f"\nYou need {count} student records — names, pronouns, email, allergies, next-of-kin.")
        print(f"All {count} of them. Press Enter to let AI handle this while you sit down.")
        choice = input("Or start typing your first JSON batch: ").strip()
        if choice:
            data = parse_json_response(choice)
            if data:
                for s in data:
                    student = Student(s["first_name"], s["last_name"], s["email"], s["pronouns"])
                    student.allergies = s.get("allergies")
                    student.next_of_kin = s.get("next_of_kin")
                    students.append(student)
            return students

    for i in range(batches):
        prompt = "Generate 10 fictional students as a JSON array. "
        prompt += "Each student needs: first_name, last_name, pronouns, email, allergies, next_of_kin. "
        prompt += "Use realistic diverse names from different cultures. "
        prompt += f"Use {school.name.lower().replace(' ', '')}@school.com as email domain. "
        prompt += "For allergies use null if no allergy. "
        prompt += "Reply with ONLY the JSON array, no explanation, no markdown, no backticks."

        response = llm.generate(prompt)
        data = parse_json_response(response)

        if data:
            for s in data:
                student = Student(s["first_name"], s["last_name"], s["email"], s["pronouns"])
                student.allergies = s.get("allergies")
                student.next_of_kin = s.get("next_of_kin")
                students.append(student)
            print(f"  Batch {i+1}/{batches} — {len(students)} students so far")
        else:
            print(f"  Warning: could not parse batch {i+1}, skipping")

    return students


# ── newsletter ────────────────────────────────────────────────────────────────

def generate_weekly_newsletter(school, week, date, graduates, llm):
    active = [s for s in school.students if not s.dropped_out and not s.graduated]
    dropouts = [s for s in school.students if s.dropped_out]
    enrolment = "\n".join(f"  {c.subject}: {len(c.enrolled_students)} students" for c in school.courses)

    prompt = f"""Write a weekly school newsletter using EXACTLY this structure. Fill in each section.

WEEKLY NEWSLETTER — {school.name} — Week {week} — {date}
{'═' * 55}

AT A GLANCE
  Active students:  {len(active)}
  Graduates:        {len(graduates)}
  Dropouts:         {len(dropouts)}
  Cohorts:          {len(school.cohorts)}

COURSE ENROLMENT
{enrolment}

THIS WEEK
  [Write 2-3 sentences summarising the week at the school. Be factual and slightly formal.]

MESSAGE FROM THE PRINCIPAL
  [Write 2-3 sentences. Upbeat but honest tone. Reference the numbers above.]

NEXT WEEK
  [Write 1-2 sentences looking ahead.]

{'─' * 55}
"""
    return llm.generate(prompt)


def save_weekly_newsletter(content, week):
    os.makedirs("weekly_newsletters", exist_ok=True)
    with open(f"weekly_newsletters/week_{week:03d}.txt", "w") as f:
        f.write(content)
    print(f"  Saved: weekly_newsletters/week_{week:03d}.txt")


def generate_monthly_newsletter(school, date, graduates, llm):
    active = [s for s in school.students if not s.dropped_out and not s.graduated]
    dropouts = [s for s in school.students if s.dropped_out]
    enrolment = "\n".join(f"  {c.subject}: {len(c.enrolled_students)} students" for c in school.courses)

    prompt = f"""Write a monthly school newsletter using EXACTLY this structure.

MONTHLY NEWSLETTER — {school.name} — {date.strftime('%B %Y')}
{'═' * 55}

MONTH IN NUMBERS
  Active students:  {len(active)}
  Graduates:        {len(graduates)}
  Dropouts:         {len(dropouts)}
  Cohorts:          {len(school.cohorts)}
  School capacity:  {school.seats} seats

COURSE ENROLMENT
{enrolment}

MONTHLY SUMMARY
  [Write 3-4 sentences summarising the month. Reference the numbers above.]

GRADUATE SPOTLIGHT
  [Write 2 sentences celebrating any graduates this month, or note if there were none.]

LOOKING AHEAD
  [Write 2-3 sentences about plans and expectations for next month.]

{'─' * 55}
"""
    return llm.generate(prompt)


def save_monthly_newsletter(content, date):
    os.makedirs("monthly_newsletters", exist_ok=True)
    filename = f"monthly_newsletters/{date.strftime('%Y_%m_%b')}_Newsletter.txt"
    with open(filename, "w") as f:
        f.write(content)
    print(f"  Saved: {filename}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("Welcome to School Simulator!")
    print("─" * 40)

    # SEATS
    seats = get_int("\nCongratulations! You've secured premises. How many seats does your school have? ")

    # OLLAMA
    print("\nTo help get your school off the ground, do you have a local AI you can lean on?")
    host = input("  Ollama address [localhost:11434]: ").strip() or "localhost:11434"
    model = input("  Model (mistral, llama3.2, phi3, gemma2:2b) [mistral]: ").strip() or "mistral"
    llm = LLMClient(host, model)
    print(f"  Connected to {model} at {host}")

    # SUBJECT
    subject = ask_or_generate(
        "You're pitching to investors and officials. What are you telling them you teach?",
        "Invent a specific and credible field of study for a school. Reply with just the subject, nothing else.",
        llm
    )
    print(f"  Subject: {subject}")

    # SCHOOL STRUCTURE
    num_courses = get_int("\nHow many courses will your school offer? ")
    courses_to_graduate = get_int("How many of those courses must a student complete to graduate? ")
    min_weeks = get_int("Minimum weeks to complete a course: ")
    max_weeks = get_int("Maximum weeks to complete a course: ")
    intake_interval = get_int("How often will you take a new intake? (weeks, e.g. 52 for annual): ")
    total_weeks = get_int("How many weeks should the simulation run? (e.g. 200 = ~5 years, 520 = 10 years): ")

    # MODE
    print("\nTime is money.")
    mode = input("Full auto (AI handles everything) or semi-auto (you choose at each step)? [auto/semi]: ").strip().lower()
    auto = (mode == "auto")
    if auto:
        print("Full auto engaged. Sit back.")

    # SCHOOL NAME
    school_name = ask_or_generate(
        "Every great school needs a name. What's yours?",
        "Invent a creative and serious name for a school. Reply with just the name, nothing else.",
        llm, auto
    )
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
            f"Write course material for '{course.subject}' in the field of {subject}. "
            f"Include a brief introduction and 3-4 key topics. Be informative.",
            llm, auto
        )
        print(f"  Material ready: {course.subject}")

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
            print(f"  Exam ready: {course.subject}")
        else:
            course.exam = []
            print(f"  Warning: could not parse exam for {course.subject}, skipping")

    # FIRST COHORT
    first_count = seats * 8
    students = generate_students(school, llm, first_count, auto if not auto else True)
    first_cohort = Cohort(1, 1, students)
    for s in students:
        s.cohort = first_cohort
        school.students.append(s)
        if school.courses:
            school.courses[0].enrolled_students.append(s)
    school.cohorts.append(first_cohort)
    print(f"\n{first_cohort} enrolled.")

    # ── SCHOOL PROFILE FILE ───────────────────────────────────────────────────

    with open("school_profile.txt", "w") as f:
        f.write(f"{school.name}\n")
        f.write(f"Subject: {school.description}\n")
        f.write(f"Seats: {school.seats} | Courses to graduate: {courses_to_graduate}\n")
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
    print("Saved: school_profile.txt")

    # ── SIMULATION ────────────────────────────────────────────────────────────

    print("\n" + "─" * 40)
    print(f"Simulation starting. {total_weeks} weeks. Good luck.")
    print("─" * 40)

    start_date = datetime.date(2026, 1, 5)
    graduates = []
    cohort_number = 1
    strike_weeks_remaining = 0

    for week in range(1, total_weeks + 1):
        week_date = start_date + datetime.timedelta(weeks=week - 1)

        # NEW INTAKE
        if week > 1 and (week - 1) % intake_interval == 0:
            cohort_number += 1
            print(f"\n--- Week {week} ({week_date}) — New intake ---")
            new_students = generate_students(school, llm, seats * 8, True)
            new_cohort = Cohort(cohort_number, week, new_students)

            if random.random() < 0.15:
                new_cohort.is_rough = True
                for s in new_students:
                    s.ability = round(random.uniform(0.1, 0.4), 2)
                print(f"  Cohort {cohort_number} looks rough...")

            for s in new_students:
                s.cohort = new_cohort
                school.students.append(s)
                if school.courses:
                    school.courses[0].enrolled_students.append(s)
            school.cohorts.append(new_cohort)
            print(f"  {new_cohort}")
        else:
            print(f"\n--- Week {week} ({week_date}) ---")

        # DISASTER: FUNDING CUT
        if random.random() < 0.01:
            lost = max(1, school.seats // 5)
            school.seats = max(1, school.seats - lost)
            print(f"  Funding cut! Lost {lost} seats. Now {school.seats} seats.")

        # DISASTER: TEACHER STRIKE
        if strike_weeks_remaining == 0 and random.random() < 0.005:
            strike_weeks_remaining = 3
            print(f"  Teacher strike! No exams for 3 weeks.")

        if strike_weeks_remaining > 0:
            strike_weeks_remaining -= 1
            for student in school.students:
                if student.dropped_out or student.graduated:
                    continue
                if random.random() < 0.08:
                    student.dropped_out = True
                    print(f"  {student} dropped out during the strike")
            save_weekly_newsletter(generate_weekly_newsletter(school, week, week_date, graduates, llm), week)
            continue

        # DROPOUT (~0.4%/week → ~55% over 200 weeks)
        for student in school.students:
            if student.dropped_out or student.graduated:
                continue
            if random.random() < 0.004:
                student.dropped_out = True
                print(f"  {student} dropped out")

        # WEEKLY EXAMS
        for student in school.students:
            if student.dropped_out or student.graduated:
                continue
            if student.course_index >= len(school.courses):
                continue
            course = school.courses[student.course_index]
            if not course.exam:
                continue

            passed = random.random() < student.ability
            subject_key = course.subject
            student.course_passes.setdefault(subject_key, 0)
            if passed:
                student.course_passes[subject_key] += 1

            if student.course_passes[subject_key] >= course.required_passes:
                next_index = student.course_index + 1
                if next_index >= courses_to_graduate:
                    student.graduated = True
                    graduates.append(student)
                    cohort_label = f"Cohort {student.cohort.number}" if student.cohort else "?"
                    print(f"  {student} GRADUATED! ({cohort_label})")
                elif next_index < len(school.courses):
                    course.enrolled_students.remove(student)
                    student.course_index = next_index
                    school.courses[next_index].enrolled_students.append(student)

        # NEWSLETTERS
        save_weekly_newsletter(generate_weekly_newsletter(school, week, week_date, graduates, llm), week)
        if week % 4 == 0:
            save_monthly_newsletter(generate_monthly_newsletter(school, week_date, graduates, llm), week_date)


    # ── FINAL SUMMARY ─────────────────────────────────────────────────────────

    print("\n" + "─" * 40)
    print(f"{total_weeks}-week simulation complete.")
    print(f"  Graduates:      {len(graduates)}")
    print(f"  Dropouts:       {len([s for s in school.students if s.dropped_out])}")
    print(f"  Still enrolled: {len([s for s in school.students if not s.dropped_out and not s.graduated])}")
    print(f"  Cohorts:        {len(school.cohorts)}")
    print("─" * 40)


if __name__ == "__main__":
    main()
