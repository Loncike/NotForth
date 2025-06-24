## OPs:

| Instruction   | Arguments                         | Description               |
|---------------|---------------------------------|---------------------------|
| store         | `<idx> <idx|num>`                |  Stores a value at the specified index. If the second argument is a number, it stores that number directly. If it’s an index, it copies the value from that index to the target index. |
| add           | `<idx|num> <idx|num> <store idx>`|  Takes the first two arguments (which can be either indices or numbers), performs addition, and stores the result at the index specified by the third argument. |
| sub           | `<idx|num> <idx|num> <store idx>`|  Takes the first two arguments (which can be either indices or numbers), performs subtraction, and stores the result at the index specified by the third argument.|
| jumpIf        | `<idx|num> <logic op> <idx|num> <label to jump to>` |  Compares the first two arguments (which can be numbers or indices) using a logical operator, and jumps to the specified label if the condition is true.|
| jump          | `<label>`                       |  Unconditionally jumps to the specified label.|
| storePos      | `<idx>`                        | Saves the current position (instruction pointer) to the specified index|
| jumpPos       | `<idx>`                  | Jumps to the position previously stored at the given index.|
| syscallargs   | `<num>`                        | Specifies the total number of arguments that will be passed to the upcoming syscall, including the syscall number itself.|
| syscall       | `<idx|num>`                    | Executes a system call using the specified syscall number and the arguments provided.                          |
> **Note**: Numbers must be prefixed with $. For example, store 0 $44 stores the number 44 at index 0, whereas store 0 1 copies the value from index 1 to index 0.

## Logic ops:
| Operator | Meaning          |
|----------|------------------|
| ==       | Equal to         |
| !=       | Not equal to     |
| <        | Less than        |
| <=       | Less than or equal to |
| >        | Greater than     |
| >=       | Greater than or equal to |

