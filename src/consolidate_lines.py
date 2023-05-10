from collections import defaultdict
import os
import re

sound_effects_regex = re.compile('\(.+\)')
period_regex = re.compile("[A-Z]+\.( )*(([A-Z]?[a-z]+|,|'|\.|\?|\!)| )+")
period_regex_noline = re.compile("[A-Z]+\.")
colon_regex = re.compile("[A-Z]+:( )*(([A-Z]?[a-z]+|,|'|\.|\?|\!)| )+")
colon_regex_noline = re.compile("[A-Z]+:")
split_line_regex = re.compile("^[A-Z]+(\.|:)?(\n((([A-Za-z]*))(,|'|\.|\?|!)?( )?)*(([A-Za-z]+)(,|'|\.|\?|!)?))+", flags=re.MULTILINE)
time_regex = re.compile("\d+:\d\d(:\d\d)?")
titles = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Rev.', 'Pres.', 'Sec.', 'Sen.', 'Rep.', 'Mx.', 'Esq.', 'Fr.', 'Pr.', 'Br.', 'Sr.']


# many lines of dialogue are broken into multiple lines of text by default;
# this function consolidates each line of dialogue to just one line of text.
def consolidate_lines(text, mode):
    if mode == '.':
        mode_regex = period_regex
    elif mode == ':':
        mode_regex = colon_regex
    else:
        mode_regex = colon_regex
    out_lines = []
    lines = text.split('\n')
    lines = [line for line in lines if line.strip()]  # get rid of empty strings    
    this_line = None
    split_name = False
    for line in lines:
        if 'http' in line:
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
            this_line += line + ' '
    out_lines.append(this_line)  # add the last line
    out_lines = [sound_effects_regex.sub('', line) for line in out_lines]
    return out_lines


# get rid of lines that don't match the relevant dialogue format;
# these lines do not matter for the purposes of NLP'ing on dialogue.
def clean_lines(text, mode: str):
    if mode == ':':
        lines = text.split('\n')
        lines = [line for line in lines if colon_regex.match(line)]
    elif mode == '.':
        lines = text.split('\n')
        lines = [line for line in lines if period_regex.match(line)]
    else:  # of the form "NAME\nLine"
        lines = split_line_regex.findall(text)
    return lines


# determine whether lines are formatted like "NAME: text", "NAME. Text", or something else
def determine_mode(text):
    lines = text.split('\n')
    colon_lines = [line for line in lines if colon_regex.match(line)]
    if len(colon_lines) > len(lines) / 4:
        return ':'
    period_lines = [line for line in lines if period_regex.match(line)]
    if len(period_lines) > len(lines) / 4:
        return '.'
    if len(colon_lines) > 10 or len(period_lines) > 10:
        if len(colon_lines) > len(period_lines):
            return ':'
        else:
            return '.'
    return 'else'


# plays use a wide variety of formatting tricks to denote stage directions,
# like "[_EXIT Mary_" or "(She laughs)".
# this function detects the stage direction format for a given text by finding the
# punctuation sequences that surround the words "enter" and "exit".
def get_stage_direction_regex(text, min_count: int = 1, n_most_common: int = -1):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    enter_exit_context = defaultdict(lambda: 0)
    for line in lines:
        tokens = line.split()
        for token in tokens:
            if 'enter' in token.lower() or 'exit' in token.lower():
                to_add = token.lower().replace('enter', '<TEXT>').replace('exit', '<TEXT>')
                if len(to_add.replace('<TEXT>', '')) == 0:
                    continue 
                if len([c for c in to_add.replace('<TEXT>', '') if c.isalpha()]) > 0:
                    # if there are other letters in the string, ignore
                    continue
                for c in ['.', '"', '(', ')', '[', ']', '+', '*', ':', '{', '}', '^', '$']:
                    to_add = to_add.replace(c, '\\'+ c)
                enter_exit_context[to_add] += 1
    scene_punct = sorted(enter_exit_context.items(), key=lambda x:x[1], reverse=True)
    scene_punct = [s for s in scene_punct if s[1] > min_count][:n_most_common]
    return [re.compile('^' + reg[0]) for reg in scene_punct]


# this is not used in the app; it was put here for testing purposes.
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
            with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
                f.writelines(lines)