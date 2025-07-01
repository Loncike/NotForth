macro print buf buf_len
syscall $1 $0 buf buf_len
end

store 100 $72
store 101 $87

print 100 $2


