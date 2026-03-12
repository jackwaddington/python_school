"""
School Simulator — Post-simulation analysis.
Runs automatically at the end of main.py, or manually:

    cd <simulation_folder>
    python3 ../src/analysis.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def run_analysis(output_dir):
    weekly_path  = os.path.join(output_dir, "weekly_stats.csv")
    students_path = os.path.join(output_dir, "students.csv")

    if not os.path.exists(weekly_path) or not os.path.exists(students_path):
        print("Analysis skipped: CSV files not found.")
        return

    weekly   = pd.read_csv(weekly_path,   parse_dates=["date"])
    students = pd.read_csv(students_path)

    print("=" * 55)
    print("SCHOOL SIMULATION ANALYSIS")
    print("=" * 55)

    # ── Overall outcomes ──────────────────────────────────────────────────────

    total = len(students)
    grads = students["graduated"].sum()
    drops = students["dropped_out"].sum()
    still = total - grads - drops

    print(f"\nTotal students ever enrolled: {total}")
    print(f"  Graduated:      {grads:4d}  ({grads/total*100:.1f}%)")
    print(f"  Dropped out:    {drops:4d}  ({drops/total*100:.1f}%)")
    print(f"  Still enrolled: {still:4d}  ({still/total*100:.1f}%)")

    # ── Outcomes by cohort ────────────────────────────────────────────────────

    print("\nOutcomes by cohort:")
    cohort_summary = students.groupby("cohort").agg(
        total=("name", "count"),
        graduated=("graduated", "sum"),
        dropped_out=("dropped_out", "sum"),
        avg_ability=("ability", "mean"),
    ).reset_index()
    cohort_summary["grad_rate"]    = (cohort_summary["graduated"]   / cohort_summary["total"] * 100).round(1)
    cohort_summary["dropout_rate"] = (cohort_summary["dropped_out"] / cohort_summary["total"] * 100).round(1)
    print(cohort_summary[["cohort", "total", "graduated", "grad_rate", "dropped_out", "dropout_rate", "avg_ability"]].to_string(index=False))

    # ── Outcomes by pronoun group ─────────────────────────────────────────────

    print("\nOutcomes by pronouns:")
    pronoun_summary = students.groupby("pronouns").agg(
        total=("name", "count"),
        graduated=("graduated", "sum"),
        dropped_out=("dropped_out", "sum"),
        avg_ability=("ability", "mean"),
    ).reset_index()
    pronoun_summary["grad_rate"] = (pronoun_summary["graduated"] / pronoun_summary["total"] * 100).round(1)
    print(pronoun_summary[["pronouns", "total", "graduated", "grad_rate", "dropped_out", "avg_ability"]].to_string(index=False))

    # ── Allergy correlation ───────────────────────────────────────────────────

    print("\nAllergy vs outcomes:")
    allergy_summary = students.groupby("has_allergy").agg(
        total=("name", "count"),
        graduated=("graduated", "sum"),
        dropped_out=("dropped_out", "sum"),
    ).reset_index()
    allergy_summary["grad_rate"] = (allergy_summary["graduated"] / allergy_summary["total"] * 100).round(1)
    allergy_summary["has_allergy"] = allergy_summary["has_allergy"].map({True: "Has allergy", False: "No allergy"})
    print(allergy_summary[["has_allergy", "total", "graduated", "grad_rate", "dropped_out"]].to_string(index=False))

    # ── Ability distribution ──────────────────────────────────────────────────

    print("\nAbility quartile outcomes:")
    students["ability_band"] = pd.cut(students["ability"], bins=[0, 0.4, 0.6, 0.8, 1.0],
                                       labels=["Low (0-0.4)", "Mid (0.4-0.6)", "Good (0.6-0.8)", "High (0.8-1.0)"])
    ability_summary = students.groupby("ability_band", observed=True).agg(
        total=("name", "count"),
        graduated=("graduated", "sum"),
        dropped_out=("dropped_out", "sum"),
    ).reset_index()
    ability_summary["grad_rate"] = (ability_summary["graduated"] / ability_summary["total"] * 100).round(1)
    print(ability_summary.to_string(index=False))

    # ── Charts ────────────────────────────────────────────────────────────────

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("School Simulation Report", fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(weekly["date"], weekly["active"],    label="Active",    color="steelblue")
    ax.plot(weekly["date"], weekly["graduates"], label="Graduates", color="green")
    ax.plot(weekly["date"], weekly["dropouts"],  label="Dropouts",  color="tomato")
    ax.set_title("Student Populations Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Students")
    ax.legend()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(6))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    ax = axes[0, 1]
    ax.bar(cohort_summary["cohort"].astype(str), cohort_summary["grad_rate"], color="steelblue")
    ax.set_title("Graduation Rate by Cohort (%)")
    ax.set_xlabel("Cohort")
    ax.set_ylabel("Graduation Rate (%)")
    ax.set_ylim(0, 100)

    ax = axes[1, 0]
    ax.pie([grads, drops, still],
           labels=["Graduated", "Dropped out", "Still enrolled"],
           colors=["green", "tomato", "steelblue"],
           autopct="%1.1f%%", startangle=90)
    ax.set_title("Overall Outcome Breakdown")

    ax = axes[1, 1]
    ax.bar(ability_summary["ability_band"].astype(str), ability_summary["grad_rate"], color="steelblue")
    ax.set_title("Graduation Rate by Ability Band (%)")
    ax.set_xlabel("Ability Band")
    ax.set_ylabel("Graduation Rate (%)")
    ax.set_ylim(0, 100)
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")

    plt.tight_layout()
    png_path = os.path.join(output_dir, "simulation_report.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"\nSaved: {png_path}")
    print("=" * 55)


if __name__ == "__main__":
    # When run directly, look for CSVs in the current directory
    run_analysis(".")
