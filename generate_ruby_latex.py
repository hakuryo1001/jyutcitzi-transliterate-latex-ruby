# import subprocess
# import argparse

# def run_transliteration(input_file):
#     # Open the input file to be used in the transliteration process
#     with open(input_file, 'r', encoding='utf-8') as f:
#         input_text = f.read()

#     # Call the existing transliteration script with subprocess
#     process = subprocess.Popen(
#         ['python3', 'transliterate.py', '-s', 'jcz_only', '-r', 'wl', '-t', 'vertical', '--use_repeat_char', 'true'],
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE
#     )
#     transliteration_output, error = process.communicate(input=input_text.encode('utf-8'))
    
#     if process.returncode != 0:
#         print(f"Error in transliteration: {error.decode('utf-8')}")
#         return None

#     # Return the transliteration result as a string
#     return transliteration_output.decode('utf-8').strip()

# def generate_ruby_latex(chinese_text, phonetic_text):
#     # Ensure both strings are of the same length
#     # if len(chinese_text) != len(phonetic_text):
#         # raise ValueError("Chinese text and phonetic text lengths do not match.")
    
#     # Create the LaTeX string with ruby annotations
#     latex_string = ''.join([f"\\ruby{{{chinese_char}}}{{{phonetic_char}}}" for chinese_char, phonetic_char in zip(chinese_text, phonetic_text)])
#     return latex_string

# def main():
#     # Parse the command-line arguments for input and output file names
#     parser = argparse.ArgumentParser(description="Generate LaTeX ruby annotations from Chinese text.")
#     parser.add_argument('input_file', help='Input file containing the Chinese text')
#     parser.add_argument('output_file', help='Output file to save the LaTeX formatted string')
#     args = parser.parse_args()

#     # Run transliteration to get the phonetic representation
#     phonetic_text = run_transliteration(args.input_file)
    
#     if phonetic_text:
#         # Read the original Chinese text from the input file again (as the transliteration was done)
#         with open(args.input_file, 'r', encoding='utf-8') as f:
#             chinese_text = f.read().strip()

#         # Generate the LaTeX ruby annotated string
#         latex_string = generate_ruby_latex(chinese_text, phonetic_text)

#         # Write the LaTeX output to the specified output file
#         with open(args.output_file, 'w', encoding='utf-8') as f:
#             f.write(latex_string)

#         print(f"LaTeX output has been written to {args.output_file}")

# if __name__ == "__main__":
#     main()


import subprocess
import argparse
import re

def run_transliteration(input_file):
    # Open the input file to be used in the transliteration process
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()

    # Call the existing transliteration script with subprocess
    process = subprocess.Popen(
        ['python3', 'transliterate.py', '-s', 'jcz_only', '-r', 'wl', '-t', 'vertical'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    transliteration_output, error = process.communicate(input=input_text.encode('utf-8'))
    
    if process.returncode != 0:
        print(f"Error in transliteration: {error.decode('utf-8')}")
        return None

    # Return the transliteration result as a string
    return transliteration_output.decode('utf-8').strip()

def generate_ruby_latex(chinese_text, phonetic_text):
    # Create the LaTeX string with ruby annotations
    latex_string = ''.join([f"\\ruby{{{chinese_char}}}{{{phonetic_char}}}" for chinese_char, phonetic_char in zip(chinese_text, phonetic_text)])
    return latex_string

def clean_up_ruby(latex_string):
    # This regular expression looks for ruby commands that wrap spaces or punctuation
    # Matches cases like \ruby{,}{,}, \ruby{}{}, \ruby{。}{。}, etc.
    ruby_pattern = re.compile(r'\\ruby\{([\W\s]*)\}\{([\W\s]*)\}')

    # Function to replace offending sequences
    def replace_ruby(match):
        chinese_char = match.group(1)
        phonetic_char = match.group(2)
        
        # If both the Chinese character and phonetic are punctuation or whitespace, keep the character only
        if chinese_char == phonetic_char and re.match(r'[\W\s]', chinese_char):
            return chinese_char
        return f"{chinese_char}"  # In case they don't need ruby, return the original Chinese char

    # Replace offending ruby sequences with the cleaned-up punctuation/space
    cleaned_latex_string = ruby_pattern.sub(replace_ruby, latex_string)
    
    return cleaned_latex_string

def main():
    # Parse the command-line arguments for input and output file names
    parser = argparse.ArgumentParser(description="Generate LaTeX ruby annotations from Chinese text.")
    parser.add_argument('input_file', help='Input file containing the Chinese text')
    parser.add_argument('output_file', help='Output file to save the LaTeX formatted string')
    args = parser.parse_args()

    # Run transliteration to get the phonetic representation
    phonetic_text = run_transliteration(args.input_file)
    
    if phonetic_text:
        # Read the original Chinese text from the input file again (as the transliteration was done)
        with open(args.input_file, 'r', encoding='utf-8') as f:
            chinese_text = f.read().strip()

        # Generate the LaTeX ruby annotated string
        latex_string = generate_ruby_latex(chinese_text, phonetic_text)

        # Clean up any ruby sequences that wrap around punctuation or spaces
        cleaned_latex_string = clean_up_ruby(latex_string)

        # Write the cleaned-up LaTeX output to the specified output file
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_latex_string)

        print(f"LaTeX output has been written to {args.output_file}")

if __name__ == "__main__":
    main()
