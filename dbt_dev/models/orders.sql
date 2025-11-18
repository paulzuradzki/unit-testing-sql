/* Minimal orders model for unit testing */
SELECT
    'North'::text AS region,
    'Apple'::text AS item,
    100::int AS amount
LIMIT 0  -- Returns no rows, just defines the schema