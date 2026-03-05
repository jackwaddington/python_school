import csv
import os


def save_csv(school, graduates, weekly_stats, output_dir):
    # Weekly stats
    if weekly_stats:
        path = os.path.join(output_dir, "weekly_stats.csv")
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=weekly_stats[0].keys())
            writer.writeheader()
            writer.writerows(weekly_stats)
        print(f"Saved: {path}")

    # Student records
    path = os.path.join(output_dir, "students.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "pronouns", "email", "cohort", "ability",
                         "graduated", "dropped_out", "courses_completed",
                         "has_allergy"])
        for s in school.students:
            writer.writerow([
                str(s),
                s.pronouns,
                s.email,
                s.cohort.number if s.cohort else 0,
                s.ability,
                s.graduated,
                s.dropped_out,
                s.course_index,
                bool(s.allergies),
            ])
    print(f"Saved: {path}")


def print_summary(school, graduates, total_weeks, elapsed_seconds=None):
    print("\n" + "─" * 40)
    print(f"{total_weeks}-week simulation complete.")
    print(f"  Graduates:      {len(graduates)}")
    print(f"  Dropouts:       {len([s for s in school.students if s.dropped_out])}")
    print(f"  Still enrolled: {len([s for s in school.students if not s.dropped_out and not s.graduated])}")
    print(f"  Cohorts:        {len(school.cohorts)}")
    if elapsed_seconds is not None:
        mins = max(1, round(elapsed_seconds / 60))
        print(f"  Run time:       {mins} min")
    print("─" * 40)
