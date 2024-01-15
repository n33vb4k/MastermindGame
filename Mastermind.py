#Mastermind Coursework
import sys
import random
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

def memory_error():
    print("Memory error")
    sys.exit(6)

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
def human_play_game(input_file, output_file, max_guesses, available_colours, code, code_len):
    count = 0
    guessed = False
    
    #iterate through input file line by line checking each guess
    for line in input_file:
        colour_freq = get_colour_frequency(code)
        count += 1
        
        #if number of guesses exceeds max guesses, then failed, break out of the loop 
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses")
            break

        #formats the line from the input file into a list of colours as a guess
        line = line.strip()
        guess = line.split(" ")

        #checks if the guess follows the rules, otherwise writes ill formed guess to output file
        guess_valid = True
        if len(guess) != code_len:
            guess_valid = False
        for colour in guess:
            if colour not in available_colours:
                guess_valid = False
        if guess_valid == False:
            output_file.write(f"Guess {count}: Ill-formed guess provided\n")
            continue
        
        output_file.write(f"Guess {count}: ")
        #adds the black and white pins to output file
        process_guess(guess, output_file, colour_freq, code)

        #win condiions
        if guess == code:
            guessed = True
            output_file.write(f"You won in {count} guesses. Congratulations!")
            next_line = input_file.readline()
            #if there is more guesses, ignore
            if next_line != "":
                output_file.write("\nThe game was completed. Further lines were ignored.")
            break

    #fail condition if guessed remains false
    if guessed == False:
        output_file.write("You lost. Please try again.")

#calculates black / white pin counts for a given guess and code
def process_guess(guess, output_file, colour_freq, code):
    black_count = 0
    white_count = 0

    #Count the blacks 
    for i in range(len(guess)):
        if guess[i] in code:
            if guess[i] == code[i] and colour_freq[guess[i]] != 0:
                black_count += 1
                colour_freq[guess[i]] -= 1
    #count the whites
    for i in range(len(guess)):
        if guess[i] in code and colour_freq[guess[i]] != 0:
            white_count += 1
            colour_freq[guess[i]] -= 1

    #if it is a proper guess (not just feedback) then write it to the output file
    if output_file != None:
        output_file.write("black "*black_count + "white "*white_count + "\n")
    
    #return -1,-1 to indicate the guess is the same as the code
    if guess == code:
        return -1,-1
    
    return black_count, white_count

#writes the guesses made by the computer to computerGame.txt
def write_to_gamefile(guess, game_file):
    temp = " ".join(guess)
    game_file.write(temp + "\n")

#generates a random guess from the list of available_colours
def generate_random_guess(guess_len, available_colours):
    guess = [random.choice(available_colours) for _ in range(guess_len)]
    return guess

#reduces the set of possible codes by checking the current guess against each possible code combination
#if the guess would have the same black/white pins compared to the combination as previously, the combination is added to the remaining possible codes
#rest of the codes are discarded
def eliminate_codes(codes, guess, feedback):
    remaining_codes = set()
    for comb in codes:
        if process_guess(guess, None, get_colour_frequency(comb), comb) == feedback:
            remaining_codes.add(comb)
    return remaining_codes

#returns the next guess after the possible codes have been reduced    
def next_guess(guess, black_count, white_count, available_colours, possible_combinations):
    # Remove last guess from possible combinations
    if tuple(guess) in possible_combinations:
        possible_combinations.remove(tuple(guess))
   
    # If no colours are the same as the code, return a new guess containing random colours not previously used (extremely uncommon)
    if black_count == 0 and white_count == 0:
        #gets the colours not including ones in guess
        temp = list(set(available_colours) - set(guess)) 
        # Randomly select colors from the remaining available colors
        return [random.choice(temp) for _ in range(len(guess))]
    
    #returns random combination from the remaining possible combinations
    return list(random.choice(list(possible_combinations)))
    
def computer_play_game(output_file, max_guesses, available_colours, code, code_len):
    #create game file to track computer guesses
    gamef = open("computerGame.txt", "w")
    gamef.write(f"code {' '.join(code)}\nplayer human\n")
    guessed = False
    count = 1
    
    # Create a set of all possible combinations of colours
    possible_codes = set(product(available_colours, repeat=code_len))
    
    #get the first guess
    guess = generate_random_guess(code_len, available_colours)
    #if initial random guess is the code, guessed is true and skip game loop
    if guess == code:
        guessed = True
    
    #write to output file as required
    output_file.write(f"Guess {count}: ")
    write_to_gamefile(guess, gamef) #writes guesses to game file

    #pins for initial guess calculated
    black_c, white_c = process_guess(guess, output_file, get_colour_frequency(code), code)

    #game loop
    while not guessed:
        count += 1
        #break out if computer has gone past max guesses
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses\n")
            break
        
        #update possible codes after each guess using eliminate_codes function to narrow down
        possible_codes = eliminate_codes(possible_codes, guess, (black_c, white_c))

        output_file.write(f"Guess {count}: ")
        #get the next guess, write to game file and calculate pins
        guess = next_guess(guess, black_c, white_c, available_colours, possible_codes)
        write_to_gamefile(guess, gamef)
        black_c, white_c = process_guess(guess, output_file, get_colour_frequency(code), code)

        #pins values will be -1,-1 the guess is correct, breaks
        if black_c == -1 and white_c == -1:
            guessed = True
            break

    if guessed:
        output_file.write(f"You won in {count} guesses. Congratulations!")
    if not guessed:
        output_file.write("You lost. Please try again.")

    gamef.close()

#------------------------------------------------------------------------------------------------

#set default parameters
input_file = None
output_file = None
code_len = 5
max_guesses = 12
available_colours = ["blue", "red", "yellow", "green", "orange"]

#sets the list of arguments to the variable args
args = sys.argv

#manage arguments
temp_colours = []
for i in range(len(args)):
    if i == 0: #0 is just the script name, no action required
        continue
    if i == 1: #set input file
        input_file = args[i]
    elif i == 2: #set output file
        output_file = args[i]
    elif i == 3: #set code length, if not a int then leave as default
        try:
            code_len = int(args[i])
        except ValueError:
            pass
    elif i == 4: #set max guesses, if not a int then leave as default
        try:
            max_guesses = int(args[i])
        except ValueError:
            pass
    else: #remaining arguments added to avaiable colours
        temp_colours.append(args[i])

#exit if no input or output file (not enough args)
if input_file == None or output_file == None:
    not_enough_args()

#if there was arguments with colours, available colours list updated
if temp_colours != []:
    available_colours = temp_colours

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

if not code_valid:
    outf.write("No or ill-formed code provided")
    no_or_ill_formed_code()
else:
    code.remove("code")

player_valid, player = check_player(inf) 

if not player_valid:
    outf.write("No or ill-formed player provided")
    no_or_ill_formed_player()

if player == "human":
    human_play_game(inf, outf, max_guesses, available_colours, code, code_len)
elif player == "computer":
    try:
        computer_play_game(outf, max_guesses, available_colours, code, code_len)
    except MemoryError:
        memory_error()

inf.close()
outf.close()

successful()

