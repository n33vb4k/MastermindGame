#Mastermind Coursework
import sys

#set up exit codes
def successful():
    sys.exit(0)

def not_enough_args():
    sys.exit(1)

def input_file_issue():
    sys.exit(2)

def output_file_issue():
    sys.exit(3)

def no_or_ill_formed_code():
    sys.exit(4)

def no_or_ill_formed_player():
    sys.exit(5)


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

print(input_file, output_file, code_len, max_guesses, available_colours)
    

