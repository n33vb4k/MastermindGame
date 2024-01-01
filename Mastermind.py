#Mastermind Coursework
import sys

#set up exit codes
def successful():
    print("The programme ran successfully")
    sys.exit(0)

def not_enough_args():
    print("Not enough programme arguments provided")
    sys.exit(1)

def input_file_issue():
    print("There was an issue with the input file")
    sys.exit(2)

def output_file_issue():
    print("There was an issue with the output file")
    sys.exit(3)

def no_or_ill_formed_code():
    print("No or ill-formed code provided")
    sys.exit(4)

def no_or_ill_formed_player():
    print("No or ill-formed player provided")
    sys.exit(5)

#checks the code is valid and returns the code as a list
def check_code(input_file, code_length, available_colours):
    line = input_file.readline().strip()
    code = line.split(" ")

    if code[0]!= "code":
        return False, None

    if len(code) != code_length+1:
        return False, None
    
    for i in range(1, len(code)):
        if code[i] not in available_colours:
            return False, None
 
    return True, code

def check_player(input_file):
    line = input_file.readline().strip()
    player = line.split(" ")

    if len(player) != 2:
        return False, None

    if player[0] != "player":
        return False, None

    if player[1] == "human" or player[1] == "computer":
        return True, player[1]
    else:
        return False, None
    


#set default parameters
input_file = None
output_file = None
code_len = 5
max_guesses = 12
available_colours = ["blue", "red", "yellow", "green", "orange"]

args = sys.argv

temp_colours = []
for i in range(len(args)):
    if i == 0:
        continue
    if i == 1:
        input_file = args[i]
    elif i == 2:
        output_file = args[i]
    elif i == 3:
        try:
            code_len = int(args[i])
        except ValueError:
            pass
    elif i == 4:
        try:
            max_guesses = int(args[i])
        except ValueError:
            pass
    else:
        temp_colours.append(args[i])

if input_file == None or output_file == None:
    not_enough_args()

if temp_colours != []:
    available_colours = temp_colours

print(input_file, output_file, code_len, max_guesses, available_colours) #DELETE

#open input file for reading
try:
    inf = open(input_file, "r")
except FileNotFoundError:
    input_file_issue()

#open output file for writing
try:
    outf = open(output_file)
    outf = open(output_file, "w")
except FileNotFoundError:
    output_file_issue()

code_valid, code = check_code(inf, code_len, available_colours)

print(f"code valid: {code_valid}, code:{code}")

if not code_valid:
    outf.write("No or ill-formed code provided")
    no_or_ill_formed_code()
else:
    code.remove("code")

player_valid, player = check_player(inf)

print(f"player valid: {player_valid}, player:{player}")

if not player_valid:
    outf.write("No or ill-formed player provided")
    no_or_ill_formed_player()






