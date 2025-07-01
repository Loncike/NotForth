macro write buf len
syscall $1 $1 buf len
end
