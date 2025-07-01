Store 0 $1   ;x = 1
Store 1 $1   ;y = 1
Store 2 $0   ;t = 0
Store 3 $10   ;counter = 10
label loop
store 2 1   ; t = y  
add 1 0 1    ; y+= x
store 0 2  ; x = t same as t = y
sub 3 $1 3
jumpIf 3 != $0 loop



