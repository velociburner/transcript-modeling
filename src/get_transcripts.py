import xml
from lxml import etree
import os
import re

in_dir = 'clean'
out_dir = 'transcripts'
sound_effects_regex = re.compile('\(.+\)')
for fname in os.listdir(in_dir):
    if not fname.endswith('.xml'):
        continue
    out_lines = []
    xmlparse = etree.parse(os.path.join(in_dir, fname))
    root = xmlparse.getroot()
    text = root.find('TEXT').text
    lines = text.split('\n')
    lines = [line for line in lines if line]  # get rid of empty strings    
    this_line = None
    split_name = False
    for line in lines:
        line = re.sub(sound_effects_regex, '', line).strip()
        if 'http' in line:  # TODO also detect e.g. 12:00:00 (regex)
            continue
        if len([c for c in line if c.isupper()]) >= len(line)/2 and ':' not in line:  # if more than half of the line is uppercase, it's probably part of a name
            if this_line is not None:
                out_lines.append(this_line + '\n')
            this_line = line + ' '
            split_name = True
        elif len(line.split(':')) >= 2:
            if split_name:  
                this_line += line
                split_name = False
            else:  # this is truly the first line of this turn
                if this_line is not None:
                    out_lines.append(this_line + '\n')  # get rid of last line
                    split_name = False
                this_line = line + ' '  # start a new line
        elif this_line is None:  # line at the beginning of the file without a speaker; disregard
            print(line)
            continue
        else:
            this_line += line + ' '
    out_lines.append(this_line)
    if fname.endswith('.txt.xml'):
        fname = fname[:-4]
    elif fname.endswith('.txt_thomass.xml'):
        fname = fname[:-12]
    elif fname.endswith('.txt'):
        fname = fname
    else:
        fname = fname + '.txt'
    with open(os.path.join(out_dir, fname), 'w') as f:
        f.writelines(out_lines)
