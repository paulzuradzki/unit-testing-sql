create table orders (
    id serial primary key,
    region text,
    item text,
    amount integer
);
-- constraints
-- region must be one of the following: 'North', 'South', 'East', 'West'
alter table orders
add constraint region_check check (region in ('North', 'South', 'East', 'West'));
-- amount must be greater than 0
alter table orders
add constraint amount_check check (amount > 0);
-- insert data
insert into orders (region, item, amount)
values ('North', 'Apple', 100);
insert into orders (region, item, amount)
values ('South', 'Banana', 200);
insert into orders (region, item, amount)
values ('East', 'Cherry', 300);
insert into orders (region, item, amount)
values ('West', 'Date', 400);
insert into orders (region, item, amount)
values ('East', 'Elderberry', 300);
insert into orders (region, item, amount)
values ('West', 'Fig', 400);