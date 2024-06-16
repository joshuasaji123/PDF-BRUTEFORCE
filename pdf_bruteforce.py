import time
import string
import fitz  # PyMuPDF
import threading
from itertools import product

# Global variables for thread synchronization
found = False
password = None
lock = threading.Lock()

def check_password(pdf_path, password):
    try:
        doc = fitz.open(pdf_path)
        if doc.is_encrypted:
            if doc.authenticate(password):
                return True
            else:
                return False
        else:
            print(f"The file {pdf_path} is not encrypted.")
            return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

def generate_passwords(charset, min_length, max_length, start, step):
    for length in range(min_length, max_length + 1):
        for i, password in enumerate(product(charset, repeat=length)):
            if i % step == start:
                yield ''.join(password)

def generate_word_combinations(words, charset, min_length, max_length, start, step):
    for word in words:
        for length in range(len(word) + 1, max_length + 1):
            for i, combo in enumerate(product(charset, repeat=length - len(word))):
                if i % step == start:
                    yield word + ''.join(combo)
                    yield ''.join(combo) + word

def worker(pdf_path, charset, min_length, max_length, words, start, step, total_combinations, start_time):
    global found, password
    passwords_tried = 0

    # Generate passwords from words and their combinations
    for password_to_check in generate_word_combinations(words, charset, min_length, max_length, start, step):
        if found:
            return
        passwords_tried += 1
        percent_complete = ((passwords_tried * step) / total_combinations) * 100
        elapsed_time = time.time() - start_time
        print(f"Trying: {password_to_check}, Tried: {passwords_tried * step}, Elapsed: {elapsed_time:.2f}s, Complete: {percent_complete:.6f}%")
        
        if check_password(pdf_path, password_to_check):
            with lock:
                if not found:  # Double-check to avoid race condition
                    found = True
                    password = password_to_check
            return

    # Generate passwords from charset
    for password_to_check in generate_passwords(charset, min_length, max_length, start, step):
        if found:
            return
        passwords_tried += 1
        percent_complete = (passwords_tried * step) / total_combinations * 100
        elapsed_time = time.time() - start_time
        print(f"Trying: {password_to_check}, Tried: {passwords_tried * step}, Elapsed: {elapsed_time:.2f}s, Complete: {percent_complete:.6f}%")
        
        if check_password(pdf_path, password_to_check):
            with lock:
                if not found:  # Double-check to avoid race condition
                    found = True
                    password = password_to_check
            return

def brute_force_pdf(pdf_path, min_length, max_length, charset, words, num_threads):
    global found, password
    start_time = time.time()

    # Calculate total combinations for brute-force
    total_combinations = sum(len(charset) ** i for i in range(min_length, max_length + 1))
    
    # Calculate total combinations for known words and their variations
    total_word_combinations = sum(len(charset) ** (max_length - len(word)) * 2 for word in words)
    
    total_combinations += total_word_combinations

    print(f"Total combinations to try: {total_combinations}")

    # Start threads for brute-force
    threads = []
    print(f"Starting {num_threads} threads for brute-force...")
    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(pdf_path, charset, min_length, max_length, words, i, num_threads, total_combinations, start_time))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    elapsed_time = time.time() - start_time
    if found:
        print(f"Password found: {password}")
        print(f"Passwords tried: {total_combinations}, Time elapsed: {elapsed_time:.2f}s")
        return password
    else:
        print(f"No password found, Passwords tried: {total_combinations}, Time elapsed: {elapsed_time:.2f}s")
        return None

def known_words_worker(pdf_path, words, charset, max_length, start, step, total_combinations, start_time):
    global found, password
    total_passwords_tried = 0

    for index, word in enumerate(words):
        if found:
            return
        if index % step != start:
            continue
        passwords_tried = 0
        word_start_time = time.time()
        print(f"Trying known word: {word}")
        if check_password(pdf_path, word):
            with lock:
                if not found:  # Double-check to avoid race condition
                    found = True
                    password = word
            return

        for length in range(len(word) + 1, max_length + 1):
            for combo in product(charset, repeat=length - len(word)):
                if found:
                    return
                passwords_tried += 1
                total_passwords_tried += 1
                password_to_check = word + ''.join(combo)
                percent_complete = (total_passwords_tried * step) / total_combinations * 100
                elapsed_time = time.time() - start_time
                print(f"Trying: {password_to_check}, Tried: {total_passwords_tried * step}, Elapsed: {elapsed_time:.2f}s, Complete: {percent_complete:.6f}%")
                if check_password(pdf_path, password_to_check):
                    with lock:
                        if not found:  # Double-check to avoid race condition
                            found = True
                            password = password_to_check
                    return

                password_to_check = ''.join(combo) + word
                percent_complete = (total_passwords_tried * step) / total_combinations * 100
                elapsed_time = time.time() - start_time
                print(f"Trying: {password_to_check}, Tried: {total_passwords_tried * step}, Elapsed: {elapsed_time:.2f}s, Complete: {percent_complete:.6f}%")
                if check_password(pdf_path, password_to_check):
                    with lock:
                        if not found:  # Double-check to avoid race condition
                            found = True
                            password = password_to_check
                    return

        word_elapsed_time = time.time() - word_start_time
        print(f"Finished trying word: {word}, Tried: {passwords_tried}, Elapsed: {word_elapsed_time:.2f}s")

    total_elapsed_time = time.time() - start_time
    print(f"Known words phase complete. Total tried: {total_passwords_tried}, Total elapsed: {total_elapsed_time:.2f}s")

def try_known_words_first(pdf_path, words, charset, max_length, num_threads):
    global found, password
    start_time = time.time()

    # Calculate total combinations for known words and their variations
    total_combinations = sum(len(charset) ** (max_length - len(word)) * 2 for word in words)

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=known_words_worker, args=(pdf_path, words, charset, max_length, i, num_threads, total_combinations, start_time))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multithreaded PDF Brute Force Password Cracker")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    parser.add_argument("--min-length", type=int, default=3, help="Minimum password length")
    parser.add_argument("--max-length", type=int, default=4, help="Maximum password length")
    parser.add_argument("--num-threads", type=int, default=4, help="Number of threads to use")

    args = parser.parse_args()

    # Default charset including letters, digits, and special characters
    charset = string.ascii_letters + string.digits + string.punctuation

    # List of common words
    words = [
        "password", "1234", 
    ]

    print(f"Starting brute-force attack on {args.pdf_path} with {args.num_threads} threads using default charset and common words...")

    # Try known words first
    try_known_words_first(args.pdf_path, words, charset, args.max_length, args.num_threads)

    # If password is not found, proceed with brute-force attack
    if not found:
        password_found = brute_force_pdf(args.pdf_path, args.min_length, args.max_length, charset, words, args.num_threads)
        if password_found:
            print(f"Password found: {password_found}")
        else:
            print("Failed to find the password.")
    else:
        print(f"Password found: {password}")
