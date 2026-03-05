import datetime
import random

from cohort import Cohort
from event import Event
from helpers import generate_students
from newsletters import generate_weekly_newsletter, save_weekly_newsletter
from newsletters import generate_monthly_newsletter, save_monthly_newsletter
from records import create_student_file


def run_simulation(school, config):
    courses_to_graduate = config["courses_to_graduate"]
    intake_interval = config["intake_interval"]
    total_weeks = config["total_weeks"]
    llm = config["llm"]
    intake_size = config["intake_size"]
    output_dir = config["output_dir"]

    print("\n" + "─" * 40)
    print(f"Simulation starting. {total_weeks} weeks. Good luck.")
    print("─" * 40)

    weekly_dropout_rate = 1 - (0.5 ** (1 / total_weeks))

    start_date = datetime.date(2026, 1, 5)
    graduates = []
    cohort_number = len(school.cohorts)
    strike_weeks_remaining = 0
    weekly_stats = []

    # Per-ceremony-period tracking
    unit_completions_period = []   # (student, course_name) — reset every 4 weeks
    graduates_period = []          # students — reset every 12 weeks

    for week in range(1, total_weeks + 1):
        week_date = start_date + datetime.timedelta(weeks=week - 1)

        # Per-week data for newsletter
        week_disasters = []
        week_completions = 0
        week_graduates_list = []

        # NEW INTAKE
        if week > 1 and (week - 1) % intake_interval == 0:
            cohort_number += 1
            print(f"\n--- Week {week} ({week_date}) — New intake ---")
            new_students = generate_students(school, llm, intake_size)
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
            for s in new_students:
                create_student_file(s, output_dir)
        else:
            print(f"\n--- Week {week} ({week_date}) ---")

        # DISASTER: FUNDING CUT
        if random.random() < 0.01:
            lost = max(1, school.seats // 5)
            school.seats = max(1, school.seats - lost)
            msg = f"Funding cut: lost {lost} seats (now {school.seats})"
            week_disasters.append(msg)
            print(f"  {msg}")

        # DISASTER: TEACHER STRIKE
        if strike_weeks_remaining == 0 and random.random() < 0.005:
            strike_weeks_remaining = 3
            msg = "Teacher strike began — no exams for 3 weeks"
            week_disasters.append(msg)
            print(f"  {msg}")

        if strike_weeks_remaining > 0:
            strike_weeks_remaining -= 1
            week_disasters.append(f"Strike ongoing ({strike_weeks_remaining} weeks remaining)")
            for student in school.students:
                if student.dropped_out or student.graduated:
                    continue
                if random.random() < 0.08:
                    student.dropped_out = True
                    print(f"  {student} dropped out during the strike")

            week_events = [e for e in school.events if e.date == week_date]
            save_weekly_newsletter(
                generate_weekly_newsletter(
                    school, week, week_date, graduates, llm,
                    week_disasters=week_disasters,
                    week_completions=0,
                    week_graduates_list=[],
                    events=week_events,
                ), week, output_dir
            )
            continue

        # DROPOUT
        for student in school.students:
            if student.dropped_out or student.graduated:
                continue
            if random.random() < weekly_dropout_rate:
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
                    graduates_period.append(student)
                    week_graduates_list.append(student)
                    cohort_label = f"Cohort {student.cohort.number}" if student.cohort else "?"
                    print(f"  {student} GRADUATED! ({cohort_label})")
                elif next_index < len(school.courses):
                    course.enrolled_students.remove(student)
                    student.course_index = next_index
                    school.courses[next_index].enrolled_students.append(student)
                    unit_completions_period.append((student, course.subject))
                    week_completions += 1

        # RECORD WEEKLY STATS
        active = [s for s in school.students if not s.dropped_out and not s.graduated]
        row = {
            "week": week,
            "date": week_date,
            "active": len(active),
            "graduates": len(graduates),
            "dropouts": len([s for s in school.students if s.dropped_out]),
            "cohorts": len(school.cohorts),
            "total_enrolled": len(school.students),
        }
        for c in school.courses:
            row[f"enrolled_{c.subject}"] = len(c.enrolled_students)
        weekly_stats.append(row)

        # UNIT AWARD CEREMONY — every 4 weeks
        if week % 4 == 0 and unit_completions_period:
            names = ", ".join(f"{s} ({c})" for s, c in unit_completions_period)
            desc = f"{len(unit_completions_period)} students received unit awards: {names}"
            event = Event(week_date, "Unit Award Ceremony", desc)
            school.events.append(event)
            print(f"  Ceremony: {len(unit_completions_period)} unit awards presented.")
            unit_completions_period = []

        # GRADUATION CEREMONY — every 12 weeks
        if week % 12 == 0 and graduates_period:
            names = ", ".join(str(s) for s in graduates_period)
            desc = f"{len(graduates_period)} students graduated: {names}"
            event = Event(week_date, "Graduation Ceremony", desc)
            school.events.append(event)
            print(f"  Ceremony: Graduation for {len(graduates_period)} students.")
            graduates_period = []

        # NEWSLETTERS
        week_events = [e for e in school.events if e.date == week_date]
        save_weekly_newsletter(
            generate_weekly_newsletter(
                school, week, week_date, graduates, llm,
                week_disasters=week_disasters,
                week_completions=week_completions,
                week_graduates_list=week_graduates_list,
                events=week_events,
            ), week, output_dir
        )
        if week % 4 == 0:
            save_monthly_newsletter(
                generate_monthly_newsletter(school, week_date, graduates, llm), week_date, output_dir
            )

    return graduates, weekly_stats
