import sys
import random
from itertools import product

# Set up the exit codes for the program
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


def check_code(input_file, code_length, available_colours):
    """
    - Checks the code is of the correct format and valid by
      reading from the input file
    - Returns tuple with boolean value for the validity of the code
      and None, or the code depending on the validity
    """
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
    """
    - Checks the player is valid by reading from the input
      file
    - Returns a tuple with a boolean value for the validity of the player
      and None or the type of player depending on the validity
    """
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


def get_colour_frequency(code):
    """
    - Takes in a list of colours
    - Returns a  dictionary which has the distinct colours as
      keys, and their frequency in the code as values
    """
    colour_freq = {}
    for colour in code:
        if colour not in colour_freq:
            colour_freq[colour] = 1
        else:
            colour_freq[colour] += 1

    return colour_freq


def human_play_game(input_file, output_file, max_guesses, 
                    available_colours, code, code_len):
    """
    - This function handles human players, reading the guesses from
      the input file, and writes to the output file accordingly depending
      on each guess
    """
    count = 0
    guessed = False
    
    for line in input_file:
        colour_freq = get_colour_frequency(code)
        count += 1
        
        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses")
            break

        # Formats the line from the input file into a list of colours as a guess
        line = line.strip()
        guess = line.split(" ")

        # Checks if the guess follows the rules
        guess_valid = True
        if len(guess) != code_len:
            guess_valid = False
        for colour in guess:
            if colour not in available_colours:
                guess_valid = False
        # Writes to output file if guess invalid
        if not guess_valid:
            output_file.write(f"Guess {count}: Ill-formed guess provided\n")
            continue
        
        output_file.write(f"Guess {count}: ")
        # Calculates and then adds the black and white pins to output file
        process_guess(guess, output_file, colour_freq, code)

        if guess == code:
            guessed = True
            output_file.write(f"You won in {count} guesses. Congratulations!")
            next_line = input_file.readline()
            # If there is more guesses, ignore and write to output file
            if next_line != "":
                output_file.write("\nThe game was completed. Further lines were ignored.")
            break

    if guessed == False:
        output_file.write("You lost. Please try again.")


def process_guess(guess, output_file, colour_freq, code):
    """
    - This function calculates the black and white pins scored by the guess
      onto the code by comparing with and updating the colour_freq dictionary
      - If there is a output file passed, then it will also write the pins to it
        otherwise it is just used as feedback to find the next optimal guess
    - Returns a tuple with the number of black pins and the number of white pins scored,
      or -1,-1 indicating the guess is correct
    """
    black_count = 0
    white_count = 0

    # Count the black pins
    for i in range(len(guess)):
        if guess[i] in code:
            if guess[i] == code[i] and colour_freq[guess[i]] != 0:
                black_count += 1
                colour_freq[guess[i]] -= 1
    # Count the white pins
    for i in range(len(guess)):
        if guess[i] in code and guess[i] != code[i] and colour_freq[guess[i]] != 0:
            white_count += 1
            colour_freq[guess[i]] -= 1

    # If it is a proper guess (not just called for feedback), write it to the output file
    if output_file is not None:
        output_file.write("black "*black_count + "white "*white_count + "\n")
    
    if guess == code:
        return -1,-1
    
    return black_count, white_count


def write_to_gamefile(guess, game_file):
    """
    - Takes in computer generated guess (list of colours), and the 
      tracking game file, formats the guess into a string and writes
      it to the game file (computerGame.txt)
    """
    temp = " ".join(guess)
    game_file.write(temp + "\n")


def generate_random_guess(guess_len, available_colours):
    """
    - Takes in the guess length and the list of available colours,
      generates a random list of colours the same length as the guess length
    - Returns the randomly generated guess
    """
    guess = [random.choice(available_colours) for _ in range(guess_len)]
    return guess


def eliminate_codes(codes, guess, feedback):
    """
    - Takes in the set of all possible codes, the most recent guess, and the number
      of black and white pins the guess scored
    - Compares the last guess with each combination, if they have the same number of
      black and white pins hit, add it to the set of remaining possible codes
    - Return the new set of remaining codes
    """
    remaining_codes = set()
    for comb in codes:
        if process_guess(guess, None, get_colour_frequency(comb), comb) == feedback:
            remaining_codes.add(comb)
    return remaining_codes

  
def next_guess(guess, black_count, white_count, available_colours,
               possible_combinations):
    """
    - This function removes the last guess from the set of possible codes so there are no
      duplicate guesses
    - In the rare case that the last guess didn't score any pins, a random guess is returned
      with the colours not used yet
    - Otherwise, a random guess in the remaining set of possible combinations is returned
    """
    if tuple(guess) in possible_combinations:
        possible_combinations.remove(tuple(guess))

    if black_count == 0 and white_count == 0:
        # Gets the colours not including ones in previous guess
        temp = list(set(available_colours) - set(guess)) 
        # Makes random guess from the remaining available colors
        return generate_random_guess(len(guess), temp)
    
    return list(random.choice(list(possible_combinations)))


def computer_play_game(output_file, max_guesses, available_colours, 
                       code, code_len):
    """
    - This function is where computer players are handled
    - A game file (computerGame.txt) is created to track the guesses generated
      by the computer algorithm
    - The black and white pins scored on each guess are calculated and written to
      the output file
    """
    # Creates/opens and overrides the game file to track computer guesses
    gamef = open("computerGame.txt", "w")
    gamef.write(f"code {' '.join(code)}\nplayer human\n")
    guessed = False
    count = 1
    
    # Create a set of all possible combinations of colours
    possible_codes = set(product(available_colours, repeat=code_len))
    
    # Start with random guess
    guess = generate_random_guess(code_len, available_colours)
    if guess == code:
        guessed = True
    
    output_file.write(f"Guess {count}: ")
    write_to_gamefile(guess, gamef) 

    # Pins scored for initial guess calculated
    black_c, white_c = process_guess(guess, output_file, get_colour_frequency(code), code)

    while not guessed:
        count += 1

        if count > max_guesses:
            output_file.write(f"You can only have {max_guesses} guesses\n")
            break

        # Update possible codes after each guess using eliminate_codes function to narrow down
        possible_codes = eliminate_codes(possible_codes, guess, (black_c, white_c))

        output_file.write(f"Guess {count}: ")
        # Get the next guess, write to game file and calculate pins
        guess = next_guess(guess, black_c, white_c, available_colours, possible_codes)
        write_to_gamefile(guess, gamef)
        black_c, white_c = process_guess(guess, output_file, get_colour_frequency(code), code)

        # Pins values will be -1,-1 the guess is correct, breaks
        if black_c == -1 and white_c == -1:
            guessed = True
            break

    if guessed:
        output_file.write(f"You won in {count} guesses. Congratulations!")
    if not guessed:
        output_file.write("You lost. Please try again.")

    gamef.close()

#------------------------------------------------------------------------------------------------

# Set default parameters
input_file = None
output_file = None
code_len = 5
max_guesses = 12
available_colours = ["blue", "red", "yellow", "green", "orange"]

# Sets the list of arguments to the variable args
args = sys.argv

# Manage arguments
temp_colours = []
for i in range(len(args)):
    # 0 is just the script name, no action required
    if i == 0: 
        continue
    if i == 1: 
        input_file = args[i]
    elif i == 2: 
        output_file = args[i]
    # Set code length, if negative or not a int then leave as default
    elif i == 3: 
        try:
            if int(args[i]) < 0:
                continue
            else:
                code_len = int(args[i])
        except ValueError:
            pass
    # Set max guesses, if negative or not a int then leave as default
    elif i == 4: 
        try:
            if int(args[i]) < 0:
                continue
            else:
                max_guesses = int(args[i])
        except ValueError:
            pass
    # Remaining arguments added to colours list
    else: 
        temp_colours.append(args[i])

if input_file is None or output_file is None:
    not_enough_args()

# If there was arguments with colours, available colours list updated
if temp_colours:
    available_colours = temp_colours

# Open input file for reading
try:
    in_f = open(input_file, "r")
except FileNotFoundError:
    input_file_issue()

# Open output file for writing
try:
    out_f = open(output_file, "w")
except FileNotFoundError:
    output_file_issue()

code_valid, code = check_code(in_f, code_len, available_colours)

if not code_valid:
    out_f.write("No or ill-formed code provided")
    no_or_ill_formed_code()
else:
    code.remove("code")

player_valid, player = check_player(in_f) 

if not player_valid:
    out_f.write("No or ill-formed player provided")
    no_or_ill_formed_player()

if player == "human":
    human_play_game(in_f, out_f, max_guesses, available_colours, 
                    code, code_len)
elif player == "computer":
    try:
        computer_play_game(out_f, max_guesses, available_colours, 
                           code, code_len)
    except MemoryError:
        memory_error()

in_f.close()
out_f.close()

successful()

