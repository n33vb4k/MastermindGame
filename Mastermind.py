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

#checks the player is valid and returns what kind of player
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
    

#complete game for human players
def human_play_game(input_file, output_file, max_guesses, available_colours, code):
    count = 0
        
    for line in input_file:
        colour_freq = {}
        for colour in code:
            if colour not in colour_freq:
                colour_freq[colour] = 1
            else:
                colour_freq[colour] += 1
        
        blackcount = 0
        whitecount = 0
        count += 1
        output_line = f"Guess {count}: "
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses")
            break

        line = line.strip()
        guesses = line.split(" ")

        guess_valid = True
        if len(guesses) != len(code):
            guess_valid = False
        for guess in guesses:
            if guess not in available_colours:
                guess_valid = False
        if guess_valid == False:
            output_file.write(f"Guess {count}: Ill-formed guess provided\n")
            continue

        for i in range(len(guesses)):
            if guesses[i] in code:
                if guesses[i] == code[i] and colour_freq[guesses[i]] != 0:
                    blackcount += 1
                    colour_freq[guesses[i]] -= 1
                else:
                    if colour_freq[guesses[i]] != 0:
                        whitecount += 1
                        colour_freq[guesses[i]] -= 1

        output_line += "black "*blackcount + "white "*whitecount + "\n"
        output_file.write(output_line)

        if guesses == code and count < max_guesses:
            output_file.write(f"You won in {count} guesses. Congratulations!\nThe game was completed. Further lines were ignored.")
            break
        elif guesses == code:
            output_file.write(f"You won in {count} guesses. Congratulations!")
            break


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

print(f"code valid: {code_valid}, code: {code}")

if not code_valid:
    outf.write("No or ill-formed code provided")
    no_or_ill_formed_code()
else:
    code.remove("code")

player_valid, player = check_player(inf)

print(f"player valid: {player_valid}, player: {player}")

if not player_valid:
    outf.write("No or ill-formed player provided")
    no_or_ill_formed_player()

if player == "human":
    human_play_game(inf, outf, max_guesses, available_colours, code)

successful()

