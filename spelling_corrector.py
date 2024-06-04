# spelling_corrector.py
import difflib


class SpellingCorrector:
    def __init__(self, correct_words):
        """
        Initialize the SpellingCorrector with a list of correct words.

        Args:
        correct_words (list): A list of correctly spelled words.
        """
        self.correct_words = correct_words

    def correct(self, word):
        """
        Correct the spelling of a word if it is likely misspelled.

        Args:
        word (str): The word to be checked and corrected.

        Returns:
        str: The corrected word if a correction is found, else the original word.
        """
        if word in self.correct_words:
            return word
        else:
            closest_match = difflib.get_close_matches(word, self.correct_words, n=1, cutoff=0.8)
            if closest_match:
                return closest_match[0]
            else:
                return word

