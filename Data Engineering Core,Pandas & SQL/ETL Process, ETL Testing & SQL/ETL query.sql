create database if not exists sales_etl;

use sales_etl;

create table sales_stage (
    invoice_id varchar(50),
    invoice_date varchar(50),
    retailer varchar(100),
    region varchar(100),
    product varchar(100),
    price_per_unit varchar(50),
    units_sold varchar(50),
    total_sales varchar(50)
);

create table sales_data (
    invoice_id varchar(50) primary key,
    invoice_date date,
    retailer varchar(100),
    region varchar(100),
    product varchar(100),
    price_per_unit decimal(10,2),
    units_sold int,
    total_sales decimal(12,2)
);

set global local_infile=1;

load data local infile 'C:/Prabakaran Intern/Weekly-Tasks/Data Engineering Core,Pandas & SQL/ETL Process, ETL Testing & SQL/Adidas US Sales Datasets.csv'
into table sales_stage
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 rows;

update sales_stage
set price_per_unit=replace(replace(price_per_unit,'$',''),',','');

update sales_stage
set total_sales=replace(replace(total_sales,'$',''),',','');

update sales_stage
set units_sold=replace(units_sold,',','');

delete from sales_stage
where invoice_id is null or invoice_id='';

delete from sales_stage
where invoice_id in (
    select invoice_id from (
        select invoice_id
        from sales_stage
        group by invoice_id
        having count(*) > 1
    ) t
);

insert into sales_data
select
    invoice_id,
    str_to_date(invoice_date,'%m/%d/%Y'),
    retailer,
    region,
    product,
    cast(price_per_unit as decimal(10,2)),
    cast(units_sold as unsigned),
    cast(total_sales as decimal(12,2))
from sales_stage
where price_per_unit regexp '^[0-9.]+$'
and units_sold regexp '^[0-9]+$';

select count(*) as source_count from sales_stage;

select count(*) as target_count from sales_data;

select invoice_id,count(*)
from sales_data
group by invoice_id
having count(*) > 1;

select sum(cast(total_sales as decimal(12,2))) as source_total
from sales_stage
where total_sales regexp '^[0-9.]+$';

select sum(total_sales) as target_total
from sales_data;

select s.invoice_id,
       cast(s.units_sold as unsigned) as source_units,
       t.units_sold as target_units
from sales_stage s
join sales_data t
on s.invoice_id=t.invoice_id
where cast(s.units_sold as unsigned) <> t.units_sold;

select region,
       sum(total_sales) as regional_sales
from sales_data
group by region;

select retailer,
       sum(total_sales) as total_revenue
from sales_data
group by retailer
having sum(total_sales) > 100000;
