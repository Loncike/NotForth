macro print
syscallargs $4
syscall $1 $0 100 99
end

store 99 $2
store 100 $72
store 101 $87

print


