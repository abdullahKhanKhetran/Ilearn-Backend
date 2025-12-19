import json
from typing import List, Dict, Any
from src.config import config

def load_student_data() -> List[Dict[str, Any]]:
    """Load student data from JSON file"""
    with open(config.STUDENT_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_average_marks(subjects: Dict[str, Dict[str, int]]) -> float:
    """Calculate average marks across all subjects"""
    total_marks = 0
    total_possible = 0
    
    for subject, marks_data in subjects.items():
        total_marks += marks_data['marks']
        total_possible += marks_data['total']
    
    return (total_marks / total_possible) * 100 if total_possible > 0 else 0

def categorize_performance(avg_marks: float, attendance: float) -> str:
    """Categorize student performance based on marks and attendance"""
    if avg_marks >= config.FANTASTIC_THRESHOLD and attendance >= config.GOOD_ATTENDANCE:
        return "Fantastic"
    elif avg_marks >= config.AVERAGE_THRESHOLD:
        return "Average"
    else:
        return "Below Average"

def format_student_data_for_embedding(student: Dict[str, Any]) -> str:
    """Convert student data to text format for embedding"""
    subjects_text = ", ".join([
        f"{subj}: {data['marks']}/{data['total']}" 
        for subj, data in student['subjects'].items()
    ])
    
    avg_marks = calculate_average_marks(student['subjects'])
    category = categorize_performance(avg_marks, student['attendance'])
    
    text = f"""
Student ID: {student['student_id']}
Name: {student['name']}
Semester: {student['semester']}
Performance Category: {category}
Average Marks: {avg_marks:.2f}%
Subjects and Marks: {subjects_text}
Attendance: {student['attendance']}%
Assignments Submitted: {student['assignments_submitted']}/{student['total_assignments']}
Performance Notes: {student['performance_notes']}
"""
    return text.strip()