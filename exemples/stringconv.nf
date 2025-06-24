;; Mult take 0-2 idx
macro mult  ;; will work on idx 0 1 and result will go in 0
jumpif 0 == $0 multbyzero
jumpif 1 == $0 multbyzero
store 2 0
store 0 $0
label multloop
sub 2 $1 2
add 0 1 0
jumpif 2 > $0 multloop
jump multend
label multbyzero
store 0 $0
label multend
end

macro strconv ;;  20 for lenght; 21 for ptr

label strconvloop
store 0 10
store 1 $10
mult
store 10 0

sub @21 $48 @21 ;; ptr - 48 
add @21 10 10  ;; acc + ptr

sub 20 $1 20
add 21 $1 21

jumpif 20 != $0 strconvloop
end

store 10 $0 ;; Acc
;; string
store 21 $22
store 22 $53 
store 23 $52
store 20 $2 ;; strlenght

strconv

