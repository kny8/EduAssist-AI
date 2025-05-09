from sqlalchemy.orm import Session

from database.database import SessionLocal
from models import User, Subject, UserSubject, Week, Assignment, Video
import bcrypt

from models.lectures import Lecture

# Create a new database session
db: Session = SessionLocal()

# Sample student users with specific IDs
students = [
    {"id": 1, "email": "anshul@yopmail.com", "password": "password", "name": "Anshul", "role": "student"},

    {"id": 2, "email": "student2@example.com", "password": "password", "name": "Student Two"},
    {"id": 3, "email": "student3@example.com", "password": "password", "name": "Student Three"},
    {"id": 4, "email": "dhruv@yopmail.com", "password": "password", "name": "Dhruv", "role": "teacher"},
    {"id": 4, "email": "prathmesh@yopmail.com", "password": "password", "name": "Dhruv", "role": "admin"},
]

for student in students:
    # Hash the password before storing
    hashed_password = bcrypt.hashpw(student["password"].encode(), bcrypt.gensalt()).decode()

    # Check if user exists by ID
    existing_user = db.query(User).filter(User.id == student["id"]).first()

    if existing_user:
        existing_user.email = student["email"]
        existing_user.password = hashed_password
        existing_user.name = student["name"]
        existing_user.role = student.get("role", "student")
    else:
        new_user = User(
            id=student["id"],
            email=student["email"],
            password=hashed_password,
            name=student["name"],
            role="student"
        )
        db.add(new_user)

subjects = [
    {"id": 1, "name": "Software Engineering"},
    # {"id": 2, "name": "Data Structures"},
    # {"id": 3, "name": "Machine Learning"},
]

for subject in subjects:
    # Check if subject already exists by ID
    existing_subject = db.query(Subject).filter(Subject.id == subject["id"]).first()

    if existing_subject:
        existing_subject.name = subject["name"]
        print(f"🔄 Updated subject: {existing_subject.name}")
    else:
        new_subject = Subject(id=subject["id"], name=subject["name"])
        db.add(new_subject)
        print(f"Added new subject: {subject['name']}")
for student in students:
    for subject in subjects:
        existing_assignment = (
            db.query(UserSubject)
            .filter(UserSubject.user_id == student["id"], UserSubject.subject_id == subject["id"])
            .first()
        )

        if not existing_assignment:
            new_assignment = UserSubject(user_id=student["id"], subject_id=subject["id"])
            db.add(new_assignment)

week_data = [
    {"id": 1, "name": "Week 1"},
    {"id": 2, "name": "Week 2"},
    {"id": 3, "name": "Week 3"},
    {"id": 4, "name": "Week 4"},
    {"id": 5, "name": "Week 5"},
    {"id": 7, "name": "Week 7"},
    {"id": 8, "name": "Week 8"},
]

for week in week_data:
    existing_week = db.query(Week).filter(Week.id == week["id"]).first()
    if existing_week:
        existing_week.name = week["name"]
    else:
        db.add(Week(id=week["id"], name=week["name"]))

lecture_data = [
    # Week 1
    {"id": 1, "week_id": 1, "sequence_no": 1,
     "name": "1.1 Deconstructing the Software Development Process - Introduction", "type": "Video",
     "url": "https://www.youtube.com/watch?v=hKm_rh1RTJQ", "video_id": "hKm_rh1RTJQ"},
    {"id": 2, "week_id": 1, "sequence_no": 2, "name": "1.2 Thinking of Software in terms of Components",
     "type": "Video", "url": "https://www.youtube.com/watch?v=81BaOIrfvJA", "video_id": "81BaOIrfvJA"},
    {"id": 3, "week_id": 1, "sequence_no": 3, "name": "AQ1.2: Activity Questions 2 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ1.2", "type": "Ungraded"}},
    {"id": 4, "week_id": 1, "sequence_no": 4, "name": "1.3 Software Development Process - Requirement Specification",
     "type": "Video", "url": "https://www.youtube.com/watch?v=SU2CBhSFUUA", "video_id": "SU2CBhSFUUA"},
    {"id": 5, "week_id": 1, "sequence_no": 5, "name": "AQ1.3: Activity Questions 3 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ1.3", "type": "Ungraded"}},
    {"id": 6, "week_id": 1, "sequence_no": 6,
     "name": "1.4 Software Development Process - Software Design and Development", "type": "Video",
     "url": "https://www.youtube.com/watch?v=iNqfWUN_hrc", "video_id": "iNqfWUN_hrc"},
    {"id": 7, "week_id": 1, "sequence_no": 7, "name": "AQ1.4: Activity Questions 4 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ1.4", "type": "Ungraded"}},
    {"id": 8, "week_id": 1, "sequence_no": 8, "name": "1.5 Testing and Maintenance", "type": "Video",
     "url": "https://www.youtube.com/watch?v=3uokL_BdoiU", "video_id": "3uokL_BdoiU"},
    {"id": 9, "week_id": 1, "sequence_no": 9, "name": "AQ1.5: Activity Questions 5 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ1.5", "type": "Ungraded"}},
    {"id": 10, "week_id": 1, "sequence_no": 10,
     "name": "1.6 Software Development Models - Waterfall (Plan and Document) Model", "type": "Video",
     "url": "https://www.youtube.com/watch?v=938T0bC7ls0", "video_id": "938T0bC7ls0"},
    {"id": 11, "week_id": 1, "sequence_no": 11, "name": "AQ1.6: Activity Questions 6 - Not Graded",
     "type": "Assignment", "content": {"description": "Assignment AQ1.6", "type": "Ungraded"}},
    {"id": 12, "week_id": 1, "sequence_no": 12, "name": "1.7 Software Development - Agile", "type": "Video",
     "url": "https://www.youtube.com/watch?v=nQzRUGuEDXs", "video_id": "nQzRUGuEDXs"},
    {"id": 13, "week_id": 1, "sequence_no": 13, "name": "AQ1.7: Activity Questions 7 - Not Graded",
     "type": "Assignment", "content": {"description": "Assignment AQ1.7", "type": "Ungraded"}},
    {"id": 14, "week_id": 1, "sequence_no": 14, "name": "Graded Assignment 1", "type": "Assignment",
     "content": {"description": "Graded Assignment 1", "type": "Graded"}},

    # Week 2
    {"id": 15, "week_id": 2, "sequence_no": 1,
     "name": "L2.1: Software Requirements - Requirements Gathering and Analysis", "type": "Video",
     "url": "https://www.youtube.com/watch?v=6cjKDEoCvMc", "video_id": "6cjKDEoCvMc"},
    {"id": 16, "week_id": 2, "sequence_no": 2, "name": "AQ2.1: Activity Questions 1 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ2.1", "type": "Ungraded"}},
    {"id": 17, "week_id": 2, "sequence_no": 3, "name": "L2.2: Identifying Users and Requirements", "type": "Video",
     "url": "https://www.youtube.com/watch?v=L9-CUa0BlLk", "video_id": "L9-CUa0BlLk"},
    {"id": 18, "week_id": 2, "sequence_no": 4, "name": "AQ2.2: Activity Questions 2 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ2.2", "type": "Ungraded"}},
    {"id": 19, "week_id": 2, "sequence_no": 5, "name": "L2.3: Functional and Non-functional Requirements",
     "type": "Video", "url": "https://www.youtube.com/watch?v=CKGjkKXpCsw", "video_id": "CKGjkKXpCsw"},
    {"id": 20, "week_id": 2, "sequence_no": 6, "name": "AQ2.3: Activity Questions 3 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ2.3", "type": "Ungraded"}},
    {"id": 21, "week_id": 2, "sequence_no": 7, "name": "L2.4: Software Requirement Specification", "type": "Video",
     "url": "https://www.youtube.com/watch?v=Ml0HET0Va_c", "video_id": "Ml0HET0Va_c"},
    {"id": 22, "week_id": 2, "sequence_no": 8, "name": "AQ2.4: Activity Questions 4 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ2.4", "type": "Ungraded"}},
    {"id": 23, "week_id": 2, "sequence_no": 9, "name": "L2.5: Behaviour Driven Design - User Stories", "type": "Video",
     "url": "https://www.youtube.com/watch?v=_KH9dSFVYTs", "video_id": "_KH9dSFVYTs"},
    {"id": 24, "week_id": 2, "sequence_no": 10, "name": "AQ2.5: Activity Questions 5 - Not Graded",
     "type": "Assignment", "content": {"description": "Assignment AQ2.5", "type": "Ungraded"}},
    {"id": 25, "week_id": 2, "sequence_no": 11, "name": "Graded Assignment 2", "type": "Assignment",
     "content": {"description": "Graded Assignment 2", "type": "Graded"}},
    # Week 3
    {"id": 26, "week_id": 3, "sequence_no": 1,
     "name": "3.1 Software User Interfaces - Introduction to Interaction Design", "type": "Video",
     "url": "https://www.youtube.com/watch?v=BOCF3RefE54", "video_id": "BOCF3RefE54"},
    {"id": 27, "week_id": 3, "sequence_no": 2, "name": "3.2 Usability goals", "type": "Video",
     "url": "https://www.youtube.com/watch?v=I1s8WWUMGQs", "video_id": "I1s8WWUMGQs"},
    {"id": 28, "week_id": 3, "sequence_no": 3, "name": "AQ3.2: Activity Questions 2 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ3.2", "type": "Ungraded"}},
    {"id": 29, "week_id": 3, "sequence_no": 4, "name": "3.3 Prototyping Techniques", "type": "Video",
     "url": "https://www.youtube.com/watch?v=jQ_vO3xjFt0", "video_id": "jQ_vO3xjFt0"},
    {"id": 30, "week_id": 3, "sequence_no": 5, "name": "AQ3.3: Activity Questions 3 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ3.3", "type": "Ungraded"}},
    {"id": 31, "week_id": 3, "sequence_no": 6,
     "name": "3.4 Evaluation using Design Heuristics - Heuristics for Understanding", "type": "Video",
     "url": "https://www.youtube.com/watch?v=Z975GdR1l40", "video_id": "Z975GdR1l40"},
    {"id": 32, "week_id": 3, "sequence_no": 7, "name": "AQ3.4: Activity Questions 4 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ3.4", "type": "Ungraded"}},
    {"id": 33, "week_id": 3, "sequence_no": 8,
     "name": "3.5 Evaluation using Design Heuristics - Heuristics for Action", "type": "Video",
     "url": "https://www.youtube.com/watch?v=EWEuCseFVEI", "video_id": "EWEuCseFVEI"},
    {"id": 34, "week_id": 3, "sequence_no": 9, "name": "AQ3.5: Activity Questions 5 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ3.5", "type": "Ungraded"}},
    {"id": 35, "week_id": 3, "sequence_no": 10,
     "name": "3.6 Evaluation using Design Heuristics - Heuristics for Feedback", "type": "Video",
     "url": "https://www.youtube.com/watch?v=lq1kTWFG3Z0", "video_id": "lq1kTWFG3Z0"},
    {"id": 36, "week_id": 3, "sequence_no": 11, "name": "AQ3.6: Activity Questions 6 - Not Graded",
     "type": "Assignment",
     "content": {"description": "Assignment AQ3.6", "type": "Ungraded"}},
    {"id": 37, "week_id": 3, "sequence_no": 12, "name": "Graded Assignment 3", "type": "Assignment",
     "content": {"description": "Graded Assignment 3", "type": "Graded"}},

    # Week 4
    {"id": 38, "week_id": 4, "sequence_no": 1, "name": "4.1 Software Project Management - Project Management Overview",
     "type": "Video", "url": "https://www.youtube.com/watch?v=MXz_9ds6PJM", "video_id": "MXz_9ds6PJM"},
    {"id": 39, "week_id": 4, "sequence_no": 2, "name": "AQ4.1: Activity Questions 1 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ4.1", "type": "Ungraded"}},
    {"id": 40, "week_id": 4, "sequence_no": 3, "name": "4.2 Project Estimation Techniques", "type": "Video",
     "url": "https://www.youtube.com/watch?v=ziDmAaOrdkY", "video_id": "ziDmAaOrdkY"},
    {"id": 41, "week_id": 4, "sequence_no": 4, "name": "AQ4.2: Activity Questions 2 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 4", "type": "Graded"}},
    {"id": 42, "week_id": 4, "sequence_no": 5, "name": "4.3 Project Scheduling", "type": "Video",
     "url": "https://www.youtube.com/watch?v=WvgqTJjp-0E", "video_id": "WvgqTJjp-0E"},
    {"id": 43, "week_id": 4, "sequence_no": 6, "name": "AQ4.3: Activity Questions 3 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 4", "type": "Graded"}},
    {"id": 44, "week_id": 4, "sequence_no": 7, "name": "4.4 Risk Management", "type": "Video",
     "url": "https://www.youtube.com/watch?v=nJ6JaNXWP2o", "video_id": "nJ6JaNXWP2o"},
    {"id": 45, "week_id": 4, "sequence_no": 8, "name": "AQ4.4: Activity Questions 4 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 4", "type": "Graded"}},
    {"id": 46, "week_id": 4, "sequence_no": 9, "name": "4.5 Project Management in Agile", "type": "Video",
     "url": "https://www.youtube.com/watch?v=54t-QUr9h18", "video_id": "54t-QUr9h18"},
    {"id": 47, "week_id": 4, "sequence_no": 10, "name": "AQ4.5: Activity Questions 5 - Not Graded",
     "type": "Assignment",
     "content": {"description": "Graded Assignment 4", "type": "Graded"}},
    {"id": 48, "week_id": 4, "sequence_no": 11, "name": "4.6 Pivotal Tracker Tutorial", "type": "Video",
     "url": "https://www.youtube.com/watch?v=3Yje9oOOaFc", "video_id": "3Yje9oOOaFc"},
    {"id": 49, "week_id": 4, "sequence_no": 12, "name": "Graded Assignment 4",
     "type": "Assignment",
     "content": {"description": "Graded Assignment 4", "type": "Graded"}},
    # Week 5
    {"id": 50, "week_id": 5, "sequence_no": 1, "name": "5.1 Software Design", "type": "Video",
     "url": "https://www.youtube.com/watch?v=U7QdwI5M2rQ", "video_id": "U7QdwI5M2rQ"},
    {"id": 51, "week_id": 5, "sequence_no": 2, "name": "AQ5.1: Activity Questions 1 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ5.1", "type": "Ungraded"}},
    {"id": 52, "week_id": 5, "sequence_no": 3, "name": "5.2 Design Modularity", "type": "Video",
     "url": "https://www.youtube.com/watch?v=8XosX-3061s", "video_id": "8XosX-3061s"},
    {"id": 53, "week_id": 5, "sequence_no": 4, "name": "AQ5.2: Activity Questions 2 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 5", "type": "Graded"}},
    {"id": 54, "week_id": 5, "sequence_no": 5, "name": "5.3 Object Oriented Design: Basic Concepts", "type": "Video",
     "url": "https://www.youtube.com/watch?v=iWnjlZItfeg", "video_id": "iWnjlZItfeg"},
    {"id": 55, "week_id": 5, "sequence_no": 6, "name": "AQ5.3: Activity Questions 3 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 5", "type": "Graded"}},
    {"id": 56, "week_id": 5, "sequence_no": 7, "name": "5.4 Unified Modelling Language Diagrams", "type": "Video",
     "url": "https://www.youtube.com/watch?v=UCK8VMTfyQw", "video_id": "UCK8VMTfyQw"},
    {"id": 57, "week_id": 5, "sequence_no": 8, "name": "AQ5.4: Activity Questions 4 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 5", "type": "Graded"}},
    {"id": 58, "week_id": 5, "sequence_no": 9,
     "name": "5.5 VeriSIM: A Learning Environment for Comprehending Software Designs", "type": "Video",
     "url": "https://www.youtube.com/watch?v=FkI4bAGfUSw", "video_id": "FkI4bAGfUSw"},
    {"id": 59, "week_id": 5, "sequence_no": 10, "name": "Graded Assignment 5", "type": "Assignment",
     "content": {"description": "Graded Assignment 5", "type": "Graded"}},
    # Week 7
    {"id": 60, "week_id": 7, "sequence_no": 1, "name": "L7.1 Software Development", "type": "Video",
     "url": "https://www.youtube.com/watch?v=9mprXqmI-SQ", "video_id": "9mprXqmI-SQ"},
    {"id": 61, "week_id": 7, "sequence_no": 2, "name": "L7.2 Rest APIs", "type": "Video",
     "url": "https://www.youtube.com/watch?v=eR9jf-0tS78", "video_id": "eR9jf-0tS78"},
    {"id": 62, "week_id": 7, "sequence_no": 3, "name": "L7.3 Version Control Systems", "type": "Video",
     "url": "https://www.youtube.com/watch?v=64s1MyvjrG0", "video_id": "64s1MyvjrG0"},
    {"id": 63, "week_id": 7, "sequence_no": 4, "name": "L7.4 Issue tracking and code review", "type": "Video",
     "url": "https://www.youtube.com/watch?v=uG7-puhBGxw", "video_id": "uG7-puhBGxw"},
    {"id": 64, "week_id": 7, "sequence_no": 5, "name": "AQ7.1+7.2+7.3+7.4: Activity Questions 1 - Not Graded",
     "type": "Assignment",
     "content": {"description": "Graded Assignment 7", "type": "Graded"}},
    {"id": 65, "week_id": 7, "sequence_no": 6, "name": "L7.5 Debugging", "type": "Video",
     "url": "https://www.youtube.com/watch?v=XUGbMazlZUk", "video_id": "XUGbMazlZUk"},
    {"id": 66, "week_id": 7, "sequence_no": 7, "name": "AQ7.5: Activity Questions 4 - Not Graded",
     "type": "Assignment",
     "content": {"description": "Graded Assignment 7", "type": "Graded"}},
    {"id": 67, "week_id": 7, "sequence_no": 8, "name": "L7.6 Software Metrics", "type": "Video",
     "url": "https://www.youtube.com/watch?v=OTEVcP89pFk", "video_id": "OTEVcP89pFk"},
    {"id": 68, "week_id": 7, "sequence_no": 9, "name": "L7.6 Software Metrics",
     "type": "Assignment",
     "content": {"description": "Graded Assignment 7", "type": "Graded"}},
    {"id": 69, "week_id": 7, "sequence_no": 10, "name": "L7.7 Writing Clean Code", "type": "Video",
     "url": "https://www.youtube.com/watch?v=PA1cKpKQ5DA", "video_id": "hKm_rh1RTJQ"},
    {"id": 70, "week_id": 7, "sequence_no": 11, "name": "AQ7.7: Activity Questions 6 - Not Graded",
     "type": "Assignment",
     "content": {"description": "Graded Assignment 7", "type": "Graded"}},
    {"id": 71, "week_id": 7, "sequence_no": 12, "name": "Graded Assignment 7", "type": "Assignment",
     "content": {"description": "Graded Assignment 7", "type": "Graded"}},

    # Week 8
    {"id": 72, "week_id": 8, "sequence_no": 1, "name": "L8.1 Software Architecture", "type": "Video",
     "url": "https://www.youtube.com/watch?v=0JEXPcS_L_w", "video_id": "0JEXPcS_L_w"},
    {"id": 73, "week_id": 8, "sequence_no": 2, "name": "AQ8.1: Activity Questions 1 - Not Graded", "type": "Assignment",
     "content": {"description": "Assignment AQ8.1", "type": "Ungraded"}},
    {"id": 74, "week_id": 8, "sequence_no": 3, "name": "L8.2 SOLID - Principles I", "type": "Video",
     "url": "https://www.youtube.com/watch?v=oPed712RsOY", "video_id": "oPed712RsOY"},
    {"id": 75, "week_id": 8, "sequence_no": 4, "name": "AQ8.2: Activity Questions 2 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 8", "type": "Graded"}},
    {"id": 76, "week_id": 8, "sequence_no": 5, "name": "L8.3 SOLID - Principles II", "type": "Video",
     "url": "https://www.youtube.com/watch?v=KPyFLiFehgU", "video_id": "KPyFLiFehgU"},
    {"id": 77, "week_id": 8, "sequence_no": 6, "name": "AQ8.3: Activity Questions 3 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 8", "type": "Graded"}},
    {"id": 78, "week_id": 8, "sequence_no": 7, "name": "L8.4 Design Patterns - Creational", "type": "Video",
     "url": "https://www.youtube.com/watch?v=CCfQ4ZmlWaw", "video_id": "CCfQ4ZmlWaw"},
    {"id": 79, "week_id": 8, "sequence_no": 8, "name": "AQ8.4: Activity Questions 4 - Not Graded", "type": "Assignment",
     "content": {"description": "Graded Assignment 8", "type": "Graded"}},
    {"id": 80, "week_id": 8, "sequence_no": 9, "name": "L8.5 Design Patterns - Structural", "type": "Video",
     "url": "https://www.youtube.com/watch?v=-KTUKkeyRHM", "video_id": "-KTUKkeyRHM"},
    {"id": 81, "week_id": 8, "sequence_no": 10, "name": "AQ8.5: Activity Questions 5 - Not Graded",
     "type": "Assignment",
     "content": {"description": "Graded Assignment 8", "type": "Graded"}},
    {"id": 82, "week_id": 8, "sequence_no": 11, "name": "L8.6 Design Patterns - Structural", "type": "Video",
     "url": "https://www.youtube.com/watch?v=immIH_tlfkI", "video_id": "immIH_tlfkI"},
    {"id": 83, "week_id": 8, "sequence_no": 12, "name": "AQ8.6: Activity Questions 6 - Not Graded",
     "type": "Assignment",
     "content": {"description": "Graded Assignment 8", "type": "Graded"}},
    {"id": 84, "week_id": 8, "sequence_no": 13, "name": "Graded Assignment 8", "type": "Assignment",
     "content": {"description": "Graded Assignment 8", "type": "Graded"}}

]

for lecture in lecture_data:
    existing_lecture = db.query(Lecture).filter(Lecture.id == lecture["id"]).first()

    if existing_lecture:
        existing_lecture.name = lecture["name"]
        existing_lecture.week_id = lecture["week_id"]
        existing_lecture.sequence_no = lecture["sequence_no"]
        existing_lecture.type = lecture["type"]
        existing_lecture.url = lecture.get("url")  # Only for video
        existing_lecture.content = lecture.get("content")
        existing_lecture.video_id = lecture.get("video_id")
    else:
        new_lecture = Lecture(
            id=lecture["id"],
            name=lecture["name"],
            week_id=lecture["week_id"],
            sequence_no=lecture["sequence_no"],
            type=lecture["type"],
            url=lecture.get("url"),
            content=lecture.get("content"),
            video_id=lecture.get("video_id")
        )
        db.add(new_lecture)

db.commit()
db.close()

print("✅ Seed data for users added/updated successfully!")
