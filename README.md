# c2vb

A Python program convert simple C / C++ code to Visual Basic 6 code

Warning: only support very little C / C++ grammar

### 特性

将 C / C++ 转成 AST 再转成 VB

- 实现基本语法
- 简单类型推断（区分 `/` 和 `\`）
- 可打印带缩进 AST
- 可生成 Graphviz dot 语言 AST

### 使用方法

```bash
$ pip install c2vb
$ c2vb sample.c
$ c2vb sample.cpp
```

```python
import c2vb

f = open('sample.c', 'r')
src = f.read()
lex = c2vb.Lexer(src) # 词法
parser = c2vb.Parser(lex.tokens) # 语法
c2vb.proc(parser.ast) # 类型推断

parser.ast.vb() == c2vb.run(file='sample.c') == c2vb.run(src=src) # 返回 VB 代码
parser.ast.dot() # 返回以 dot 语言表示的 AST
str(parser.ast) # 返回字符串带缩进 AST
```

### 注意

- 不支持预处理命令(`#include` `#define` ...)
  - 可以试试 `g++ -E file.cpp` 来处理 `#define`
- `++`  `--` 是被看作赋值的，不能在表达式中出现。
- 不支持 `struct` `class`
- 不支持数组初始化
  - 也就是说 `const` 数组不行
- 不能连赋值 `a=b=c`
- 高级语法一个都没有实现
  - 注意删掉 `cin/cout` 因为没有实现运算符重载
- `for(s1;s2;s3;)` `s1` 必须为赋值或定义，`s2` 必须为数学表达式，`s3` 必须为赋值
- 所有 `for` 都将被翻译为 `Do While ... Loop`
- 不支持 `do ... while()`
- 语句只有 if/for/while/return/break/const/变量定义/函数调用
  - 也就是说 表达式 加 `;` 当语句是不行的
- 类型只有 `int/float/double/bool/string`

### 贡献

欢迎提 bug, issue, pull request

TODO:

- 表达式中含有 `++` `--`
  - 这件事比较麻烦因为这会把一个赋值变成两三个
- 连赋值 `a=b=c`
- 特殊 `for` 翻译成 `For` （遥遥无期）
- C / C++ 中常用函数写入语法之中方便运行
- 数组初始化
- `string` 特异化

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
