/*
 Sum and pivot
 */
with grouped as (
	select region,
		sum(amount) as sale_amount
	from orders
	group by region
	order by region
)
select sum(
		case
			when region = 'East' then sale_amount
		end
	) as sales_east,
	sum(
		case
			when region = 'North' then sale_amount
		end
	) as sales_north,
	sum(
		case
			when region = 'South' then sale_amount
		end
	) as sales_south,
	sum(
		case
			when region = 'West' then sale_amount
		end
	) as sales_west
from grouped;