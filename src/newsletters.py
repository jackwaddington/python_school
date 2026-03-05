import os


def generate_weekly_newsletter(school, week, date, graduates, llm,
                                week_disasters=None, week_completions=0,
                                week_graduates_list=None, events=None):
    active = [s for s in school.students if not s.dropped_out and not s.graduated]
    dropouts = [s for s in school.students if s.dropped_out]
    enrolment = "\n".join(f"  {c.subject}: {len(c.enrolled_students)} students" for c in school.courses)

    # Ceremony countdown
    weeks_to_unit = 4  - (week % 4)  if week % 4  != 0 else 0
    weeks_to_grad = 12 - (week % 12) if week % 12 != 0 else 0
    unit_line = "THIS WEEK" if weeks_to_unit == 0 else f"in {weeks_to_unit} week(s)"
    grad_line  = "THIS WEEK" if weeks_to_grad  == 0 else f"in {weeks_to_grad} week(s)"

    # Disasters
    disaster_text = "\n".join(f"  {d}" for d in (week_disasters or [])) or "  None."

    # New graduates this week
    new_grads = week_graduates_list or []
    new_grad_names = ", ".join(str(s) for s in new_grads) if new_grads else "None this week."

    # Ceremony events this week
    ceremony_block = ""
    if events:
        lines = "\n".join(f"  {e.title}: {e.description}" for e in events)
        ceremony_block = f"\nCEREMONY THIS WEEK\n{lines}\n"

    # The data block — printed in the file regardless of what the AI writes
    data_block = f"""WEEKLY NEWSLETTER — {school.name} — Week {week} — {date}
{'═' * 55}

THE FACTS THIS WEEK
  Active students:      {len(active)}
  New graduates:        {len(new_grads)}
  Graduated (total):    {len(graduates)}
  Dropouts (total):     {len(dropouts)}
  Unit completions:     {week_completions}
  Cohorts running:      {len(school.cohorts)}

COURSE ENROLMENT
{enrolment}

EVENTS
{disaster_text}

NEW GRADUATES
  {new_grad_names}

UPCOMING CEREMONIES
  Unit Award Ceremony:  {unit_line}
  Graduation Ceremony:  {grad_line}
{ceremony_block}{'─' * 55}
"""

    prompt = f"""You are the principal of {school.name}, a school teaching {school.description}.
Write this week's staff newsletter in your own voice — direct, warm, occasionally wry.
You lived through this week. React to it honestly. Pleased by progress, troubled by losses,
shaken by disasters, moved by graduations. Do not invent students, events, or outcomes
beyond what is listed below.

{data_block}
Using only the facts above, write the newsletter below.

THIS WEEK
[2-3 sentences. Write as a person who was here this week, not a statistician.
Reference the numbers but react to them — don't just repeat them.]

MESSAGE FROM THE PRINCIPAL
[2-3 sentences spoken directly to staff and students. If something went wrong,
say so plainly. If something went right, name it. No generic encouragement.]

NEXT WEEK
[1-2 sentences. If a ceremony is coming, say something real about it.]
{'─' * 55}
"""
    narrative = llm.generate(prompt)
    return data_block + narrative


def save_weekly_newsletter(content, week, output_dir):
    folder = os.path.join(output_dir, "weekly_newsletters")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"week_{week:03d}.txt")
    with open(path, "w") as f:
        f.write(content)
    print(f"  Saved: {path}")


def generate_monthly_newsletter(school, date, graduates, llm):
    active = [s for s in school.students if not s.dropped_out and not s.graduated]
    dropouts = [s for s in school.students if s.dropped_out]
    enrolment = "\n".join(f"  {c.subject}: {len(c.enrolled_students)} students" for c in school.courses)

    # Events this month
    month_events = [e for e in school.events
                    if e.date.year == date.year and e.date.month == date.month]
    events_block = ""
    if month_events:
        lines = "\n".join(f"  {e.title} ({e.date}): {e.description}" for e in month_events)
        events_block = f"\nEVENTS THIS MONTH\n{lines}\n"

    data_block = f"""MONTHLY NEWSLETTER — {school.name} — {date.strftime('%B %Y')}
{'═' * 55}

THE MONTH IN NUMBERS
  Active students:  {len(active)}
  Graduates:        {len(graduates)}
  Dropouts:         {len(dropouts)}
  Cohorts:          {len(school.cohorts)}
  School capacity:  {school.seats} seats

COURSE ENROLMENT
{enrolment}
{events_block}{'─' * 55}
"""

    prompt = f"""You are the principal of {school.name}, a school teaching {school.description}.
Write this month's newsletter in your own voice. You have perspective on the whole month —
what went well, what didn't, who left, who succeeded. Be honest and specific.
Do not invent students, events, or outcomes beyond what is listed below.

{data_block}
Using only the facts above, write the newsletter below.

MONTHLY SUMMARY
[3-4 sentences. Reflect on the month honestly — the numbers, the mood, what this means
for the school. Reference the school's field if it's relevant.]

GRADUATE SPOTLIGHT
[2 sentences. If graduates are named in EVENTS THIS MONTH above, name them and say something
specific. If no graduates this month, say so plainly — don't pretend otherwise.]

LOOKING AHEAD
[2-3 sentences. What does next month need to be? Be direct about challenges or expectations.]

{'─' * 55}
"""
    narrative = llm.generate(prompt)
    return data_block + narrative


def save_monthly_newsletter(content, date, output_dir):
    folder = os.path.join(output_dir, "monthly_newsletters")
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{date.strftime('%Y_%m_%b')}_Newsletter.txt")
    with open(filename, "w") as f:
        f.write(content)
    print(f"  Saved: {filename}")
