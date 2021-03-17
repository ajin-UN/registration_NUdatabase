
DELIMITER //

CREATE PROCEDURE enrollcourse(
IN code CHAR(10),
IN ID CHAR(10),
IN year CHAR(10),
IN semester CHAR(10),
out x integer)
BEGIN
	IF (SELECT * FROM (SELECT PrereqUoSCode FROM requires WHERE UoSCode = code) T WHERE PrereqUoSCode NOT IN (SELECT UoSCode FROM transcript WHERE Grade is not null)) IS NULL THEN
		INSERT INTO transcript VALUE(ID, code, semester, year, null);
        update uosoffering set Enrollment = Enrollment + 1 where UoSCode = code;
        set x = 0;
	ELSE
		set x = 1;
	END IF;
END; //

DELIMITER ;

DROP PROCEDURE enrollcourse;




DELIMITER //
CREATE PROCEDURE withdraw(
IN code char(10),
IN ID CHAR(10),
OUT warn Integer)
begin
	update transcript SET Grade = 1 WHERE UoSCode = code;
    select Grade into warn from transcript where UoSCode = code and StudId = ID;
	delete from transcript where UoSCode = code and StudId = ID;
    update uosoffering set Enrollment = Enrollment - 1 where UoSCode = code;
    
end; // 
DELIMITER ;

drop procedure withdraw;

-- If the Enrollment number goes below 50% of the MaxEnrollment, then a warning
-- message should 
delimiter //
CREATE TRIGGER enrollment_check before update ON `project3-nudb`.transcript
FOR EACH ROW
BEGIN
	IF (select Enrollment from uosoffering where uosoffering.UoSCode = new.UoSCode and uosoffering.Semester = new.Semester and uosoffering.Year = new.Year) < (select MaxEnrollment from uosoffering where uosoffering.UoSCode = new.UoSCode and uosoffering.Semester = new.Semester and uosoffering.Year = new.Year)
    THEN
        set new.Grade = 0 ;
	END IF;
END;//
delimiter ;

drop trigger enrollment_check;






