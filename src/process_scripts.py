from src.clean_scripts import determine_mode, consolidate_lines, titles
from collections import defaultdict
import os
import re


# mode = ':' or '.'
def get_speakers(lines, mode=':'):
    if mode == 'else':
        mode = ':'
    speaker_lines = defaultdict(lambda: [])
    for i, line in enumerate(lines):  # enumerate lines so we can order them after consolidating speakers
        splt = [token for token in line.split(mode) if token]  # speaker name; omit empty strings
        if len(splt) <= 1 or line.startswith('['):
            continue
        speaker = splt[0].split(',')[0].split('(')[0]
        speaker_lines[speaker].append((i, mode.join(splt[1:]).strip()))
    # now try to suss out which speakers (if any) are the same person
    # if speaker only has one line, that's likely someone's introductory line
    probably_introductory = [speaker for speaker in speaker_lines.keys() if len(speaker_lines[speaker])==1]
    pseudonyms = defaultdict(lambda: [])
    for speaker in probably_introductory:
        initials = [name_part[0] for name_part in speaker.split()]
        try:
            initial_regex = re.compile("".join([f"{i}\.?" for i in initials]))
        except re.error:
            probably_introductory.remove(speaker)
            del speaker_lines[speaker]
            continue
        lastname = speaker.split()[-1]
        lastname_regex = re.compile(f"({'|'.join([title[:-1] for title in titles])})?(\.)?( )?{lastname.lower()}")
        firstname = speaker.split()[0]
        # check if initials/first name/last name match another name
        for possible_pseudonym in speaker_lines.keys():
            if possible_pseudonym not in probably_introductory:
                # TODO account for multiple speakers with same last name
                if initial_regex.match(possible_pseudonym.lower()) or lastname_regex.match(possible_pseudonym.lower()):
                    pseudonyms[speaker].append(possible_pseudonym)
                if possible_pseudonym.startswith(firstname):
                    pseudonyms[speaker].append(possible_pseudonym)
    pseuds_to_speaker = {}
    for speaker in pseudonyms.keys():
        for pseud in pseudonyms[speaker]:
            pseuds_to_speaker[pseud] = speaker
    # TODO check that ppl only have one pseudonym
    out_speaker_lines = defaultdict(lambda: [])
    for speaker in speaker_lines.keys():
        if speaker in pseuds_to_speaker.keys():  # if pseudonym, add to lines attributed to full name
            out_speaker_lines[pseuds_to_speaker[speaker]].extend(speaker_lines[speaker])
            # sort lines so they're in the order they appeared in in the narrative
            out_speaker_lines[pseuds_to_speaker[speaker]] = sorted(out_speaker_lines[pseuds_to_speaker[speaker]], key=lambda x:x[0])
        else:
            out_speaker_lines[speaker].extend(speaker_lines[speaker])
    return out_speaker_lines
    

def preprocess(file):
    text = file.read().decode('utf-8')
    mode = determine_mode(text)
    lines = consolidate_lines(text, mode)
    return lines


if __name__ == '__main__':
    in_dir = '../final_project/play_scripts'
    for fname in os.listdir(in_dir):
        if fname.endswith('.txt'):
            print(fname)
            with open(os.path.join(in_dir, fname), 'r', encoding='utf-8') as f:
                text = f.read()
            mode = determine_mode(text)
            lines = text.split('\n')
            speakers = get_speakers(lines, mode)