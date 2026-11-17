from data_layer import Course, Enrollment, Student
from repository_layer import Repository


def read_required_text(text):
    text = text.strip()
    if not text:
        raise ValueError("текст не может быть пустым")
    return text


class LearningService:
    def __init__(self, students: Repository, courses: Repository,
                 enrollments: Repository):
        self.students = students
        self.courses = courses
        self.enrollments = enrollments

    def register_student(self, name):
        return self.students.add(Student(read_required_text(name)))

    def get_students(self):
        return self.students.get_all()

    def create_course(self, title):
        return self.courses.add(Course(read_required_text(title)))

    def get_courses(self):
        return self.courses.get_all()

    def rename_course(self, course_id, title):
        title = read_required_text(title)
        course = self.courses.get(course_id)
        course.title = title
        return self.courses.update(course)
    
    def delete_course(self, course_id):
        self.courses.get(course_id)
        for enrollment in self.enrollments.get_all():
            if enrollment.course_id == course_id:
                self.enrollments.delete(enrollment.id)
        self.courses.delete(course_id)


    def enroll_student(self, student_id, course_id):
        self.students.get(student_id)
        self.courses.get(course_id)
        for enrollment in self.enrollments.get_all():
            if (enrollment.student_id == student_id
                    and enrollment.course_id == course_id):
                raise ValueError("ученик уже записан на этот курс")
        return self.enrollments.add(Enrollment(student_id, course_id))

    def get_student_courses(self, student_id):
        self.students.get(student_id)
        courses = []
        for enrollment in self.enrollments.get_all():
            if enrollment.student_id == student_id:
                courses.append(self.courses.get(enrollment.course_id))
        return courses

    def cancel_enrollment(self, student_id, course_id):
        self.students.get(student_id)
        self.courses.get(course_id)
        for enrollment in self.enrollments.get_all():
            if (enrollment.student_id == student_id
                    and enrollment.course_id == course_id):
                self.enrollments.delete(enrollment.id)
                return
        raise ValueError("ученик не записан на этот курс")
