# Vehicle Matching Solution

This repository contains a solution for matching vehicle descriptions to a database of vehicles. The solution uses a combination of string similarity measures, regex patterns, and a custom spelling corrector to handle misspellings and variations in descriptions.

## Repository Structure

- `main.py`: The main script to run the solution.
- `spelling_corrector.py`: Contains the `SpellingCorrector` class used to correct misspelled words in descriptions.
- `utils.py`: Contains various utility functions for text cleaning, similarity computation, regex generation, and pattern matching.
- `data/`: Folder containing the following files:
  - `data.sql`: Script to populate the database with vehicle data.
  - `inputs.txt`: Test data containing vehicle descriptions.
  - `gt.txt`: Ground truth data for testing.
- `.env.sample`: Sample environment variables file.

## Setup

1.  **Install Conda**: If you don't have Conda installed, download and install it from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

2.  **Create Conda Environment**:

    ```sh
    conda create --name vehicle-matching python=3.10
    conda activate vehicle-matching
    ```

3.  **Install Dependencies**:

    ```sh
        pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**:

    - Create a `.env` file in the root directory.
    - Add the following environment variables to the `.env` file:

    ```sh

        DB_NAME=your_database_name
        DB_USER=your_database_user
        DB_PASSWORD=your_database_password
        DB_HOST=your_database_host
        DB_PORT=your_database_port
    ```

## Running the Solution:

- Run the solution using the following command:

  ```sh
  python main.py
  ```

  The solution operates in two modes: user and test and you will be prompted to choose one.

## Solution:

### User Mode

In this mode, you can interactively enter vehicle descriptions and get the best matching vehicle from the database.

- The user is prompted to enter a vehicle description.
- The description is cleaned and corrected for spelling errors using the SpellingCorrector.
- The cleaned description is matched against the column values using regex patterns and string similarity measures.
- The best match is returned along with the confidence score.
- If two matches tie on confidences, the one with more listings it returned.

### Test Mode

In this mode, the solution tests the accuracy of matching using predefined test data.

- The test descriptions are read from data/inputs.txt.
- The ground truth vehicle IDs are read from data/gt.txt.
- Each description is cleaned and corrected using the SpellingCorrector.
- Descriptions are matched against the database and the results are compared with the ground truth.
- The accuracy is reported.

## Key Utilities:

- `clean_text(text)`: Cleans the input text by removing special characters.
- `clean_description(description, corrector)`: Cleans and corrects the description using the spelling corrector.
- `sequence_similarity(seq1, seq2)`: Computes the similarity between two sequences.
- `generate_patterns(unique_values)`: Generates regex patterns for matching.
- `generate_correct_words_list(conn)`: Generates a list of correct words from the database.
- `Spelling Corrector`:
  The SpellingCorrector class is used to correct misspelled words in the descriptions. It uses a list of correct words generated from the database and matches words with possible misspellings using the difflib library.

## Assumptions:

- `Greater Overlap Means Greater Match`: While creating gt.txt, it was assumed that a greater overlap between the description and the vehicle attributes indicates a greater match.
  Substring and Superstring Matching:

- The regex patterns are generated to match both substrings and superstrings of the attributes. This ensures that partial matches are also considered during the matching process.

## Results:

- The solution achieved an accuracy of 93.75% on the test data.

## Future Improvements:

- A regular expression based approach does not perform very well where semantic understanding of
  the text is required. A hybrid approach with machine
  learning incorporated can be used to improve the accuracy of the approach
