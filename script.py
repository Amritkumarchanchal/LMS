import datetime

import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = input("Please enter your auth token: ")
HEADERS = {"Content-Type": "application/json",
           "Authorization": "Bearer {}".format(TOKEN)
           }

def create_institution(name, description, is_active=True, parent=None):
    print(f"Creating institution: {name}")
    url = f"{BASE_URL}/v1/institution/institutions/"
    payload = {
        "name": name,
        "description": description,
        "is_active": is_active,
        "parent": parent
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def create_course(name, description, visibility, institutions):
    print(f"Creating course: {name}")
    url = f"{BASE_URL}/courses/"
    payload = {
        "name": name,
        "description": description,
        "visibility": visibility,
        "institutions": institutions
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def create_module(title, description, sequence, course_id):
    print(f"Creating module: {title}")
    url = f"{BASE_URL}/modules/"
    payload = {
        "title": title,
        "description": description,
        "sequence": sequence,
        "course": course_id
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def create_section(title, description, sequence, module_id):
    print(f"Creating section: {title}")
    url = f"{BASE_URL}/sections/"
    payload = {
        "title": title,
        "description": description,
        "sequence": sequence,
        "module": module_id
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def create_video(source, transcript, start_time, end_time, section_id, sequence):
    print(f"Creating video: {source}")
    url = f"{BASE_URL}/items/videos/"
    payload = {
        "source": source,
        "transcript": transcript,
        "start_time": start_time,
        "end_time": end_time,
        "section": section_id,
        "sequence": sequence
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def create_assessment(title, question_visibility_limit, time_limit, section_id, sequence):
    print(f"Creating assessment: {title}")
    url = f"{BASE_URL}/items/assessments/"
    payload = {
        "title": title,
        "question_visibility_limit": question_visibility_limit,
        "time_limit": time_limit,
        "section": section_id,
        "sequence": sequence
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def create_question(text, assessment_id, options, solution_option_index):
    print(f"Creating question: {text}")
    url = f"{BASE_URL}/v1/assessment/questions/"
    payload = {
        "text": text,
        "type": "MCQ",
        "marks": 1,
        "assessment": assessment_id,
        "options": options,
        "solution_option_index": solution_option_index
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def create_student(email, password, first_name, last_name, role):
    print(f"Creating student: {email}")
    url = f"{BASE_URL}/v1/auth/signup/"
    payload = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "role": role
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def create_course_instance(course_id, start_date, end_date):
    print(f"Creating course instance for course {course_id}")
    url = f"{BASE_URL}/course-instances/"
    payload = {
      "course_id": course_id,
      "start_date": start_date,
      "end_date": end_date
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def create_user_course_binding(user_id, course_id):
    print(f"Binding user {user_id} to course {course_id}")
    url = f"{BASE_URL}/v1/user/api/user-course/"
    payload = {
      "user": user_id,
      "course": course_id
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

# Main Workflow
try:
    institution_id = create_institution(f"IIT RPR {str(datetime.datetime.now())}", "We are a good institution")

    course_id = create_course(f"Discrete Mathematics 11 {str(datetime.datetime.now())}", "A course on the Rule of Sum and Rule of Product", "public", [1])

    module_id = create_module("Introduction to Counting", "Explaining fundamental combinatorics rules", 1, course_id)

    section_id = create_section("Sums and Products", "Learn the foundational rules of Sum and Product", 1, module_id)

    course_instance_id = create_course_instance(course_id, "2025-01-01", "2025-06-06")

    # for i in range(1, 16, 2):
    #     create_video("https://youtu.be/2XXXSL7hjnI?si=a0r4iQR_JglU8GV4", None, i*1, i*21, section_id, i)

    # assessment_ids = []
    # for i in range(2, 17, 2):
    #     assessment_id = create_assessment(f"Assessment {i//2}", 1, 90, section_id, i)
    #     assessment_ids.append(assessment_id)

    # questions = [
    #     {"text": "How many students are participating in at least one of these two clubs?",
    #      "options": [{"option_text": "18"}, {"option_text": "30"}, {"option_text": "12"}, {"option_text": "36"}],
    #      "solution_option_index": 1},
    #     {"text": "How many books can the person choose from?",
    #      "options": [{"option_text": "65"}, {"option_text": "25"}, {"option_text": "40"}, {"option_text": "50"}],
    #      "solution_option_index": 0},
    #     {"text": "How many outfit combinations can the person create?",
    #      "options": [{"option_text": "20"}, {"option_text": "9"}, {"option_text": "5"}, {"option_text": "25"}],
    #      "solution_option_index": 0},
    #     {"text": "How many different travel routes can the traveler choose?",
    #      "options": [{"option_text": "6"}, {"option_text": "5"}, {"option_text": "3"}, {"option_text": "9"}],
    #      "solution_option_index": 0},
    #     {"text": "How many different options do students have to participate in the festival?",
    #      "options": [{"option_text": "9"}, {"option_text": "7"}, {"option_text": "11"}, {"option_text": "14"}],
    #      "solution_option_index": 2},
    #     {"text": "How many meal combinations are available if customers can choose either breakfast or lunch?",
    #      "options": [{"option_text": "18"}, {"option_text": "22"}, {"option_text": "14"}, {"option_text": "26"}],
    #      "solution_option_index": 3},
    #     {"text": "How many different purchase combinations are possible?",
    #      "options": [{"option_text": "35"}, {"option_text": "47"}, {"option_text": "51"}, {"option_text": "57"}],
    #      "solution_option_index": 2},
    #     {"text": "How many total travel options does the traveler have?",
    #      "options": [{"option_text": "10"}, {"option_text": "12"}, {"option_text": "14"}, {"option_text": "18"}],
    #      "solution_option_index": 3}
    # ]

    # for assessment_id, question in zip(assessment_ids, questions):
    #     create_question(question["text"], assessment_id, question["options"], question["solution_option_index"])

    # for i in range(4):
    #     student_id = create_student(f"{str(datetime.datetime.now().time().second)}student{i}@gmail.com", f"student{i}", f"Student{i}", "mylastname", "student")
    #     create_user_course_binding(student_id, course_instance_id)

    print("Setup completed successfully!")
except Exception as e:
    print(f"An error occurred: {e}")