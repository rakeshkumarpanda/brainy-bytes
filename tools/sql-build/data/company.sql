-- Orbit Tech: departments and employees, with a manager for each employee.
CREATE TABLE departments (
  id        INTEGER PRIMARY KEY,
  name      TEXT NOT NULL UNIQUE,
  location  TEXT NOT NULL
);
CREATE TABLE employees (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  dept_id     INTEGER REFERENCES departments(id),
  manager_id  INTEGER REFERENCES employees(id),
  salary      INTEGER NOT NULL,
  hired       TEXT NOT NULL
);
INSERT INTO departments VALUES
 (1, 'Engineering', 'Bengaluru'),
 (2, 'Sales',       'Mumbai'),
 (3, 'Support',     'Bhubaneswar'),
 (4, 'Research',    'Hyderabad');
INSERT INTO employees VALUES
 (1,  'Priya',   1, NULL, 250000, '2018-04-02'),
 (2,  'Rahul',   1, 1,    150000, '2019-07-15'),
 (3,  'Sneha',   1, 2,     90000, '2022-01-10'),
 (4,  'Imran',   1, 2,     95000, '2021-11-01'),
 (5,  'Lata',    2, 1,    140000, '2019-03-20'),
 (6,  'Joseph',  2, 5,     70000, '2023-06-05'),
 (7,  'Kiran',   2, 5,     70000, '2022-09-12'),
 (8,  'Mohan',   3, 1,     85000, '2020-02-28'),
 (9,  'Tara',    3, 8,     45000, '2024-01-08'),
 (10, 'Zoya',    NULL, 1,  60000, '2025-05-19');
