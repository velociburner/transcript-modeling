import os
import re

sound_effects_regex = re.compile('\(.+\)')
period_regex = re.compile("[A-Z]+\.( )?(([A-Z]?[a-z]+|,|'|\.|\?|\!)| )+")
colon_regex = re.compile("[A-Z]+:( )?(([A-Z]?[a-z]+|,|'|\.|\?|\!)| )+")
split_line_regex = re.compile("^[A-Z]+(\.|:)?(\n((([A-Za-z]*))(,|'|\.|\?|!)?( )?)*(([A-Za-z]+)(,|'|\.|\?|!)?))+", flags=re.MULTILINE)

def consolidate_lines(text, mode):
    if mode == '.':
        mode_regex = period_regex
    elif mode == ':':
        mode_regex = colon_regex
    out_lines = []
    lines = text.split('\n')
    lines = [line for line in lines if line]  # get rid of empty strings    
    this_line = None
    split_name = False
    for line in lines:
        line = re.sub(sound_effects_regex, '', line).strip()
        if 'http' in line:  # TODO also detect e.g. 12:00:00 (regex)
            continue
        if mode_regex.match(line):
            if split_name:  
                this_line += line
                split_name = False
            else:  # this is truly the first line of this turn
                if this_line is not None:
                    out_lines.append(this_line + '\n')  # get rid of last line
                this_line = line + ' '  # start a new line
        elif len([c for c in line if c.isupper()]) >= len(line)/2:  # if more than half of the line is uppercase, it's probably part of a name
            if this_line is not None:
                out_lines.append(this_line + '\n')
            this_line = line + ' '
            split_name = True
        elif this_line is None:  # line at the beginning of the file without a speaker; disregard
            continue
        else:
            # print(line)
            this_line += line + ' '
    out_lines.append(this_line)  # last line
    return out_lines


def clean_lines(text, mode: str):
    # print(mode)
    if mode == ':':
        lines = text.split('\n')
        lines = [line for line in lines if colon_regex.match(line)]
    elif mode == '.':
        lines = text.split('\n')
        lines = [line for line in lines if period_regex.match(line)]
    else:  # of the form "NAME\nLine"
        lines = split_line_regex.findall(text)
    return lines


def determine_mode(text):
    lines = text.split('\n')
    lines = [line for line in lines if line.strip()]
    colon_lines = [line for line in lines if colon_regex.match(line)]
    # print(lines[90:100])
    # print(len(colon_lines), len(lines) / 2)
    # if len(colon_lines) > len(lines) / 2:
    #     return ':'
    period_lines = [line for line in lines if period_regex.match(line)]
    # print(len(period_lines), len(lines) / 2)
    # if len(period_lines) > len(lines) / 2:
    #     return '.'
    if len(colon_lines) > 10 or len(period_lines) > 10:
        if len(colon_lines) > len(period_lines):
            return ':'
        else:
            return '.'
    return 'else'


if __name__ == "__main__":
    in_dir = '../final_project'
    out_dir = '../final_project/play_scripts'
    for fname in os.listdir(in_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(in_dir, fname), 'r', encoding='utf-8') as f:
                text = f.read()
            mode = determine_mode(text)
            if mode == 'else':
                continue
            lines = consolidate_lines(text, mode)
            # lines = clean_lines(text, mode=mode)
            # lines = [line + '\n' for line in lines]
            with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
                f.writelines(lines)