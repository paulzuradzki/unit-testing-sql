/* Pivot and unpivot 

This is just to demo testing a multi-step CTE.
*/
WITH grouped AS
  (SELECT region, sum(amount) AS sale_amount
   FROM orders
   GROUP BY region
   ORDER BY region),
     pivoted AS
  (SELECT sum(CASE WHEN region = 'East' THEN sale_amount END) AS sales_east,
          sum(CASE WHEN region = 'North' THEN sale_amount END) AS sales_north,
          sum(CASE WHEN region = 'South' THEN sale_amount END) AS sales_south,
          sum(CASE WHEN region = 'West' THEN sale_amount END) AS sales_west
   FROM grouped)
SELECT 'East' AS region, sales_east AS sale_amount
FROM pivoted
UNION ALL
SELECT 'North' AS region, sales_north AS sale_amount
FROM pivoted
UNION ALL
SELECT 'South' AS region, sales_south AS sale_amount
FROM pivoted
UNION ALL
SELECT 'West' AS region, sales_west AS sale_amount
FROM pivoted;