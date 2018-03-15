import ply.lex as lex
import ply.yacc as yacc
import sqlite3

# Database Setup
conn = sqlite3.connect('bibtex.db')
cursor = conn.cursor()
CREATE = '''CREATE TABLE IF NOT EXISTS bibtex (
            bibkey varchar(50) PRIMARY KEY NOT NULL,
            bibtype varchar(50) ,
            address varchar(255) ,
            author varchar(255) NOT NULL,
            booktitle varchar(255) ,
            chapter varchar(50) ,
            edition varchar(25) ,
            journal varchar(100) ,
            number varchar(25) ,
            pages varchar(25) ,
            publisher varchar(100) ,
            school varchar(100) ,
            title varchar(255) ,
            volume varchar(50) ,
            year varchar(25)
            );'''
cursor.execute(CREATE)

# Valid field definitions
entry = {}
fields = ['bibkey','bibtype','address','author','booktitle',
          'chapter','edition','journal','number','pages','publisher',
          'school','title','volume','year']

top_level_fields = ['article','book','booklet','conference','inbook','incollection',
                    'inproceedings','manual','masterthesis','misc','phdthesis','proceedings',
                    'techreport','unpublished']

def set_records_null():
    for i in fields:
        entry[i] = None

# Lexical Grammar
tokens = ['AT','NEWLINE','COMMENT','WHITESPACE','JUNK',
          'NUMBER','NAME','LBRACE','RBRACE','LPAREN','RPAREN',
          'EQUALS','HASH','COMMA','QUOTE','STRING']

# Top Level
t_AT = r'\@'
t_NEWLINE = r'\n'
t_COMMENT = r'\%~[\n]*\n'
t_JUNK = r'~[\@\n\ \r\t]+'

# in-entry
def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

t_NAME = r'[A-Za-z0-9\!\$\&\*\+\-\.\/\:\;\<\>\?\[\]\^\_\‘\|]+'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_HASH = r'\#'
t_COMMA = r'\,'
t_QUOTE = r'\"'
t_STRING = r'{[^{}]+}'
t_ignore = ' \t'

def t_error(t):
    print("Illegal character ’%s’" % t.value[0])
    t.lexer.skip(1)

# Syntactic Grammar
def p_bibfile(p):
    '''bibfile : entries'''
    p[0] = p[1]

def p_entries(p):
    '''entries : entry NEWLINE entries
            | entry'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1]+p[2]+p[3]

def p_entry(p):
    '''entry : AT NAME LBRACE key COMMA fields RBRACE'''
    p[0] = p[1]+p[2]+p[3]+p[4]+p[5]+p[6]+p[7]


    if p[2] in top_level_fields:
        entry['bibkey'] = p[4]
        entry['bibtype'] = p[2]
        insert_sql = '''INSERT INTO bibtex(bibkey,bibtype,address, author, booktitle, chapter, edition,journal, number, pages, publisher, school, title, volume, year)\
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        data = (entry['bibkey'],entry['bibtype'],entry['address'],entry['author'],entry['booktitle'],entry['chapter'],entry['edition'],entry['journal'],entry['number'],entry['pages'],entry['publisher'],entry['school'],entry['title'],entry['volume'],entry['year'])
        try:
            cursor.execute(insert_sql,data)
            conn.commit()
            print("Entry added with key",entry['bibkey'])
        except sqlite3.IntegrityError:
            print("Entry already exists for",entry['bibkey'])
        set_records_null()
    else:
        print("Illegal Top Level Field",p[2])
        exit(1)

def p_key(p):
    '''key : NAME
           | NUMBER'''
    p[0] = p[1]

def p_fields(p):
    '''fields : field COMMA fields
              | field'''
    if len(p) == 2:
        p[0] = p[1]
    else :
        p[0] = p[1]+p[2]+p[3]

def p_field(p):
    '''field : NAME EQUALS LBRACE value RBRACE'''

    if p[1] in fields:
        p[0] = p[1]+p[2]+p[3]+p[4]+p[5]
        entry[p[1]] = p[4]
    else:
        print("Illegal Field Found",p[1])
        exit(1)

def p_value(p):
    '''value : STRING
             | NUMBER
             | NAME'''
    p[0] = p[1]



if __name__ == "__main__":

    set_records_null()

    data = '''@article{key9,author = {{Sarkar, Santonu}},title = {{XYZ Research}}}
              @proceedings{key8,author = {{Sarkar, Santonu}},title = {{XYZ Research}}}'''
    lex.lex()
    yacc.yacc()
    lex.input(data)

    print("Token List")
    print()
    while True:
        tok = lex.token()
        if not tok:
            break
        print(tok)

    print()
    yacc.parse(data)
    conn.close()
