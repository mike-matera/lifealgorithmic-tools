# Massage imported data for the Cabrillo Courses schema. 

# create schema matera_cabrillo_courses; 

drop table if exists program_course; 
drop table if exists program; 
drop table if exists course; 

create table course (
	ControlNumber char(12) primary key,
    CourseID char(12),
    TOPCode char(6), 
    CreditStatus char(1), 
    MaximumUnits float,
    MinimumUnits float, 
    SAMCode char(1), 
    Date date
);

insert into course 
	select `Control Number`, `Course ID`, `TOP Code`, 
		`Credit Status`, `Maximum Units`, `Minimum Units`, 
		`SAM Status`, `Issue/Update Date`
	from MasterCourseFile;

create table program ( 
	ControlNumber char(5) primary key,
    Title varchar(64),
    TOPCode char(6),
    AwardType char(1),
    CreditType char(1),
    ApprovedDate date,
    Status varchar(16),
    InactiveDate date
);

# Truncates some dates that also have time of day. Ignore.
insert into program (ControlNumber, Title, TOPCode, AwardType, CreditType, ApprovedDate, Status, InactiveDate)
	select `Program Control Number`, `Title`, `TOP Code`, `Program Award`,
		`Credit Type`, IF (`Approved Date` = '', NULL, `Approved Date`),
        TRIM(`Proposal Status`), IF (`Inactive Date` = '', NULL, `Inactive Date`)
	from ProgramFile
    where `Program Control Number` != '';


create table program_course (
	ProgramControlNumber char(5),
    CourseControlNumber char(12),
    constraint primary key (ProgramControlNumber, CourseControlNumber),
    constraint prog_course_fk_1 foreign key (ProgramControlNumber)
		references program (ControlNumber),
    constraint prog_course_fk_2 foreign key (CourseControlNumber)
		references course (ControlNumber)
);

insert into program_course (ProgramControlNumber, CourseControlNumber)
	select `Program Control Number`, `Course Control Number`
    from ProgramCourseFile
    where `Program Control Number` != '';
    