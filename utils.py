import re
import difflib
from spelling_corrector import SpellingCorrector
from psycopg2 import sql

replacements = {
    '4x4': 'Four Wheel Drive',
    '4WD': 'Four Wheel Drive',
}


def sequence_similarity(seq1, seq2):
    return difflib.SequenceMatcher(None, seq1, seq2).ratio()


def replace_word(text, old, new):
    return re.sub(re.escape(old), new, text)

def perform_replacements(description):
    for old, new in replacements.items():
        description = replace_word(description, old, new)
    return description
 

def clean_text(text):
    cleaned_text = re.sub(r'[\-\/\,\.\;\:\!\@\#\$\%\^\&\*\(\)\+\=\[\]\{\}\|\\\'\"\<\>\?]', '', text)
    cleaned_text = cleaned_text.strip()
    return cleaned_text

def split_description(description, corrector):
    """
    Split description into words and replace them with correct spellings if any.

    Args:
    description (str): The description to be processed.
    corrector (SpellingCorrector): The spelling corrector instance.

    Returns:
    str: The processed description with corrected spellings.
    """
    words = description.split()
    corrected_words = [corrector.correct(word) for word in words]
    return ' '.join(corrected_words)

def clean_description(description, corrector):
    cleaned_description = clean_text(description)
    corrected_description = split_description(cleaned_description, corrector)
    final_description = perform_replacements(corrected_description)
    return final_description


def find_longest_string(string_list):
    if not string_list:  
        return None  
    
    longest_string = string_list[0]
    for string in string_list[1:]:
        if len(string) > len(longest_string):
            longest_string = string
            
    return longest_string

def generate_regex_for_word(word):
    pattern = r'\b'
    for i, char in enumerate(word):
        pattern += char
        if i < len(word) - 1:
            pattern += r'('
    pattern += r'.*' + r')?' * (len(word) - 1) + r'\b'
    return pattern

def generate_combined_regex(words):
    word_list = words.split()
    word_patterns = [generate_regex_for_word(word) for word in word_list]
    if len(word_patterns) == 1:
        return word_patterns[0]

    else:
        full_string_pattern = generate_regex_for_word(words)
        combined_pattern = '|'.join([full_string_pattern] + word_patterns)
        return combined_pattern

def generate_patterns(unique_values):
    patterns = {value: re.compile(generate_combined_regex(clean_text(value)), re.IGNORECASE) for value in unique_values}
    return patterns


def generate_correct_words_list(conn):
    """
    Generate a list of correct words for all columns with word length greater than 4.

    Args:
    conn: The database connection object.

    Returns:
    list: A list of words.
    """
    columns = ['make', 'model', 'badge', 'transmission_type', 'fuel_type', 'drive_type']
    correct_words = set()

    with conn.cursor() as cur:
        for column in columns:
            cur.execute(sql.SQL("SELECT DISTINCT {} FROM vehicle").format(sql.Identifier(column)))
            values = [row[0] for row in cur.fetchall()]
            for value in values:
                words = value.split()
                for word in words:
                    if len(word) > 4:
                        correct_words.add(word)

    return list(correct_words)