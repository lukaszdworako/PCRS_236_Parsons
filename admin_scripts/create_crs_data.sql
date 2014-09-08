CREATE DATABASE crs_data;

CREATE ROLE instructors;
GRANT ALL PRIVILEGES ON DATABASE crs_data TO instructors;

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