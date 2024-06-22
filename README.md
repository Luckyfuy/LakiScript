# LakiScript

## 语法

```bnf
statements -> NEWLINE* expr (NEWLINE+ statement)* NEWLINE*

statement -> KEYWORD:return expr?
          -> KEYWORD:continue
          -> KEYWORD:break
          -> expr

expr -> KEYWORD:var IDENTIFIER EQ expr
     -> IDENTIFIER (EQ | PLUSEQ | MINUSEQ | MULEQ | DIVEQ | POWEQ) expr
     -> comp ((KEYWORD:and | KEYWORD:or) comp)*

comp -> KEYWORD:not comp
     -> arith ((EE | NE | LT | GT | LTE | GTE) arith)*

arith -> term ((PLUS | MINUS) term)*

term -> factor ((MUL | DIV | MOD) factor)*

factor -> (PLUS | MINUS) factor
       -> power

power -> call (POW factor)*

call -> atom (LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN)?

atom -> INT | FLOAT | STRING | IDENTIFIER
     -> LPAREN expr RPAREN
     -> list-expr
     -> if-expr
     -> for-expr
     -> while-expr
     -> func-expr

list-expr -> LBRACKET (expr (COMMA expr)*)? RBRACKET

if-expr -> KEYWORD:if expr LBRACE statements RBRACE
           (KEYWORD:elif expr LBRACE statements RBRACE)*
           (KEYWORD:else LBRACE statements RBRACE)?

for-expr -> KEYWORD:for IDENTIFIER EQ expr KEYWORD:to expr (KEYWORD:step expr)? LBRACE statements RBRACE

while-expr -> KEYWORD:while expr LBRACE statements RBRACE

func-expr -> KEYWORD:func IDENTIFIER? LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN ARROW expr
          -> KEYWORD:func IDENTIFIER? LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN ARROW LBRACE statements RBRACE
```