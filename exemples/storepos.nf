store 0 $420
print 0

store 1 $69
storePos 100
jump testLabel
print 0
print 1

jump end

label testLabel
store 0 1
store 1 $1312
jumpPos 100

label end
