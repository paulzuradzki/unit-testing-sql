CREATE TABLE orders (id serial PRIMARY KEY, region text, item text, amount integer);

ALTER TABLE orders ADD CONSTRAINT region_check CHECK (region IN ('North', 'South', 'East',
                                                                 'West'));
ALTER TABLE orders ADD CONSTRAINT amount_check CHECK (amount > 0);

INSERT INTO orders (region, item, amount)
VALUES ('North', 'Apple', 201);

INSERT INTO orders (region, item, amount)
VALUES ('South', 'Banana', 301);

INSERT INTO orders (region, item, amount)
VALUES ('East', 'Cherry', 401);

INSERT INTO orders (region, item, amount)
VALUES ('West', 'Date', 301);

INSERT INTO orders (region, item, amount)
VALUES ('East', 'Elderberry', 301);

INSERT INTO orders (region, item, amount)
VALUES ('West', 'Fig', 401);
