# Tokens

reserved = {
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'implies': 'IMPLIES',
    'equals': 'EQUALS'
    }

tokens = [
    'LPAREN','RPAREN',
    'IDENTIFIER',
    ] + list(reserved.values())

t_LPAREN     = r'\('
t_RPAREN     = r'\)'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'IDENTIFIER')
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()

# Parsing rules

precedence = (
    ('left', 'IMPLIES', 'EQUALS'),
    ('left', 'AND', 'OR'),
    ('nonassoc', 'LPAREN', 'RPAREN', 'NOT'),
    )

# dictionary of identifiers
identifiers = []

def p_expr(p):
    '''
    expr : paren_expr
         | not_expr
         | and_expr
         | or_expr
         | implies_expr
         | equals_expr
         | identifier_expr
    '''
    p[0] = p[1]

def p_paren_expr(p):
    '''
    paren_expr : LPAREN expr RPAREN
    '''
    p[0] = p[2]

def p_not_expr(p):
    '''
    not_expr : NOT expr
    '''
    p[0] = ('NOT', p[2])

def p_and_expr(p):
    '''
    and_expr : expr AND expr
    '''
    p[0] = ('AND', p[1], p[3])

def p_or_expr(p):
    '''
    or_expr : expr OR expr
    '''
    p[0] = ('OR', p[1], p[3])

def p_implies_expr(p):
    '''
    implies_expr : expr IMPLIES expr
    '''
    p[0] = ('IMPLIES', p[1], p[3])

def p_equals_expr(p):
    '''
    equals_expr : expr EQUALS expr
    '''
    p[0] = ('EQUALS', p[1], p[3])

def p_identifier_expr(p):
    '''
    identifier_expr : IDENTIFIER
    '''
    if p[1] not in identifiers:
        identifiers.append(p[1])
    p[0] = ('IDENTIFIER', p[1])

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
yacc.yacc()

result = yacc.parse('A and C equals D and E')
print result

# creates a truth table

def binary_values():
    for i in range(0, pow(2,len(identifiers))):
        binary_string = (bin(i)[2:]).zfill(len(identifiers))
        yield binary_string

def test_for(binary_string):
    values = []
    for i in binary_string:
        if (i is '1'):
            values.append(True)
        elif (i is '0'):
            values.append(False)
    return values

for i in binary_values():
    print test_for(i)

