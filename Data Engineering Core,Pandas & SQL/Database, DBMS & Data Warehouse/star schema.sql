create database sales_dw;

use sales_dw;

create table dim_date (
    date_key int primary key,
    full_date date,
    day int,
    month int,
    month_name varchar(20),
    quarter int,
    year int
);

create table dim_customer (
    customer_key int primary key auto_increment,
    customer_id varchar(20),
    customer_name varchar(100),
    gender varchar(10),
    city varchar(50),
    country varchar(50)
);

create table dim_product (
    product_key int primary key auto_increment,
    product_id varchar(20),
    product_name varchar(100),
    category varchar(50),
    brand varchar(50),
    price decimal(10,2)
);

create table dim_store (
    store_key int primary key auto_increment,
    store_id varchar(20),
    store_name varchar(100),
    city varchar(50),
    country varchar(50)
);

create table fact_sales (
    sales_key int primary key auto_increment,
    date_key int,
    customer_key int,
    product_key int,
    store_key int,
    quantity int,
    total_amount decimal(12,2),
    foreign key (date_key) references dim_date(date_key),
    foreign key (customer_key) references dim_customer(customer_key),
    foreign key (product_key) references dim_product(product_key),
    foreign key (store_key) references dim_store(store_key)
);

insert into dim_date values
(20240101,'2024-01-01',1,1,'january',1,2024),
(20240102,'2024-01-02',2,1,'january',1,2024);

insert into dim_customer (customer_id,customer_name,gender,city,country) values
('c001','arun kumar','male','chennai','india'),
('c002','priya sharma','female','mumbai','india');

insert into dim_product (product_id,product_name,category,brand,price) values
('p001','laptop','electronics','dell',60000.00),
('p002','mobile','electronics','samsung',20000.00);

insert into dim_store (store_id,store_name,city,country) values
('s001','central mall','chennai','india'),
('s002','city plaza','mumbai','india');

insert into fact_sales (date_key,customer_key,product_key,store_key,quantity,total_amount) values
(20240101,1,1,1,2,120000.00),
(20240102,2,2,2,1,20000.00);

select * from dim_date;

select * from dim_customer;

select * from dim_product;

select * from dim_store;

select * from fact_sales;

select count(*) as total_sales from fact_sales;

select sum(total_amount) as total_revenue from fact_sales;

select p.product_name,
       sum(f.quantity) as total_quantity_sold
from fact_sales f
join dim_product p
on f.product_key=p.product_key
group by p.product_name;

select c.customer_name,
       sum(f.total_amount) as total_spent
from fact_sales f
join dim_customer c
on f.customer_key=c.customer_key
group by c.customer_name;

select d.year,
       sum(f.total_amount) as yearly_revenue
from fact_sales f
join dim_date d
on f.date_key=d.date_key
group by d.year;

select s.store_name,
       sum(f.total_amount) as store_revenue
from fact_sales f
join dim_store s
on f.store_key=s.store_key
group by s.store_name;
