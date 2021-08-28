# LakiScript

```bnf
expr -> KEYWORD:var IDENTIFIER EQ expr
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

if-expr -> KEYWORD:if expr { expr* }
           ( KEYWORD:elif expr { expr* } )*
           ( KEYWORD:else { expr* } )?

for-expr -> KEYWORD:for IDENTIFIER EQ expr KEYWORD:to expr
            (KEYWORD:step expr)? { expr* }

while-expr -> KEYWORD:while expr { expr* }
```