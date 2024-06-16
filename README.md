```markdown
# PDF-BRUTEFORCE
Python-based brute-force password cracker that uses multithreading.

## Overview
This tool attempts to crack the password of an encrypted PDF file using a brute-force approach. It utilizes multithreading to speed up the process and can try combinations of known words and characters from a specified charset.

## Features
- Multithreaded brute-force attack
- Tries common words and their combinations first
- Configurable password length and charset
- Detailed progress logging with high precision

## Requirements
- Python 3.x
- PyMuPDF (`fitz`)
- `itertools` (standard library)

## Installation
1. Install Python 3.x from [python.org](https://www.python.org/).
2. Install the required Python package:
    ```bash
    pip install pymupdf
    ```

## Usage
To run the script, use the following command:

```bash
python pdf_bruteforce.py <pdf_path> --min-length <min_length> --max-length <max_length> --num-threads <num_threads>
```

### Arguments
- `pdf_path`: Path to the encrypted PDF file.
- `--min-length`: Minimum password length to try (default: 3).
- `--max-length`: Maximum password length to try (default: 4).
- `--num-threads`: Number of threads to use for the brute-force attack (default: 4).

### Example
```bash
python pdf_bruteforce.py topsecret.pdf --min-length 4 --max-length 11 --num-threads 16
```

### Detailed Explanation
- **Charset**: The script uses a default charset that includes letters, digits, and special characters:
    ```python
    charset = string.ascii_letters + string.digits + string.punctuation
    ```
- **Common Words**: The script starts by trying a list of common words and their combinations with the charset:
    ```python
    words = ["password", "12345"]
    ```
- **Multithreading**: The script uses multiple threads to speed up the brute-force process. Each thread works on a different segment of the password space.
- **Progress Logging**: The script logs the progress of the brute-force attack, including the percentage complete with a precision of six decimal places.

### Script Breakdown
1. **Global Variables**: Used for thread synchronization.
    ```python
    found = False
    password = None
    lock = threading.Lock()
    ```

2. **Password Check Function**: Attempts to open the PDF with the given password.
    ```python
    def check_password(pdf_path, password):
        ...
    ```

3. **Password Generators**: Generate possible passwords from the charset and known words.
    ```python
    def generate_passwords(charset, min_length, max_length, start, step):
        ...
    def generate_word_combinations(words, charset, min_length, max_length, start, step):
        ...
    ```

4. **Worker Function**: Each thread runs this function to try passwords.
    ```python
    def worker(pdf_path, charset, min_length, max_length, words, start, step, total_combinations, start_time):
        ...
    ```

5. **Brute-Force Function**: Coordinates the brute-force attack using multiple threads.
    ```python
    def brute_force_pdf(pdf_path, min_length, max_length, charset, words, num_threads):
        ...
    ```

6. **Known Words Worker**: Tries known words and their combinations first.
    ```python
    def known_words_worker(pdf_path, words, charset, max_length, start, step, total_combinations, start_time):
        ...
    ```

7. **Known Words Phase**: Runs the known words phase using multiple threads.
    ```python
    def try_known_words_first(pdf_path, words, charset, max_length, num_threads):
        ...
    ```

8. **Main Function**: Parses arguments and starts the brute-force attack.
    ```python
    if __name__ == "__main__":
        import argparse

        parser = argparse.ArgumentParser(description="Multithreaded PDF Brute Force Password Cracker")
        parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
        parser.add_argument("--min-length", type=int, default=3, help="Minimum password length")
        parser.add_argument("--max-length", type=int, default=4, help="Maximum password length")
        parser.add_argument("--num-threads", type=int, default=4, help="Number of threads to use")

        args = parser.parse_args()

        charset = string.ascii_letters + string.digits + string.punctuation
        words = ["JOSH", "joshua@g47"]

        print(f"Starting brute-force attack on {args.pdf_path} with {args.num_threads} threads using default charset and common words...")

        try_known_words_first(args.pdf_path, words, charset, args.max_length, args.num_threads)

        if not found:
            password_found = brute_force_pdf(args.pdf_path, args.min_length, args.max_length, charset, words, args.num_threads)
            if password_found:
                print(f"Password found: {password_found}")
            else:
                print("Failed to find the password.")
        else:
            print(f"Password found: {password}")
    ```

## Notes
- Ensure you have the necessary permissions to attempt to crack the PDF file.
- The brute-force attack can take a significant amount of time depending on the password length and complexity.
- Use responsibly and ethically.

## License
This project is licensed under the MIT License.
```

This README provides a comprehensive guide on how to use the script, including installation, usage, and a detailed explanation of how the script works. If you have any further questions or need additional information, feel free to ask!