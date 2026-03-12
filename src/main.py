import datetime
import os
import re
import time

from analysis import run_analysis
from exam_runner import run_exam_for_user
from export import save_csv, print_summary
from setup import run_setup
from simulation import run_simulation


def _safe_name(text):
    name = re.sub(r"[^\w]", "_", text)
    return re.sub(r"_+", "_", name).strip("_")


def main():
    print("""
You are on planet Earth.

A year has 365 days. A week has 7 days. A day has 24 hours.
To find the number of days in a month, count your knuckles.
Make an exception for February — and a modulo calculation.

We cannot change these things.

We can change:

  — what we teach
  — who we teach it to
  — how many seats are in the room
  — how long it takes to pass a course
  — how often a new cohort walks through the door

A local AI will help with the paperwork.
You will make the decisions that matter.

Let's build a school.
""")
    print("─" * 40)

    # Create a temporary output folder — renamed once we know the school name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = timestamp
    os.makedirs(output_dir, exist_ok=True)

    school, config = run_setup(output_dir)

    # Rename folder to include school name now that we know it
    named_dir = f"{timestamp}_{_safe_name(school.name)}"
    os.rename(output_dir, named_dir)
    config["output_dir"] = named_dir
    print(f"\nOutput folder: {named_dir}/")

    sim_start = time.time()
    graduates, weekly_stats = run_simulation(school, config)
    elapsed = time.time() - sim_start

    save_csv(school, graduates, weekly_stats, named_dir)
    print_summary(school, graduates, config["total_weeks"], elapsed)
    run_analysis(named_dir)

    run_exam_for_user(school)


if __name__ == "__main__":
    main()
