"""
@author: Yulin Wen

Project
"""
from collections import defaultdict
from prettytable import PrettyTable
import unittest
import sqlite3


class Student:
    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.courses = defaultdict(str)

    def add_grade(self, course, grade):
        self.courses[course] = grade

    def summary(self):
        passed = list()
        for course, grade in self.courses.items():
            if grade != 'F':
                passed.append(course)
        return [self.cwid, self.name, self.major, sorted(list(passed))]

    @staticmethod
    def get_field_name():
        return ['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required', 'Remaining Electives']


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

    @staticmethod
    def get_field_name():
        return ['CWID', 'Name', 'Dept', 'Course', 'Students']


class University:
    def __init__(self, stud_path, inst_path, grade_path, major_path, show_summary=True):
        self.students = dict()
        self.instructors = dict()
        self.majors = defaultdict(lambda: defaultdict(set))
        self.enroll_students(stud_path)
        self.hire_instructors(inst_path)
        self.release_score(grade_path)
        self.assign_majors(major_path)

        if show_summary:
            self.summary_major()
            self.summary_students()
            self.summary_instructors()
        self.sql_test()

    def enroll_students(self, path):
        """ load grades files """
        self.load_data(path, 'student')

    def hire_instructors(self, path):
        """ load instructors file """
        self.load_data(path, 'instructor')

    def release_score(self, path):
        """ load grades files """
        self.load_data(path, 'grade')

    def assign_majors(self, path):
        """ load major file"""
        self.load_data(path, 'major')

    def load_data(self, path, file_type):
        """ load data """
        if file_type == 'grade':
            """ load grades data
            Each line has the format: Student_CWID  Course  LetterGrade  Instructor_CWID """
            data = list(self.file_reader(path, 4))
            for s_id, course, grade, i_id in data:
                self.students[s_id].add_grade(course, grade)
                self.instructors[i_id].add_student(course)
        else:
            data = list(self.file_reader(path, 3))
            if file_type == 'student':
                """ load students data
                Each line has the format: CWID  Name  Major """
                for cwid, name, major in data:
                    student = Student(cwid, name, major)
                    self.students[cwid] = student
            elif file_type == 'instructor':
                """ load instructors file
                Each line has the format: CWID  Name  Department """
                for cwid, name, dept in data:
                    instructor = Instructor(cwid, name, dept)
                    self.instructors[cwid] = instructor
            else:
                """ load major data
                Each line has the format: Major  Flag  Course """
                for major, flag, course in data:
                    self.majors[major][flag].add(course)

    @staticmethod
    def file_reader(path, expected, sep='\t', head=False):
        """ From HW8 """
        try:
            file = open(path)
        except FileNotFoundError:
            raise FileNotFoundError("Can't open", path)
        with file:
            for index, line in enumerate(file):
                """ skip the head line"""
                if head:
                    head = False
                    continue
                curr_line = str(line).strip().split(sep)
                if len(curr_line) != expected:
                    raise ValueError(
                        "{} have {} fields on line {} but {} expected".format(path, len(line), index, expected))
                yield tuple(curr_line)

    def summary_students(self):
        """ student PrettyTable """
        table = PrettyTable()
        table.field_names = Student.get_field_name()
        for student in self.students.values():
            row = student.summary()
            # student.summary() formation: CWID, Name, Major, Completed Courses.
            row.append(sorted(self.majors[row[2]]['R'].difference(row[3])))
            if len(self.majors[row[2]]['E'].difference(row[3])) == len(self.majors[row[2]]['E']):
                row.append(sorted(self.majors[row[2]]['E']))
            else:
                row.append('None')
            table.add_row(row)
            yield row
        print(table)

    def summary_instructors(self):
        """ instructor PrettyTable """
        table = PrettyTable()
        table.field_names = Instructor.get_field_name()
        for instructor in self.instructors.values():
            for course in instructor.summary():
                table.add_row(course)
        print(table)

    def summary_major(self):
        """ major PrettyTable """
        table = PrettyTable()
        table.field_names = ['Dept', 'Required', 'Electives']
        for dept, flag in self.majors.items():
            table.add_row([dept, sorted(flag['R']), sorted(flag['E'])])
        print(table)

    @staticmethod
    def sql_test():
        """ Test execute the sql """
        db_file = '/Users/kriswen/SSW810-Project/810_startup.db'
        db = sqlite3.connect(db_file)
        sql_test = """select CWID, Name, Dept, Course, Studens from Instructors left join
                            (select Instructor_CWID, Course, count(Student_CWID) as Studens from Grades group by Course)
                      where Instructors.CWID = Instructor_CWID;"""
        table = PrettyTable()
        table.field_names = Instructor.get_field_name()
        for row in db.execute(sql_test):
            table.add_row(row)
        print(table)


class ProjectTest(unittest.TestCase):
    stevens = University('/Users/kriswen/Downloads/810/data/students.txt',
                         '/Users/kriswen/Downloads/810/data/instructors.txt',
                         '/Users/kriswen/Downloads/810/data/grades.txt',
                         '/Users/kriswen/Downloads/810/data/majors.txt')

    def test_stud(self):
        """ test if every student is setup properly """
        expected = [['10103', 'Baldwin, C', 'SFEN', ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687'],
                              ['SSW 540', 'SSW 555'], 'None'],
                    ['10115', 'Wyatt, X', 'SFEN', ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687'],
                              ['SSW 540', 'SSW 555'], 'None'],
                    ['10172', 'Forbes, I', 'SFEN', ['SSW 555', 'SSW 567'], ['SSW 540', 'SSW 564'],
                              ['CS 501', 'CS 513', 'CS 545']],
                    ['10175', 'Erickson, D', 'SFEN', ['SSW 564', 'SSW 567', 'SSW 687'], ['SSW 540', 'SSW 555'],
                              ['CS 501', 'CS 513', 'CS 545']],
                    ['10183', 'Chapman, O', 'SFEN', ['SSW 689'], ['SSW 540', 'SSW 555', 'SSW 564', 'SSW 567'],
                              ['CS 501', 'CS 513', 'CS 545']],
                    ['11399', 'Cordova, I', 'SYEN', ['SSW 540'], ['SYS 612', 'SYS 671', 'SYS 800'], 'None'],
                    ['11461', 'Wright, U', 'SYEN', ['SYS 611', 'SYS 750', 'SYS 800'], ['SYS 612', 'SYS 671'],
                              ['SSW 540', 'SSW 565', 'SSW 810']],
                    ['11658', 'Kelly, P', 'SYEN', [], ['SYS 612', 'SYS 671', 'SYS 800'],
                              ['SSW 540', 'SSW 565', 'SSW 810']],
                    ['11714', 'Morton, A', 'SYEN', ['SYS 611', 'SYS 645'], ['SYS 612', 'SYS 671', 'SYS 800'],
                              ['SSW 540', 'SSW 565', 'SSW 810']],
                    ['11788', 'Fuller, E', 'SYEN', ['SSW 540'], ['SYS 612', 'SYS 671', 'SYS 800'], 'None']]

        calculated = list(self.stevens.summary_students())
        self.assertEqual(expected, calculated)

    def test_major(self):
        """ test if the majors is setup properly """
        expected = {'SFEN': {'R': {'SSW 540', 'SSW 555', 'SSW 564', 'SSW 567'},
                             'E': {'CS 501', 'CS 513', 'CS 545'}},
                    'SYEN': {'R': {'SYS 612', 'SYS 671', 'SYS 800'},
                             'E': {'SSW 540', 'SSW 565', 'SSW 810'}}}
        calculated = dict()
        for major, info in self.stevens.majors.items():
            calculated[major] = {flag: courses for flag, courses in info.items()}

        self.assertEqual(expected, calculated)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
