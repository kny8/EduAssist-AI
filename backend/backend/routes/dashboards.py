from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import re
from collections import Counter

from database.database import get_db
from utils.auth import get_current_user
from models import Quiz, Week, Lecture, Chat, ChatMessage, CodeChat, CodeChatMessage
from models import User
from datetime import datetime, timedelta

router = APIRouter()

# Common programming topics keywords mapping
TOPIC_KEYWORDS = {
    "Variables & Types": ["variable", "type", "int", "string", "bool", "float", "declare", "datatype"],
    "Functions": ["function", "method", "parameter", "argument", "return", "def ", "define", "call"],
    "Loops": ["loop", "for", "while", "iteration", "iterate", "repeat", "break", "continue"],
    "Conditionals": ["if", "else", "elif", "condition", "switch", "case", "ternary"],
    "Arrays/Lists": ["array", "list", "index", "element", "append", "insert", "push", "pop"],
    "Dictionaries": ["dict", "dictionary", "hash", "map", "key", "value", "pair"],
    "Objects/Classes": ["class", "object", "instance", "property", "attribute", "method", "constructor"],
    "Inheritance": ["inherit", "inheritance", "extend", "override", "super", "parent", "child"],
    "Recursion": ["recursion", "recursive", "base case", "call stack"],
    "Error Handling": ["try", "catch", "except", "error", "exception", "handle", "raise", "throw"],
    "Debugging": ["debug", "debugger", "log", "print", "trace", "error", "bug", "fix"],
    "File I/O": ["file", "read", "write", "open", "close", "io", "input", "output"],
    "Strings": ["string", "str", "concat", "substring", "split", "join", "format"],
    "Modules/Packages": ["import", "module", "package", "library", "require", "include"],
    "Algorithms": ["algorithm", "sort", "search", "complexity", "big o", "efficiency"],
    "Data Structures": ["data structure", "queue", "stack", "tree", "graph", "linked list"],
    "Web Development": ["html", "css", "javascript", "dom", "api", "request", "response"],
    "Databases": ["database", "sql", "query", "table", "join", "key", "relation"],
    "Frameworks": ["framework", "django", "flask", "react", "angular", "vue", "express"],
    "Testing": ["test", "unit test", "integration test", "mock", "assert", "expect", "verify"]
}

def sentiment_from_text(text):
    """Simple rule-based sentiment extraction for confusion and frustration"""
    confusion_words = ["confused", "confusing", "unclear", "don't understand", "don't get it", 
                       "what does", "how does", "not sure", "lost", "complicated", "complex", 
                       "hard to understand", "struggling", "not clear", "clarify", "explain", "help me understand"]
    
    frustration_words = ["frustrated", "frustrating", "annoying", "fed up", "tired of", 
                         "sick of", "doesn't work", "not working", "failed", "error", "problem", 
                         "issue", "bug", "stuck", "difficult", "hard", "impossible", "waste", 
                         "terrible", "horrible", "hate"]
    
    text_lower = text.lower()
    
    # Calculate scores
    confusion_score = sum(1 for word in confusion_words if word in text_lower) / len(confusion_words)
    confusion_score = min(confusion_score * 3, 1.0)  # Scale up but cap at 1.0
    
    frustration_score = sum(1 for word in frustration_words if word in text_lower) / len(frustration_words)
    frustration_score = min(frustration_score * 3, 1.0)  # Scale up but cap at 1.0
    
    return {
        "confusion": confusion_score,
        "frustration": frustration_score
    }

def extract_topics_from_text(text):
    """Extract topics from text based on keyword matches"""
    text_lower = text.lower()
    matching_topics = []
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matching_topics.append(topic)
                break
    
    return matching_topics

def analyze_chat_messages(db: Session, week_id: int = None):
    """Analyze chat messages to extract common searches and topics"""
    # If week_id is provided, get all lectures in that week
    if week_id:
        lectures = db.query(Lecture).filter(Lecture.week_id == week_id).all()
        lecture_ids = [lecture.id for lecture in lectures]
        lecture_map = {lecture.id: lecture.name for lecture in lectures}
        
        if not lecture_ids:
            return []  # No lectures in this week
    else:
        # If no week_id, get all lectures
        lectures = db.query(Lecture).all()
        lecture_ids = [lecture.id for lecture in lectures]
        lecture_map = {lecture.id: lecture.name for lecture in lectures}
    
    # Base query to get user messages with lecture context
    chat_query = db.query(
        ChatMessage.message, 
        Chat.lecture_id,
        func.count(ChatMessage.id).label("count")
    ).join(Chat).filter(ChatMessage.sender == "user")
    
    # If we have lecture_ids, filter by them
    if week_id and lecture_ids:
        chat_query = chat_query.filter(Chat.lecture_id.in_(lecture_ids))
    
    # Get chat messages grouped by both message text and lecture
    chat_messages = chat_query.group_by(ChatMessage.message, Chat.lecture_id).order_by(desc("count")).all()
    
    # Also get code chat messages (not filtered by lecture since they're not tied to lectures)
    code_query = db.query(CodeChatMessage.message, func.count(CodeChatMessage.id).label("count")) \
                   .filter(CodeChatMessage.sender == "user")
    
    # Execute code chat query
    code_messages = code_query.group_by(CodeChatMessage.message).order_by(desc("count")).limit(30).all()
    
    # Combine results - store lecture context for regular chats
    message_data = {}
    for message, lecture_id, count in chat_messages:
        message_text = message.strip()
        if len(message_text) > 10 and ("?" in message_text or any(w in message_text.lower() for w in ["how", "what", "why", "when", "who", "which", "where", "can", "could"])):
            lecture_name = lecture_map.get(lecture_id, "Unknown Lecture")
            
            if message_text in message_data:
                message_data[message_text]["count"] += count
                if lecture_name not in message_data[message_text]["lectures"]:
                    message_data[message_text]["lectures"].append(lecture_name)
            else:
                message_data[message_text] = {
                    "count": count,
                    "lectures": [lecture_name]
                }
    
    # Add code chat messages
    for message, count in code_messages:
        message_text = message.strip()
        if len(message_text) > 10 and ("?" in message_text or any(w in message_text.lower() for w in ["how", "what", "why", "when", "who", "which", "where", "can", "could"])):
            if message_text in message_data:
                message_data[message_text]["count"] += count
            else:
                message_data[message_text] = {
                    "count": count,
                    "lectures": ["Code Exercises"]  # Mark as coming from code exercise context
                }
    
    # Extract topics and analyze sentiment
    for message_text, data in message_data.items():
        topics = extract_topics_from_text(message_text)
        sentiments = sentiment_from_text(message_text)
        
        # Add topics and sentiments to the data
        data["topics"] = topics if topics else ["General"]
        data["sentiments"] = sentiments
        
        # If no specific topics found but we have lecture context, derive topics from lecture names
        if not topics and "lectures" in data:
            lecture_derived_topics = []
            for lecture_name in data["lectures"]:
                words = re.findall(r'\b[a-zA-Z]{4,}\b', lecture_name)
                for word in words:
                    if word.lower() not in ["lecture", "introduction", "video", "assignment"]:
                        lecture_derived_topics.append(word)
            
            if lecture_derived_topics:
                data["topics"] = lecture_derived_topics
    
    # Convert to list format and filter relevant items
    results = []
    for message_text, data in message_data.items():
        # Only keep messages that match known topics or have high sentiment
        if data["topics"] or data["sentiments"]["confusion"] > 0.2 or data["sentiments"]["frustration"] > 0.2:
            results.append({
                "query": message_text,
                "count": data["count"],
                "topics": data["topics"],
                "sentiments": data["sentiments"],
                "lectures": data["lectures"][:3] if len(data["lectures"]) > 3 else data["lectures"]  # Limit to 3 lectures
            })
    
    # Sort by count and take top 20
    results.sort(key=lambda x: x["count"], reverse=True)
    return results[:20]

@router.get("/student_dashboard", summary="Get Dashboard Data")
def get_dashboard(db: Session = Depends(get_db),
                  currentUser=Depends(get_current_user)):
    """
    Returns dashboard data including latest quiz data from the database.
    """
    # Get user details
    user = db.query(User).filter(User.id == currentUser).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get latest quizzes (last 7 days)
    latest_quizzes = db.query(Quiz).filter(
        and_(
            Quiz.date <= datetime.now(),
            Quiz.date >= datetime.now() - timedelta(days=7)
        )
    ).order_by(Quiz.date.desc()).all()

    # Get all quizzes for the study plan section
    all_quizzes = db.query(Quiz).order_by(Quiz.date.desc()).all()
    
    # Format quizzes for the study plan dropdown
    quizzes_list = [
        {
            "id": quiz.id,
            "name": quiz.name,
            "date": quiz.date.strftime("%d/%m/%Y"),
            "after": quiz.after,
            "week_id": quiz.after
        }
        for quiz in all_quizzes
    ]
    
    # Get all weeks and their lectures
    all_weeks = db.query(Week).order_by(Week.id).all()
    
    # Create a dictionary of weeks with their lectures
    weeks_data = {}
    for week in all_weeks:
        lectures = db.query(Lecture).filter(Lecture.week_id == week.id).order_by(Lecture.sequence_no).all()
        
        weeks_data[week.id] = {
            "id": week.id,
            "title": week.name,
            "type": "week",
            "completed": True,  # Default to completed 
            "lectures": [
                {
                    "id": lecture.id,
                    "name": lecture.name,
                    "type": lecture.type
                }
                for lecture in lectures
            ]
        }

    # Format upcoming deadlines including quizzes
    upcoming_deadlines = [
        {
            "title": quiz.name,
            "type": "Quiz",
            "due_date": quiz.date.strftime("%d/%m")
        }
        for quiz in latest_quizzes
    ]

    # Add other deadlines (you can fetch these from other tables if needed)
    upcoming_deadlines.extend([
        {"title": "Lx 1.1", "type": "Graded Assignment", "due_date": "02/02"},
        {"title": "Lx 2.1", "type": "Graded Assignment", "due_date": "09/02"},
    ])

    # Sort deadlines by date
    upcoming_deadlines.sort(key=lambda x: x["due_date"])

    # Format study plan steps from latest quizzes
    study_plan_steps = [
        {
            "step": idx + 1,
            "date": quiz.date.strftime("%b %d")
        }
        for idx, quiz in enumerate(latest_quizzes)
    ]

    return {
        "user": {
            "id": currentUser,
            "name": user.name,
            "student_email": user.email
        },
        "pick_up_where_left_off": {
            "question": "Explain how to create effective wireframes"
        },
        "study_plan": {
            "type": "Quiz",
            "steps": study_plan_steps,
            "quizzes": quizzes_list,
            "weeks_data": weeks_data
        },
        "upcoming_deadlines": upcoming_deadlines,
        "past_results": {
            "labels": ["Week 1", "Week 2", "Week 3"],
            "data": [4.5, 5, 3.8],
            "title": "Total Grade Contribution"
        },
        "quick_links": [
            {"title": "Course Grading Document", "url": "/grading-document"},
            {"title": "Slides Used in Lectures", "url": "/lecture-slides"},
            {"title": "Previous Year Papers", "url": "/previous-papers"},
            {"title": "Practice Assignment Solution", "url": "/assignment-solution"}
        ]
    }


@router.get("/teacher_dashboard")
def get_teacher_dashboard(week_id: int = None, db: Session = Depends(get_db)):
    # Fetch actual weeks from the database
    db_weeks = db.query(Week).order_by(Week.id).all()
    
    if not db_weeks:
        # If no weeks in database, use default hardcoded data
        db_weeks = [
            type('Week', (), {'id': 1, 'name': 'Week 1'}),
            type('Week', (), {'id': 2, 'name': 'Week 2'}),
            type('Week', (), {'id': 3, 'name': 'Week 3'}),
            type('Week', (), {'id': 4, 'name': 'Week 4'})
        ]
        print("No weeks found in database, using default weeks")
    
    # Create a mapping from week_id to week_name and a list of available week names
    week_mapping = {week.id: week.name for week in db_weeks}
    available_weeks = [week.name for week in db_weeks]
    
    print(f"Available weeks from database: {available_weeks}")
    
    # Default data for all weeks with explicit number values
    all_weeks_data = {}
    
    # For each week in the database, create a data entry
    for week in db_weeks:
        week_name = week.name
        week_id_num = week.id
        
        # Get lectures for this week
        lectures = db.query(Lecture).filter(Lecture.week_id == week_id_num).order_by(Lecture.sequence_no).all()
        lecture_names = [lecture.name for lecture in lectures]
        
        # Get real common searches for this week from chat messages
        week_searches = analyze_chat_messages(db, week_id_num)
        
        # NO mock data - if no real data, just return empty array
        if not week_searches:
            week_searches = []
            
        # Get aggregated topic counts from chat data
        topic_counts = {}
        for search in week_searches:
            for topic in search["topics"]:
                if topic in topic_counts:
                    topic_counts[topic] += search["count"]
                else:
                    topic_counts[topic] = search["count"]
        
        # Convert to list and sort
        topic_list = [{"name": topic, "percentage": int(count / sum(topic_counts.values()) * 100) if topic_counts.values() else 0} 
                     for topic, count in topic_counts.items()]
        topic_list.sort(key=lambda x: x["percentage"], reverse=True)
        
        # Create assignment questions based on the number of lectures
        assignment_questions = []
        for i, lecture in enumerate(lectures):
            # Create 1-2 questions per lecture
            assignment_questions.append({
                "question": f"Q{i*2+1}", 
                "correct": 75 if i % 3 != 0 else 40,  # Lower score for every 3rd lecture
                "lecture_id": lecture.id,
                "lecture_name": lecture.name
            })
            assignment_questions.append({
                "question": f"Q{i*2+2}", 
                "correct": 85 if i % 3 != 1 else 45,  # Lower score for every 3rd+1 lecture
                "lecture_id": lecture.id,
                "lecture_name": lecture.name
            })
        
        # If no lectures, use default questions
        if not assignment_questions:
            assignment_questions = [
                {"question": f"Q{4*(week_id_num-1)+1}", "correct": 75},
                {"question": f"Q{4*(week_id_num-1)+2}", "correct": 85},
                {"question": f"Q{4*(week_id_num-1)+3}", "correct": 90},
                {"question": f"Q{4*(week_id_num-1)+4}", "correct": 40 if week_id_num % 2 == 1 else 60},
            ]
        
        # Generate suggestions based on chat sentiment analysis
        chat_based_suggestions = []
        
        # Add suggestions based on topics with high confusion/frustration
        topics_with_issues = []
        for search in week_searches:
            if search["sentiments"]["confusion"] > 0.6 or search["sentiments"]["frustration"] > 0.6:
                for topic in search["topics"]:
                    if topic not in topics_with_issues and topic != "General":
                        topics_with_issues.append(topic)
                        
                        # Add specific suggestion
                        if search["sentiments"]["confusion"] > 0.6:
                            chat_based_suggestions.append(f"Students show high confusion about '{topic}' concepts")
                        if search["sentiments"]["frustration"] > 0.6:
                            chat_based_suggestions.append(f"Students appear frustrated when working with '{topic}'")
        
        # Add lecture-specific suggestions
        lecture_issues = {}
        for search in week_searches:
            if "lectures" in search and search["sentiments"]["confusion"] > 0.5:
                for lecture_name in search["lectures"]:
                    if lecture_name not in lecture_issues:
                        lecture_issues[lecture_name] = 0
                    lecture_issues[lecture_name] += 1
        
        # Add suggestions for lectures with multiple confusion indicators
        for lecture_name, count in lecture_issues.items():
            if count >= 2:
                chat_based_suggestions.append(f"Multiple students have questions about '{lecture_name}'")
                
        # Combine with standard suggestions
        all_suggestions = chat_based_suggestions + get_suggestions_for_week(week_id_num, lecture_names)
                
        # Create a default data structure for this week with lecture information
        all_weeks_data[week_name] = {
            "assignment_problem_area": assignment_questions,
            "completion_console": [
                {"name": f"Graded Assn. {week_id_num}", "completion": 80 - (week_id_num * 5)},
                {"name": f"Practice Assn. {week_id_num}", "completion": 30 + (week_id_num * 5)},
            ],
            "searched_topics": topic_list[:5] if topic_list else get_topics_for_week(week_id_num, lecture_names),
            "gpt_suggestions": all_suggestions[:8],  # Limit to 8 suggestions
            "lectures": [
                {
                    "id": lecture.id,
                    "name": lecture.name,
                    "sequence_no": lecture.sequence_no,
                    "type": lecture.type if hasattr(lecture, 'type') else "Lecture"
                }
                for lecture in lectures
            ],
            "lecture_count": len(lectures),
            "common_searches": week_searches
        }
    
    # Log the request and response for debugging
    print(f"Received request for teacher dashboard with week_id: {week_id}")
    
    # If a specific week is requested, return data for that week
    if week_id is not None:
        if week_id not in week_mapping:
            print(f"Week {week_id} not found. Available weeks: {available_weeks}")
            raise HTTPException(status_code=404, detail=f"Week {week_id} not found. Available week IDs are {list(week_mapping.keys())}")
            
        week_name = week_mapping[week_id]
        if week_name not in all_weeks_data:
            raise HTTPException(status_code=404, detail=f"No data available for week {week_name}")
            
        response_data = all_weeks_data[week_name].copy()
        response_data["weeks"] = [{"id": w.id, "name": w.name} for w in db_weeks]  # Return week objects with IDs
        response_data["current_week"] = week_name
        print(f"Returning data for week: {week_name}")
        return response_data
    
    # Otherwise, combine data from all weeks (for overview)
    combined_data = {
        "assignment_problem_area": [],
        "completion_console": [],
        "searched_topics": [],
        "gpt_suggestions": [],
        "lectures": [],
        "weeks": [{"id": w.id, "name": w.name} for w in db_weeks],  # Return week objects with IDs
        "current_week": "All Weeks",
        "total_lecture_count": sum(all_weeks_data[week_name].get("lecture_count", 0) for week_name in all_weeks_data),
        "common_searches": []
    }
    
    # Combine data from all weeks
    for week_name, week_data in all_weeks_data.items():
        combined_data["assignment_problem_area"].extend(week_data["assignment_problem_area"])
        
        # Just take the latest completion data
        if week_name == available_weeks[-1]:
            combined_data["completion_console"] = week_data["completion_console"]
        
        # Take the most searched topics across all weeks
        for topic in week_data["searched_topics"]:
            existing_topic = next((t for t in combined_data["searched_topics"] if t["name"] == topic["name"]), None)
            if existing_topic:
                existing_topic["percentage"] = max(existing_topic["percentage"], topic["percentage"])
            else:
                combined_data["searched_topics"].append(topic)
        
        # Include all suggestions, but limit to prevent too many
        combined_data["gpt_suggestions"].extend(week_data["gpt_suggestions"][:2])
        
        # Add lectures with week information
        if "lectures" in week_data:
            week_lectures = [
                {**lecture, "week_name": week_name, "week_id": next(w.id for w in db_weeks if w.name == week_name)}
                for lecture in week_data["lectures"]
            ]
            combined_data["lectures"].extend(week_lectures)
            
        # Combine common searches and keep count totals
        if "common_searches" in week_data:
            for search in week_data["common_searches"]:
                # Look for an existing search with the same query
                existing_search = next((s for s in combined_data["common_searches"] if s["query"] == search["query"]), None)
                if existing_search:
                    # Update count if exists
                    existing_search["count"] += search["count"]
                    # Add topics if new
                    for topic in search["topics"]:
                        if topic not in existing_search["topics"]:
                            existing_search["topics"].append(topic)
                    # Average the sentiments
                    for sentiment, value in search["sentiments"].items():
                        if sentiment in existing_search["sentiments"]:
                            existing_search["sentiments"][sentiment] = (existing_search["sentiments"][sentiment] + value) / 2
                        else:
                            existing_search["sentiments"][sentiment] = value
                    # Combine lectures (if present)
                    if "lectures" in search:
                        if "lectures" not in existing_search:
                            existing_search["lectures"] = []
                        for lecture in search["lectures"]:
                            if lecture not in existing_search["lectures"]:
                                existing_search["lectures"].append(lecture)
                else:
                    # Add new search
                    combined_data["common_searches"].append(search.copy())
    
    # Sort searched_topics by percentage (descending)
    combined_data["searched_topics"].sort(key=lambda x: x["percentage"], reverse=True)
    
    # Limit suggestions to top 5
    combined_data["gpt_suggestions"] = combined_data["gpt_suggestions"][:5]
    
    # Sort lectures by week and sequence number
    combined_data["lectures"].sort(key=lambda x: (x.get("week_id", 0), x.get("sequence_no", 0)))
    
    # Sort common searches by count (descending)
    combined_data["common_searches"].sort(key=lambda x: x["count"], reverse=True)
    
    # Limit to top 10 searches
    combined_data["common_searches"] = combined_data["common_searches"][:10]
    
    return combined_data

# Helper functions for generating week-specific data
def get_topics_for_week(week_id, lecture_names=None):
    # If we have lecture names, use them to generate realistic topics
    if lecture_names and len(lecture_names) > 0:
        topics = []
        for i, lecture_name in enumerate(lecture_names[:2]):  # Use first 2 lectures
            # Extract keywords from lecture name
            keywords = [word for word in lecture_name.split() if len(word) > 3]
            topic_name = keywords[0] if keywords else f"Topic from {lecture_name}"
            topics.append({
                "name": topic_name, 
                "percentage": 60 + (i * 10) + (week_id * 5) % 30
            })
        return topics
    
    # Default topics if no lecture names provided
    topics_by_week = {
        1: [
            {"name": "Variables & Types", "percentage": 60},
            {"name": "Functions", "percentage": 40},
        ],
        2: [
            {"name": "Loops", "percentage": 70},
            {"name": "Conditionals", "percentage": 55},
        ],
        3: [
            {"name": "Arrays/Lists", "percentage": 85},
            {"name": "Recursion", "percentage": 90},
        ],
        4: [
            {"name": "Objects/Classes", "percentage": 95},
            {"name": "Inheritance", "percentage": 80},
        ]
    }
    return topics_by_week.get(week_id, [
        {"name": f"Topic A - Week {week_id}", "percentage": 50 + (week_id * 5)},
        {"name": f"Topic B - Week {week_id}", "percentage": 40 + (week_id * 5)},
    ])

def get_suggestions_for_week(week_id, lecture_names=None):
    # If we have lecture names, use them to generate relevant suggestions
    if lecture_names and len(lecture_names) > 0:
        suggestions = []
        for lecture_name in lecture_names[:2]:  # Use first 2 lectures
            suggestions.append(f"Students are struggling with concepts from '{lecture_name}'")
            suggestions.append(f"Consider creating additional exercises for '{lecture_name}'")
        
        # Add some generic suggestions
        suggestions.extend([
            "Review sessions before assignments have shown to improve performance",
            f"Students in Week {week_id} would benefit from more interactive examples"
        ])
        return suggestions
    
    # Default suggestions if no lecture names provided
    suggestions_by_week = {
        1: [
            "Focus more on explaining variable scope",
            "Students are struggling with function parameters",
            "Consider a review session on basic data types",
            "More exercises on function return values would help",
        ],
        2: [
            "Many students are confused about nested loops",
            "Create more exercises for complex conditionals",
            "Review session on loop efficiency would be beneficial",
            "Consider creating a cheat sheet for loop patterns",
        ],
        3: [
            "Recursion is a major pain point - dedicate more time to it",
            "Consider visual aids for explaining array operations",
            "Students need more practice with array manipulation",
            "Create step-by-step guides for recursive problems",
        ],
        4: [
            "Students are struggling with object-oriented concepts",
            "Provide more examples of inheritance in practice",
            "Consider creating a project that reinforces OOP principles",
            "More visual diagrams for class relationships would help",
        ]
    }
    return suggestions_by_week.get(week_id, [
        f"Focus on core concepts for Week {week_id}",
        f"Students need more practice with Week {week_id} material",
        f"Consider reviewing prerequisites for Week {week_id}",
        f"Additional resources might help with Week {week_id} topics",
    ])


@router.get("/admin_dashboard")
def get_admin_dashboard():
    return {
        "weekly_performance": [
            {"week": "Wk 1", "score": 60},
            {"week": "Wk 2", "score": 72},
            {"week": "Wk 3", "score": 80},
            {"week": "Wk 4", "score": 50},  # Low performance week
            {"week": "Wk 5", "score": 85},
            {"week": "Wk 6", "score": 90},
            {"week": "Wk 7", "score": 83},
            {"week": "Wk 8", "score": 89},
            {"week": "Wk 9", "score": 45},  # Low performance week
            {"week": "Wk 10", "score": 87},
        ],
        "genai_perception": [
            {"week": "Week 1", "perception": 20},
            {"week": "Week 2", "perception": 40},
            {"week": "Week 3", "perception": 35},
            {"week": "Week 4", "perception": 50},
            {"week": "Week 5", "perception": 60},
        ],
        "key_issues": [
            "Issue A",
            "Issue B",
            "Issue C",
            "Issue D",
            "Issue E",
        ],
        "key_stats": {
            "weekly_users": 150,
            "doubt_queries": 45,
            "solves_bookmarked": 78,
        },
    }
