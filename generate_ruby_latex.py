import subprocess
import argparse
import unicodedata
import sys

SENTINEL = "\uFDD0"  # Noncharacter used to keep 1:1 alignment per source char.

def run_transliteration(input_text):
    process = subprocess.Popen(
        [
            'python3',
            'transliterate.py',
            '-s', 'jcz_only',
            '-r', 'wl',
            '-t', 'vertical',
            '-x', 'False',
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    transliteration_output, error = process.communicate(input=input_text.encode('utf-8'))

    if process.returncode != 0:
        print(f"Error in transliteration: {error.decode('utf-8')}", file=sys.stderr)
        return None

    return transliteration_output.decode('utf-8')


def add_sentinels(text):
    return SENTINEL.join(text)


def split_by_sentinel(phonetic_text):
    return phonetic_text.split(SENTINEL)


def is_punctuation_or_symbol(ch):
    category = unicodedata.category(ch)
    return category.startswith('P') or category.startswith('S')


def should_ruby(ch):
    if ch.isspace():
        return False
    if is_punctuation_or_symbol(ch):
        return False
    return True


def generate_ruby_latex(chinese_text, phonetic_tokens):
    if len(phonetic_tokens) != len(chinese_text):
        print(
            f"Warning: length mismatch (text={len(chinese_text)} tokens={len(phonetic_tokens)}).",
            file=sys.stderr,
        )

    output = []
    max_len = min(len(chinese_text), len(phonetic_tokens))
    for i in range(max_len):
        chinese_char = chinese_text[i]
        phonetic_char = phonetic_tokens[i]

        if should_ruby(chinese_char) and phonetic_char and phonetic_char != chinese_char:
            output.append(f"\\ruby{{{chinese_char}}}{{{phonetic_char}}}")
        else:
            output.append(chinese_char)

    if len(chinese_text) > max_len:
        output.append(chinese_text[max_len:])

    return ''.join(output)


def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX ruby annotations from Chinese text.")
    parser.add_argument('input_file', help='Input file containing the Chinese text')
    parser.add_argument('output_file', help='Output file to save the LaTeX formatted string')
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as f:
        chinese_text = f.read()

    marked_text = add_sentinels(chinese_text)
    phonetic_text = run_transliteration(marked_text)

    if phonetic_text is None:
        return

    phonetic_tokens = split_by_sentinel(phonetic_text)
    latex_string = generate_ruby_latex(chinese_text, phonetic_tokens)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        f.write(latex_string)

    print(f"LaTeX output has been written to {args.output_file}")


if __name__ == "__main__":
    main()
