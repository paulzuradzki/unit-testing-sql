/* Sum and pivot */
WITH grouped AS
  (SELECT region, sum(amount) AS sale_amount
   FROM orders
   GROUP BY region
   ORDER BY region)
SELECT sum(CASE WHEN region = 'East' THEN sale_amount END) AS sales_east,
       sum(CASE WHEN region = 'North' THEN sale_amount END) AS sales_north,
       sum(CASE WHEN region = 'South' THEN sale_amount END) AS sales_south,
       sum(CASE WHEN region = 'West' THEN sale_amount END) AS sales_west
FROM grouped;