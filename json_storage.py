import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from data_layer import Course, Enrollment, Student
from repository_layer import MemoryRepository
from service_layer import LearningService, read_required_text


def repository_data(repository):
    return {
        "items": [vars(item) for item in repository.get_all()],
        "next_id": repository.next_id,
    }


def save_learning(filename, service):
    path = Path(filename)
    data = {
        "students": repository_data(service.students),
        "courses": repository_data(service.courses),
        "enrollments": repository_data(service.enrollments),
    }

    temporary_path = None
    try:
        # Запись сначала идёт во временный файл рядом с целевым.
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as file:
            temporary_path = Path(file.name)
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def restore_repository(data, model):
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("ожидался объект с массивом items")

    items = []
    for record in data["items"]:
        if not isinstance(record, dict):
            raise ValueError("каждый элемент массива items должен быть объектом")
        fields = record.copy()
        try:
            item_id = fields.pop("id")
            item = model(**fields)
        except (KeyError, TypeError):
            raise ValueError(f"неверный набор полей для {model.__name__}") from None

        if model is Student:
            if not isinstance(item.name, str):
                raise ValueError("имя ученика должно быть строкой")
            read_required_text(item.name)
        elif model is Course:
            if not isinstance(item.title, str):
                raise ValueError("название курса должно быть строкой")
            read_required_text(item.title)

        item.id = item_id
        items.append(item)

    return MemoryRepository(items, data.get("next_id"))


def load_learning(filename):
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"не удалось прочитать JSON: {error}") from error

    if not isinstance(data, dict):
        raise ValueError("в файле должен быть объект с данными обучения")

    students = restore_repository(data.get("students"), Student)
    courses = restore_repository(data.get("courses"), Course)
    enrollments = restore_repository(data.get("enrollments"), Enrollment)

    pairs = set()
    for enrollment in enrollments.get_all():
        if type(enrollment.student_id) is not int or type(enrollment.course_id) is not int:
            raise ValueError("ID ученика и курса в записи должны быть целыми числами")
        students.get(enrollment.student_id)
        courses.get(enrollment.course_id)
        pair = (enrollment.student_id, enrollment.course_id)
        if pair in pairs:
            raise ValueError("ученик записан на один курс несколько раз")
        pairs.add(pair)

    return LearningService(students, courses, enrollments)
