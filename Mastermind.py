#Mastermind Coursework
import sys
import time
import random
import copy
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

    #makes sure input file is of the necessary format
    if code[0]!= "code":
        return False, None
    
    #makes sure code length is same as argument
    if len(code) != code_length+1:
        return False, None
    
    #makes sure all colours in code are in available_colours list
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
    
    #iterate through input file line by line checking each guess
    for line in input_file:
        colour_freq = get_colour_frequency(code)
        blackcount = 0
        whitecount = 0
        count += 1
        output_line = f"Guess {count}: "
        #if number of guesses exceeds max guesses, then failed, break out of the loop 
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses")
            break

        #formats the line from the input file into a list of colours as a guess
        line = line.strip()
        guesses = line.split(" ")

        #checks if the guess follows the rules, otherwise writes ill formed guess to output file
        guess_valid = True
        if len(guesses) != len(code):
            guess_valid = False
        for guess in guesses:
            if guess not in available_colours:
                guess_valid = False
        if guess_valid == False:
            output_file.write(f"Guess {count}: Ill-formed guess provided\n")
            continue
        
        output_file.write(f"Guess {count}: ")
        process_computer_guess(guesses, output_file, colour_freq, code)

        #win conditions
        if guesses == code and count < max_guesses:
            output_file.write(f"You won in {count} guesses. Congratulations!\nThe game was completed. Further lines were ignored.")
            guessed = True
            break
        elif guesses == code:
            output_file.write(f"You won in {count} guesses. Congratulations!")
            guessed = True
            break

    #fail condition if guessed remains false
    if guessed == False:
        output_file.write("You lost. Please try again.")

#calculates black / white pin counts for a given guess and code
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

    #if it is a proper guess (not just feedback) then write it to the output file
    if output_file != None:
        output_file.write("black "*blackcount + "white "*whitecount + "\n")
    
    #return -1,-1 to indicate the guess is the same as the code
    if guesses == code:
        return -1,-1
    
    return blackcount, whitecount

#writes the guesses made by the computer to computerGame.txt
def write_to_gamefile(guesses, game_file):
    temp = " ".join(guesses)
    game_file.write(temp + "\n")

def generate_random_guess(guess_len, available_colours):
    #generate first guess (random):
    guesses = []
    for _ in range(guess_len):
        colour = random.choice(available_colours)
        guesses.append(colour)
    return guesses

def eliminate_codes(codes, guess, feedback):
    remaining_codes = set()
    for code in codes:
        if process_computer_guess(guess, None, get_colour_frequency(code), code) == feedback:
            remaining_codes.add(code)
    return remaining_codes

def calculate_minmax_scores(codes):
    scores = {}
    for guess in codes:
        max_score = float('inf')
        for feedback in product(range(len(guess) + 1), repeat=2):
            eliminated_codes = eliminate_codes(codes, guess, feedback)
            score = max(len(codes) - len(eliminated_codes), 0)
            if score == 0:
                break  # No need to continue if score is already 0
            max_score = min(max_score, score)
        scores[guess] = max_score
    return scores

def select_next_guess(scores):
    min_max_score = min(scores.values())
    min_max_score_guesses = [guess for guess, score in scores.items() if score == min_max_score]
    return min(min_max_score_guesses)

def kuth_computer_play_game(output_file, max_guesses, available_colours, code):
    gamef = open("computerGame.txt", "w")
    gamef.write(f"code {' '.join(code)}\nplayer human\n")
    guessed = False
    guess_len = len(code)
    count = 1

    possible_codes = set(product(available_colours, repeat=guess_len))

    while not guessed:
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses\n")
            break

        current_guess = select_next_guess(calculate_minmax_scores(possible_codes))

        output_file.write(f"Guess {count}: ")
        guesses = list(current_guess)
        write_to_gamefile(guesses, gamef)
        black_c, white_c = process_computer_guess(guesses, output_file, get_colour_frequency(code), code)

        if black_c == -1 and white_c == -1:
            output_file.write(f"You won in {count} guesses. Congratulations!")
            guessed = True
            break

        possible_codes = eliminate_codes(possible_codes, current_guess, (black_c, white_c))

        count += 1

    if not guessed:
        output_file.write("You lost. Please try again.")

    gamef.close()


#------------------------------------------------------------

def next_guess(guesses, blackcount, whitecount, available_colours, possible_combinations):
    # Remove last guess from possible combinations
    if tuple(guesses) in possible_combinations:
        possible_combinations.remove(tuple(guesses))
    
    # If no colours are the same as the code, return a new guess containing random colours not previously used
    if blackcount == 0 and whitecount == 0:
        temp = set(available_colours) - set(guesses)
        # Randomly select colors from the remaining available colors
        return [random.choice(list(temp)) for _ in range(len(guesses))]

    # Filter possible combinations based on the feedback
    # filtered_combinations = [comb for comb in possible_combinations
    #                          if process_computer_guess(list(comb), None, get_colour_frequency(guesses), guesses) == (blackcount, whitecount)]
    filtered_combinations = list(eliminate_codes(possible_combinations, guesses, (blackcount, whitecount)))

    # If there are still valid combinations, choose a random one, if there are none, return a random guess
    if filtered_combinations:
        return list(random.choice(filtered_combinations))
    else:
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
    
    # Create a list of all possible combinations of colours
    possible_codes = set(product(available_colours, repeat=guess_len))

    output_file.write(f"Guess {count}: ")
    write_to_gamefile(guesses, gamef)
    black_c, white_c = process_computer_guess(guesses, output_file, get_colour_frequency(code), code)

    while not guessed:
        if black_c == -1 and white_c == -1:
            output_file.write(f"You won in {count} guesses. Congratulations!")
            guessed = True
            break

        count += 1
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses\n")
            break

        output_file.write(f"Guess {count}: ")
        guesses = next_guess(guesses, black_c, white_c, available_colours, possible_codes)
        write_to_gamefile(guesses, gamef)
        black_c, white_c = process_computer_guess(guesses, output_file, get_colour_frequency(code), code)

    if not guessed:
        output_file.write("You lost. Please try again.")

    gamef.close()
    

#------------------------------------------------------------
    
def next_guess_final(guesses, blackcount, whitecount, available_colours, possible_combinations):
    # Remove last guess from possible combinations
    if tuple(guesses) in possible_combinations:
        possible_combinations.remove(tuple(guesses))
    
    # If no colours are the same as the code, return a new guess containing random colours not previously used
    if blackcount == 0 and whitecount == 0:
        temp = set(available_colours) - set(guesses)
        # Randomly select colors from the remaining available colors
        return [random.choice(list(temp)) for _ in range(len(guesses))]

    return list(random.choice(list(possible_combinations)))
    
def computer_play_game_final(output_file, max_guesses, available_colours, code):
    gamef = open("computerGame.txt", "w")
    gamef.write(f"code {' '.join(code)}\nplayer human\n")
    guessed = False
    guess_len = len(code)
    count = 1
    kuths = True

    if guess_len > 2:
        kuths = False
    
    # Create a set of all possible combinations of colours
    possible_codes = set(product(available_colours, repeat=guess_len))

    if not kuths:
        #generate first guess (random):
        guesses = generate_random_guess(guess_len, available_colours)
    else:
        guesses = select_next_guess(calculate_minmax_scores(possible_codes))
    
    output_file.write(f"Guess {count}: ")
    write_to_gamefile(guesses, gamef)
    black_c, white_c = process_computer_guess(guesses, output_file, get_colour_frequency(code), code)

    while not guessed:
        count += 1
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses\n")
            break
        
        possible_codes = eliminate_codes(possible_codes, guesses, (black_c, white_c))

        output_file.write(f"Guess {count}: ")
        if not kuths:
            guesses = next_guess_final(guesses, black_c, white_c, available_colours, possible_codes)
        else:
            guesses = select_next_guess(calculate_minmax_scores(possible_codes))
        
        write_to_gamefile(guesses, gamef)
        black_c, white_c = process_computer_guess(guesses, output_file, get_colour_frequency(code), code)

        if black_c == -1 and white_c == -1:
            output_file.write(f"You won in {count} guesses. Congratulations!")
            guessed = True
            break

    if not guessed:
        output_file.write("You lost. Please try again.")

    gamef.close()


#------------------------------------------------------------


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
    outf = open(output_file) #to check existance first
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
    computer_play_game_final(outf, max_guesses, available_colours, code)
    endtime =  time.process_time()
    print(f"computer player took: {endtime - starttime}s")

inf.close()
outf.close()

successful()

