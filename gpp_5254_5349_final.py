# Kiosses Athanasios - Sioulas Alexandros
# 5254 - 5349

import sys
import copy

# ---------------------- Lexer ----------------------
class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        if self.source_code:
            self.current_char = self.source_code[self.position]
        else:
            None
        
        
        # Reserved Words
        self.reserved_words = {
            'πρόγραμμα': 'PROGRAM',
            'δήλωση': 'DECLARATION',
            'εάν': 'IF',
            'τότε': 'THEN',
            'αλλιώς': 'ELSE',
            'εάν_τέλος': 'END_IF',
            'επανάλαβε': 'REPEAT',
            'μέχρι': 'UNTIL',
            'όσο': 'WHILE',
            'όσο_τέλος': 'END_WHILE',
            'για': 'FOR',
            'έως': 'TO',
            'με_βήμα': 'STEP',
            'για_τέλος': 'END_FOR',
            'διάβασε': 'READ',
            'γράψε': 'WRITE',
            'συνάρτηση': 'FUNCTION',
            'διαδικασία': 'PROCEDURE',
            'διαπροσωπεία': 'INTERFACE',
            'αρχή_προγράμματος': 'BEGIN_PROGRAM',
            'τέλος_προγράμματος': 'END_PROGRAM',
            'είσοδος': 'INPUT',
            'έξοδος': 'OUTPUT',
            'αρχή_συνάρτησης': 'BEGIN_FUNCTION',
            'τέλος_συνάρτησης': 'END_FUNCTION',
            'αρχή_διαδικασίας': 'BEGIN_PROCEDURE',
            'τέλος_διαδικασίας': 'END_PROCEDURE',
            'ή': 'OR',
            'και': 'AND',
            'εκτέλεσε': 'CALL',
            'όχι': 'NOT'
        }

        # Symbols and Operators
        self.symbols = {
            '+': 'PLUS',
            '-': 'MINUS',
            '*': 'TIMES',
            '/': 'DIV',
            ':=': 'ASSIGN',
            '=': 'EQ',
            '<>': 'NE',
            '<': 'LT',
            '>': 'GT',
            '<=': 'LE',
            '>=': 'GE',
            ';': 'SEMICOLON',
            ',': 'COMMA',
            ':': 'COLON',
            '(': 'LPAREN',
            ')': 'RPAREN',
            '[': 'LBRACK',
            ']': 'RBRACK',
            '{': 'LBRACE',
            '}': 'RBRACE',
            '%': 'PERCENT'
        }
    
    # Moves to next character
    def advance(self):
        if self.current_char == '\n':
            self.line += 1
        self.position += 1
        if self.position < len(self.source_code):
            self.current_char = self.source_code[self.position]
        else:
            self.current_char = None
    
    # Skip Spaces
    def skip_spaces(self):
        while self.current_char == ' ' or self.current_char =='\t' or self.current_char == '\n' or self.current_char == '\r':
            self.advance()

    # Skip Comments
    def skip_comment(self):
        if self.current_char == '{':
            while self.current_char != '}':
                self.advance()
            self.advance()  

    # Get potential identifier or reserved word
    def get_identifier(self):
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char in "άέήίύόώ_"):
            result += self.current_char
            self.advance()
        token_type = self.reserved_words.get(result, 'ID')
        return token_type, result

    # Get potential integer
    def get_integer(self):
        result = ""
        start_line = self.line
        while self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return 'INTEGER', result, start_line

    # Get potential symbol or operator
    def get_symbol(self):
        start_line = self.line
        char = self.current_char
        self.advance()
        if char in (':', '<', '>'):
            potential_symbol = char + self.current_char
            if potential_symbol in self.symbols:
                self.advance()
                return self.symbols[potential_symbol], potential_symbol, start_line
        return self.symbols.get(char, 'UNKNOWN'), char, start_line

    # Returns next token
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char == ' ' or self.current_char =='\t' or self.current_char == '\n' or self.current_char == '\r':
                self.skip_spaces()
                continue
            if self.current_char == '{':
                self.skip_comment()
                continue
            if self.current_char.isalpha():
                return self.get_identifier()
            if self.current_char.isdigit():
                return self.get_integer()
            if self.current_char in self.symbols:
                return self.get_symbol()
            
            # In case of uknown character
            unknown_char = self.current_char
            start_line = self.line
            self.advance()
            return 'UNKNOWN', unknown_char, start_line
        
        return 'EOF', None, self.line

    # Returns a list of all the tokens from the source code
    def tokenize(self):
        tokens = []
        token = self.get_next_token()
        while token[0] != 'EOF':
            tokens.append(token)
            token = self.get_next_token()
        return tokens

# ---------------------- Parser ----------------------
class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        if len(self.tokens) == 0:
            raise ParserError("No tokens to parse!")
        self.current_token = self.tokens[self.pos]

    # Error Message with token info
    def error(self, message="Syntax error"):
        line_info = f" on line {self.current_token[2]}" if len(self.current_token) >= 3 else ""
        raise ParserError(message + " at token " + str(self.current_token) + line_info)

    def parse_next_token(self, token_type):
        if self.current_token[0] == token_type:
            token = self.current_token
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            return token
        else:
            self.error(f"Expected token {token_type}, got {self.current_token}")

    def parse(self):
        return self.program()

    # program : 'πρόγραμμα' ID programblock
    def program(self):
        self.parse_next_token('PROGRAM')
        id_token = self.parse_next_token('ID')
        pb = self.programblock()
        return ('program', id_token, pb)

    # programblock : declarations subprograms 'αρχή_προγράμματος' sequence 'τέλος_προγράμματος'
    def programblock(self):
        decl = self.declarations()
        subprogs = self.subprograms()
        self.parse_next_token('BEGIN_PROGRAM')
        seq = self.sequence()
        self.parse_next_token('END_PROGRAM')
        return ('programblock', decl, subprogs, seq)

    # declarations : ( 'δήλωση' varlist )* | empty
    def declarations(self):
        decls = []
        while self.current_token[0] == 'DECLARATION':
            self.parse_next_token('DECLARATION')
            varlist_node = self.varlist()
            decls.append(varlist_node)
        return ('declarations', decls)

    # varlist : ID ( ',' ID )*
    def varlist(self):
        ids = []
        id_token = self.parse_next_token('ID')
        ids.append(id_token)
        while self.current_token[0] == 'COMMA':
            self.parse_next_token('COMMA')
            id_token = self.parse_next_token('ID')
            ids.append(id_token)
        return ('varlist', ids)

    # subprograms : ( func | proc )*
    def subprograms(self):
        subprogs = []
        while self.current_token[0] in ('FUNCTION', 'PROCEDURE'):
            if self.current_token[0] == 'FUNCTION':
                subprog = self.func()
            else:
                subprog = self.proc()
            subprogs.append(subprog)
        return ('subprograms', subprogs)

    # func : 'συνάρτηση' ID '(' formalparlist  ')' funcblock
    def func(self):
        self.parse_next_token('FUNCTION')
        id_token = self.parse_next_token('ID')
        self.parse_next_token('LPAREN')
        formal_params = self.formalparlist()
        self.parse_next_token('RPAREN')
        funcblk = self.funcblock()
        return ('function', id_token, formal_params, funcblk)

    # proc : 'διαδικασία' ID '(' formalparlist  ')' procblock
    def proc(self):
        self.parse_next_token('PROCEDURE')
        id_token = self.parse_next_token('ID')
        self.parse_next_token('LPAREN')
        formal_params = self.formalparlist()
        self.parse_next_token('RPAREN')
        procblk = self.procblock()
        return ('procedure', id_token, formal_params, procblk)

    # formalparlist : varlist | empty
    def formalparlist(self):
        if self.current_token[0] == 'ID':
            return self.varlist()
        else:
            return ('formalparlist', [])

    # funcblock : 'διαπροσωπεία' funcinput funcoutput declarations 'αρχή_συνάρτησης' sequence 'τέλος_συνάρτησης'
    def funcblock(self):
        self.parse_next_token('INTERFACE')
        func_input = self.funcinput()
        func_output = self.funcoutput()
        decls = self.declarations()
        subprogs = self.subprograms()
        self.parse_next_token('BEGIN_FUNCTION')
        seq = self.sequence()
        self.parse_next_token('END_FUNCTION')
        return ('funcblock', func_input, func_output, decls, subprogs, seq)

    # procblock : 'διαπροσωπεία' funcinput funcoutput declarations 'αρχή_διαδικασίας' sequence 'τέλος_διαδικασίας'
    def procblock(self):
        self.parse_next_token('INTERFACE')
        func_input = self.funcinput()
        func_output = self.funcoutput()
        decls = self.declarations()
        subprogs = self.subprograms()
        self.parse_next_token('BEGIN_PROCEDURE')
        seq = self.sequence()
        self.parse_next_token('END_PROCEDURE')
        return ('procblock', func_input, func_output, decls, subprogs, seq)

    # funcinput : 'είσοδος' varlist | empty
    def funcinput(self):
        if self.current_token[0] == 'INPUT':
            self.parse_next_token('INPUT')
            return self.varlist()
        return ('funcinput', [])

    # funcoutput : 'έξοδος' varlist | empty
    def funcoutput(self):
        if self.current_token[0] == 'OUTPUT':
            self.parse_next_token('OUTPUT')
            return self.varlist()
        return ('funcoutput', [])

    # sequence : statement ( ';' statement )*
    def sequence(self):
        stmts = []
        stmts.append(self.statement())
        while self.current_token[0] == 'SEMICOLON':
            self.parse_next_token('SEMICOLON')
            if self.current_token[0] in ('END_PROGRAM', 'END_FUNCTION', 'END_PROCEDURE', 'END_IF', 'END_WHILE', 'END_FOR'):
                break
            stmts.append(self.statement())
        return ('sequence', stmts)

    # statement : assignment_stat | if_stat | while_stat | do_stat | for_stat | input_stat | print_stat | call_stat
    def statement(self):
        token_type = self.current_token[0]
        if token_type == 'ID':
            next_token = self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None
            if next_token and next_token[0] == 'ASSIGN':
                return self.assignment_stat()
            else:
                return self.call_stat()
        elif token_type == 'IF':
            return self.if_stat()
        elif token_type == 'WHILE':
            return self.while_stat()
        elif token_type == 'REPEAT':
            return self.do_stat()
        elif token_type == 'FOR':
            return self.for_stat()
        elif token_type == 'READ':
            return self.input_stat()
        elif token_type == 'WRITE':
            return self.print_stat()
        elif token_type == 'CALL':
            return self.call_stat()
        else:
            self.error("Unknown statement starting with token " + str(self.current_token))

    # assignment_stat : ID ':=' expression
    def assignment_stat(self):
        id_token = self.parse_next_token('ID')
        self.parse_next_token('ASSIGN')
        expr = self.expression()
        return ('assignment', id_token, expr)

    # if_stat : 'εάν' condition 'τότε' sequence elsepart 'εάν_τέλος'
    def if_stat(self):
        self.parse_next_token('IF')
        cond = self.condition()
        self.parse_next_token('THEN')
        seq = self.sequence()
        else_part = self.elsepart()
        self.parse_next_token('END_IF')
        return ('if', cond, seq, else_part)

    # elsepart : 'αλλιώς' sequence | empty
    def elsepart(self):
        if self.current_token[0] == 'ELSE':
            self.parse_next_token('ELSE')
            seq = self.sequence()
            return seq
        else:
            return None

    # while_stat : 'όσο' condition 'επανάλαβε' sequence 'όσο_τέλος'
    def while_stat(self):
        self.parse_next_token('WHILE')
        cond = self.condition()
        self.parse_next_token('REPEAT')
        seq = self.sequence()
        self.parse_next_token('END_WHILE')
        return ('while', cond, seq)

    # do_stat : 'επανάλαβε' sequence 'μέχρι' condition
    def do_stat(self):
        self.parse_next_token('REPEAT')
        seq = self.sequence()
        self.parse_next_token('UNTIL')
        cond = self.condition()
        return ('do', seq, cond)

    # for_stat : 'για' ID ':=' expression 'έως' expression step 'επανάλαβε' sequence 'για_τέλος'
    def for_stat(self):
        self.parse_next_token('FOR')
        id_token = self.parse_next_token('ID')
        self.parse_next_token('ASSIGN')
        start_expr = self.expression()
        self.parse_next_token('TO')
        end_expr = self.expression()
        step_expr = self.step()
        self.parse_next_token('REPEAT')
        seq = self.sequence()
        self.parse_next_token('END_FOR')
        return ('for', id_token, start_expr, end_expr, step_expr, seq)

    # step : 'με_βήμα' expression | empty
    def step(self):
        if self.current_token[0] == 'STEP':
            self.parse_next_token('STEP')
            expr = self.expression()
            return expr
        else:
            return None

    # print_stat : 'γράψε' expression
    def print_stat(self):
        self.parse_next_token('WRITE')
        expr = self.expression()
        return ('print', expr)

    # input_stat : 'διάβασε' ID
    def input_stat(self):
        self.parse_next_token('READ')
        id_token = self.parse_next_token('ID')
        return ('read', id_token)

    # call_stat : 'εκτέλεσε' ID idtail
    def call_stat(self):
        self.parse_next_token('CALL')
        id_token = self.parse_next_token('ID')
        tail = self.idtail()
        return ('call', id_token, tail)

    # idtail : actualpars | empty
    def idtail(self):
        if self.current_token[0] == 'LPAREN':
            return self.actualpars()
        else:
            return None

    # actualpars : '(' actualparlist ')'
    def actualpars(self):
        self.parse_next_token('LPAREN')
        actual_list = self.actualparlist()
        self.parse_next_token('RPAREN')
        return actual_list

    # actualparlist : actualparitem ( ',' actualparitem )* | empty
    def actualparlist(self):
        items = []
        if self.current_token[0] in ('INTEGER', 'ID', 'LPAREN', 'PLUS', 'MINUS'):
            items.append(self.actualparitem())
            while self.current_token[0] == 'COMMA':
                self.parse_next_token('COMMA')
                items.append(self.actualparitem())
        return items

    # actualparitem : expression | '%' ID
    def actualparitem(self):
        if self.current_token[0] == 'PERCENT':
            self.parse_next_token('PERCENT')
            id_token = self.parse_next_token('ID')
            return ('by_reference', id_token)
        else:
            return self.expression()

    # condition : boolterm ( 'ή' boolterm )*
    def condition(self):
        left = self.boolterm()
        while self.current_token[0] == 'OR':
            self.parse_next_token('OR')
            right = self.boolterm()
            left = ('or', left, right)
        return left

    # boolterm : boolfactor ( 'και' boolfactor )*
    def boolterm(self):
        left = self.boolfactor()
        while self.current_token[0] == 'AND':
            self.parse_next_token('AND')
            right = self.boolfactor()
            left = ('and', left, right)
        return left

    # boolfactor : 'όχι' '[' condition ']' | '[' condition ']' | expression relational_oper expression
    def boolfactor(self):
        if self.current_token[0] == 'NOT':
            self.parse_next_token('NOT')
            self.parse_next_token('LBRACK')
            cond = self.condition()
            self.parse_next_token('RBRACK')
            return ('not', cond)
        elif self.current_token[0] == 'LBRACK':
            self.parse_next_token('LBRACK')
            cond = self.condition()
            self.parse_next_token('RBRACK')
            return cond
        else:
            left = self.expression()
            op = self.relational_oper()
            right = self.expression()
            return ('relation', left, op, right)

    # expression : optional_sign term ( add_oper term )*
    def expression(self):
        sign = self.optional_sign()
        node = self.term()
        if sign is not None:
            node = ('unary', sign, node)
        while self.current_token[0] in ('PLUS', 'MINUS'):
            op = self.add_oper()
            right = self.term()
            node = ('binop', op, node, right)
        return node

    # term : factor ( mul_oper factor )*
    def term(self):
        node = self.factor()
        while self.current_token[0] in ('TIMES', 'DIV'):
            op = self.mul_oper()
            right = self.factor()
            node = ('binop', op, node, right)
        return node

    # factor : INTEGER | '(' expression ')' | ID idtail
    def factor(self):
        token_type = self.current_token[0]
        if token_type == 'INTEGER':
            token = self.parse_next_token('INTEGER')
            return ('integer', token)
        elif token_type == 'LPAREN':
            self.parse_next_token('LPAREN')
            node = self.expression()
            self.parse_next_token('RPAREN')
            return node
        elif token_type == 'ID':
            id_token = self.parse_next_token('ID')
            tail = self.idtail()
            return ('id', id_token, tail)
        else:
            self.error("Unexpected token in factor: " + str(self.current_token))

    # relational_oper : '=' | '<=' | '>=' | '<>' | '<' | '>'
    def relational_oper(self):
        token = self.current_token
        if token[0] in ('EQ', 'LE', 'GE', 'NE', 'LT', 'GT'):
            self.parse_next_token(token[0])
            return token[1]
        else:
            self.error("Expected relational operator, got: " + str(token))

    # add_oper : '+' | '-'
    def add_oper(self):
        token = self.current_token
        if token[0] in ('PLUS', 'MINUS'):
            self.parse_next_token(token[0])
            return token[1]
        else:
            self.error("Expected add operator, got: " + str(token))

    # mul_oper : '*' | '/'
    def mul_oper(self):
        token = self.current_token
        if token[0] in ('TIMES', 'DIV'):
            self.parse_next_token(token[0])
            return token[1]
        else:
            self.error("Expected mul operator, got: " + str(token))

    # optional_sign : add_oper | empty
    def optional_sign(self):
        if self.current_token[0] in ('PLUS', 'MINUS'):
            return self.add_oper()
        else:
            return None

# ---------------------- Intermediate Code Generator ----------------------
class CodeGenerator:
    def __init__(self, symtab, prog_name, param_map):
        self.quads = []
        self.temp_count = 0
        self.symtab = symtab # Αυτό είναι το instance του SymbolTable
        self.program_name = prog_name
        self.param_map = param_map
        self.current_function = None
        self.current_codegen_level = -1 # Ξεχωριστό level για τον CodeGenerator
        self.symtab_snapshots = []

    def new_temp(self):
        self.temp_count += 1
        name = f"t@{self.temp_count}"
        self.symtab.add_temp(name)
        return name

    def next_quad(self):
        return len(self.quads) + 1

    def gen_quad(self, op, a1, a2, res):
        qn = self.next_quad() 

        if op == 'beginblock':
            block_name_for_quad = a1 
            
            if self.symtab.scopes and self.symtab.scopes[-1].get('name') == block_name_for_quad:
                current_scope_dict_in_symtab = self.symtab.scopes[-1]
                current_scope_dict_in_symtab['start_quad'] = qn 
            
                if len(self.symtab.scopes) > 1: 
                    parent_scope_dict_in_symtab = self.symtab.scopes[-2] 
                    for entity_in_parent in parent_scope_dict_in_symtab.get('entities', []):
                        if entity_in_parent.get('name') == block_name_for_quad and \
                           entity_in_parent.get('kind') in ('function', 'procedure'):
                            entity_in_parent['start_quad'] = qn
                            break 
            else:
                # Σφάλμα συγχρονισμού μεταξύ SymbolTable και CodeGenerator
                print(f"CRITICAL SYNC ERROR in gen_quad('beginblock'): SymbolTable top scope "
                      f"'{self.symtab.scopes[-1].get('name') if self.symtab.scopes else 'None'}' "
                      f"does not match block name '{block_name_for_quad}'")

        self.quads.append([qn, op, a1, a2, res]) 

        if op == 'endblock':
            self.symtab_snapshots.append(self.symtab.get_active_scopes_snapshot())

    def backpatch(self, lst, target):
        for i in lst:
            self.quads[i-1][4] = str(target)

    def makelist(self, i):
        return [i]

    def merge(self, a, b):
        return a + b

    def generate_condition(self, node):
        
        kind = node[0]

        # 1) Βασική σχέση: b := (expr relop expr)
        if kind == 'relation':
            left_node, op_symbol, right_node = node[1], node[2], node[3]
            L = self.generate_expression(left_node)
            R = self.generate_expression(right_node)

            # 1α) το quad για το conditional branch
            q_true = self.next_quad()
            self.gen_quad(op_symbol, L, R, '')    # backpatch σε then/body

            # 1β) ένα άδειο jump για το false
            q_false = self.next_quad()
            self.gen_quad('jump', '', '', '')      # backpatch σε else/exit

            return [q_true], [q_false]

        # 2) Λογικό AND: A and B
        if kind == 'and':
            left, right = node[1], node[2]
            t1, f1 = self.generate_condition(left)
            # αν το αριστερό είναι true → συνεχίζω στο δεξί
            self.backpatch(t1, self.next_quad())
            t2, f2 = self.generate_condition(right)
            # true = όσα αληθεύουν και από τα δύο, false = όσα έχουν ήδη false ή εκείνα που false στο δεξί
            return t2, self.merge(f1, f2)

        # 3) Λογικό OR: A or B
        if kind == 'or':
            left, right = node[1], node[2]
            t1, f1 = self.generate_condition(left)
            # αν το αριστερό είναι false → συνεχίζω στο δεξί
            self.backpatch(f1, self.next_quad())
            t2, f2 = self.generate_condition(right)
            # true = true αριστερό ή δεξί, false = false από τα δύο
            return self.merge(t1, t2), f2

        # 4) Λογικό NOT
        if kind == 'not':
            inner = node[1]
            t, f = self.generate_condition(inner)
            return f, t

        raise Exception(f"Unsupported condition node in generate_condition: {node}")
   
    # ——— Expression‐level generation ———
    def generate_expression(self, node):
        kind = node[0]

        # integer literal
        if kind == 'integer':
            return node[1][1]

        # variable or function‐call
        if kind == 'id':
            name = node[1][1]
            tail = node[2]

            # Semantic check: must be declared
            ent = self.symtab.lookup(name)

            # Function call inside expression
            if tail is not None:
                if ent.get('kind') != 'function':
                    raise Exception(f"Semantic error: '{name}' is not a function, cannot be called in expression.")

                func_name = name
                formal_params = self.param_map.get(func_name, [])
                actual_params = tail

                if len(actual_params) != len(formal_params):
                    raise Exception(f"Semantic error: Argument count mismatch for function '{func_name}'. "
                                    f"Expected {len(formal_params)}, got {len(actual_params)}.")

                # pass each argument
                for i, arg_node in enumerate(actual_params):
                    formal_name, expected_mode, _ = formal_params[i]
                    if isinstance(arg_node, tuple) and arg_node[0] == 'by_reference':
                        value = arg_node[1][1]
                        mode_str = 'inout'
                    else:
                        value = self.generate_expression(arg_node)
                        mode_str = 'in'

                    if expected_mode == 'REF' and mode_str != 'inout':
                        raise Exception(f"Semantic Error in call to function '{func_name}': "
                                        f"Parameter '{formal_name}' is output but passed by value.")
                    if expected_mode == 'CV' and mode_str != 'in':
                        raise Exception(f"Semantic Error in call to function '{func_name}': "
                                        f"Parameter '{formal_name}' is input but passed by reference.")

                    self.gen_quad('par', value, mode_str, func_name)

                # return‐by‐value
                ret_temp = self.new_temp()
                self.gen_quad('par', ret_temp, 'RET', func_name)
                self.gen_quad('call', '', '', func_name)
                return ret_temp

            # simple variable
            if ent.get('kind') not in ('variable', 'parameter', 'temp'):
                raise Exception(f"Semantic error: '{name}' of kind '{ent.get('kind')}' cannot be used as a value in an expression.")
            return name

        # binary operations
        if kind == 'binop':
            op = node[1]
            L = self.generate_expression(node[2])
            R = self.generate_expression(node[3])
            t = self.new_temp()
            self.gen_quad(op, L, R, t)
            return t

        # unary operations
        if kind == 'unary':
            sign = node[1]
            val = self.generate_expression(node[2])
            if sign == '+':
                return val
            else:
                t = self.new_temp()
                self.gen_quad('-', '0', val, t)
                return t

        raise Exception(f"Unsupported expression node: {node}")


    # ——— Statement generation ———
    def generate_statement(self, node):
        kind = node[0]

        if kind == 'assignment':
            var_name = node[1][1]
            if var_name != self.current_function:
                self.symtab.lookup(var_name)
            rhs = self.generate_expression(node[2])
            if var_name == self.current_function:
                self.gen_quad('retv', rhs, '', '')
            else:
                self.gen_quad(':=', rhs, '', var_name)
            return

        if kind == 'print':
            val = self.generate_expression(node[1])
            self.gen_quad('out', val, '', '')
            return

        if kind == 'read':
            name = node[1][1]
            self.symtab.lookup(name)
            self.gen_quad('in', '', '', name)
            return

        if kind == 'call':
            proc_name = node[1][1]
            args = node[2] or []

            ent = self.symtab.lookup(proc_name)
            if ent.get('kind') != 'procedure':
                raise Exception(f"Semantic error: '{proc_name}' is not a procedure.")

            formal_params = self.param_map.get(proc_name, [])
            if len(args) != len(formal_params):
                raise Exception(f"Semantic error: Argument count mismatch for procedure '{proc_name}'. "
                                f"Expected {len(formal_params)}, got {len(args)}.")

            for i, arg_node in enumerate(args):
                formal_name, expected_mode, _ = formal_params[i]
                if isinstance(arg_node, tuple) and arg_node[0] == 'by_reference':
                    value = arg_node[1][1]
                    mode_str = 'inout'
                else:
                    value = self.generate_expression(arg_node)
                    mode_str = 'in'

                if expected_mode == 'REF' and mode_str != 'inout':
                    raise Exception(f"Semantic Error in call to procedure '{proc_name}': "
                                    f"Parameter '{formal_name}' is output but passed by value.")
                if expected_mode == 'CV' and mode_str != 'in':
                    raise Exception(f"Semantic Error in call to procedure '{proc_name}': "
                                    f"Parameter '{formal_name}' is input but passed by reference.")

                self.gen_quad('par', value, mode_str, proc_name)

            # actual call
            self.gen_quad('call', '', '', proc_name)
            return

        # υπόλοιπα (if / while / for / do) αμετάβλητα...
        if kind == 'if':    self.generate_if(node); return
        if kind == 'while': self.generate_while(node); return
        if kind == 'for':   self.generate_for(node); return
        if kind == 'do':    self.generate_do(node); return

        raise Exception(f"Unsupported statement node: {node}")

    def generate_sequence(self, seq_node):
        for stmt in seq_node[1]:
            self.generate_statement(stmt)

    def _process_declarations_and_subprograms(self, declarations_node, subprograms_node):
        # Βοηθητική μέθοδος για επεξεργασία δηλώσεων και ορισμών subprograms. 
        # Προσθήκη τοπικών μεταβλητών
        if declarations_node and declarations_node[0] == 'declarations':
            for varlist_node in declarations_node[1]:
                if varlist_node[0] == 'varlist':
                    for id_token in varlist_node[1]:
                        self.symtab.add_variable(id_token[1])
        
        if subprograms_node and subprograms_node[0] == 'subprograms':
            for sp_def_node in subprograms_node[1]: 
                sp_name_token = sp_def_node[1]
                sp_name = sp_name_token[1]
                sp_kind = sp_def_node[0] 
                param_info_list = self.param_map.get(sp_name, [])
                arg_modes_list = [info[1] for info in param_info_list] 

                self.symtab.add_subprogram_entry(sp_name, sp_kind, arg_modes_list)




    # ——— Functions & procedures ———
    def generate_procedure(self, node):
        # node = ('procedure', id_token, formal_params_node, procblock_node)
        proc_name = node[1][1]
        procblock_node = node[3]
        # procblock_node = ('procblock', func_input, func_output, declarations_node, subprograms_node, seq_node)
        declarations_node = procblock_node[3]
        subprograms_node = procblock_node[4] # Εμφωλιασμένα subprograms
        seq_node = procblock_node[5] # Σώμα της διαδικασίας

        parent_function_before = self.current_function
        
        self.symtab.enter_scope(name=proc_name)
        self.current_function = proc_name

        # Προσθήκη παραμέτρων
        formal_params_info = self.param_map.get(proc_name, [])
        for pname, pmode, _ in formal_params_info:
            self.symtab.add_parameter(pname, pmode)

        # Επεξεργασία τοπικών δηλώσεων και εμφωλιασμένων subprogram definitions
        self._process_declarations_and_subprograms(declarations_node, subprograms_node)
        
        # Τώρα παράγουμε τον κώδικα για τα εμφωλιασμένα subprograms
        if subprograms_node and subprograms_node[0] == 'subprograms':
            for sp_def_node in subprograms_node[1]:
                if sp_def_node[0] == 'function':
                    self.generate_function(sp_def_node) 
                else:
                    self.generate_procedure(sp_def_node)
        
        self.current_function = proc_name 

        self.gen_quad('beginblock', proc_name, '', '')
        self.generate_sequence(seq_node) 
        self.gen_quad('endblock', proc_name, '', '')

        self.symtab.exit_scope()
        self.current_function = parent_function_before

    def generate_function(self, node):
        # node = ('function', id_token, formal_params_node, funcblock_node)
        func_name = node[1][1]
        funcblock_node = node[3]
        # funcblock_node = ('funcblock', func_input, func_output, declarations_node, subprograms_node, seq_node)
        declarations_node = funcblock_node[3]
        subprograms_node = funcblock_node[4] # Εμφωλιασμένα subprograms (αν υπάρχουν)
        seq_node = funcblock_node[5] 

        parent_function_before = self.current_function

        self.symtab.enter_scope(name=func_name)
        self.current_function = func_name

        # Προσθήκη παραμέτρων 
        formal_params_info = self.param_map.get(func_name, [])
        for pname, pmode, _ in formal_params_info:
            self.symtab.add_parameter(pname, pmode)

        # Επεξεργασία τοπικών δηλώσεων και (τυχόν) εμφωλιασμένων subprogram definitions
        self._process_declarations_and_subprograms(declarations_node, subprograms_node)
        
        # Τώρα παράγουμε τον κώδικα για τα (τυχόν) εμφωλιασμένα subprograms
        if subprograms_node and subprograms_node[0] == 'subprograms':
            for sp_def_node in subprograms_node[1]:
                if sp_def_node[0] == 'function':
                    self.generate_function(sp_def_node)
                else:
                    self.generate_procedure(sp_def_node)

        self.current_function = func_name # Επαναφορά

        self.gen_quad('beginblock', func_name, '', '')
        self.generate_sequence(seq_node)
        self.gen_quad('endblock', func_name, '', '')

        self.symtab.exit_scope()
        self.current_function = parent_function_before

    def generate_program(self, node):
        program_name = node[1][1]
        programblock_node = node[2]
        declarations_node = programblock_node[1]
        subprograms_node = programblock_node[2] 
        main_seq_node = programblock_node[3]

        self.symtab.enter_scope(name=program_name)
        self.current_function = None

        # Επεξεργασία global declarations και subprogram definitions (προσθήκη στο symtab)
        self._process_declarations_and_subprograms(declarations_node, subprograms_node)

        # Παραγωγή του κώδικα για τα subprograms
        if subprograms_node and subprograms_node[0] == 'subprograms':
            for sp_def_node in subprograms_node[1]:
                if sp_def_node[0] == 'function':
                    self.generate_function(sp_def_node)
                else: 
                    self.generate_procedure(sp_def_node)
        
        self.current_function = None 

        self.gen_quad('beginblock', program_name, '', '')
        self.generate_sequence(main_seq_node)
        self.gen_quad('halt', '', '', '')
        self.gen_quad('endblock', program_name, '', '')

        self.symtab.exit_scope()
        return self.quads

    
    # ——— If / While / For / Do ———
    def generate_if(self, node):
        tlist, flist = self.generate_condition(node[1])
        then_quad = self.next_quad(); self.backpatch(tlist, then_quad)
        self.generate_sequence(node[2])
        jump_over = None
        if node[3]:
            jump_over = self.next_quad()
            self.gen_quad('jump', '', '', '')
        else_quad = self.next_quad()
        self.backpatch(flist, else_quad)
        if node[3]:
            self.generate_sequence(node[3])
            end_if = self.next_quad(); self.backpatch([jump_over], end_if)

    def generate_while(self, node):
        start = self.next_quad()
        tlist, flist = self.generate_condition(node[1])
        body_quad = self.next_quad(); self.backpatch(tlist, body_quad)
        self.generate_sequence(node[2])
        self.gen_quad('jump', '', '', str(start))
        exit_quad = self.next_quad(); self.backpatch(flist, exit_quad)

    def generate_for(self, node):
        var = node[1][1]
        start_val = self.generate_expression(node[2])
        self.gen_quad(':=', start_val, '', var)
        loop_start = self.next_quad()
        end_val = self.generate_expression(node[3])
        self.gen_quad('<=', var, end_val, loop_start + 2)
        q_false = self.next_quad(); self.gen_quad('jump', '', '', '')
        self.generate_sequence(node[5])
        step = self.generate_expression(node[4]) if node[4] else '1'
        t = self.new_temp(); self.gen_quad('+', var, step, t)
        self.gen_quad(':=', t, '', var)
        self.gen_quad('jump', '', '', str(loop_start))
        end_label = self.next_quad(); self.backpatch([q_false], end_label)

    def generate_do(self, node):
        loop_start = self.next_quad()
        self.generate_sequence(node[1])
        exit_line = self.next_quad() + 1
        cond = node[2]; op = cond[2]
        L = self.generate_expression(cond[1])
        R = self.generate_expression(cond[3])
        self.gen_quad(op, L, R, str(exit_line + 1))
        self.gen_quad('jump', '', '', str(loop_start))


# ---------------------- Symbol Table ----------------------
class SymbolTable:
    def __init__(self):
        self.scopes = []           # dynamic scope stack
        self.closed_scopes = []    # closed scopes history
        self.current_level = -1    # nesting level

    def enter_scope(self, name=None):
        self.current_level += 1
        scope = {
            'level': self.current_level,
            'name': name,
            'entities': [],
            'max_offset': 0,
            'start_quad': None,
            'frame_length': None 
        }
        self.scopes.append(scope)

    def exit_scope(self):
        if not self.scopes:
            return None 
        
        exiting_scope_dict = self.scopes.pop()
        self.current_level -= 1
        max_offset_abs = abs(exiting_scope_dict.get('max_offset', 0))
        calculated_frame_len = 0
        is_main_program_scope = (exiting_scope_dict.get('level') == 0) 

        if is_main_program_scope:
            calculated_frame_len = max_offset_abs + 4 if max_offset_abs > 0 else 4 
        else: 
            if max_offset_abs == 0: # Αν δεν έχει τοπικές/temps/params που παίρνουν offset
                calculated_frame_len = 12 + 4 # Ελάχιστο
            else:
                calculated_frame_len = max_offset_abs + 4
        
        # Ευθυγράμμιση σε πολλαπλάσιο του 4 
        calculated_frame_len = (calculated_frame_len + 3) & ~3 
        
        exiting_scope_dict['frame_length'] = calculated_frame_len 
        
        if self.scopes: 
            parent_scope_dict = self.scopes[-1] 
            for entity_in_parent in parent_scope_dict.get('entities', []):
                if entity_in_parent.get('name') == exiting_scope_dict.get('name') and \
                   entity_in_parent.get('kind') in ('function', 'procedure'):
                    entity_in_parent['frame_length'] = calculated_frame_len
                    if exiting_scope_dict.get('start_quad') is not None:
                        entity_in_parent['start_quad'] = exiting_scope_dict.get('start_quad')
                    break
        
        self.closed_scopes.append(exiting_scope_dict) # Προσθήκη του scope που έκλεισε στη λίστα των κλειστών
        return exiting_scope_dict 

    def get_active_scopes_snapshot(self):
        return copy.deepcopy(self.scopes)

    def _alloc_offset(self):
        if not self.scopes: 
            print("Warning: _alloc_offset called with no active scope. Creating a temporary one.")
            self.enter_scope("__implicit_global__" if self.current_level < 0 else "__implicit_temp__")

        scope = self.scopes[-1]
        if scope['max_offset'] > 0:
            off = scope['max_offset'] + 4
        else:
            off = 12 # Αρχικό offset για την πρώτη μεταβλητή/παράμετρο σε ένα scope
        scope['max_offset'] = off
        return off

    def lookup(self, name):
        for scope in reversed(self.scopes):
            for ent in scope['entities']:
                if ent['name'] == name:
                    return ent
        raise Exception(f"Semantic error: '{name}' used but not declared in current or enclosing scopes")

    def add_variable(self, name):
        off = self._alloc_offset()
        self.scopes[-1]['entities'].append({'kind':'variable','name':name,'offset':off})

    def add_parameter(self, name, mode):
        off = self._alloc_offset()
        self.scopes[-1]['entities'].append({'kind':'parameter','name':name,'offset':off,'parMode':mode})

    def add_temp(self, name):
        off = self._alloc_offset()
        self.scopes[-1]['entities'].append({'kind':'temp','name':name,'offset':off})

    def find_closed_scope(self, name, expected_level):
        for scope_dict in reversed(self.closed_scopes):
            if scope_dict.get('name') == name and scope_dict.get('level') == expected_level:
                return scope_dict
        return None
    
    def push_existing_scope(self, scope_dict):
        self.scopes.append(scope_dict)
        self.current_level = scope_dict.get('level', self.current_level) 

    def pop_scope(self):
        if self.scopes:
            scope = self.scopes.pop()
            if self.scopes:
                self.current_level = self.scopes[-1].get('level', self.current_level -1 if self.current_level > -1 else -1)
            else:
                self.current_level = -1
            return scope
        return None

    def add_subprogram_entry(self, name, kind, arg_kinds_list, start_quad=None, frame_length=None):
        # Προσθέτει ένα function/procedure entry στο τρεχον ενεργό scope.
        if not self.scopes:
            raise Exception(f"SymbolTable Error: Cannot add subprogram entry '{name}'. No active scope.")
        # Έλεγχος για διπλότυπο entry στο τρέχον scope
        for entity in self.scopes[-1]['entities']:
            if entity['name'] == name and entity['kind'] in ('function', 'procedure'):
                print(f"Warning: Subprogram '{name}' already declared in current scope. Overwriting or ignoring.")
                return 

        entry = {'kind':kind, 'name':name, 'start_quad':start_quad, 'frame_length':frame_length, 'args':arg_kinds_list}
        self.scopes[-1]['entities'].append(entry)

# ---------------------- Static Symbol Build ----------------------

def build_symbol_table(node, symtab, param_map): 
    if not isinstance(node, tuple):
        return

    kind = node[0]

    if kind == 'program':
        # node[0] = 'program', node[1] = ID token, node[2] = programblock_node
        if len(node) > 2 and isinstance(node[2], tuple):
            build_symbol_table(node[2], symtab, param_map)

    elif kind == 'programblock':
        # programblock_node: ('programblock', decls_tup, subprogs_tup, seq_node)
        # Επεξεργαζόμαστε μόνο τα subprograms για το param_map
        if len(node) > 2 and isinstance(node[2], tuple): 
            build_symbol_table(node[2], symtab, param_map)

    elif kind == 'subprograms':
        # subprograms_node: ('subprograms', list_of_subprogram_nodes)
        if len(node) > 1 and isinstance(node[1], list):
            for sp_node in node[1]: 
                build_symbol_table(sp_node, symtab, param_map)

    elif kind in ('function', 'procedure'):
        # ('function', id_token, formal_params_node, funcblock_node)
        # ('procedure', id_token, formal_params_node, procblock_node)
        
        if len(node) < 4: 
            print(f"Warning (build_symbol_table): Malformed function/procedure node: {node}")
            return

        func_proc_name_token = node[1]
        if not (isinstance(func_proc_name_token, tuple) and len(func_proc_name_token) > 1):
            print(f"Warning (build_symbol_table): Malformed ID token for function/procedure: {func_proc_name_token}")
            return
        name = func_proc_name_token[1] 

        block_node = node[3] # funcblock_node ή procblock_node
        # funcblock/procblock: ('funcblock'|'procblock', func_input, func_output, declarations, subprograms, sequence)
        
        if not (isinstance(block_node, tuple) and len(block_node) > 5):
            print(f"Warning (build_symbol_table): Malformed block node for {name}: {block_node}")
            return

        func_input_node  = block_node[1] # ('funcinput', varlist_node or [])
        func_output_node = block_node[2] # ('funcoutput', varlist_node or [])
        
        nested_subprograms_node = block_node[4]  # Επεξεργαζόμαστε τα εμφωλιασμένα για το param_map τους

        # Φτιάχνουμε το param_map και τα arg_kinds για την τρέχουσα func/proc
        current_pm_entries = []
    
        # Επεξεργασία παραμέτρων εισόδου
        if func_input_node and func_input_node[0] == 'varlist':
            # func_input_node is ('varlist', [id_token1, id_token2,...])
            for id_token in func_input_node[1]:
                if isinstance(id_token, tuple) and len(id_token) > 1:
                    current_pm_entries.append((id_token[1], 'CV', None)) # (param_name, mode, type)
                    
                else:
                    print(f"Warning (build_symbol_table): Malformed ID token in input params for {name}: {id_token}")

        # Επεξεργασία παραμέτρων εξόδου
        if func_output_node and func_output_node[0] == 'varlist':
            # func_output_node is ('varlist', [id_token1, id_token2,...])
            for id_token in func_output_node[1]:
                if isinstance(id_token, tuple) and len(id_token) > 1:
                    current_pm_entries.append((id_token[1], 'REF', None))
                    
                else:
                    print(f"Warning (build_symbol_table): Malformed ID token in output params for {name}: {id_token}")
        
        if name in param_map and param_map[name] != current_pm_entries:
            print(f"Warning (build_symbol_table): Re-defining param_map for '{name}'. Previous: {param_map[name]}, New: {current_pm_entries}")
            pass
        param_map[name] = current_pm_entries

      
        # Αναδρομική κλήση για τα εμφωλιασμένα subprograms 
        if isinstance(nested_subprograms_node, tuple):
            build_symbol_table(nested_subprograms_node, symtab, param_map)

    else:
        if isinstance(node, tuple):
            for child_node_part in node[1:]: # Εξετάζουμε όλα τα μέρη του tuple μετά το kind
                if isinstance(child_node_part, tuple):
                    build_symbol_table(child_node_part, symtab, param_map)
                elif isinstance(child_node_part, list):
                    for item_in_list in child_node_part:
                        if isinstance(item_in_list, tuple):
                            build_symbol_table(item_in_list, symtab, param_map)


# ---------------------- Final Code Generator ----------------------
class FinalCodeGenerator:
    def __init__(self, quads, symtab, program_name):
        self.quads = quads
        self.symtab = symtab
        self.program_name = program_name
        self.asm_code = []
        self.frame_lengths = {} 
        self.active_scope_level_for_final_code = -1 
        self.newline_label_generated = False # str_nl 
        self.compute_frame_lengths()

    def compute_frame_lengths(self):
        self.frame_lengths.clear()
        global_scope_info = next((s for s in self.symtab.closed_scopes if s.get('level') == 0), None)
        if not global_scope_info:
            print("CRITICAL Error: Cannot compute frame lengths - Global scope info not found in closed_scopes.")
            return

        global_scope_entities = global_scope_info.get('entities', [])

        for scope in self.symtab.closed_scopes:
            name = scope.get('name')
            if name:
                max_offset_abs = abs(scope.get('max_offset', 0))
                if max_offset_abs == 0:
                    if name == self.program_name:
                        frame_len = abs(global_scope_info.get('max_offset',0))
                        frame_len = max(4, frame_len)
                    else:
                        frame_len = 12 + 4 
                else:
                    frame_len = max_offset_abs + 4

                frame_len = (frame_len + 3) & ~3 # Align to 4 bytes
                self.frame_lengths[name] = frame_len

                # Update the frame_length in the global scope's entity list for this func/proc
                if scope.get('level') > 0 :
                    func_proc_entry = next((entry for entry in global_scope_entities
                                            if entry.get('name') == name and
                                               entry.get('kind') in ('function', 'procedure')), None)
                    if func_proc_entry:
                        # Update the dictionary reference within global_scope_entities
                        func_proc_entry['frame_length'] = frame_len

    def find_entity_in_scope(self, name, scope):
        # Helper to find entity by name within a specific scope dictionary
        for ent in scope.get('entities', []):
            if ent.get('name') == name:
                return ent
        return None

    def find_symbol_static_info(self, name):
        # Πρώτα προσπαθούμε όπως πριν στα closed_scopes
        for scope in reversed(self.symtab.closed_scopes):
            for ent in scope.get('entities', []):
                if ent.get('name') == name:
                    return {
                        'kind':    ent['kind'],
                        'level':   scope['level'],
                        'offset':  ent.get('offset'),
                        'parMode': ent.get('parMode')
                    }

        # Αν δεν το βρούμε, ελέγχουμε και στα ακόμα ανοιχτά scopes
        for scope in reversed(self.symtab.scopes):
            for ent in scope.get('entities', []):
                if ent.get('name') == name:
                    return {
                        'kind':    ent['kind'],
                        'level':   scope['level'],
                        'offset':  ent.get('offset'),
                        'parMode': ent.get('parMode')
                    }

        raise ValueError(f"Symbol '{name}' not found anywhere (closed or active scopes).")

    def get_operand_info(self, operand):
        # Returns static info dict for variable/temp/literal
        if isinstance(operand, (int, str)) and str(operand).lstrip('-').isdigit():
            return {'kind': 'literal', 'value': int(operand)}
        elif isinstance(operand, str):
            if not operand: # Handle empty string case
                 raise ValueError("Attempted to get info for an empty operand string.")
            return self.find_symbol_static_info(operand)
        else:
            raise TypeError(f"Unsupported operand type for get_operand_info: {operand}")

    def gnlvcode(self, var_info): 
        code = []
        target_level = var_info.get('level')
        # Το active_scope_level_for_final_code είναι το επίπεδο της τρέχουσας ρουτίνας.
        level_diff = self.active_scope_level_for_final_code - target_level
        if level_diff <= 0:
            raise Exception(f"gnlvcode: Invalid level_diff for non-local access.")

        code.append(f"lw t0, -4(sp)") 
        for _ in range(level_diff - 1):
            code.append(f"lw t0, -4(t0)") 
        
        code.append(f"addi t0, t0, -{var_info['offset']}") 
        return code

    def loadvr(self, operand, target_reg, current_sp_or_fp_base='sp'): 
        info = self.get_operand_info(operand)
        code = []
        
        if info['kind'] == 'literal':
            code.append(f"li {target_reg}, {info['value']}")
        elif info['kind'] in ('variable', 'temp', 'parameter'):
            var_level = info['level']
            var_offset = info['offset']
            is_ref = info.get('parMode') == 'REF'
            base_for_access = current_sp_or_fp_base 

            if var_level == 0: 
                base_for_access = 'gp'
                if is_ref:
                    code.append(f"lw t0, -{var_offset}({base_for_access})")
                    code.append(f"lw {target_reg}, 0(t0)")
                else:
                    code.append(f"lw {target_reg}, -{var_offset}({base_for_access})")
            
            elif var_level == self.active_scope_level_for_final_code: # Τοπική ή παράμετρος στο τρέχον πλαίσιο
                if is_ref: 
                    code.append(f"lw t0, -{var_offset}({base_for_access})") 
                    code.append(f"lw {target_reg}, 0(t0)")             
                else: 
                    code.append(f"lw {target_reg}, -{var_offset}({base_for_access})")
            else: 
                gnlv_code_lines = self.gnlvcode(info) 
                code.extend(gnlv_code_lines)
                if is_ref: 
                    code.append(f"lw t0, 0(t0)")       
                    code.append(f"lw {target_reg}, 0(t0)") 
                else: 
                    code.append(f"lw {target_reg}, 0(t0)")
        else:
            raise TypeError(f"Cannot load operand of kind {info['kind']}")
        return code

    def storerv(self, source_reg, target_variable_name, current_sp_or_fp_base='sp'):
        info = self.get_operand_info(target_variable_name)
        code = []

        if info['kind'] not in ('variable', 'temp', 'parameter'):
             raise TypeError(f"Cannot store into operand of kind {info['kind']}")

        target_level = info['level']
        target_offset = info['offset']
        is_ref = info.get('parMode') == 'REF'
        base_for_access = current_sp_or_fp_base

        if target_level == 0: 
            base_for_access = 'gp'
            if is_ref: 
                code.append(f"lw t0, -{target_offset}({base_for_access})") 
                code.append(f"sw {source_reg}, 0(t0)")
            else:
                code.append(f"sw {source_reg}, -{target_offset}({base_for_access})")
        elif target_level == self.active_scope_level_for_final_code: 
            if is_ref: 
                code.append(f"lw t0, -{target_offset}({base_for_access})") 
                code.append(f"sw {source_reg}, 0(t0)")             
            else: 
                code.append(f"sw {source_reg}, -{target_offset}({base_for_access})")
        else: 
            gnlv_code_lines = self.gnlvcode(info)
            code.extend(gnlv_code_lines)
            if is_ref: 
                code.append(f"lw t0, 0(t0)") 
                code.append(f"sw {source_reg}, 0(t0)")
            else: 
                code.append(f"sw {source_reg}, 0(t0)")
        return code

    def _generate_newline_code(self):
        code = []
        code.append(f"la a0, str_nl")
        code.append(f"li a7, 4") 
        code.append(f"ecall")
        return code
        
    def generate_code(self):
        self.asm_code = []
        data_section = []
        self.newline_label_generated = False

        main_begin_quad_num = next((n for n, op, a1, _, _ in self.quads if op == 'beginblock' and a1 == self.program_name), None)
        if main_begin_quad_num is None: raise ValueError(f"Main program beginblock not found.")

        initial_text = [".text", f"L0: \t# Jump to main", f"\tj L{main_begin_quad_num}"] # Αλλαγή σε L{main_begin_quad_num} αντί για Lmain
        
        generated_quad_code = []
        param_passing_buffer = {} # Dictionary: { callee_name: [params_list], temp_fp_for_params: 'reg_name'}

        for n_quad, op, a1, a2, res in self.quads:
            current_quad_asm = [f"L{n_quad}: \t# {n_quad}: {op}, {a1}, {a2}, {res}"]

            # Ενημέρωση self.active_scope_level_for_final_code στο beginblock
            if op == 'beginblock':
                scope_name_for_level = a1
                scope_info_for_level = next((s for s in reversed(self.symtab.closed_scopes) if s.get('name') == scope_name_for_level), None)
                if not scope_info_for_level and self.symtab.scopes and self.symtab.scopes[-1].get('name') == scope_name_for_level:
                    scope_info_for_level = self.symtab.scopes[-1]
                if scope_info_for_level: self.active_scope_level_for_final_code = scope_info_for_level.get('level')
                else: raise ValueError(f"Scope info for {scope_name_for_level} not found in beginblock.")

            if op == 'beginblock':
                scope_name = a1
                frame_len = self.frame_lengths.get(scope_name)
                if frame_len is None: raise ValueError(f"Frame length for '{scope_name}' not computed.")

                if scope_name == self.program_name:
                    current_quad_asm[0] = f"L{n_quad}: \t# {n_quad}: {op}, {a1}, {a2}, {res}\nLmain:" 
                    current_quad_asm.append(f"\taddi sp, sp, {frame_len}") 
                    current_quad_asm.append(f"\tmv gp, sp")
                else: # func / proc prologue
                    current_quad_asm.append(f"\tsw ra, 0(sp)") 

            elif op == 'endblock':
                scope_name = a1
                if scope_name != self.program_name: # func / proc epilogue
                    current_quad_asm.append(f"\tlw ra, 0(sp)") 
                    current_quad_asm.append(f"\tjr ra")

            elif op == 'halt': 
                current_quad_asm.append(f"\tli a0, 0")
                current_quad_asm.append(f"\tli a7, 93")
                current_quad_asm.append(f"\tecall")

            elif op in ['+', '-', '*', '/']:
                op_map = {'+':'add','-':'sub','*':'mul','/':'div'}
                current_quad_asm.extend([f"\t{line}" for line in self.loadvr(a1, 't1')]) 
                current_quad_asm.extend([f"\t{line}" for line in self.loadvr(a2, 't2')]) 
                current_quad_asm.append(f"\t{op_map[op]} t1, t1, t2") 
                current_quad_asm.extend([f"\t{line}" for line in self.storerv('t1', res)])

            elif op == ':=':
                current_quad_asm.extend([f"\t{line}" for line in self.loadvr(a1, 't1')])
                current_quad_asm.extend([f"\t{line}" for line in self.storerv('t1', res)])

            elif op in ['<','<=','>','>=','=','<>']:
                branch_map = {'<':'blt','<=':'ble','>':'bgt','>=':'bge','=':'beq','<>':'bne'}
                current_quad_asm.extend([f"\t{line}" for line in self.loadvr(a1, 't1')])
                current_quad_asm.extend([f"\t{line}" for line in self.loadvr(a2, 't2')])
                current_quad_asm.append(f"\t{branch_map[op]} t1, t2, L{res}")

            elif op == 'jump':
                current_quad_asm.append(f"\tj L{res}")

            elif op == 'in':
                current_quad_asm.append(f"\tli a7, 5")
                current_quad_asm.append(f"\tecall")
                current_quad_asm.extend([f"\t{line}" for line in self.storerv('a0', res)])

            elif op == 'out':
                current_quad_asm.extend([f"\t{line}" for line in self.loadvr(a1, 'a0')])
                current_quad_asm.append(f"\tli a7, 1")
                current_quad_asm.append(f"\tecall")
                if not self.newline_label_generated:
                    data_section.append("str_nl: .asciz \"\\n\"")
                    self.newline_label_generated = True
                current_quad_asm.extend([f"\t{line}" for line in self._generate_newline_code()])

            elif op == 'retv': 
                current_quad_asm.extend([f"\t{line}" for line in self.loadvr(a1, 't1')]) 
                current_quad_asm.append(f"\tlw t0, -8(sp)")  
                current_quad_asm.append(f"\tsw t1, 0(t0)")
            
            elif op == 'par':
                callee = res
                temp_fp_register_to_use = "fp" 

                if callee not in param_passing_buffer:
                    param_passing_buffer[callee] = {'params': [], 'temp_fp_reg_name_used': temp_fp_register_to_use}
                    callee_frame_len = self.frame_lengths.get(callee)
                    if callee_frame_len is None:
                        raise ValueError(f"Frame length for callee '{callee}' not found for 'par' quad.")
                    current_quad_asm.append(f"\taddi {temp_fp_register_to_use}, sp, {callee_frame_len}")
                
                param_info_for_buffer = {
                    'value_name': a1, 
                    'mode': a2,
                    'index': len(param_passing_buffer[callee]['params']) 
                }
                param_passing_buffer[callee]['params'].append(param_info_for_buffer)

                if a2 == 'RET': 
                    temp_var_info = self.get_operand_info(a1)
                    current_quad_asm.append(f"\taddi t0, sp, -{temp_var_info['offset']}") 
                    current_quad_asm.append(f"\tsw t0, -8({temp_fp_register_to_use})") 
                else:
                    param_slot_offset_val = 12 + param_info_for_buffer['index'] * 4
                    if a2 == 'in': 
                        current_quad_asm.extend([f"\t{line}" for line in self.loadvr(a1, 't0')]) 
                        current_quad_asm.append(f"\tsw t0, -{param_slot_offset_val}({temp_fp_register_to_use})") 
                    elif a2 == 'inout': 
                        actual_param_info = self.get_operand_info(a1)
                        if actual_param_info['level'] == 0: 
                            current_quad_asm.append(f"\taddi t0, gp, -{actual_param_info['offset']}") 
                        elif actual_param_info['level'] == self.active_scope_level_for_final_code: 
                            current_quad_asm.append(f"\taddi t0, sp, -{actual_param_info['offset']}") 
                        else: 
                            gnlv_lines = self.gnlvcode(actual_param_info) 
                            current_quad_asm.extend([f"\t{line}" for line in gnlv_lines])
                        current_quad_asm.append(f"\tsw t0, -{param_slot_offset_val}({temp_fp_register_to_use})") # Χρήση "fp"

            elif op == 'call':
                callee_name = res
                callee_begin_label = f"L{next(qn for qn, q_op, q_a1, _, _ in self.quads if q_op == 'beginblock' and q_a1 == callee_name)}"
                
                call_info = param_passing_buffer.pop(callee_name, None) 
                if call_info is None:
                    if callee_name not in self.param_map or not self.param_map[callee_name]: 
                        print(f"Warning: Calling function {callee_name} which might not have had its 'fp' (temp base for params) set up if no 'par' quads preceded.")
                        temp_fp_for_this_call = "s1" # Fallback, για το fp
                    else:
                         raise ValueError(f"No pre-calculated fp or params in buffer for call to {callee_name}, but params expected.")

                else:
                    temp_fp_for_this_call = call_info['temp_fp_reg_name_used']

                callee_frame_len = self.frame_lengths.get(callee_name)

                current_quad_asm.append(f"\tsw sp, -4({temp_fp_for_this_call})") 
                current_quad_asm.append(f"\taddi sp, sp, {callee_frame_len}") 
                current_quad_asm.append(f"\tjal {callee_begin_label}")
                current_quad_asm.append(f"\taddi sp, sp, -{callee_frame_len}") 
            
            generated_quad_code.extend(current_quad_asm)

        if data_section:
            self.asm_code = [".data"] + data_section + initial_text + generated_quad_code
        else:
            self.asm_code = initial_text + generated_quad_code
            
        return self.asm_code
    
# ---------------------- Main Execution Logic ----------------------
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python gpp_5254_5349_new.py <filename>")
        sys.exit(1)

    input_filename = sys.argv[1]
    base_filename = "output" 
    int_filename = base_filename + ".int"
    sym_filename = base_filename + ".sym"
    asm_filename = base_filename + ".asm"

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            src = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
        sys.exit(1)

    # --- Compilation Pipeline ---
    codegen = None 
    final_gen = None 

    try:
        # 1. Lexer & Parser
        print(f"Parsing '{input_filename}'...")
        lexer = Lexer(src)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        tree = parser.parse()
        print("Parsing completed.")

        program_name = tree[1][1]

        # 2. Symbol Table Construction (Static Pass)
        print("Building symbol table (static pass)...")
        symtab = SymbolTable()
        param_map = {} # Stores parameter modes {func_name: [(param_name, mode, type), ...]}
        build_symbol_table(tree, symtab, param_map)
        print("Symbol table static build completed.")
        # print("Initial Global Scope:", symtab.scopes[0]) 

        # 3. Intermediate Code Generation
        print("Generating intermediate code...")
        codegen = CodeGenerator(symtab, program_name, param_map)
        quads = codegen.generate_program(tree)
        print(f"Intermediate code generation completed ({len(quads)} quads).")

        # 4. Write Intermediate Code (.int)
        with open(int_filename, "w", encoding="utf-8") as int_file:
            for q in quads:
                int_file.write(f"{q[0]}: {q[1]}, {q[2]}, {q[3]}, {q[4]}\n")
        print(f"Intermediate code written to {int_filename}")

        print("Initializing final code generator (for frame lengths)...")
        final_gen = FinalCodeGenerator(quads, codegen.symtab, program_name) 
        print("Final code generator initialized.")

        # 5. Write Symbol Table Snapshots (.sym)
        print(f"Writing symbol table snapshots to {sym_filename}...")
        with open(sym_filename, "w", encoding="utf-8") as sym_file:
            sym_file.write("--- Symbol Table Snapshots ---\n")

            if not codegen.symtab_snapshots:
                 sym_file.write("\nNo snapshots were recorded.\n")
                 print("Warning: No symbol table snapshots recorded by CodeGenerator.")

            for i, snapshot in enumerate(codegen.symtab_snapshots):
                sym_file.write(f"\n--- Snapshot {i+1} ---\n")
                if not snapshot:
                    sym_file.write("(Empty snapshot)\n")
                    continue

                snapshot_global_scope = snapshot[0] if snapshot and snapshot[0].get('level') == 0 else None

                for scope_in_snapshot in snapshot:
                    sym_file.write(f"\nScope: {scope_in_snapshot.get('name', 'Unnamed')} (Level: {scope_in_snapshot.get('level', '?')})\n")
                    sym_file.write("  Entities:\n")
                    if not scope_in_snapshot.get('entities'):
                        sym_file.write("    (No entities)\n")
                    else:
                        for e in scope_in_snapshot.get('entities', []):
                            kind = e.get('kind', '?')
                            name = e.get('name', '?')
                            offset = e.get('offset', '?')
                            mode = e.get('parMode', '')
                            args = e.get('args', '')
                            start_q = e.get('start_quad', 'N/A') # Give default if None
                            # Get the FINAL calculated frame length
                            entity_final_frame_l_raw = final_gen.frame_lengths.get(name) if final_gen and kind in ('function','procedure') else e.get('frame_length')
                            start_q_str = f"{start_q:<4}" if start_q is not None else "N/A "
                            entity_final_frame_l_str = f"{entity_final_frame_l_raw:<4}" if entity_final_frame_l_raw is not None else "N/A "
                           
                            if kind in ('variable', 'temp'):
                                sym_file.write(f"    - {name:<15} | {kind:<10} | offset: {offset}\n")
                            elif kind == 'parameter':
                                sym_file.write(f"    - {name:<15} | {kind:<10} | offset: {offset:<4} | mode: {mode}\n")
                            elif kind in ('function', 'procedure'):
                                # Use the formatted strings
                                sym_file.write(f"    - {name:<15} | {kind:<10} | start_quad: {start_q_str} | frame: {entity_final_frame_l_str} | args: {args}\n")
                            else:
                                sym_file.write(f"    - {name:<15} | {kind:<10}\n")

                sym_file.write("===============================================\n")
        print(f"Symbol table snapshots written to {sym_filename}")

        # 6. Final Code Generation (if final_gen was initialized)
        if final_gen:
            print("Generating final assembly code...")
            asm_lines = final_gen.generate_code()
            print("Final assembly code generation completed.")

            # 7. Write Final Assembly Code (.asm)
            with open(asm_filename, "w", encoding="utf-8") as asm_file:
                 for line in asm_lines:
                     if ':' in line and not line.strip().startswith('.'): # Label
                         asm_file.write(line + "\n")
                     elif line.strip().startswith('.'): # Directive
                         asm_file.write(line + "\n")
                     else: # Instruction
                         asm_file.write("    " + line + "\n")
            print(f"Final assembly code written to {asm_filename}")
        else:
            print("Skipping final code generation due to earlier errors.")

    except (ParserError, ValueError, TypeError, RuntimeError, IndexError, Exception) as e:
        print(f"\n--- COMPILATION FAILED ---")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Message: {e}")
        import traceback
        traceback.print_exc()
        print("-----------------------------")
        sys.exit(1)

    print("\nCompilation finished successfully.")