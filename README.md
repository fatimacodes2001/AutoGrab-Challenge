# Vehicle Matching Solution

This repository contains a solution for matching vehicle descriptions to a database of vehicles. The solution uses a combination of string similarity measures, regex patterns, and a custom spelling corrector to handle misspellings and variations in descriptions.

## Repository Structure

- `main.py`: The main script to run the solution.
- `spelling_corrector.py`: Contains the `SpellingCorrector` class used to correct misspelled words in descriptions.
- `utils.py`: Contains various utility functions for text cleaning, similarity computation, regex generation, and pattern matching.
- `data/`: Folder containing the following files:
  - `database_population.sql`: Script to populate the database with vehicle data.
  - `inputs.txt`: Test data containing vehicle descriptions.
  - `gt.txt`: Ground truth data for testing.
- `.env.sample`: Sample environment variables file.

## Setup

1. **Install Conda**: If you don't have Conda installed, download and install it from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

2. **Create Conda Environment**:
   ```sh
   conda create --name vehicle-matching python=3.10
   conda activate vehicle-matching
   ```
