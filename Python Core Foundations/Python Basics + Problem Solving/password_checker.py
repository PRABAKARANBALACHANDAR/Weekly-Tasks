password =input ("Enter your password: ")
if len (password )<8 :
    print ("Password must be at least 8 characters long")
    exit ()
c_count =i_count =0 
for char in password :
    if char .isdigit ():
        c_count +=1 
        continue 
    elif char .isupper ():
        i_count +=1 
        continue 
    else :
        continue 
if c_count >=2 and i_count >=2 :
    print ("Strong Password")
elif c_count ==1 and i_count ==1 :
    print ("Medium Password")
else :
    print ("Weak Password")
