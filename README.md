# LakiScript

## 语法

```bnf
statements -> NEWLINE* expr (NEWLINE+ statement)* NEWLINE*

statement -> KEYWORD:return expr?
          -> KEYWORD:continue
          -> KEYWORD:break
          -> expr

expr -> KEYWORD:var IDENTIFIER EQ expr
     -> IDENTIFIER ( EQ | PLUSEQ | MINUSEQ | MULEQ | DIVEQ | POWEQ ) expr
     -> comp (( KEYWORD:and | KEYWORD:or ) comp)*

comp -> KEYWORD:not comp
     -> arith (( EE | NE | LT | GT | LTE | GTE ) arith)*

arith -> term (( PLUS | MINUS ) term)*

term -> factor (( MUL | DIV ) factor)*

factor -> ( PLUS | MINUS ) factor
       -> power

power -> atom (POW factor)*

atom -> INT | FLOAT | IDENTIFIER
     -> LPAREN expr RPAREN
     -> if-expr
     -> for-expr
     -> while-expr

if-expr -> KEYWORD:if expr LBRACE statements RBRACE
           ( KEYWORD:elif expr LBRACE statements RBRACE )*
           ( KEYWORD:else LBRACE statements RBRACE )?

for-expr -> KEYWORD:for IDENTIFIER EQ expr KEYWORD:to expr (KEYWORD:step expr)? LBRACE statements RBRACE

while-expr -> KEYWORD:while expr LBRACE statements RBRACE
```