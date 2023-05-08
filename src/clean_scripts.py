from collections import defaultdict
import os
import re
from io import StringIO

sound_effects_regex = re.compile('\(.+\)')
period_regex = re.compile("[A-Z]+\.( )*(([A-Z]?[a-z]+|,|'|\.|\?|\!)| )+")
period_regex_noline = re.compile("[A-Z]+\.")
colon_regex = re.compile("[A-Z]+:( )*(([A-Z]?[a-z]+|,|'|\.|\?|\!)| )+")
colon_regex_noline = re.compile("[A-Z]+:")
split_line_regex = re.compile("^[A-Z]+(\.|:)?(\n((([A-Za-z]*))(,|'|\.|\?|!)?( )?)*(([A-Za-z]+)(,|'|\.|\?|!)?))+", flags=re.MULTILINE)
time_regex = re.compile("\d+:\d\d(:\d\d)?")
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
    # if sum([x[1] for x in scene_punct]) >= len(lines) * 0.05:
    #     print(scene_punct)
    return [re.compile('^' + reg) for reg in scene_punct]

titles = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Rev.', 'Pres.', 'Sec.', 'Sen.', 'Rep.', 'Mx.', 'Esq.', 'Fr.', 'Pr.', 'Br.', 'Sr.']
# TODO fits scene regex or act regex => must have a new line


def consolidate_lines(text, mode):
    text = '\n'.join([line.strip() for line in text.split('\n')])  # remove extra space from beginning of lines
    if mode == '.':
        lines = text.split('\n\n')
        lines = [line.replace('\n', ' ').strip() for line in lines if line.strip()]  # get rid of empty strings  
        mode_regex = period_regex
        mode_regex_noline = period_regex_noline
    elif mode == ':':
        lines = text.split('\n\n')
        lines = [line.replace('\n', ' ').strip() for line in lines if line.strip()]  # get rid of empty strings  
        mode_regex = colon_regex
        mode_regex_noline = colon_regex_noline
    else:        
        lines = text.split('\n\n')
        lines = [line.replace('\n', ': ').strip() for line in lines if line.strip()]   
        mode_regex = colon_regex
        mode_regex_noline = colon_regex_noline
    # lines = text.split('\n\n')
    # lines = [line.replace('\n', ' ') for line in lines if line.strip()]  # get rid of empty strings  
    out_lines = []  
    this_line = None
    split_name = False
    stage_direction_regeces = get_stage_direction_regex(text)
    for line in lines:
        for reg in stage_direction_regeces:
            for directions in set(reg.findall(line)):
                line = line.replace(directions, '<Scene>' + directions + '<Scene>')
        if 'http' in line:  # TODO also detect e.g. 12:00:00 (regex)
            continue
        if mode_regex.match(line):
            # if period_regex.match(line):  # replace period bt speaker and line with a colon, for consistency
            if mode == '.':
                split_line = line.split('.')
                line = split_line[0].strip() + ':' + '.'.join(split_line[1:])
            if split_name:  
                this_line += line
                split_name = False
            else:  # this is truly the first line of this turn
                if this_line is not None:
                    out_lines.append(this_line + '\n')  # get rid of last line
                this_line = line + ' '  # start a new line
        elif mode_regex_noline.match(line):
            if mode == '.':
                split_line = line.split('.')
                line = split_line[0] + ':' + '.'.join(split_line[1:])
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
    # for line in out_lines:
    #     # line = re.sub(sound_effects_regex, '', line).strip()
    #     line = sound_effects_regex.sub('', line)
    out_lines = [sound_effects_regex.sub('', line) for line in out_lines]
    return out_lines


def clean_lines(text, mode: str):
    for title in titles:
        text.replace(title, title[:-1])  # take period off of titles
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
    lines = text.split('\n\n')
    lines = [line.replace('\n', ' ') for line in lines]
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


if __name__ == "__main__":
    in_dir = '../final_project/'
    out_dir = '../final_project/play_scripts'
    for fname in os.listdir(in_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(in_dir, fname), 'r', encoding='utf-8') as f:
                text = f.read()
            mode = determine_mode(text)
            lines = consolidate_lines(text, mode)
            # lines = clean_lines(text, mode=mode)
            # lines = [line + '\n' for line in lines]
            with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
                f.writelines(lines)