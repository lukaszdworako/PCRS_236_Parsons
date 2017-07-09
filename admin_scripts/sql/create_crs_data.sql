CREATE DATABASE crs_data;

CREATE ROLE instructors;
GRANT ALL PRIVILEGES ON DATABASE crs_data TO instructors;

-- The following requires that we not use peer authentication
-- since 'instructor' is not a user. Make sure the following 
-- line is set within /etc/postgresql/VERSION/main/pg_hba.conf
-- local   crs_data     all                                     md5
CREATE USER instructor with password 'instructor';
GRANT instructors to instructor;
CREATE ROLE students;

-- -- An example of creating an instructor
-- CREATE user diane with password 'diane';
-- GRANT instructors to diane;

-- -- An example of creating a student
-- CREATE user noel with password 'noel';
-- GRANT students to noel;

-- Setup the testing database
CREATE DATABASE crs_data_test;
CREATE ROLE dev;
GRANT ALL ON DATABASE crs_data_test TO dev;
