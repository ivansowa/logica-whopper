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

tree = yacc.parse('A and B implies A')

# creates a truth table

def truth_table(variables):
    for i in range(0, pow(2,len(variables))):
        l = list((bin(i)[2:]).zfill(len(variables)))
        for i in range(0, len(l)):
            if l[i] is '1':
                l[i] = True
            else:
                l[i] = False
        yield l

def resolve(tree, d):
    if (tree[0] is 'AND'):
        return resolve(tree[1], d) and resolve(tree[2], d)
    elif (tree[0] is 'OR'):
        return resolve(tree[1], d) or resolve(tree[2], d)
    elif (tree[0] is 'NOT'):
        return not resolve(tree[1], d)
    elif (tree[0] is 'IMPLIES'):
        return (not resolve(tree[1], d) or resolve(tree[2], d))
    elif (tree[0] is 'EQUALS'):
        return resolve(tree[1], d) is resolve(tree[2], d)
    elif (tree[0] is 'IDENTIFIER'):
        return d[tree[1]]

def execute(tree):
    for i in truth_table(identifiers):
        d = {}
        for j in range(0,len(identifiers)):
            d[identifiers[j]] = i[j]
        if resolve(tree, d) is False:
            failed = True
            print('Expressao invalida')
            break
    else:
        print('Exressao valida.')

#change the tree variable values

while 1:
    try:
        s = input('calc > ')   # Use raw_input on Python 2
    except EOFError:
        break
    execute(yacc.parse(s))

