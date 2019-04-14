"""
@author: Yulin Wen

Project
"""
from collections import defaultdict
from prettytable import PrettyTable
import unittest


class Student:
    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.courses = defaultdict(str)

    def add_grade(self, course, grade):
        self.courses[course] = grade

    def summary(self):
        return [self.cwid, self.name, sorted(list(self.courses.keys()))]


class Instructor:
    def __init__(self, cwid, name, department):
        self.cwid = cwid
        self.name = name
        self.department = department
        self.courses = defaultdict(int)

    def add_student(self, course):
        self.courses[course] += 1

    def summary(self):
        for course, people in self.courses.items():
            yield [self.cwid, self.name, self.department, course, people]


class University:
    def __init__(self, stud_path, inst_path, grade_path):
        self.students = dict()
        self.instructors = dict()
        self.enroll_students(stud_path)
        self.hire_instructors(inst_path)
        self.release_score(grade_path)
        self.summary_students()
        self.summary_instructors()

    def enroll_students(self, path):
        """ load grades files """
        self.load_data(path, 'student')

    def hire_instructors(self, path):
        """ load instructors file """
        self.load_data(path, 'instructor')

    def release_score(self, path):
        """ load grades files """
        self.load_data(path, 'grade')

    def load_data(self, path, file_type):
        """ load data """
        if file_type == 'grade':
            """ load grades files
            Each line has the format: Student_CWID  Course  LetterGrade  Instructor_CWID """
            data = list(self.file_reader1(path, 4))
            for line in data:
                self.students[line[0]].add_grade(line[1], line[2])
                self.instructors[line[3]].add_student(line[1])
        else:
            data = list(self.file_reader1(path, 3))
            for line in data:
                if file_type == 'student':
                    """ load students file
                    Each line has the format: CWID  Name  Major """
                    student = Student(line[0], line[1], line[2])
                    self.students[line[0]] = student
                else:
                    """ load instructors file
                    Each line has the format: CWID  Name  Department """
                    instructor = Instructor(line[0], line[1], line[2])
                    self.instructors[line[0]] = instructor

    @staticmethod
    def file_reader1(path, expected, sep='\t'):
        """ From HW8 """
        try:
            file = open(path)
        except FileNotFoundError:
            raise FileNotFoundError("Can't open", path)
        with file:
            for index, line in enumerate(file):
                curr_line = str(line).strip().split(sep)
                if len(curr_line) != expected:
                    raise ValueError(
                        "{} have {} fields on line {} but {} expected".format(path, len(line), index, expected))
                yield tuple(curr_line)

    def summary_students(self):
        """ student PrettyTable """
        table = PrettyTable()
        table.field_names = ['CWID', 'Name', 'Completed Courses']
        for student in self.students.values():
            table.add_row(student.summary())
        print(table)

    def summary_instructors(self):
        """ instructor PrettyTable """
        table = PrettyTable()
        table.field_names = ['CWID', 'Name', 'Dept', 'Course', 'Students']
        for instructor in self.instructors.values():
            for course in instructor.summary():
                table.add_row(course)
        print(table)


class HW9Test(unittest.TestCase):
    stevens = University('/Users/kriswen/Downloads/students.txt',
                         '/Users/kriswen/Downloads/instructors.txt',
                         '/Users/kriswen/Downloads/grades.txt')

    def test_stud_num(self):
        """ test number of the students """
        file = open('/Users/kriswen/Downloads/students.txt')
        actual_num = len(self.stevens.students)
        expect_num = len([line for line in file])
        self.assertEqual(actual_num, expect_num)

    def test_inst_num(self):
        """ test number of the instructors """
        file = open('/Users/kriswen/Downloads/instructors.txt')
        actual_num = len(self.stevens.instructors)
        expect_num = len([line for line in file])
        self.assertEqual(actual_num, expect_num)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)