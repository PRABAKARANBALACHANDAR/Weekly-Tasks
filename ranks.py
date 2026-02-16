stud={}
sub=['Tamil','English','Maths','Science','Social']
while True:
    student_id=int(input("Enter id or '0' to quit:"))
    if student_id==0:
        break
    stud_marks={}
    total=0
    for i in range(5):
        mark=int(input(f"Enter mark for {sub[i]}:"))
        stud_marks[sub[i]]=mark
        total+=mark
    stud[student_id]=stud_marks
    stud[student_id]['total']=total
    stud[student_id]['rank']=0


def assign_ranks(student_data):
    sorted_stud = dict(sorted(student_data.items(), key=lambda x: x[1]['total'], reverse=True))

    prev_total = None
    prev_rank = 0
    current_rank = 0

    for index, (student_id, data) in enumerate(sorted_stud.items(), start=1):
        current_rank = index
        
        if data['total'] == prev_total:
            data['rank'] = prev_rank
        else:
            data['rank'] = current_rank
            prev_rank = current_rank
        
        prev_total = data['total']
    
    return sorted_stud

stud = assign_ranks(stud)
print(stud)

    



