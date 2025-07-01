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
      <td>printnum</td>
      <td>&lt;idx|num&gt;</td>
      <td>print the number to the stdout</td>
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
      <td>syscall</td>
      <td>&lt;idx|num&gt;</td>
      <td>Executes a system call using the specified syscall number and the arguments provided.</td>
    </tr>
    <tr>
      <td>include</td>
      <td>&lt;str&gt;</td>
      <td>Includes other .nf files</td>
    </tr>
  </tbody>
</table>

> **Note**: Numbers must be prefixed with $. For example, store 0 $44 stores the number 44 at index 0, whereas store 0 1 copies the value from index 1 to index 0.

> To dereference a pointer (i.e., access the value at the address stored in a memory index), prefix the index with @.
> **Note**: The @ prefix is used only for reading (dereferencing). Writing to a dereferenced pointer must be done manually.
## Logic ops:
| Operator | Meaning          |
|----------|------------------|
| ==       | Equal to         |
| !=       | Not equal to     |
| <        | Less than        |
| <=       | Less than or equal to |
| >        | Greater than     |
| >=       | Greater than or equal to |

