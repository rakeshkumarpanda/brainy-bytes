-- Sunrise School: students, teachers, courses and marks.
CREATE TABLE teachers (
  id    INTEGER PRIMARY KEY,
  name  TEXT NOT NULL,
  subject TEXT NOT NULL
);
CREATE TABLE students (
  id     INTEGER PRIMARY KEY,
  name   TEXT NOT NULL,
  class  INTEGER NOT NULL,
  city   TEXT,
  house  TEXT
);
CREATE TABLE courses (
  id          INTEGER PRIMARY KEY,
  title       TEXT NOT NULL,
  teacher_id  INTEGER REFERENCES teachers(id)
);
CREATE TABLE marks (
  student_id  INTEGER NOT NULL REFERENCES students(id),
  course_id   INTEGER NOT NULL REFERENCES courses(id),
  score       INTEGER CHECK (score BETWEEN 0 AND 100),
  PRIMARY KEY (student_id, course_id)
);
INSERT INTO teachers VALUES
 (1, 'Mrs Rao',   'Maths'),
 (2, 'Mr Das',    'Science'),
 (3, 'Ms Iyer',   'English'),
 (4, 'Mr Khan',   'Art');
INSERT INTO students VALUES
 (1, 'Anu',    8, 'Pune',    'Red'),
 (2, 'Bala',   8, 'Chennai', 'Blue'),
 (3, 'Chitra', 9, 'Pune',    'Green'),
 (4, 'Dev',    9, 'Delhi',   'Red'),
 (5, 'Esha',   10, 'Delhi',  'Blue'),
 (6, 'Farhan', 10, NULL,     'Green'),
 (7, 'Gauri',  8, 'Chennai', NULL),
 (8, 'Hari',   9, 'Pune',    'Blue');
INSERT INTO courses VALUES
 (1, 'Algebra',      1),
 (2, 'Physics',      2),
 (3, 'Poetry',       3),
 (4, 'Chemistry',    2),
 (5, 'Robotics',     NULL);
INSERT INTO marks VALUES
 (1, 1, 92), (1, 2, 78), (1, 3, 85),
 (2, 1, 64), (2, 3, 71),
 (3, 1, 88), (3, 2, 95), (3, 4, 81),
 (4, 2, 55), (4, 4, NULL),
 (5, 1, 99), (5, 3, 90), (5, 4, 87),
 (6, 2, 47),
 (7, 3, 76);
