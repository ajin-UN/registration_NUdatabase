import mysql.connector
import datetime

#connect python with mysql
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="tt287593",
  database="project3-nudb"
)
mydb.autocommit = False
mycursor = mydb.cursor()

def login():
    username = input('please input username: ')
    password = input('please input password: ')
    mycursor.execute("SELECT * FROM student WHERE Id = %s and Password = binary %s", (username, password,))
    row = mycursor.fetchall()
    if len(row) == 1:
        print("Student", username, "log-in successfully.")
        print("-------------------------------------------------------------------------------")

        return row[0][0]
    print("Login Failed! username and/or password you entered was invalid. Please try again")
    print("-------------------------------------------------------------------------------")
    login()


def course(ID):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    if month >= 6:
        quarter = "Q2"
    else:
        quarter = "Q1"
    id = str(ID)
    year = str(year)
    sql = "SELECT transcript.UoSCode, unitofstudy.UoSName, Grade FROM transcript, unitofstudy WHERE Semester =%s and StudId = %s " \
          "and year = %s and transcript.UoSCode = unitofstudy.UoSCode "
    d = (quarter, id, year,)
    mycursor.execute(sql, d)
    print("This is the courses you has taken in", quarter, year)
    print("-------------------------------------------------------------------------------")
    for row in mycursor.fetchall():
        print("Class title:  ", row[1])
        print("Class number: ", row[0])
        print("Grade:        ", row[2])
        print(" ")
    print("-------------------------------------------------------------------------------")
    option = display_menu()
    return option


def display_menu():
    #Transcript, Enroll, Withdraw, Personal Details and Logout.
    print("This is the student menu screen:")
    print("**********************************")
    print("1. Transcript")
    print("2. Enroll")
    print("3. Withdraw")
    print("4. Personal Details")
    print("5. Logout")
    print("**********************************")
    option = input('please enter number from 1-5 to choose an option: ')
    return option

# figure 3. The TRANSCRIPT screen: full transcript with all courses and grades
def transcript(student_id):

    class_numbers = []
    class_names = []
    class_grades = []
    mycursor.execute("SELECT * FROM transcript")
    transcripts = mycursor.fetchall()
    mycursor.execute("SELECT UoSCode, UoSName FROM unitofstudy")
    unitofstudy = mycursor.fetchall()
    mycursor.execute("SELECT * FROM uosoffering")
    uosoffering = mycursor.fetchall()
    mycursor.execute("SELECT * FROM faculty")
    faculty = mycursor.fetchall()

    print("This is the transcript for studentID: ", student_id)
    print("-----------------------------------------------------------")
    for row in transcripts:
        for row_u in unitofstudy:
            if row[0] == student_id and row_u[0] == row[1]:
                class_names.append(row_u[1])
                class_numbers.append(row[1])
                class_grades.append(row[-1])
                print("Class title:  ", row_u[1])
                print("Class number: ", row[1])
                print("Grade:        ", row[-1])
                print("")
    print("-----------------------------------------------------------")
    print("You can either enter an class number listed above to see the class details")
    print("or go back to the student menu by enter 'BACK': ")
    option = input("Please enter your option here: ")
    if option == "BACK":
        main(ID)
    elif option in class_numbers:
        for i in range(0, len(class_numbers)):
            for row_o in uosoffering:
                for row_f in faculty:
                    if class_numbers[i] == option and option == row_o[0] and row_o[-1] == row_f[0]:
                        print("___________________________________________")
                        print("Following is the details of ", option, ": ")
                        print("Class number:      ", option)
                        print("Class name:        ", class_names[i])
                        print("Year:              ", row_o[2])
                        print("Quatar:            ", row_o[1])
                        print("Enrollment:        ", row_o[4])
                        print("Max enrollment     ", row_o[5])
                        print("Instructor name    ", row_f[1])
                        print("___________________________________________")
                        print("")
                        transcript(student_id)

    else:
        print("This is an invalid input, please enter again: ")
        transcript(student_id)


def enroll(ID):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    if month > 6:
        quarter = "Q2"
        nextyear = year + 1
        nextquarter = "Q1"
    else:
        quarter = "Q1"
        nextyear = year
        nextquarter = "Q2"
    year = str(year)
    nextyear = str(nextyear)
    id = str(ID)
    # courses in this quarter and next quarter
    sql = "select lecture.UoSCode, UoSName, lecture.Semester, lecture.Year, lecture.ClassTime, Enrollment, MaxEnrollment " \
          "from lecture, uosoffering, unitofstudy where ((lecture.year = %s and lecture.Semester = %s) or (lecture.year = %s and lecture.Semester = %s)) " \
          "and lecture.UoSCode = uosoffering.UoSCode and lecture.Year = uosoffering.Year and lecture.Semester = uosoffering.Semester and unitofstudy.UoSCode = lecture.UoSCode "

    d = (year, quarter, nextyear, nextquarter,)
    mycursor.execute(sql, d)
    course = mycursor.fetchall()

    #course student has passed
    sql = "select distinct UoSCode from transcript where Grade is not null and StudId = %s"
    d = (id,)
    mycursor.execute(sql,d)
    stucourse = mycursor.fetchall()

    #course student has taken
    sql = "select distinct UoSCode from transcript where StudId = %s"
    d = (id,)
    mycursor.execute(sql, d)
    stu = mycursor.fetchall()

    i = 1
    select_course = []
    canenroll = []
    print("This is the enroll for studentID: ", id)
    print("-----------------------------------------------------------")
    for row in course:
        take = True
        for s in stu:
            if row[0] == s[0]:
                take = False
        if take == True:
            print(i,". Class title:          ", row[1])
            print("    Class number:         ", row[0])
            print("    Semester and Year:    ", row[2], row[3])
            print("    Class time:           ", row[4])
            print("")
            canenroll.append(row)
            select_course.append(str(i))
            i = i + 1

    print("-----------------------------------------------------------")
    print("You can either enter number from 1-", i - 1, "to enroll a course")
    print("or go back to the student menu by enter 'BACK': ")
    option = input("Please enter your option here: ")
    if option == "BACK":
        main(ID)
    elif option in select_course:
        option = int(option)
        c = canenroll[option - 1]
        print("___________________________________________")

        if c[5] < c[6]:
            y = 0
            try:
                v = mycursor.callproc('enrollcourse', [c[0], id, c[3], c[2],y,])
                mydb.commit()
            except mysql.connector.Error as error :
                print("Failed to update record to database rollback: {}".format(error))
                mydb.rollback()
            if v[4] == 0:
                print("Successfully enroll in this course!")
            if v[4] == 1:
                mycursor.execute("SELECT * FROM (SELECT PrereqUoSCode FROM requires WHERE UoSCode = %s) T WHERE PrereqUoSCode NOT IN "
                                 "(SELECT UoSCode FROM transcript WHERE Grade is not null)", (c[0],))
                print("SORRY! You can not enroll in this course, because you have not complete pre-requisites course: ")
                for row in mycursor.fetchall():
                    print(row[0])

        else:
            print("SORRY! You can not enroll in this course, because the maximum enrollment number has been reached.")
        print("___________________________________________")
        print("")
        enroll(ID)
    else:
        print("This is an invalid input, please enter again: ")
        enroll(ID)


def personalDetail(ID):
    print("This is the personal detail for studentID: ", ID)
    print("-----------------------------------------------------------")
    d = (str(ID),)
    mycursor.execute("SELECT * FROM student WHERE Id = %s", d)
    row = mycursor.fetchall()
    row = row[0]
    print("Student ID:       ", row[0])
    print("Student Name:     ", row[1])
    print("Student Address:  ", row[3])
    print("-----------------------------------------------------------")
    print("You can enter number 1 to change your password")
    print("You can enter number 2 to change your address")
    print("or go back to the student menu by enter 'BACK': ")
    option = input("Please enter your option here: ")
    if option == "BACK":
        main(ID)
    elif option == "1":
        newpassword = input("Please enter your new password:")
        update = "update student set Password = %s WHERE Id = %s"
        d = (newpassword, str(ID),)
        try:
            mycursor.execute(update, d)
            mydb.commit()
        except mysql.connector.Error as error :
                print("Failed to update record to database rollback: {}".format(error))
                mydb.rollback()

        personalDetail(ID)

    elif option == "2":
        newaddress = input("Please enter your new address:")
        update = "update student set Address = %s WHERE Id = %s"
        d = (newaddress,str(ID),)
        try:
            mycursor.execute(update, d)
            mydb.commit()
        except mysql.connector.Error as error :
                print("Failed to update record to database rollback: {}".format(error))
                mydb.rollback()

        personalDetail(ID)
    else:
        print("This is an invalid input, please enter again: ")
        personalDetail(ID)


def withdraw(ID):
    year = datetime.datetime.now().year
    nextyear = year + 1
    month = datetime.datetime.now().month
    if month >= 6:
        quarter = "Q2"
    else:
        quarter = "Q1"
    id = str(ID)
    year = str(year)
    nextyear = str(nextyear)
    sql = "SELECT transcript.UoSCode, unitofstudy.UoSName, Grade, transcript.Semester, transcript.Year FROM transcript, unitofstudy WHERE ((Semester =%s and year = %s) || (year = %s)) " \
          "and StudId = %s and transcript.UoSCode = unitofstudy.UoSCode and Grade is null"
    d = (quarter, year, nextyear, id,)
    mycursor.execute(sql, d)
    course = []
    print("You can withdraw these courses:")
    print("-------------------------------------------------------------------------------")
    for row in mycursor.fetchall():
        print("Class title:       ",     row[1])
        print("Class number:      ",     row[0])
        print("Semester and Year: ",     row[3], row[4])
        print("Grade:             ",     row[2])
        print(" ")
        course.append(row[0])
    print("-------------------------------------------------------------------------------")
    print("You can enter an class number listed above to withdraw the course")
    print("or go back to the student menu by enter 'BACK': ")
    mycursor.execute("SELECT * FROM uosoffering")
    uosoffering = mycursor.fetchall()
    option = input("Please enter your option here: ")

    if option == "BACK":
        main(ID)
    elif option in course:
        try:
            warn = 2
            w = mycursor.callproc('withdraw', [option,id,warn, ])
            mydb.commit()
            if w[2] == 0:
                print("Successfully withdraw the course!")
                print("WARNING::::enrollment number goes below 50% of the MaxEnrollment!")
                print("-------------------------------------------------------------------------------")
            else:
                print("Successfully withdraw the course!")
                print("-------------------------------------------------------------------------------")
        except mysql.connector.Error as error :
                print("Failed to update record to database rollback: {}".format(error))
                mydb.rollback()

        withdraw(ID)
    else:
        print("This is an invalid input, please enter again: ")
        print("-------------------------------------------------------------------------------")
        withdraw(ID)

def logout():
    login()

def main(ID):
    option = course(ID)
    if option == "1":
        transcript(ID)
    elif option == "2":
        enroll(ID)
    elif option == "3":
        withdraw(ID)
    elif option == "4":
        personalDetail(ID)
    elif option == "5":
        logout()
    else:
        print("This is an invalid input, please enter again: ")
        main(ID)

ID = login()
main(ID)



