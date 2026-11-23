-- Bytes Bazaar: a small online shop used across the SQL chapters.
CREATE TABLE customers (
  id      INTEGER PRIMARY KEY,
  name    TEXT NOT NULL,
  city    TEXT,
  email   TEXT UNIQUE,
  joined  TEXT NOT NULL
);
CREATE TABLE products (
  id        INTEGER PRIMARY KEY,
  name      TEXT NOT NULL,
  category  TEXT NOT NULL,
  price     INTEGER NOT NULL CHECK (price > 0),
  stock     INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE orders (
  id           INTEGER PRIMARY KEY,
  customer_id  INTEGER REFERENCES customers(id),
  order_date   TEXT NOT NULL,
  status       TEXT NOT NULL
);
CREATE TABLE order_items (
  order_id    INTEGER NOT NULL REFERENCES orders(id),
  product_id  INTEGER NOT NULL REFERENCES products(id),
  qty         INTEGER NOT NULL CHECK (qty > 0),
  PRIMARY KEY (order_id, product_id)
);
INSERT INTO customers VALUES
 (1, 'Asha',   'Pune',        'asha@mail.in',   '2025-01-10'),
 (2, 'Ravi',   'Delhi',       'ravi@mail.in',   '2025-02-02'),
 (3, 'Meera',  'Chennai',     'meera@mail.in',  '2025-02-20'),
 (4, 'Kabir',  'Pune',        NULL,             '2025-03-05'),
 (5, 'Sara',   'Bhubaneswar', 'sara@mail.in',   '2025-03-18'),
 (6, 'Arjun',  NULL,          'arjun@mail.in',  '2025-04-01'),
 (7, 'Nisha',  'Delhi',       'nisha@mail.in',  '2025-04-22'),
 (8, 'Vikram', 'Chennai',     NULL,             '2025-05-09');
INSERT INTO products VALUES
 (1, 'Pencil box',      'Stationery',  120, 40),
 (2, 'Notebook',        'Stationery',   60, 150),
 (3, 'Water bottle',    'Kitchen',     250, 25),
 (4, 'Lunch box',       'Kitchen',     399, 0),
 (5, 'Headphones',      'Electronics', 1499, 12),
 (6, 'Phone charger',   'Electronics', 699, 30),
 (7, 'Cricket ball',    'Sports',      180, 60),
 (8, 'Football',        'Sports',      850, 8),
 (9, 'Desk lamp',       'Electronics', 1250, 0),
 (10, 'Geometry set',   'Stationery',   95, 70);
INSERT INTO orders VALUES
 (101, 1, '2025-06-01', 'delivered'),
 (102, 2, '2025-06-03', 'delivered'),
 (103, 1, '2025-06-10', 'shipped'),
 (104, 3, '2025-06-11', 'delivered'),
 (105, 5, '2025-06-15', 'cancelled'),
 (106, 7, '2025-06-18', 'delivered'),
 (107, 2, '2025-06-21', 'pending'),
 (108, 3, '2025-06-25', 'shipped'),
 (109, 5, '2025-07-02', 'delivered'),
 (110, 1, '2025-07-05', 'pending');
INSERT INTO order_items VALUES
 (101, 1, 2), (101, 2, 5),
 (102, 5, 1),
 (103, 3, 1), (103, 7, 3),
 (104, 6, 2), (104, 2, 10),
 (105, 8, 1),
 (106, 10, 4), (106, 1, 1),
 (107, 5, 1), (107, 6, 1),
 (108, 7, 2),
 (109, 2, 3), (109, 3, 2),
 (110, 8, 1);
CREATE TABLE warehouses (
  city      TEXT PRIMARY KEY,
  capacity  INTEGER NOT NULL
);
INSERT INTO warehouses VALUES
 ('Pune', 5000), ('Mumbai', 8000), ('Chennai', 4000), ('Kolkata', 3000);
