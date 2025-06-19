Store 0 1   ;x = 1
Store 1 1   ;y = 1
Store 2 0   ;t = 0
Store 3 10   ;counter = 10
Store 100 0 ;const for 0
Store 101 1 ;const for 1
label loop
print 0
add 1 100 2  ; t = y  we add y to 0 and save it to t 
add 1 0 1    ; y+= x
add 2 100 0  ; x = t same as t = y
sub 3 101 3
jumpIf 3 != 100 loop



