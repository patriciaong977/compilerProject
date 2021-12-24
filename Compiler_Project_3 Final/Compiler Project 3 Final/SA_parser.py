from typing import NamedTuple
from lexer import *
import sys
from time import gmtime, localtime, strftime

# FIX TERM OR EXPRESSION PRIME FACTOR LOGIC WILL GLITCH OUT AFTER a+b


class Symbol():
    def __init__(self, name, memoryLocationOffset, type):
        self.name = name
        self.memoryLocation = memoryLocationOffset
        self.type = type


class parser():

    keyWords = {'while': 'keyword', 'integer': 'keyword', 'if': 'keyword', 'else': 'keyword',
                'endif': 'keyword', 'get': 'keyword', 'put': 'keyword', 'boolean': 'keyword', 'begin': 'keyword',
                'end': 'keyword', 'true': 'keyword', 'false': 'keyword', 'function': 'keyword', 'return': 'keyword', 'real': 'keyword'}
    separator = {'(': 'separator', ')': 'separator', ',': 'separator',
                 ';': 'separator', '{': 'separator', '}': 'separator', '#': 'separator'}
    operator = {'/': 'operator', '=': 'operator', '>': 'operator', '<': 'operator', '+': 'operator', '-': 'operator',
                '==': 'operator', '/=': 'operator', '*': 'operator', '<=': 'operator', '>=': 'operator', '=>': 'operator', '=<': 'operator', '!=': 'operator', }

    # Data structures for:
    # Symbol Table
    symbolTable = dict()
    currentMemoryLocationOffset = 7000
    # Instruction Table
    instruction_list = list()
    temp_names_list = []

    def __init__(self, lexemes):
        self.lexemes = lexemes
        self.ptr_token = iter(lexemes)
        self.token = next(self.ptr_token)
        current_time = strftime("%Y-%m-%d %H-%M-%S", localtime())
        self.outputFile = open(
            "SA_output_test" + str(current_time) + ".txt", "w")

        self.outputFileSemantic = open(
            "SA_outputSemantic_test" + str(current_time) + ".txt", "w")

    def iterate(self):
        self.token = next(self.ptr_token, None)

    def generateInstruction(self, instructionType, operand):
        self.instruction_list.append((instructionType, operand))

    def statement_list(self):
        self.print_token_lex()
        self.statement()
        self.statement_list_prime()

    def statement_list_prime(self):
        if (self.token == "{" or self.token == "if"
            or self.token == "get" or self.token == "put"
            or self.token == "while" or self.token == "return"
                or (lexer.identifierFsm(lexer, self.token) == 1 and self.token not in self.keyWords)):
            self.print_prod_rule("<Statement List Prime> -> <Statement List>")
            self.statement_list()
        elif self.token == "integer" or self.token == "boolean":
            self.print_prod_rule(
                "Error: unexpected qualifier in statement_list_prime")
        else:
            self.print_prod_rule("<Statement List Prime> -> e")

    def statement(self):
        if self.token == "{":
            self.print_prod_rule("<Statement> -> <Compound>")
            self.compound()
        elif lexer.identifierFsm(lexer, self.token) == 1 and self.token not in self.keyWords:
            self.print_prod_rule("<Statement> -> <Assign>")
            self.assign()
        elif self.token == "if":
            self.print_prod_rule("<Statement> -> <If>")
            self._if()
        elif self.token == "get":
            self.print_prod_rule("<Statement> -> <Get>")
            self.get()
        elif self.token == "put":
            self.print_prod_rule("<Statement> -> <Put>")
            self.put()
        elif self.token == "while":
            self.print_prod_rule("<Statement> -> <While>")
            self.while_loop()
        elif self.token == "return":
            self.print_prod_rule("<Statement> -> <Return>")
            self.Return()
        else:
            print(
                "Error: Expected <Statement> type: begin, if, get, put, while, or <Identifier> type.")
            sys.exit(1)

    def Return(self):
        self.print_prod_rule("Return -> return ; |  return <Expression> ;")
        if self.token == "return":
            self.iterate()
            self.print_token_lex()
            self.ReturnPrime()
            if self.token == ";":
                self.iterate()
            else:
                print("Error: expected \";\" in <Return>")

    def ReturnPrime(self):
        if self.token != ";":
            self.expression()

    def compound(self):
        self.print_prod_rule("<Compound> ->  { <Statement List> }")
        self.iterate()
        self.statement_list()
        if self.token == "}":
            self.print_token_lex()
            self.iterate()
        else:
            print("Error: Expected \"}\" in compound statement.")
            sys.exit(1)

    def assign(self):
        self.print_prod_rule("<Assign> -> <Identifier> = <Expression> ;")

        if self.token in self.symbolTable:
            destinationOperand = self.symbolTable[self.token].memoryLocation
        else:
            print("ERROR: Undefined identifier symbol: " + self.token + ".")
            sys.exit(1)

        self.iterate()
        self.print_token_lex()

        if self.token == "=":
            self.iterate()
            self.print_token_lex()
            self.expression()

            self.generateInstruction("POPM", destinationOperand)

            self.print_token_lex()
            if self.token == ";":
                self.iterate()
            else:
                print("Error: Expected \";\" in <Assign>.")

        else:
            print("Error: Expected \"=\" in <Assign>.")
            sys.exit(1)

    def _if(self):
        self.print_prod_rule(
            "<If> -> if (<Condition>) <Statement> <IfPrime> endif")
        self.iterate()
        self.print_token_lex()
        if (self.token == "("):
            self.iterate()
            self.print_token_lex()
            self.condition()
            self.print_token_lex()
            if self.token == ")":
                save_instruction_number = len(self.instruction_list)
                self.generateInstruction("X", -1)
                self.iterate()
                self.print_token_lex()
                self.statement()
                self.IfPrime(save_instruction_number)
                if self.token == "endif":
                    self.print_token_lex()
                    self.iterate()
                else:
                    print("Error: Expected separator \"endif\"")
                    sys.exit(1)
            else:
                print("Error: Expected separator \")\" ")
                sys.exit(1)
        else:
            print("Error: Expected separator \"(\" ")
            sys.exit(1)

            # R18. <If> ::=         if  ( <Condition>  ) <Statement> <IfPrime>   endif   |
            # R18b <IfPrime> ::=    else  <Statement>  | e

    def IfPrime(self, previous_saved_instruction_number):
        save_instruction_number = len(self.instruction_list)
        self.generateInstruction("X", -1)
        self.instruction_list[previous_saved_instruction_number] = (
            "JUMPZ", len(self.instruction_list) + 1)
        if self.token == 'else':
            self.print_prod_rule("<IfPrime> -> else  <Statement>")
            self.iterate()
            self.print_token_lex()
            self.statement()
            self.instruction_list[save_instruction_number] = (
                "JUMP", len(self.instruction_list) + 1)
        else:
            self.print_prod_rule("<IfPrime> -> e")

    def while_loop(self):
        self.print_prod_rule("<While> -> while (<Condition>) <Statement>")
        self.iterate()
        self.print_token_lex()
        if (self.token == "("):
            self.iterate()
            self.print_token_lex()
            temp_label_instruction_index = len(self.instruction_list)
            self.generateInstruction("LABEL", "")
            self.condition()
            self.print_token_lex()
            if self.token == ")":
                temp_jumpz_instruction_index = len(self.instruction_list)
                self.generateInstruction("JUMPZ", -1)
                self.iterate()
                self.print_token_lex()
                self.statement()
                self.generateInstruction(
                    "JUMP", temp_label_instruction_index + 1)
                self.instruction_list[temp_jumpz_instruction_index] = (
                    self.instruction_list[temp_jumpz_instruction_index][0], len(self.instruction_list) + 1)
            else:
                print("Error: Expected separator \")\" ")
                sys.exit(1)
        else:
            print("Error: Expected separator \"(\" ")
            sys.exit(1)

    def get(self):
        self.print_prod_rule("<Get> -> get(<IDs>)")
        self.iterate()
        self.print_token_lex()
        if (self.token == "("):
            self.iterate()
            self.print_token_lex()
            if lexer.identifierFsm(self, self.token) == 1 and self.token not in self.keyWords:
                if self.token in self.symbolTable:
                    saved_memory_location = self.symbolTable[self.token].memoryLocation
                else:
                    print("ERROR: undeclared variable in get()")
                    sys.exit(1)
                self.IDs()
                self.print_token_lex()
                if self.token == ")":
                    self.generateInstruction("STDIN", " ")
                    self.generateInstruction("POPM", saved_memory_location)
                    self.iterate()
                    self.print_token_lex()
                    if self.token == ";":
                        self.iterate()
                    else:
                        print("Error: Expected \";\" in <Get>.")
                else:
                    print("Error: Expected separator \")\" ")
                    sys.exit(1)
            else:
                print("Error: expected an identifier in <get> ")
                sys.exit(1)
        else:
            print("Error: Expected separator \"(\" ")
            sys.exit(1)

    def put(self):
        self.print_prod_rule("<Put> -> put (<Expression>)")
        self.iterate()
        self.print_token_lex()
        if (self.token == "("):
            self.iterate()
            self.print_token_lex()
            self.expression()
            self.print_token_lex()
            if self.token == ")":
                self.generateInstruction("STDOUT", " ")
                self.iterate()
                self.print_token_lex()
                if self.token == ";":
                    self.iterate()
                else:
                    print("Error: Expected \";\" in <put>.")
            else:
                print("Error: Expected separator \")\" ")
                sys.exit(1)
        else:
            print("Error: Expected separator \"(\" ")
            sys.exit(1)

    def condition(self):
        self.print_prod_rule(
            "<Condition> -> <Expression> <Relop> <Expression>")
        self.expression()
        save_token = self.token
        if save_token == ">=":
            save_operand_1 = self.currentMemoryLocationOffset
            self.generateInstruction("POPM", save_operand_1)
            self.currentMemoryLocationOffset += 1
        elif save_token == "<=":
            self.generateInstruction("GRT", "nil")
        self.relop()
        self.expression()
        if save_token == ">":
            self.generateInstruction("GRT", "nil")
        elif save_token == "<":
            self.generateInstruction("LES", "nil")
        elif save_token == "==":
            self.generateInstruction("EQU", "nil")
        elif save_token == "!=":
            self.generateInstruction("NEQ", "nil")
        elif save_token == ">=":
            save_operand_2 = self.currentMemoryLocationOffset
            self.generateInstruction("POPM", self.currentMemoryLocationOffset)
            self.currentMemoryLocationOffset += 1
            self.generateInstruction("PUSHM", save_operand_1)
            self.generateInstruction("PUSHM", save_operand_2)
            self.generateInstruction("GRT", "nil")
            # Since we have saved the operands in memory we can use them multiple times
            # by pushing the value on to the stack from memory
            self.generateInstruction("PUSHM", save_operand_1)
            self.generateInstruction("PUSHM", save_operand_2)
            self.generateInstruction("EQU", "nil")
            # This final EQU makes sure that both the GTR and EQU were true, by checking
            # If they add up to 2 (true + true)
            self.generateInstruction("ADD", "nil")
            self.generateInstruction("PUSHI", 2)
            self.generateInstruction("EQU", "nil")
            self.currentMemoryLocationOffset += 1
        elif save_token == "<=":
            save_operand_2 = self.currentMemoryLocationOffset
            self.generateInstruction("POPM", self.currentMemoryLocationOffset)
            self.currentMemoryLocationOffset += 1
            self.generateInstruction("PUSHM", save_operand_1)
            self.generateInstruction("PUSHM", save_operand_2)
            self.generateInstruction("LES", "nil")
            # Since we have saved the operands in memory we can use them multiple times
            # by pushing the value on to the stack from memory
            self.generateInstruction("PUSHM", save_operand_1)
            self.generateInstruction("PUSHM", save_operand_2)
            self.generateInstruction("EQU", "nil")
            # This final EQU makes sure that both the GTR and EQU were true, by checking
            # If they add up to 2 (true + true)
            self.generateInstruction("ADD", "nil")
            self.generateInstruction("PUSHI", 2)
            self.generateInstruction("EQU", "nil")
            self.currentMemoryLocationOffset += 1

    def relop(self):
        if self.token == "==":
            self.print_prod_rule("<Relop> -> ==")
            self.iterate()
            self.print_token_lex()

        elif self.token == ">":
            self.print_prod_rule("<Relop> -> >")
            self.iterate()
            self.print_token_lex()

        elif self.token == ">=":
            self.print_prod_rule("<Relop> -> >=")
            self.iterate()
            self.print_token_lex()

        elif self.token == "<":
            self.print_prod_rule("<Relop> -> <")
            self.iterate()
            self.print_token_lex()

        elif self.token == "<=":
            self.print_prod_rule("<Relop> -> <=")
            self.iterate()
            self.print_token_lex()

        elif self.token == "/=":
            self.print_prod_rule("<Relop> -> /=")
            self.iterate()
            self.print_token_lex()

        elif self.token == "!=":
            self.print_prod_rule("<Relop> -> !=")
            self.iterate()
            self.print_token_lex()

        else:
            print("ERROR: Expected Relop of == or > or < or /= ")
            sys.exit(1)

    def expression(self):
        # print a rule
        self.print_prod_rule("<Expression> -> <Term> <Expression Prime>")
        self.term()
        if self.token == "+" or self.token == "-":
            save_token = str(self.token)
            self.expressionPrime()
            if save_token == "+":
                self.generateInstruction("ADD", "nil")
            elif save_token == "-":
                self.generateInstruction("SUB", "nil")

    def expressionPrime(self):

        if self.token == "+":
            self.print_token_lex()
            self.print_prod_rule(
                "<Expression Prime> -> + <Term> <Expression Prime>")
            self.iterate()
            self.print_token_lex()
            self.term()
            self.expressionPrime()

        elif self.token == "-":
            self.print_token_lex()
            self.print_prod_rule(
                "<Expression Prime> -> - <Term> <Expression Prime>")
            self.iterate()
            self.print_token_lex()
            self.term()
            self.expressionPrime()
        else:
            self.print_prod_rule(
                "<Expression Prime> -> e")

    def term(self):
        self.print_prod_rule("<Term> -> <Factor> <Term Prime>")
        self.factor()
        if self.token == "*" or self.token == "/":
            save_token = str(self.token)
            self.termPrime()
            if save_token == "*":
                self.generateInstruction("MUL", "nil")
            elif save_token == "/":
                self.generateInstruction("DIV", "nil")

    def termPrime(self):

        if self.token == "*":
            self.print_token_lex()
            self.print_prod_rule(
                "<Term Prime> -> * <Term Prime>")
            self.iterate()
            self.print_token_lex()
            self.factor()
            self.termPrime()
        elif self.token == "/":
            self.print_token_lex()
            self.print_prod_rule("<Term Prime> -> / <Term Prime>")
            self.iterate()
            self.print_token_lex()
            self.factor()
            self.termPrime()
        else:
            self.print_prod_rule("<Term Prime> -> e")

    def factor(self):
        self.print_prod_rule("<Factor> -> - <Primary> | <Primary>")
        if self.token == "-":
            self.iterate()
            self.print_token_lex()
            self.primary()
        else:
            self.primary()

    def IDs(self):
        if lexer.identifierFsm(lexer, self.token) == 1 and self.token not in self.keyWords:
            self.print_prod_rule("IDs -> <Identifier>  | <Identifier>, <IDs>")
            self.IDsPrime()

    def IDsPrime(self):
        self.iterate()
        if self.token == ",":
            print("saw the comma")
            self.print_token_lex()
            self.iterate()
            self.temp_names_list.append(self.token)
            self.print_token_lex()
            self.IDs()

    def primary(self):
        self.print_prod_rule(
            "<Primary> -> <Identifier> | <Integer> | <Identifier> ( <IDs> ) | ( <Expression> ) | <Real> | true | false ")
        if lexer.identifierFsm(lexer, self.token) == 1:
            # instruction for operand to operator determined in expression()
            if self.token in self.symbolTable:
                operand = self.symbolTable[self.token].memoryLocation
                instructionType = "PUSHM"
            else:
                self.outputFileSemantic.write(
                    "ERROR: Undeclared identifier: " + self.token + ".")
                print("ERROR: Undeclared identifier: " + self.token + ".")
                sys.exit(1)
            self.iterate()
            if self.token == "(":
                self.print_token_lex()
                self.iterate()
                self.print_token_lex()
                self.IDs()
                if self.token == ")":
                    self.print_token_lex()
                    self.iterate()
                else:
                    print("Error: factor() expected a closing parenthesis")
                    sys.exit(1)

        elif lexer.integerFSM(lexer, self.token) == 1 or lexer.realFSM(lexer, self.token) == 1 or self.token == "true" or self.token == "false":
            operand = self.token
            instructionType = "PUSHI"
            self.iterate()

        elif self.token == "(":

            self.iterate()
            self.print_token_lex()
            self.expression()
            self.print_token_lex()

            if self.token == ")":
                self.iterate()
            else:
                print("Error: factor() expected a closing parenthesis")
                sys.exit(1)

        else:
            print("Error: factor() expected an id")
            sys.exit(1)

        self.generateInstruction(instructionType, operand)

    def Empty(self):
        self.print_prod_rule("<Empty> -> e")

    def Rat21F(self):
        # This should be either a loop or a function that represents a rule that includes the entire text of the program
        # I believe this is StatementList()
        # change next time, this is temporary, crashes because line 69, prob doesn't know the token is a string for FSM
        self.print_prod_rule(
            "Rat21F -> <Opt Function Definitions>  #  <Opt Declaration List>  <Statement List>  #")
        self.print_token_lex()
        self.OptFuncDef()
        if self.token != "#":
            print("Error: Rat21F() expected a \"#\"")
            sys.exit(1)
        self.iterate()
        self.print_token_lex()
        self.OptDeclarationList()
        self.statement_list()
        self.print_token_lex()
        if self.token != "#":
            print("Error: Rat21F() expected a \"#\"")
            sys.exit(1)
        self.print_instruction_list()
        self.print_symbol_table()
        self.outputFile.close()

    def OptFuncDef(self):
        if self.token == "function":
            self.print_prod_rule(
                "<Opt Function Definitions> -> <Function Definitions> ")
            self.FunctionDefinitions()
        else:
            self.print_prod_rule("<Opt Function Definitions> ->  <Empty>")
            self.Empty()

    def FunctionDefinitions(self):
        self.print_prod_rule(
            "<Function Definitions> -> <Function> | <Function> <Function Definitions>")
        if self.token == "function":
            self.Function()
            self.print_token_lex()
            self.FunctionDefinitions()

    def Function(self):
        self.print_prod_rule(
            "<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        if self.token == "function":
            self.iterate()
            self.print_token_lex()
            if lexer.identifierFsm(lexer, self.token) == 1 and self.token not in self.keyWords:
                self.iterate()
                self.print_token_lex()
                if self.token == "(":
                    self.iterate()
                    self.print_token_lex()
                    self.ParameterList()
                    if self.token == ")":
                        self.iterate()
                        self.print_token_lex()
                        self.OptDeclarationList()
                        self.Body()
                    else:
                        print("Error: expected \")\"")
                        sys.exit(1)
                else:
                    print("Error: expected \"(\"")
                    sys.exit(1)
        else:
            print("Error: expected keyword \"function\"")
            sys.exit(1)

    def Body(self):
        self.print_prod_rule("<Body> -> {  < Statement List>  }")
        if self.token == "{":
            self.iterate()
            self.statement_list()
            self.print_token_lex()
            if self.token == "}":
                self.iterate()
            else:
                print("Error: expected \"}\"")
                sys.exit(1)
        else:
            print("Error: expected \"{\"")
            sys.exit(1)

    def ParameterList(self):
        self.print_prod_rule("<Opt Parameter List> ->  <Parameter List>")
        if lexer.identifierFsm(self, self.token) == 1 and self.token not in self.keyWords:
            self.IDs()
            self.print_token_lex()
            self.Qualifier()
            self.ParameterListPrime()
        else:
            self.print_prod_rule("<Opt Parameter List> -> <Empty>")
            self.Empty()

    def ParameterListPrime(self):
        self.iterate()
        self.print_token_lex()
        if self.token == ",":
            self.print_token_lex()
            self.iterate()
            self.print_token_lex()
            self.ParameterList()

    def OptDeclarationList(self):
        if self.token == "integer" or self.token == "boolean" or self.token == "real":
            self.print_prod_rule(
                "<Opt Declaration List> -> <Declaration List>")
            self.DeclarationList()
        else:
            self.print_prod_rule("<Opt Declaration List> ->  <Empty>")
            self.Empty()

    def DeclarationList(self):
        self.print_prod_rule(
            "<Declaration List> -> <Declaration> <Declaration List Prime>")
        self.Declaration()
        # self.iterate()
        # next token needs to be semicolon ; after calling Declaration
        if self.token == ";":
            self.print_token_lex()
            # Call DeclarationListPrime
            self.DeclarationListPrime()
        else:
            print("Error: Expected ';' after <identifier>")
            sys.exit(1)

    def DeclarationListPrime(self):
        self.iterate()
        self.print_token_lex()
        if self.token == "integer" or self.token == "boolean" or self.token == "real":
            # If token is start of other declaration, return to declaration list
            self.print_prod_rule(
                "<Declaration List Prime> -> <Declaration List>")
            self.DeclarationList()
        else:
            self.print_prod_rule("<Declaration List Prime> -> e")

    def Declaration(self):
        self.print_prod_rule("<Declaration> -> <Qualifier> <identifier>")
        type = self.token
        self.Qualifier()
        # Qualifier rule passes, take the next token from lexer and check if it is identifier type
        self.iterate()
        self.print_token_lex()
        if lexer.identifierFsm(self, self.token) == 1 and self.token not in self.keyWords:
            self.temp_names_list.clear()
            self.temp_names_list.append(self.token)
            self.IDs()
            for name in self.temp_names_list:
                if name not in self.symbolTable:
                    self.symbolTable[name] = Symbol(
                        name, self.currentMemoryLocationOffset, type)
                    self.currentMemoryLocationOffset += 1
                else:
                    self.outputFileSemantic.write("ERROR: Attempted redeclaration of symbol: " + name + ".\n")
                    print("ERROR: Attempted redeclaration of symbol: " + name + ".\n")
                    sys.exit(1)
        else:
            print("Error: Expected identifier to come after Qualifier")
            sys.exit(1)

    def Qualifier(self):
        if self.token == "integer":
            self.print_prod_rule("<Qualifier> -> integer")
        elif (self.token == "boolean"):
            self.print_prod_rule("<Qualifier> -> boolean")
        elif (self.token == "real"):
            self.print_prod_rule("<Qualifier> -> real")
        else:
            # output error and exit program, prevents returning function call
            print("Error: Expected qualifier of integer or boolean.")
            sys.exit(1)

    def print_token_lex(self):
        # write the token and lexeme found

        print(self.token)
        if self.token in self.operator:
            print(self.operator[self.token], ":", self.token)
            self.outputFile.write(f"Operator : \t\t{self.token} \n")
        elif self.token in self.keyWords:
            print(f"is Keyword? : {self.token}")
            self.outputFile.write(f"Keyword : \t\t{self.token} \n")
        elif self.token in self.separator:
            print(self.separator[self.token], "      :", self.token)
            self.outputFile.write(f"Separator : \t{self.token} \n")

        else:
            # For identifier
            result = lexer.identifierFsm(lexer, self.token)
            if result == 1:
                print(f"is identifier? : {self.token}")
                self.outputFile.write(f"Identifier : \t{self.token} \n")

            # For integer
            elif result == 0:
                resultInt = lexer.integerFSM(lexer, self.token)
                if resultInt == 1:
                    print(f"is Integer? : {self.token}")
                    self.outputFile.write(f"Integer : \t{self.token} \n")

                # For real
                elif resultInt == 0:
                    resultReal = lexer.realFSM(lexer, self.token)
                    if resultReal == 1:
                        print(f"is Real? : {self.token}")
                        self.outputFile.write(f"Real : \t{self.token} \n")

                    else:
                        self.outputFile.write(
                            f"ILLEGAL TOKEN : \t{self.token} \n")
                        print("not a valid token")

    def print_prod_rule(self, rule):
        # print out all productions rules
        self.outputFile.write("\t" + rule + "\n")
        print(rule)

    def print_instruction_list(self):
        self.outputFileSemantic.write(
            "{:<12}  {:<15}  {:<12}\n".format("Instruction", "Type", "Operand"))
        for i, (instructionType, operand) in enumerate(self.instruction_list, start=1):
            self.outputFileSemantic.write("{:<12}  {:<12}  {:<12}\n".format(
                str(i), str(instructionType), str(operand)))
        self.outputFileSemantic.write("\n")

    def print_symbol_table(self):
        self.outputFileSemantic.write("{:<12}  {:<15}  {:<12}\n".format(
            "Identifier", "MemoryLocation", "Type"))
        for symbol in self.symbolTable.values():
            self.outputFileSemantic.write("{:<12}  {:<15}  {:<12}\n".format(
                str(symbol.name), str(symbol.memoryLocation), str(symbol.type)))
        self.outputFileSemantic.write("\n")
