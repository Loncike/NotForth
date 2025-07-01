store 0 $1   ;x = 0
store 1 $1   ;y = 1
store 2 $0   ;t = 0

store 3 $10   ;i = 10
label forloop
store 2 0     ; t = x  
add 0 1 0     ; x = x+y
store 1 2     ; y = t 
printnum 0    ; print x
sub 3 $1 3    ; i = i-1
jumpif 3 != $0 forloop



