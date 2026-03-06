# School Simulator

A terminal-based Python simulation of a school. A local LLM (Ollama) generates the content — courses, material, exams, students, newsletters. You provide the seed: a city, a subject, and a few parameters. The simulation runs itself.

Built as a learning project for OOP in Python, and a proof of concept that OOP can model surprisingly complex real-world logic.

This project is complete. It expresses what I set out to explore — OOP, local LLMs, and newsletter design — and I'm moving on to other things. The remaining headroom is prompt optimisation, which isn't where my interest lies right now.

---

## Motivation

I've delivered training courses professionally — the process was often the same:
a domain expert provides the subject, a writer turns it into material, a testing expert writes an exam *based on that material*.
This project explores how much of that process a local AI can assist with:

- **Subject** — you pitch it, or the AI invents one
- **Material** — you write it, or the AI drafts it (and you can review it on screen)
- **Exam** — the AI writes questions *from the material*, so they're grounded in what was taught
- **Simulation** — the AI populates the school and runs it

A second thread runs through this project: I've spent time making newsletters, and there's always an algorithm behind them. A principle I keep coming back to is borrowed from observability engineering — if you send engineers too many alerts, they start ignoring all of them. A newsletter that costs more to produce than it delivers in value isn't a newsletter, it's noise.

The approach here is to separate the two jobs cleanly: let the data tell you what happened (counts, sums, comparisons), then let the AI narrate it. The data comes first. The AI fills in the human voice around it.

And hereforth we have a newsletter. You can tell your team to start their weekend early - the King is in town and the newsletter is scheduled to be sent, based on a bunch of stuff they did on Monday and Tuesday.

---

## Setup

### 1. Install Ollama and pull a model

```bash
# Install Ollama (macOS)
brew install ollama

# Pull the recommended model (4.4GB)
ollama pull mistral

# Start the Ollama server
ollama serve
```

### 2. Clone and run

```bash
git clone https://github.com/jackwaddington/python_school.git
cd python_school

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install requests matplotlib pandas

python3 src/main.py
```

Other models (`llama3.2`, `phi3`, `gemma2:2b`) should work but are little tested. Ollama defaults to `localhost:11434`.

---

## How It Works

1. You answer a few setup questions (city, subject, Ollama connection)
2. You choose **auto** or **semi-auto** mode
3. Structural parameters use sensible defaults — override in semi-auto if you want
4. The AI generates courses, material, exams, and students
5. The simulation runs for however many weeks you set
6. A timestamped output folder is created with newsletters, student profiles, course materials, and CSVs

In **full auto**, the minimum input is: city, subject, and press Enter for everything else. And start your weekend early.

---

## Parameters

### Always asked

| Parameter | Default | Notes |
|---|---|---|
| City | Helsinki | Used in the school name |
| Subject | AI-generated | The field of study |
| Ollama host | localhost:11434 | |
| Ollama model | mistral | |

### Defaults in auto mode — asked in semi-auto

| Parameter | Default | What it controls |
|---|---|---|
| Seats | 20 | School capacity |
| Number of courses | 3 | Courses created |
| Courses to graduate | = num courses | Graduation threshold |
| Min weeks per course | 4 | Lower bound of course duration |
| Max weeks per course | 12 | Upper bound of course duration |
| Intake interval | 52 weeks | How often a new cohort arrives |
| Total weeks | 200 | Length of simulation (~4 years) |

### Hardcoded — fixed in the simulation engine

| Variable | Value | What it controls |
|---|---|---|
| `student.ability` | random 0.3–0.9 | Probability of passing each weekly exam |
| Rough cohort ability | random 0.1–0.4 | Ability range when a cohort is flagged as rough |
| Rough cohort chance | 15% per new intake | Probability each new cohort is a disaster |
| Base dropout rate | 0.4% per week | ~55% cumulative dropout over 200 weeks |
| Strike dropout spike | 8% per week | Dropout rate during a teacher strike |
| Funding cut rate | 1% per week | Chance of losing 20% of seats that week |
| Teacher strike rate | 0.5% per week | Chance of a 3-week exam blackout starting |
| Strike duration | 3 weeks | How long a strike lasts |
| Students per seat | ×1.1 | First cohort size |
| Batch size | 10 students | Students generated per LLM call |
| Simulation start date | 2026-01-05 | Calendar date for week 1 |

---

## Newsletters

Every week the simulation writes a newsletter to disk. Every 4 weeks, a monthly edition too.

The prompt is structured in two parts:

1. **Hard facts** — numbers, disasters, new graduates, ceremony countdowns — hardcoded into the prompt
2. **AI narrative** — 3 short sections written by the principal (This Week, Message from the Principal, Next Week)

The AI is given the principal's voice and told to react to the data, not just restate it.

---

## Output Files

Each run creates a timestamped folder:

```
YYYYMMDD_HHMM_CitySchoolOfSubject/
    school_profile.txt
    weekly_stats.csv
    students.csv
    courses/
        Course_Name/
            material.txt
            exam.txt
    students/
        cohort_01/
            First_Last/
                profile.txt
    weekly_newsletters/
        week_001.txt
        week_002.txt
        ...
    monthly_newsletters/
        2026_01_Jan_Newsletter.txt
        ...
```

Output folders are gitignored automatically.

---

## OOP Structure

| File | Class | Key attributes |
|---|---|---|
| `student.py` | `Student` | `ability`, `course_index`, `course_passes`, `graduated`, `dropped_out`, `cohort` |
| `course.py` | `Course` | `subject`, `field`, `material`, `exam`, `enrolled_students`, `required_passes` |
| `school.py` | `School` | `name`, `description`, `seats`, `students`, `courses`, `cohorts`, `events` |
| `cohort.py` | `Cohort` | `number`, `intake_week`, `students`, `is_rough` |
| `event.py` | `Event` | `date`, `title`, `description` |
| `llm_client.py` | `LLMClient` | `host`, `model`, `generate(prompt)` |
| `helpers.py` | — | `generate_students()`, `ask_or_generate()`, `ask_or_default()`, `parse_json_response()` |
| `setup.py` | — | `run_setup()` — school wizard, returns school + config |
| `simulation.py` | — | `run_simulation()` — weekly loop, events, newsletters |
| `newsletters.py` | — | `generate_weekly_newsletter()`, `generate_monthly_newsletter()` |
| `records.py` | — | `create_course_files()`, `create_student_file()` |
| `export.py` | — | `save_csv()`, `print_summary()` |
| `exam_runner.py` | — | `run_exam_for_user()` — interactive MCQ for the user |
