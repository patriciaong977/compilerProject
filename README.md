# Compilers and Languages Semester Project
Collaborated with @turbo6412 , MKPark, STruong

## Summary
Final version of the compiler project from CPSC 323. The project language is python.

The compiler consists of a lexical analyzer, syntax analyzer and a semantic analyzer. 
It takes a fictional language named Rat21F to generate tokens and write out the results to an output file. It prints both tokens and lexemes. 

## Assignment 1 : Writing a Lexical Analyzer
The problem statement is such, given a source code file: 
1. Read the file
2. Use the lexical analysis process to mint tokens out of the read file 
3. Use the syntax analysis process to define the structures of the source code
4. Finally, use the intermediate code generation and other final processes to finalize the compiler and have it create a working program for execution of the source code file. 

**In the design of the program,** we wrote the REs for Identifiers, Real and Integer, and show the NFSM using Thompson. 
![image](https://user-images.githubusercontent.com/23037963/218324310-ae39c0a2-24a4-4e4a-a4bf-c2bf224b6511.png)
![image](https://user-images.githubusercontent.com/23037963/218324350-43213375-7623-4a40-8fc9-3ce42b873be7.png)

## Assignment 2: Writing a Syntax Analyzer
The problem statement is such, 
1. Rewrite the grammar Rat21F to remove any left recursion
    (Also, use left factorization if necessary) 
2. Use the lexer()  generated in the assignment 1 to get the tokens
3. The parser should print to an output file the tokens, lexemes and 
    the production rules used
4. Error handling: if a syntax error occurs, your parser should generate a meaningful error message, such as token, lexeme, line number, and error type etc. 
Then, your program may exit or you may continue for further analysis.
Basically the program must be able to parse the entire program if it is syntactically correct.

**In the design of the program,** we utilized the Recursive Descent Parser (RDP) method to go through the RA21F grammar rules and get rid of left-recursion and backtracking. Then we made one function or procedure per non-terminal symbol
    
## Assignment 3: Writing a Semantic Analyzer
Part 1)  Symbol table Handling (2%): 
Every identifier declared in the program should be placed in a symbol table and accessed by the symbol table handling procedures.

1. Each entry in the symbol table should hold the lexeme, and a "memory address" where an  identifier is placed within the symbol table.  
    - For example, define a global integer variable called "Memory_address" and set initially 7000 and increment it by one when a new identifier is declared and placed into the table. 

2. You need to write a procedure that will check to see if a particular identifier is already in the table, a procedure that will insert into the table and a procedure that will printout all identifiers in the table. 
    - If an identifier is used without declaring it, then the parser should provide an error message. Also, if an identifier is already in the table and wants to declare it for the second time, then the parser should provide an error message. Also, you should check the type match.

Part 2) Generating the assembly code (8%):
Modify your parser according to the simplified Rat21F and add code to your parser that will produce the assembly code instructions. The instructions should be kept in an array and at the end, the content of the array is printed out to produce the listing of assembly code. Your array should hold at least 1000 assembly instructions. The instruction starts from 1.

The listing should include an array index for each entry so that it serves as label to jump to.  

The compiler should also produce a listing of all the identifiers.  

**In the design of the program,** we built on top of the previous project’s Syntax analyzer. We used a dictionary to represent our symbol table, and an array to represent our instructions list.  Our grammar routines generate assembly instructions and symbols that are printed to an output file upon successful compilation.
