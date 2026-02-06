num1 =[1 ,5 ,7 ,8 ,10 ,12 ,15 ,18 ,20 ,22 ,25 ,30 ]
num =tuple (num1 )
def use_filter (num ):
    even =list (filter (lambda x :x %2 ==0 ,num ))
    odd =list (filter (lambda x :x %2 !=0 ,num ))
    print ("Even numbers using filter:",even )
    print ("Odd numbers using filter:",odd )
use_filter (num )
def without_filter (num ):
    even_numbers =[x for x in num if x %2 ==0 ]
    odd_numbers =[x for x in num if x %2 !=0 ]
    print ("Even numbers:",even_numbers )
    print ("Odd numbers:",odd_numbers )
without_filter (num )
