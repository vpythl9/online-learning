import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from json_storage import load_learning, save_learning
from main import main
from repository_layer import MemoryRepository
from service_layer import LearningService


class LearningServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = LearningService(
            MemoryRepository(), MemoryRepository(), MemoryRepository()
        )

    def test_student_can_enroll_and_cancel(self):
        student = self.service.register_student(" Анна ")
        course = self.service.create_course("Python")
        self.assertEqual(student.name, "Анна")

        self.service.enroll_student(student.id, course.id)
        self.assertEqual(self.service.get_student_courses(student.id), [course])

        self.service.cancel_enrollment(student.id, course.id)
        self.assertEqual(self.service.get_student_courses(student.id), [])

    def test_duplicate_enrollment_is_rejected(self):
        student = self.service.register_student("Анна")
        course = self.service.create_course("Python")
        self.service.enroll_student(student.id, course.id)

        with self.assertRaisesRegex(ValueError, "уже записан"):
            self.service.enroll_student(student.id, course.id)

    def test_delete_course_removes_only_its_enrollments(self):
        anna = self.service.register_student("Анна")
        boris = self.service.register_student("Борис")
        python_course = self.service.create_course("Python")
        git_course = self.service.create_course("Git")
        self.service.enroll_student(anna.id, python_course.id)
        self.service.enroll_student(boris.id, python_course.id)
        self.service.enroll_student(anna.id, git_course.id)

        self.service.delete_course(python_course.id)

        self.assertEqual(self.service.get_courses(), [git_course])
        self.assertEqual(self.service.get_students(), [anna, boris])
        self.assertEqual(self.service.get_student_courses(anna.id), [git_course])
        self.assertEqual(self.service.get_student_courses(boris.id), [])

    def test_delete_unknown_course_reports_an_error(self):
        course = self.service.create_course("Python")

        with self.assertRaisesRegex(ValueError, "не найден"):
            self.service.delete_course(999)

        self.assertEqual(self.service.get_courses(), [course])


class JsonStorageTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "обучение.json"
        self.service = LearningService(
            MemoryRepository(), MemoryRepository(), MemoryRepository()
        )

    def test_save_and_load_restores_students_courses_and_enrollments(self):
        student = self.service.register_student("Анна")
        course = self.service.create_course("Программирование")
        self.service.enroll_student(student.id, course.id)

        save_learning(self.path, self.service)
        restored = load_learning(self.path)

        self.assertIn("Программирование", self.path.read_text(encoding="utf-8"))
        self.assertEqual(restored.get_students()[0].id, student.id)
        self.assertEqual(restored.get_students()[0].name, student.name)
        self.assertEqual(restored.get_courses()[0].id, course.id)
        self.assertEqual(restored.get_student_courses(student.id)[0].title, course.title)
        restored.cancel_enrollment(student.id, course.id)
        self.assertEqual(restored.get_student_courses(student.id), [])

    def test_load_preserves_the_next_id_after_a_deletion(self):
        course = self.service.create_course("Python")
        self.service.delete_course(course.id)

        save_learning(self.path, self.service)
        restored = load_learning(self.path)

        self.assertEqual(restored.get_courses(), [])
        self.assertEqual(restored.create_course("Git").id, course.id + 1)

    def test_save_replaces_an_existing_snapshot(self):
        course = self.service.create_course("Python")
        save_learning(self.path, self.service)
        self.service.rename_course(course.id, "Основы Python")

        save_learning(self.path, self.service)

        self.assertEqual(load_learning(self.path).get_courses()[0].title, "Основы Python")

    def test_invalid_json_is_rejected(self):
        self.path.write_text("{", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "не удалось прочитать JSON"):
            load_learning(self.path)

    def test_missing_file_reports_an_error(self):
        with self.assertRaises(FileNotFoundError):
            load_learning(self.path)

    def test_enrollment_for_missing_course_is_rejected(self):
        student = self.service.register_student("Анна")
        course = self.service.create_course("Python")
        self.service.enroll_student(student.id, course.id)
        save_learning(self.path, self.service)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data["courses"]["items"].clear()
        self.path.write_text(json.dumps(data), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "не найден"):
            load_learning(self.path)

    def test_menu_keeps_current_courses_when_open_fails(self):
        self.path.write_text("{", encoding="utf-8")
        output = io.StringIO()
        actions = ["3", "Python", "11", str(self.path), "4", "0"]

        with patch("builtins.input", side_effect=actions), redirect_stdout(output):
            main()

        self.assertIn("ошибка: не удалось прочитать JSON", output.getvalue())
        self.assertIn("1. Python", output.getvalue())
