from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

db_file = '/Users/kriswen/Documents/GitHub/SSW810/810_startup.db'


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/student_courses')
def student_courses():
    db = sqlite3.connect(db_file)
    query = """select s.CWID, s.Name, s.Major, count(g.Course) as complete
               from Students s join Grades g on s.CWID=g.Student_CWID
               group by s.CWID, s.Name, s.Major"""

    results = db.execute(query)
    data = [{'cwid': cwid, 'name': name, 'major': major, 'complete': complete}
            for cwid, name, major, complete in results]
    db.close()

    return render_template('students_courses.html',
                           title="Stevens Repository",
                           my_header="Stevens Repository",
                           table_title="Number of completed courses by Student",
                           students=data)


@app.route('/choose_student')
def choose_student():
    db = sqlite3.connect(db_file)
    query = "select CWID, Name from Students group by CWID, Name"

    results = db.execute(query)
    students = [{'cwid': cwid, 'name': name} for cwid, name in results]
    db.close()
    return render_template('student.html', students=students)


# @app.route('/show_student', methods=['POST'])
# def show_student():
#     request =
#     if request.method == 'POST':
#         cwid = request.form['cwid']
#
#         query = "select Course, Grade from Grades where Student_CWID = ?"
#         args = (cwid,)
#         table_title = "Courses/Grades for CWID {}".format(cwid)
#
#         db = sqlite3.connect(db_file)
#         results = db.execute(query, args)
#         rows = [{'course': course, 'grade': grade} for course, grade in results]
#         db.close()
#
#         return render_template('display_student_grade.html',
#                                title="Stevens Repository",
#                                table_title=table_title,
#                                rows=rows)


@app.route('/instructors')
def instructors():
    db = sqlite3.connect(db_file)
    query = """select CWID, Name, Dept, Course, Students from Instructors left join
                    (select Instructor_CWID, Course, count(Student_CWID) as Students from Grades group by Course)
               where Instructors.CWID = Instructor_CWID"""

    results = db.execute(query)
    data = [{'cwid': cwid, 'name': name, 'dept': dept, 'courses': courses, 'students': students}
            for cwid, name, dept, courses, students in results]
    db.close()
    return render_template('instructors.html',
                           title="Stevens Repository",
                           my_header="Stevens Repository",
                           table_title="Number of students by course and instructor",
                           instructors=data)


if __name__ == '__main__':
    app.run(debug=True)
