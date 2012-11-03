#!/usr/bin/env python2

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
class SyntaxException(Exception):
    def __init__(self, token):
        self.token = token
    def __str__(self):
        return 'Syntax error at ' + self.token.value
    def printPretty(self, expression):
        print(expression)
        print('~' * self.token.lexpos + '^')

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
    raise SyntaxException(t)

import ply.yacc as yacc
yacc.yacc()

def parse(expression):
    global identifiers
    identifiers = []
    return yacc.parse(expression)


# creates a truth table ---------------------------------------------
import sys
out = sys.stdout

import locale
locale.setlocale(locale.LC_NUMERIC, "")

def truth_table(variables):
    for i in range(0, pow(2,len(variables))):
        l = list((bin(i)[2:]).zfill(len(variables)))
        for i in range(0, len(l)):
            if l[i] is '1':
                l[i] = True
            else:
                l[i] = False
        yield l

class table_decorator:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args):
        if len(args) == 3:
            self.table = args[-1]
            args = args[:-1]

        result = (args[0], self.function(*args))
        if not (result in self.table):
            self.table.append(result)
        return result[1]

@table_decorator
def resolve(tree, d):
    '''
    Returns the result of the expression (True of False)
    '''
    if (tree[0] is 'AND'):
        first = resolve(tree[1], d)
        second = resolve(tree[2], d)
        return first and second
    elif (tree[0] is 'OR'):
        first = resolve(tree[1], d)
        second = resolve(tree[2], d)
        return first or second
    elif (tree[0] is 'NOT'):
        return not resolve(tree[1], d)
    elif (tree[0] is 'IMPLIES'):
        first = not resolve(tree[1], d)
        second = resolve(tree[2], d)
        return first or second
    elif (tree[0] is 'EQUALS'):
        return resolve(tree[1], d) is resolve(tree[2], d)
    elif (tree[0] is 'IDENTIFIER'):
        return d[tree[1]]

def createResolveDict(l):
    d = {}
    for i in range(0,len(identifiers)):
        d[identifiers[i]] = l[i]
    return d

def printableTree(tree):
    if (tree[0] is 'AND'):
        return printableTree(tree[1]) + ' and ' + printableTree(tree[2])
    elif (tree[0] is 'OR'):
        return printableTree(tree[1]) + ' or ' + printableTree(tree[2])
    elif (tree[0] is 'NOT'):
        return 'not ' + printableTree(tree[1])
    elif (tree[0] is 'IMPLIES'):
        return printableTree(tree[1]) + ' implies ' + printableTree(tree[2])
    elif (tree[0] is 'EQUALS'):
        return printableTree(tree[1]) + ' equals ' + printableTree(tree[2])
    elif (tree[0] is 'IDENTIFIER'):
        return tree[1]


def format_num(num):
    """
    Format a number according to given places.
    Adds commas, etc. Will truncate floats into ints.
    """
    try:
        inum = int(num)
        return locale.format("%.*f", (0, inum), True)
    except (ValueError, TypeError):
        return str(num)

def get_max_width(table, index):
    '''
    Returns the max length of the table values,
    that will be used to format the table.
    '''
    return max([len(format_num(row[index])) for row in table])

def print_table(table):
    '''
    Prints the final truth table.
    '''
    col_paddings = []
    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))
    for row in table:
        for i in range(0, len(row)):
            col = format_num(row[i]).rjust(col_paddings[i] + 2)
            print >> out, col,
        print >> out
    print >> out


def execute(expression):
    '''
    Executes the program --------------------------------------------
    '''
    tree = parse(expression)
    failed = False
    table = []
    loop = 1

    for line in truth_table(identifiers):
        table2 = []
        line.append(resolve(tree, createResolveDict(line), table2))
        header = []
        newLine = []
        for element in table2:
            if (loop is 1):
                header.append(printableTree(element[0]))
            newLine.append(str(element[1]))
        if (loop is 1):
            table.append(header)
        table.append(newLine)
        if line[-1] is False:
            failed = True
        loop = loop + 1
    print_table(table)
    if(failed):
        print >> out, 'Invalid expression.',
    else:
        print >> out, 'Valid expression.',
    print >> out


# Main loop ---------------------------------------------------------
while 1:
    expr = ''
    try:
        expr = raw_input('whopper > ')
        execute(expr)
    except EOFError:
        print
        break
    except KeyboardInterrupt:
        print
        continue
    except SyntaxException, e:
        print('Syntax error:')
        e.printPretty(expr)
        print('')
        continue
