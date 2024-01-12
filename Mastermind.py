#Mastermind Coursework
import sys
import time
from itertools import product

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

    if output_file != None:
        output_file.write("black "*blackcount + "white "*whitecount + "\n")
        
    if guesses == code:
        return -1,-1
    return blackcount, whitecount

def write_to_gamefile(guesses, game_file):
    temp = " ".join(guesses)
    game_file.write(temp + "\n")

def eliminate_codes(codes, guess, feedback):
    remaining_codes = set()
    for code in codes:
        if process_computer_guess(guess, None, get_colour_frequency(code), code) == feedback:
            remaining_codes.add(code)
    return remaining_codes

def calculate_minmax_scores(unused_codes, codes):
    scores = {}
    for guess in unused_codes:
        max_score = float('inf')
        for feedback in product(range(len(guess) + 1), repeat=2):
            eliminated_codes = eliminate_codes(codes, guess, feedback)
            score = max(len(codes) - len(eliminated_codes), 0)
            max_score = min(max_score, score)
        scores[guess] = max_score
    return scores

def select_next_guess(scores):
    min_max_score = min(scores.values())
    min_max_score_guesses = [guess for guess, score in scores.items() if score == min_max_score]
    return min(min_max_score_guesses)

def computer_play_game(output_file, max_guesses, available_colours, code):
    gamef = open("computerGame.txt", "w")
    gamef.write(f"code {' '.join(code)}\nplayer human\n")
    guessed = False
    guess_len = len(code)
    count = 1

    remaining_codes = list(product(available_colours, repeat=guess_len))

    while not guessed:
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses\n")
            break

        current_guess = select_next_guess(calculate_minmax_scores(remaining_codes, remaining_codes))
        output_file.write(f"Guess {count}: ")
        guesses = list(current_guess)
        write_to_gamefile(guesses, gamef)
        black_c, white_c = process_computer_guess(guesses, output_file, get_colour_frequency(code), code)

        if black_c == -1 and white_c == -1:
            output_file.write(f"You won in {count} guesses. Congratulations!")
            guessed = True
            break

        remaining_codes = eliminate_codes(remaining_codes, current_guess, (black_c, white_c))

        count += 1

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
    starttime = time.process_time()
    computer_play_game(outf, max_guesses, available_colours, code)
    endtime =  time.process_time()
    print(f"computer player took: {endtime - starttime}s")
#add computer player

inf.close()
outf.close()

successful()

