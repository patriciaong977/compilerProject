#!/usr/bin/env python3

from lexer import *
from SA_parser import *
from enum import Enum
from time import gmtime, localtime, strftime


# For multiple output files using time executed


def main():
    class States(Enum):
        DEFAULT = 0
        TOKEN_KEY_ID = 1  # for keyWord and identifier
        END_TOKEN = 2
        COMMENT = 3
        TOKEN_NUMBER = 4
        TOKEN_SEP_OPR = 5
        TOKEN_ILLEGAL = 6

    keyWords = {'while': 'keyword', 'integer': 'keyword', 'if': 'keyword', 'else': 'keyword',
                'endif': 'keyword', 'get': 'keyword', 'put': 'keyword', 'boolean': 'keyword', 'begin': 'keyword',
                'end': 'keyword', 'true': 'keyword', 'false': 'keyword', 'function': 'keyword', 'return': 'keyword', 'real': 'keyword'}
    separator = {'(': 'separator', ')': 'separator', ',': 'separator',
                 ';': 'separator', '{': 'separator', '}': 'separator', '#': 'separator'}
    operator = {'/': 'operator', '=': 'operator', '>': 'operator', '<': 'operator', '+': 'operator', '-': 'operator',
                '==': 'operator', '/=': 'operator', '*': 'operator', '<=': 'operator', '>=': 'operator', '=>': 'operator', '=<': 'operator', '!=': 'operator', }

    # one char on purpose for separator and operator to build the token ex: % + % = %%
    sep_opr_chars = ['/', '=', '>', '<', '+',
                     '-', '*', '(', ')', ';', '{', '}', '#', ',', '!']

    # dataFlag = False

    # Class obj
    lexerClass = lexer("test")

    val = input("Enter filename: ")
    # val = "test2.txt"

    file = open(val)
    # fileName = val
    # sourceCodeFile = open(file, encoding = 'utf-8')

    a = file.read()
    a += '\n'

    # Multiple outputfile according to time executed
    current_time = strftime("%Y-%m-%d %H-%M-%S", localtime())

    outputFile = open("LA_output_test" + str(current_time) + ".txt", "w")
    # sourceCodeFile = a.split("\n")

    state = States.DEFAULT

    lexemes = []

    backup = False

    current_token = ""
    # for line in sourceCodeFile:
    # print(line)
    # print(state)
    line = a
    i = 0

    outputFile.write(f"TOKEN: \t\t\t LEXEME: \n")

    while i < len(line):
        if i < len(line):
            current_char = line[i]
        else:
            current_char = " "

        if i < len(line) - 1:
            next_char = line[i+1]
        else:
            next_char = ""
        char_check = ord(current_char)

        if state == States.DEFAULT:
            # print("In default state, current char:" + current_char)
            # whitespace, tabs, null
            if current_char != " " and current_char != "\t" and current_char != "\n" and current_char != "\r":

                #  letters (upper, lower) and underscore
                if (char_check >= 65 and char_check <= 90) or (char_check >= 95 and char_check <= 122):
                    # print("We should be entering state for keyword/id")
                    current_token += current_char
                    state = States.TOKEN_KEY_ID
                # integers
                elif char_check >= 48 and char_check <= 57:
                    current_token += current_char
                    state = States.TOKEN_NUMBER
                elif current_char in sep_opr_chars:
                    if current_char + next_char != "/*":
                        current_token = current_char
                        state = States.TOKEN_SEP_OPR
                    else:
                        i = i + 1
                        state = States.COMMENT
                else:
                    current_token += current_char
                    state = States.TOKEN_ILLEGAL

        elif state == States.COMMENT:
            if current_char + next_char == "*/":
                i = i + 1
                state = States.DEFAULT

        elif state == States.TOKEN_KEY_ID:
            # print("We are now in keyword/id state, current char = " + current_char)
            if lexerClass.identifierFsm(current_token + current_char) == 0:
                # print("We should be entering state for end token")
                backup = True
                state = States.END_TOKEN
            else:
                current_token += current_char

        elif state == States.TOKEN_NUMBER:
            # print(current_token + current_char)
            if lexerClass.integerFSM(current_token + current_char) == 0:
                if lexerClass.realFSM(current_token + current_char) == 0:
                    backup = True
                    state = States.END_TOKEN
                else:
                    current_token += current_char
            else:
                current_token += current_char

        elif state == States.TOKEN_SEP_OPR:
            if (current_token in operator or current_token in separator) and (current_token + current_char not in operator and current_token + current_char not in separator):
                backup = True
                state = States.END_TOKEN
            elif current_char not in sep_opr_chars:
                backup = True
                state = States.END_TOKEN
            else:
                current_token += current_char

        elif state == States.END_TOKEN:
            # print(current_token)
            lexemes.append(current_token)
            current_token = ""
            backup = True
            state = States.DEFAULT

        elif state == States.TOKEN_ILLEGAL:
            if current_char != " " and current_char != "\t" and current_char != "\n" and current_char != "\r":
                current_token += current_char
            else:
                backup = True
                state = States.END_TOKEN

        if backup:
            # print("backup")
            i -= 1
            backup = False
        i += 1

    print(lexemes)

    for token in lexemes:
        if token in operator:
            print(operator[token], ":", token)
            outputFile.write(f"Operator : \t\t{token} \n")
        elif token in keyWords:
            print(f"is Keyword? : {token}")
            outputFile.write(f"Keyword : \t\t{token} \n")
        elif token in separator:
            print(separator[token], "      :", token)
            outputFile.write(f"Separator : \t{token} \n")

        else:
            # For identifier
            result = lexerClass.identifierFsm(token)
            if result == 1:
                print(f"is identifier? : {token}")
                outputFile.write(f"Identifier : \t{token} \n")

            # For integer
            elif result == 0:
                resultInt = lexerClass.integerFSM(token)
                if resultInt == 1:
                    print(f"is Integer? : {token}")
                    outputFile.write(f"Integer : \t{token} \n")

                # For real
                elif resultInt == 0:
                    resultReal = lexerClass.realFSM(token)
                    if resultReal == 1:
                        print(f"is Real? : {token}")
                        outputFile.write(f"Real : \t{token} \n")

                    else:
                        outputFile.write(f"ILLEGAL TOKEN : \t{token} \n")
                        print("not a valid token")

    # sourceCodeFile.close()
    outputFile.close()

    parserClass = parser(lexemes)
    parserClass.Rat21F()


if __name__ == "__main__":
    main()
