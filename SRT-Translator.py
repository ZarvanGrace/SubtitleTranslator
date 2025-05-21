import re
from googletrans import Translator

def parse_srt(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\n+', content.strip())
    subtitles = []

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            idx = lines[0]
            timing = lines[1]
            text_lines = lines[2:]
            subtitles.append({
                'index': idx,
                'time': timing,
                'text': text_lines
            })
    return subtitles

def merge_text(subtitles):
    flat_text = []
    map_structure = []
    for sub in subtitles:
        sentence = ' '.join(sub['text']).strip()
        flat_text.append(sentence)
        map_structure.append(len(sub['text']))
    return ' '.join(flat_text), map_structure

def smart_split(translated_text, map_structure):
    words = translated_text.split()
    total_words = len(words)
    chunks = []
    idx = 0

    for line_count in map_structure:
        if line_count == 1:
            chunk_len = total_words // len(map_structure)
            chunk = ' '.join(words[idx:idx + chunk_len])
            chunks.append([chunk])
            idx += chunk_len
        else:
            # Split proportionally for multi-line subtitles
            chunk_len = total_words // len(map_structure)
            line_words = chunk_len // line_count
            lines = []
            for i in range(line_count):
                line = ' '.join(words[idx:idx + line_words])
                lines.append(line)
                idx += line_words
            chunks.append(lines)
    return chunks

def rebuild_srt(subtitles, translated_chunks, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for sub, trans_lines in zip(subtitles, translated_chunks):
            f.write(f"{sub['index']}\n")
            f.write(f"{sub['time']}\n")
            for line in trans_lines:
                f.write(f"{line}\n")
            f.write("\n")

def main(input_file, output_file):
    translator = Translator()
    subtitles = parse_srt(input_file)
    full_text, structure = merge_text(subtitles)

    print("[*] Translating text to Persian...")
    translated = translator.translate(full_text, dest='fa').text

    translated_chunks = smart_split(translated, structure)
    rebuild_srt(subtitles, translated_chunks, output_file)
    print(f"[✓] Translated SRT saved to '{output_file}'")

if __name__ == '__main__':
    main('input.srt', 'translated.srt')
