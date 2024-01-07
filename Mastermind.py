#Mastermind Coursework
import sys
import random
import itertools

#set up exit codes
def successful():
    print("The program ran successfully")
    sys.exit(0)

def not_enough_args():
    print("Not enough program arguments provided")
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

#returns dictionary with colour and number of times it appears in the code
def get_colour_frequency(code):
    colour_freq = {}
    for colour in code:
        if colour not in colour_freq:
            colour_freq[colour] = 1
        else:
            colour_freq[colour] += 1

    return colour_freq

#complete game for human players
def human_play_game(input_file, output_file, max_guesses, available_colours, code):
    count = 0
    guessed = False

    for line in input_file:
        colour_freq = get_colour_frequency(code)
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
        
        #Count the blacks 
        for i in range(len(guesses)):
            if guesses[i] in code:
                if guesses[i] == code[i] and colour_freq[guesses[i]] != 0:
                    blackcount += 1
                    colour_freq[guesses[i]] -= 1
                    
        #count the whites
        for i in range(len(guesses)):
            if guesses[i] in code and colour_freq[guesses[i]] != 0:
                whitecount += 1
                colour_freq[guesses[i]] -= 1

        output_line += "black "*blackcount + "white "*whitecount + "\n"
        output_file.write(output_line)

        if guesses == code and count < max_guesses:
            output_file.write(f"You won in {count} guesses. Congratulations!\nThe game was completed. Further lines were ignored.")
            guessed = True
            break
        elif guesses == code:
            output_file.write(f"You won in {count} guesses. Congratulations!")
            guessed = True
            break
    
    if guessed == False:
        output_file.write("You lost. Please try again.")

def process_computer_guess(guesses, output_file, colour_freq, code):
    blackcount = 0
    whitecount = 0
    #check for blacks then whites
    for i in range(len(guesses)):
        if guesses[i] in code:
            if guesses[i] == code[i] and colour_freq[guesses[i]] != 0:
                blackcount += 1
                colour_freq[guesses[i]] -= 1
                
    for i in range(len(guesses)):
        if guesses[i] in code and colour_freq[guesses[i]] != 0:
            whitecount += 1
            colour_freq[guesses[i]] -= 1

    if output_file != None:
        output_file.write("black "*blackcount + "white "*whitecount + "\n")
        
    if guesses == code:
        return -1,-1
    return blackcount, whitecount

def write_to_gamefile(guesses, game_file):
    temp = " ".join(guesses)
    game_file.write(temp + "\n")

def next_guess(guesses, blackcount, whitecount, available_colours):
    if blackcount == 0 and whitecount == 0:
        # Randomly select colors from available colors
        return [random.choice(available_colours) for _ in range(len(guesses))]

    # Create a list of all possible combinations of colors
    possible_combination = list(itertools.product(available_colours, repeat = len(guesses)))

    # Iterate through each combination and check against feedback
    for combination in possible_combination:
        modified_guess = list(combination)
        current_blackcount, current_whitecount = process_computer_guess(modified_guess, None, get_colour_frequency(guesses), guesses)

        if current_blackcount == blackcount and current_whitecount == whitecount:
            # Found a permutation that matches the feedback
            return modified_guess

    # If no exact match is found, return a random guess
    return [random.choice(available_colours) for _ in range(len(guesses))]


def computer_play_game(output_file, max_guesses, available_colours, code):
    gamef = open("computerGame.txt", "w")
    gamef.write(f"code {' '.join(code)}\nplayer human\n")
    guessed = False
    guess_len = len(code)
    count = 1
    #generate first guess (random):
    guesses = []
    for _ in range(guess_len):
        colour = random.choice(available_colours)
        guesses.append(colour)

    output_file.write(f"Guess {count}: ")
    write_to_gamefile(guesses, gamef)
    black_c, white_c = process_computer_guess(guesses, output_file, get_colour_frequency(code), code)

    while not guessed:
        if black_c == -1 and white_c == -1:
            output_file.write(f"You won in {count} guesses. Congratulations!")
            guessed = True
            break
        
        count += 1
        if count == max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses\n")
            break

        output_file.write(f"Guess {count}: ")
        guesses = next_guess(guesses, black_c, white_c, available_colours)
        write_to_gamefile(guesses, gamef)
        black_c, white_c = process_computer_guess(guesses, output_file, get_colour_frequency(code), code)
            
    if not guessed:
        output_file.write("You lost. Please try again.")
    
    gamef.close()


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

print(input_file, output_file, code_len, max_guesses, available_colours) #delete before submission

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

print(f"code valid: {code_valid}, code: {code}") #delete before submission

if not code_valid:
    outf.write("No or ill-formed code provided")
    no_or_ill_formed_code()
else:
    code.remove("code")

player_valid, player = check_player(inf) 

print(f"player valid: {player_valid}, player: {player}") #delete before submission

if not player_valid:
    outf.write("No or ill-formed player provided")
    no_or_ill_formed_player()

if player == "human":
    human_play_game(inf, outf, max_guesses, available_colours, code)
elif player == "computer":
    computer_play_game(outf, max_guesses, available_colours, code)
#add computer player

inf.close()
outf.close()

successful()

