from repository_layer import MemoryRepository
from service_layer import LearningService


MENU = """
1. зарегистрировать ученика
2. показать учеников
3. создать курс
4. показать курсы
5. переименовать курс
6. записать ученика на курс
7. показать курсы ученика
8. отменить запись на курс
0. выйти
"""


def read_id(prompt):
    try:
        item_id = int(input(prompt))
    except ValueError:
        raise ValueError("ID должен быть целым числом") from None
    if item_id < 1:
        raise ValueError("ID должен быть больше нуля")
    return item_id


def print_courses(courses):
    if not courses:
        print("курсов пока нет")
    for course in courses:
        print(f"{course.id}. {course.title}")


def main():
    service = LearningService(
        MemoryRepository(), MemoryRepository(), MemoryRepository()
    )

    while True:
        try:
            print(MENU)
            choice = input("выберите действие: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                student = service.register_student(input("имя ученика: "))
                print(f"ученик зарегистрирован, ID: {student.id}")
            elif choice == "2":
                students = service.get_students()
                if not students:
                    print("учеников пока нет")
                for student in students:
                    print(f"{student.id}. {student.name}")
            elif choice == "3":
                course = service.create_course(input("название курса: "))
                print(f"курс создан, ID: {course.id}")
            elif choice == "4":
                print_courses(service.get_courses())
            elif choice == "5":
                course_id = read_id("ID курса: ")
                service.rename_course(course_id, input("новое название: "))
                print("курс переименован")
            elif choice == "6":
                student_id = read_id("ID ученика: ")
                course_id = read_id("ID курса: ")
                service.enroll_student(student_id, course_id)
                print("ученик записан на курс")
            elif choice == "7":
                student_id = read_id("ID ученика: ")
                print_courses(service.get_student_courses(student_id))
            elif choice == "8":
                student_id = read_id("ID ученика: ")
                course_id = read_id("ID курса: ")
                service.cancel_enrollment(student_id, course_id)
                print("запись отменена")
            elif choice == "9":
                course_id = read_id("ID курса: ")
                service.delete_course(course_id)
                print("курс удалён")

            else:
                print("такого пункта меню нет")
        except ValueError as error:
            print(f"ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            print()
            break

    print("программа завершена")


if __name__ == "__main__":
    main()
