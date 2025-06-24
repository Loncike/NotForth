## OPs:

<table>
  <thead>
    <tr>
      <th>Instruction</th>
      <th>Arguments</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>store</td>
      <td>&lt;idx&gt; &lt;idx|num&gt;</td>
      <td>Stores a value at the specified index. If the second argument is a number, it stores that number directly. If it’s an index, it copies the value from that index to the target index.</td>
    </tr>
    <tr>
      <td>add</td>
      <td>&lt;idx|num&gt; &lt;idx|num&gt; &lt;store idx&gt;</td>
      <td>Takes the first two arguments (which can be either indices or numbers), performs addition, and stores the result at the index specified by the third argument.</td>
    </tr>
    <tr>
      <td>sub</td>
      <td>&lt;idx|num&gt; &lt;idx|num&gt; &lt;store idx&gt;</td>
      <td>Takes the first two arguments (which can be either indices or numbers), performs subtraction, and stores the result at the index specified by the third argument.</td>
    </tr>
    <tr>
      <td>jumpIf</td>
      <td>&lt;idx|num&gt; &lt;logic op&gt; &lt;idx|num&gt; &lt;label to jump to&gt;</td>
      <td>Compares the first two arguments (which can be numbers or indices) using a logical operator, and jumps to the specified label if the condition is true.</td>
    </tr>
    <tr>
      <td>jump</td>
      <td>&lt;label&gt;</td>
      <td>Unconditionally jumps to the specified label.</td>
    </tr>
    <tr>
      <td>storePos</td>
      <td>&lt;idx&gt;</td>
      <td>Saves the current position (instruction pointer) to the specified index</td>
    </tr>
    <tr>
      <td>jumpPos</td>
      <td>&lt;idx&gt;</td>
      <td>Jumps to the position previously stored at the given index.</td>
    </tr>
    <tr>
      <td>syscallargs</td>
      <td>&lt;num&gt;</td>
      <td>Specifies the total number of arguments that will be passed to the upcoming syscall, including the syscall number itself.</td>
    </tr>
    <tr>
      <td>syscall</td>
      <td>&lt;idx|num&gt;</td>
      <td>Executes a system call using the specified syscall number and the arguments provided.</td>
    </tr>
  </tbody>
</table>
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

