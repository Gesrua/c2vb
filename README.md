# c2vb

A program convert simple C / C++ code to Visual Basic 6 code

### 特性

- 实现基本语法
- 简单类型推断（区分 `/` 和 `\`）

### 注意

- 不支持预处理命令(`#include` `#define` ...)
- `++`  `--` 是被看作赋值的，不能在表达式中出现。
- 不支持 `struct` `class`
- 高级语法一个都没有实现
  - 注意删掉 `cin/cout` 因为没有实现运算符重载
- `for(s1;s2;s3;)` `s1` 必须为赋值或定义，`s2` 必须为数学表达式，`s3` 必须为赋值
- 所有 `for` 都将被翻译为 `Do While ... Loop`
- 不支持 `do ... while()`
- 语句只有 if/for/while/return/break/const/变量定义/函数调用
  - 也就是说 表达式 加 `;` 当语句是不行的

### 贡献

欢迎提 bug, issue, pull request

### 支持的语法

```
statements   --> statement | statements statement
statement    --> if | while | for | const | declare | return | break
               | "{" statements "}"
               | call ";" | assigns ";"
program      --> program ( const | declare | func )
expr         --> 支持函数调用, 数组, `- ! ~ * / % + - < <= > >= == != & ^ | && ||`
               | 字符串常量
type         --> "int" | "float" | "double" | "string" | "void" | "bool"
identifier   --> ID | identifier"["expr"]"
call         --> identifier "(" ")"
               | identifier "(" expr ( "," expr )* ")"
assign_opt   --> "+=" | "-=" | "*=" | "/=" | "%=" 
               | "&=" | "^=" | "|=" | "="
assign       --> ( "++" | "--" ) identifier
               | identifier ( "++" | "--" )
               | identifier assign_opt expr
assigns      --> assign ( "," assign )*
arg          --> type identifier
func         --> type identifier "(" ")" statement
               | type identifier "(" arg ( "," arg )* ")" statement
const        --> "const" declare
if           --> "if" "(" expr ")" statement
               | "if" "(" expr ")" statement "else" statement
for          --> "for" "(" (declare | assigns ";" ) expr ";" assigns ")" statement
while        --> "while" "(" expr ")" statement
return       --> "return"
               | "return" expr ";"
break        --> "break" ";"
declare_item --> identifier
               | identifier "=" expr
declare      --> type declare_item ( "," declare_item )* ";"
```
