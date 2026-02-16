select count(*) as total_students from students;

select avg(score_avg) as avg_score from students;

select sum(pass_flag) / count(*) * 100 as pass_rate_pct from students;

select student_id, score_avg from students order by score_avg desc limit 5;

select age_group, count(*) as students, round(avg(score_avg),2) as avg_score
from students
group by age_group
order by students desc;
