import json
import math

from course import Course
from event import Event
from exam import Exam
from llm_client import LLMClient
from newsletter import Newsletter
from school import School
from student import Student
from exam_result import ExamResult

def ask_or_generate(question, prompt, llm):
    print(f"\n{question}")
    user_input = input("Type your answer or press Enter to let AI decide: ")
    if user_input.strip() == "":
        print("Asking AI...")
        return llm.generate(prompt)
    return user_input




def main():
    print("Welcome to School Simulator!")
    print("-------------------------------")
    host = input("Enter your Ollama address [localhost:11434]: ").strip() or "localhost:11434"
    model = input("Enter your model name (e.g. mistral, llama3.2, phi3, gemma2:2b): ")
    llm = LLMClient(host, model)
    print(f"\nConnected to {model} at {host}")


# SCHOOL NAME
    school_name = ask_or_generate(
            "What is the nameof your school?",
            "Invent a creative and serious name for a school. Reply with just the name, no explination, nothing else.",
            llm)
    print(f"\nSchool name: {school_name}")


# SCHOOL DESCRIPTION
    school_description = ask_or_generate(
            "What does your school teach?",
            "Invent a subject or field of study for a school. Reply with just the subject, no explanation.",
            llm
            )
    print(f"Subject: {school_description}")


# SIZE - NUMBER OF SEATS
    while True:
        try:
            seats = int(input("\nHow many seats does your school have? "))
            break
        except ValueError:
            print("Please enter a number.")

# CREATE SCHOOL
    school = School(school_name, school_description, seats)
    print(f"\n{school}")


# CREATE COURSES
    course_list = ask_or_generate(
            "Please provide the list of courses your school teaches",
            f"Based on {school_description} provide EXACTLY 3 course names, one per line. No numbers, no 'Course 1:', no bullet points, no prefixes of any kind. Just the course name on each line. Nothing else.",
            llm
            )

    print(repr(course_list))

    courses = [c.strip() for c in course_list.strip().split("\n") if c.strip()]

    for course_name in courses:
        course = Course(course_name, school_description)
        school.courses.append(course)


# WRITE COURSE MATERIAL
    for course in school.courses:
        course.material = llm.generate(f"Write course material for a course called '{course.subject}'. Include a brief introduction and 3-4 topics covered in the course. Be informative and engaging.")
        print(f"Generated material for: {course.subject}")


# WRITE EXAM QUESTIONS

    for course in school.courses:
        prompt = "Based on this course material:\n\n"
        prompt += course.material
        prompt += "\n\nGenerate 2 multiple choice questions. Reply with ONLY a JSON array, no explanation, no markdown, no backticks."
        prompt += ' Format: [{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A"}]'
    
        response = llm.generate(prompt)
        response = response.strip()
        response = response.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        print(repr(response))

        try:
            course.exam = json.loads(response)
            print(f"Generated exam for: {course.subject}")
        except json.JSONDecodeError:
            try:
                course.exam = json.loads(response + "]")
                print(f"Generated exam for: {course.subject} (fixed truncation)")
            except json.JSONDecodeError:
                print(f"Warning: could not parse exam JSON for {course.subject}, skipping")
                course.exam = []

# GENERATE STUDENTS

    total_students = school.seats * 8
    batches = math.ceil(total_students / 10)

    for i in range(batches):
        prompt = "Generate 10 fictional students as a JSON array. Each student needs: first_name, last_name, pronouns, email, allergies, next_of_kin. "
        prompt += "Use realistic diverse names from different cultures. "
        prompt += f"Use {school.name.lower().replace(' ', '')}@school.com as email domain. "
        prompt += "For allergies use null if no allergy. "
        prompt += "Reply with ONLY the JSON array, no explanation, no markdown, no backticks."

        response = llm.generate(prompt)
        response = response.strip()
        response = response.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        response = response.replace(": None", ": null").replace(":None", ":null")

        print(repr(response))

        try:
            students_data = json.loads(response)

            for s in students_data:
                student = Student(s["first_name"], s["last_name"], s["email"], s["pronouns"])
                student.allergies = s["allergies"]
                student.next_of_kin = s["next_of_kin"]
                school.students.append(student)

            print(f"Batch {i+1}/{batches} - {len(school.students)} students so far")
        except json.JSONDecodeError:
            print(f"Warning: Could not parse student batch {i+1}, skipping")



if __name__ == "__main__":
    main()

