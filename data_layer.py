class Student:
    def __init__(self, name):
        self.id = None
        self.name = name


class Course:
    def __init__(self, title):
        self.id = None
        self.title = title


class Enrollment:
    def __init__(self, student_id, course_id):
        self.id = None
        self.student_id = student_id
        self.course_id = course_id
