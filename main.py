import os
import re
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import difflib
from spelling_corrector import SpellingCorrector

from utils import (sequence_similarity, replace_word, perform_replacements, clean_text, clean_description, find_longest_string, generate_regex_for_word, generate_combined_regex, generate_patterns, generate_correct_words_list)

def connect_db():
    load_dotenv()
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

def fetch_unique_values(conn, column_name):
    with conn.cursor() as cur:
        cur.execute(sql.SQL("SELECT DISTINCT {} FROM vehicle").format(sql.Identifier(column_name)))
        values = [row[0] for row in cur.fetchall()]
    return values

def get_vehicle_listing_counts(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT vehicle_id, COUNT(*) as listing_count
            FROM listing
            GROUP BY vehicle_id
        """)
        listing_counts = {row[0]: row[1] for row in cur.fetchall()}
    return listing_counts


def get_vehicle_data(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM vehicle")
        vehicles = cur.fetchall()
    return vehicles


def parse_attributes(description, column_patterns):
    matches = {key: [] for key in column_patterns.keys()}

    for key, patterns in column_patterns.items():
        for value, pattern in patterns.items():
            match = re.search(pattern, description)
   
            if match:

                #print(f"{match.group()} in description was matched with {value}") 
                match_text = match.group()
                s = difflib.SequenceMatcher(None, match_text, value)
                match_block = s.find_longest_match(0, len(match_text), 0, len(value))
                
                if match_block.size > 0:
                    source_text = match_text if len(match_text) < len(value) else value
                    target_text = value if source_text == match_text else match_text
                    overlapping_text = source_text[match_block.a:match_block.a + match_block.size]
  
                #print(f"Extracted overlapping text: {overlapping_text}")
                matches[key].append(overlapping_text.strip())

    return matches

def compute_confidence(matches, vehicle_attributes):
    total_confidence = 0
    column_weight = (10 / 6) 

    for attribute, match_values in matches.items():
        match_value = find_longest_string(match_values)
        if match_value and vehicle_attributes[attribute]:
            match_similarity = sequence_similarity(match_value, clean_text(vehicle_attributes[attribute]))
            total_confidence += match_similarity * column_weight

    return total_confidence


def match_description(description, vehicles, column_patterns, conn):
    matches = parse_attributes(description, column_patterns)
    #print(matches)
    best_match = None
    max_confidence = 0
    max_listings = 0  
    
    listing_counts = get_vehicle_listing_counts(conn)

    for vehicle in vehicles:
        vehicle_id, make, model, badge, transmission_type, fuel_type, drive_type = vehicle
        vehicle_attributes = {
            'make': make,
            'model': model,
            'badge': badge,
            'transmission_type': transmission_type,
            'fuel_type': fuel_type,
            'drive_type': drive_type
        }

        confidence = compute_confidence(matches, vehicle_attributes)
        listings = listing_counts.get(vehicle_id, 0) 
        if confidence > max_confidence or (confidence == max_confidence and listings > max_listings):
            max_confidence = confidence
            max_listings = listings
            best_match = vehicle

    return best_match, max_confidence

def user_mode(conn, corrector):
    vehicles = get_vehicle_data(conn)
    column_patterns = {
        'make': generate_patterns(fetch_unique_values(conn, 'make')),
        'model': generate_patterns(fetch_unique_values(conn, 'model')),
        'badge': generate_patterns(fetch_unique_values(conn, 'badge')),
        'transmission_type': generate_patterns(fetch_unique_values(conn, 'transmission_type')),
        'fuel_type': generate_patterns(fetch_unique_values(conn, 'fuel_type')),
        'drive_type': generate_patterns(fetch_unique_values(conn, 'drive_type'))
    }

    while True:
        description = input("Enter car description (or type 'exit' to quit): ")
        description = clean_description(description, corrector=corrector)
        if description.lower() == 'exit':
            break
        best_match, confidence = match_description(description, vehicles, column_patterns, conn)
        if best_match:
            vehicle_id = best_match[0]
            print(f"Vehicle ID: {vehicle_id}")
            print(f"Confidence: {confidence}")
        else:
            print("Vehicle ID: Not Found")
            print("Confidence: 0")

def test_mode(conn, corrector):
    vehicles = get_vehicle_data(conn)
    column_patterns = {
        'make': generate_patterns(fetch_unique_values(conn, 'make')),
        'model': generate_patterns(fetch_unique_values(conn, 'model')),
        'badge': generate_patterns(fetch_unique_values(conn, 'badge')),
        'transmission_type': generate_patterns(fetch_unique_values(conn, 'transmission_type')),
        'fuel_type': generate_patterns(fetch_unique_values(conn, 'fuel_type')),
        'drive_type': generate_patterns(fetch_unique_values(conn, 'drive_type'))
    }

    with open('data/inputs.txt', 'r') as f_inputs, open('data/gt.txt', 'r') as f_gt:
        descriptions = f_inputs.readlines()
        gt_ids = f_gt.readlines()

    correct_matches = 0
    total = 0

    for description, gt_id in zip(descriptions, gt_ids):

        description = clean_description(description, corrector=corrector)
        gt_id = gt_id.strip()
        best_match, confidence = match_description(description, vehicles, column_patterns, conn)
        if best_match and best_match[0] == gt_id:
            correct_matches += 1
        else:
            print(f"Missed Match: Description: {description}")
            print(f"Expected Vehicle ID: {gt_id}")
            print(f"Matched Vehicle ID: {best_match[0] if best_match else 'None'}")
            print(f"Confidence: {confidence}")
        total += 1

    accuracy = (correct_matches / total) * 100
    print(f"Accuracy: {accuracy:.2f}%")

def main():
    conn = connect_db()
    correct_words_list = generate_correct_words_list(conn)
    corrector = SpellingCorrector(correct_words_list)
    mode = input("Enter mode (user/test): ").strip().lower()
    if mode == 'user':
        user_mode(conn, corrector)
    elif mode == 'test':
        test_mode(conn, corrector)
    else:
        print("Invalid mode. Please enter 'user', or 'test'.")

if __name__ == "__main__":
    main()