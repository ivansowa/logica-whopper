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

result = yacc.parse('A and C equals D')
print result

# creates a truth table

And = lambda x,y:x and y
Or = lambda x,y:x or y
Not = lambda x:not x
Implies = lambda x,y:Or(Not(x), y)

def fixed_table(p):
    """
    Generate true/false permutations for the given number of variables.
    Ex: if p=2
    Returns (not necessarily in this order):
        True, True
        True, False
        False, False
        False, True
    """
    if p is 1:
        yield [True]
        yield [False]
    else:
        for i in fixed_table(p - 1):
            yield i + [True]
            yield i + [False]

def truth_table(variables, expr):
    """
    Takes an array of variables and displays a truth table
    for each possible value combination of vars.
    """
    for cond in fixed_table(len(variables)):
        values = dict(zip(variables, cond))
        yield cond + [eval_expr(values, expr)]

def eval_expr(values, expr):
    """
    Takes a dictionary values {var1 : val1, var2 : val2} and a tuple
    expr (lambda, var1, var2) returns evaluated value.
    expr needs to be in a LISP like format (operator, arg1, arg2).

    Returns the value of expr when variables are set according to
    values.
    """
    argarr = []
    for arg in expr[1:]:
        if (type(arg) in [tuple, list]):
            argarr.append(eval_expr(values, arg))
        elif (arg in values):
            argarr.append(values[arg])
        else:
            raise ValueError('Invalid expr')
    return expr[0](*argarr)

for i in truth_table(['x','y'], (Implies, 'x', 'y')):
    print i

