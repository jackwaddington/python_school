import json
import math

from student import Student


def generate_students(school, llm, count):
    students = []
    batches = math.ceil(count / 10)

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


def ask_or_default(prompt, default, auto):
    """In auto mode return default silently. In semi, show default in brackets."""
    if auto:
        return default
    val = input(f"{prompt} [{default}]: ").strip()
    return int(val) if val else default
