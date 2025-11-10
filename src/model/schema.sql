CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0)
);

INSERT OR IGNORE INTO products (name, quantity) VALUES ('Apple', 50);
INSERT OR IGNORE INTO products (name, quantity) VALUES ('Banana', 75);
INSERT OR IGNORE INTO products (name, quantity) VALUES ('Onion', 30);
INSERT OR IGNORE INTO products (name, quantity) VALUES ('Milk', 20);
INSERT OR IGNORE INTO products (name, quantity) VALUES ('Bread', 40);
INSERT OR IGNORE INTO products (name, quantity) VALUES ('Egg', 60);
INSERT OR IGNORE INTO products (name, quantity) VALUES ('Cheese', 15);