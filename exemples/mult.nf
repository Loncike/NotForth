input 0
input 1

store 100 0 ;; copy 0 into 100, the idx mult uses
store 101 1 ;; same
storepos 102
jump mult
store 0 103 ;;copy back from 103 to 0
print 0
exit

; 100, 101 idx x, y; 102 idx return pos; 103 stores the return value 
label mult
add 100 103 103
sub 101 $1 101
jumpif 101 != $0 mult 
jumppos 102


