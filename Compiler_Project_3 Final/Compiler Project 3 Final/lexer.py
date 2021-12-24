class lexer:

    def __init__(self, name):
        self.name = name
        self.tricks = []    # creates a new empty list for each dog

    def checkKey(self, char, hashTable):
        if char in hashTable:
            return hashTable[char]
        else:
            return False

    def identifierFsm(self, id_str):
        FSM = [[1, 4, 5], [2, 3, 5], [2, 3, 5],
               [2, 3, 5], [4, 4, 5], [5, 5, 5]]
        state = 0
        length_str = len(id_str)

        # get every ascii value of string and put into array
        ascii_values = [ord(character) for character in id_str]
        for i in range(length_str):

            # check if the current ascii value is an identifier
            char_check = ascii_values[i]

            if char_check >= 65 and char_check <= 90 or char_check >= 95 and char_check <= 122:
                state = FSM[state][0]

            elif char_check >= 48 and char_check <= 57:
                state = FSM[state][1]

            else:
                state = FSM[state][2]

        if state == 1 or state == 2 or state == 3:
            return 1

        else:
            return 0

    # Integer FSM
    def integerFSM(self, int_str):
        length_str = len(int_str)

        FSM = [[2, 1], [2, 1], [2, 2]]
        state = 0

        # get every ascii value of line and put into array
        ascii_values = [ord(character) for character in int_str]
        for i in range(length_str):
            # check if the current ascii value is an identifier
            char_check = ascii_values[i]

            if char_check >= 48 and char_check <= 57:
                state = FSM[state][1]

            # elseif a decimal then call function realFSM

            elif char_check == 46:
                # self.realFSM(int_str) fixed for SA
                return 0
            else:
                state = FSM[state][0]

        if state == 1:
            return 1

        return 0

    # Real FSM - same logic as integer, just takes in a decimal now
    # input: 22.20
    def realFSM(self, real_str):
        length_str = len(real_str)

        FSM = [[2, 1], [2, 1], [2, 2]]
        state = 0
        dec_count = 0 
        
        # get every ascii value of line and put into array
        ascii_values = [ord(character) for character in real_str]
        for i in range(length_str):
            # check if the current ascii value is an identifier
            char_check = ascii_values[i]

            if char_check >= 48 and char_check <= 57 or char_check == 46:
                if char_check == 46: 
                    dec_count += 1
                state = FSM[state][1]

            else:
                state = FSM[state][0]

        if state == 1 and dec_count == 1:
            return 1

        return 0   


# class Dog:

#     def __init__(self, name):
#         self.name = name
#         self.tricks = []    # creates a new empty list for each dog

#     def add_trick(self, trick):
#         self.tricks.append(trick)

# >>> d = Dog('Fido')
# >>> e = Dog('Buddy')
# >>> d.add_trick('roll over')
# >>> e.add_trick('play dead')
# >>> d.tricks
# ['roll over']
# >>> e.tricks
# ['play dead']
