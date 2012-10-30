# Tokens

reserved = {
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'implies': 'IMPLIES',
    'equals': 'EQUALS',
    'true' : 'TRUE',
    'false' : 'FALSE'
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

result = yacc.parse('A and C equals D')
print result

# creates a truth table

And=lambda x,y:x and y
Or=lambda x,y:x or y
Not=lambda x:not x
Impl=lambda x,y:Or(Not(x), y)

def p_fixed_table(p):
    if p is 1:
        yield [True]
        yield [False]
    else:
        for i in p_fixed_table(p - 1):
            yield i + [True]
            yield i + [False]

def p_truth_table(identifiers, expr):
    for cond in p_fixed_table(len(identifiers)):
        values = dict(zip(identifiers, cond))
        yield cond + [p_eval_expr(values, expr)]

def p_eval_expr(values, expr):
    argarr = []
    for arg in expr[1:]:
        if (type(arg) in [tuple, list]):
            argarr.append(eval_expr(values, arg))
        elif (arg in values):
            argarr.append(values[arg])
        else:
            raise ValueError('Invalid expr')
    return expr[0](*argarr)

print([i for i in p_truth_table(['x','y'], (Impl, 'x', 'y'))])
