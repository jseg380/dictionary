from os import mkdir                        # To create directories
from os import path as ospath               # To check if a path exists
from threading import Thread,local          # To use multi-threading
from math import ceil as round_up           # To distribute task between threads
from requests import get                    # To make get requests
from requests.sessions import Session       # To improve get requests efficiency
from bs4 import BeautifulSoup               # HTML parser
from time import time                       # To measure time
from subprocess import call                 # To call a shell script
from os import listdir
import re


################################################################################
# DECLARATIONS

# Tuple with all the letters in the alphabet

ALPHABET = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

SOL_PATH = str(input('Where do you want to save the definitions files? '))
DATA_PATH = f'{SOL_PATH}/.letter_files'
ALL_WORDS = f'{DATA_PATH}/all_words.txt'

# Threads

processes = len(ALPHABET)
thread_local = local()
thread_num = 9
process_per_thread = round_up(processes / thread_num)
thread_list = []


################################################################################
# FUNCTIONS

#···············································································
# Misc functions

def separate() -> None:
    """ # separate 

        This function separates the words in different files. All words starting \
        with the letter 'a' are copied in the file 'a.txt' and so on. 
        Spanish has accents so it's possible for a word to begin with an accented \
        vowel, this program takes care of it in quite a rudimentary but effective way.

        Parameters
        ----------
        all_words : file
            File containing all words
    """

    all_words = open(ALL_WORDS, 'r')

    # Open file containing all words in Spanish dictionary
    word = all_words.readline()

    while word != '':

        if word[0] in ALPHABET:
            letter_file = open(f'{DATA_PATH}/{word[0]}.txt', 'a')

            letter_file.write(word)

            letter_file.close()
        else:
            match word[0]:
                case 'á':
                    letter_file = open(f'{DATA_PATH}/a.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
                case 'Á':
                    letter_file = open(f'{DATA_PATH}/a.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
                case 'é':
                    letter_file = open(f'{DATA_PATH}/e.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
                case 'í':
                    letter_file = open(f'{DATA_PATH}/i.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
                case 'ñ':
                    letter_file = open(f'{DATA_PATH}/n.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
                case 'ó':
                    letter_file = open(f'{DATA_PATH}/o.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
                case 'Ó':
                    letter_file = open(f'{DATA_PATH}/o.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
                case 'ú':
                    letter_file = open(f'{DATA_PATH}/u.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
                case _:
                    print(f'UNEXPECTED word {word}')
                    letter_file = open(f'{DATA_PATH}/unexpected.txt', 'a')
                    letter_file.write(word)
                    letter_file.close()
        
        word = all_words.readline()


    all_words.close() # Close file

def check_dirs() -> None:
    """ # check_dirs
    
        As the name suggests, this function check for the existence of the \
        directories necessary to get and store all the information.
    """
    if not ospath.exists(SOL_PATH):
        print(f'Creating dir {SOL_PATH}')
        mkdir(SOL_PATH)
    
        print('Creating directories...')
        for i in ALPHABET:
            if not ospath.exists(f'{SOL_PATH}/{i}'):
                mkdir(f'{SOL_PATH}/{i}')
        print('...directories created')
    
    if not ospath.exists(DATA_PATH):
        mkdir(DATA_PATH)
    
        response = get('https://raw.githubusercontent.com/JorgeDuenasLerin/diccionario-espanol-txt/master/0_palabras_todas_no_conjugaciones.txt')
        all_words = open(ALL_WORDS, 'w+')

        all_words.write(response.text)
        separate()

        all_words.close()


#···············································································
# Making get requests

def get_page(word:str, opened_session:Session) -> None:
    """ # get_page
    
        It gets the HTML page of the word's RAE definition using the \
            session opened_session and writes the desired content in a file
            with name the word.
        NOTE: It gets only the contents of the div with id "resultados" which \
            contains the definition of the word, everything else is ignored.
            The purpose of using an already opened session is to improve speed.
        
        Parameters
        ----------
        word : str
            Word which its definition will be obtained
        opened_session : Session
            Session (from requests.Session) with which make the get request
    """
    url = 'https://dle.rae.es/' + word

    # dle.rae.es requires a valid User-Agent header to obtain a get request
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'}

    if not ospath.exists(f'{SOL_PATH}/{word[0]}/{word}.html'):
        response = opened_session.get(url, headers=user_agent, timeout=10)

        html = BeautifulSoup(response.text, features='html.parser')

        get_definitions_word(word, html)


def get_session() -> Session:
    """ # get_session

        It returns the current session if there is one, in case there \
        is not, it creates one

        Returns
        -------
        Session: The current session
    """
    if not hasattr(thread_local,'session'):
        thread_local.session = Session() # Create a new Session if not exists
    return thread_local.session


def thread_function(thread, session:Session) -> None:
    """ # thread_function

        Function that is asigned to every thread at the begining of the program \
        it distributes the words between different threads in order to improve \
        efficiency.
        It is made to handle the situation where the number of tasks is not a \
        multiple of the number of threads, by giving the last thread less \
        number of tasks. The algorithm for distributing tasks can be improved.

        Parameters
        ----------
        thread : int
            Number of the thread
        session : Session
            Current session (used to make requests more efficiently)
    """
    bottom = thread * process_per_thread
    top = bottom
    if (thread + 1) * process_per_thread < processes:
        top += process_per_thread - 1
    else:
        top = processes - 1

    for i in range(bottom, top+1, 1):
        origin = open(f'{DATA_PATH}/{ALPHABET[i]}.txt', 'r')
        print(f'Obtaining words that begin with {ALPHABET[i]}...')

        word = origin.readline().replace('\n', '')  # Ahead reading
        while word != '':   # Read until EOF is reached
            get_page(word, session)

            word = origin.readline().replace('\n', '')  # Read next word
        
        print(f'... obtained all words that begin with {ALPHABET[i]}')
        origin.close()


def get_definitions_word(word, html) -> None:
    """ # get_definitions_word

        It extracts the definitions of the HTML page definition of the word \
        and writes them in a plain text file with the name of the word.

        Parameters
        ----------
        word : str
            The word whose definitions are in the HTML and want to be saved
        html : bs4.BeautifulSoup
            The HTML containing the definition of the word
    """
    aceptions = html.find_all('article')

    if word[0] not in ALPHABET:
        match word[0]:
                case 'á':
                    result = open(f'{SOL_PATH}/a/{word}.txt', 'w+')
                case 'Á':
                    result = open(f'{SOL_PATH}/a/{word}.txt', 'w+')
                case 'é':
                    result = open(f'{SOL_PATH}/e/{word}.txt', 'w+')
                case 'í':
                    result = open(f'{SOL_PATH}/i/{word}.txt', 'w+')
                case 'ñ':
                    result = open(f'{SOL_PATH}/n/{word}.txt', 'w+')
                case 'ó':
                    result = open(f'{SOL_PATH}/o/{word}.txt', 'w+')
                case 'Ó':
                    result = open(f'{SOL_PATH}/o/{word}.txt', 'w+')
                case 'ú':
                    result = open(f'{SOL_PATH}/u/{word}.txt', 'w+')
                # case _:
                #     pass
    else:
        result = open(f'{SOL_PATH}/{word[0]}/{word}.txt', 'w+')

    for aception in aceptions:
        result.write(aception.find('header').text + '\n')

        description = aception.find('p', class_='n2')

        if description != None:
            result.write(description.text + '\n')

        definitions = aception.find_all('p', class_=re.compile("j[0-9]*"))

        for definition in definitions:
            result.write(definition.text + '\n')
    
    result.close()


#···············································································
# Verification functions

def verify_quantity() -> None:
    """ # verify_quantity

        It verifies the amount of files that there are and compares it to \
        the amount of words that there are in the document containing all words.
    """
    for i in ALPHABET:
        file = open(f'{DATA_PATH}/{i}.txt', 'r')
        length = len(file.readlines())
        real_length = len(listdir(f'{SOL_PATH}/{i}'))
        number_errors = 0

        if length != real_length:
            print(f'ERROR. Letter {i} should have {length} but instead has {real_length}.')
            number_errors += 1
    
    print(f'Verification finished. {number_errors} errors found')


def verify_letter(letter) -> None:
    """ # verify_letter

        It verifies the files of a certain letters. When it encounters a \
        problem it stops and lets you know what file is missing.
    """
    file = open(f'{DATA_PATH}/{letter}.txt', 'r')

    theoretical_words = file.readlines()

    real_words = listdir(f'{SOL_PATH}/{letter}')

    # Standardise both lists so they can be compared

    for i in range(len(theoretical_words)):
        theoretical_words[i] = theoretical_words[i].replace(' ', '_')
        theoretical_words[i] = theoretical_words[i].replace('\n', '')

    for i in range(len(real_words)):
        real_words[i] = real_words[i].replace(' ', '_')
        real_words[i] = real_words[i].replace('.txt', '')


    # Once both lists are standardised, sort them

    theoretical_words.sort()
    real_words.sort()


    difference:bool = False

    print(f'There should be {len(theoretical_words)} that begin with {letter}')
    print(f'There are {len(real_words)} files of words that begin with {letter}')

    for i in range(len(theoretical_words)):
        if theoretical_words[i] != real_words[i] and not difference:
            print(f'{theoretical_words[i]} differs from {real_words[i]}. Position {i}')
            bottom = -1
            top = 5
            print('Theoretical' + '{:>20}'.format('Real'))
            for j in range(bottom, top, 1):
                print(f'{theoretical_words[i+j]} {i+j}' + '{:>30}'.format(f'{real_words[i+j]} {i+j}'))
            
            if input('Skip? [y/n] ') not in ('y', 'Y', 'Yes', 'yes', 'YES'):
                difference = True

    if not difference:
        print('Success! There are no words missing')


def verification_menu() -> None:
    """ # menu

        Menu for the verification functions
    """
    print('VERIFICATION PROGRAM')
    print('Options:\n1. Verify the number of words\n2. Verify the words of one specific letter\n3. Exit')
    option = str(input())

    match option:
        case '1':
            verify_quantity()
        case '2':
            letter = str(input('Input a letter to verify if all its files are downloaded: '))
            verify_letter(letter)
        case '3':
            return None
        case _:
            print('Unknown option. Try again')

    input('Press Enter to continue')

    verification_menu()


################################################################################
# PROGRAM

# Check if the directories necessary exist, if not, create them
check_dirs()

# Remove all empty files
call(['remove_empty.sh', SOL_PATH])

# Create session
session = get_session()

# Program itself
start = time()
for i in range(thread_num):
    thread_list.append(Thread(target=thread_function, args=[i, session]))
    thread_list[i].start()

for i in range(thread_num):
    thread_list[i].join()
end = time()

print(f'FINISHED! in {end - start} seconds')

# Verificate files
verification_menu()