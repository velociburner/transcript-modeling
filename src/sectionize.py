from collections import defaultdict
import os
import re


act_regex = re.compile("act (\d*|(x?((i)?(v|x))|(v)?i{1,3}|x{1,3}i{0,3}[x]?))")
scene_regex = re.compile("scene (\d*|(x?((i)?(v|x))|(v)?i{1,3}|x{1,3}i{0,3}[x]?))")
speech_regex = re.compile("[A-Z]+(\.|:)( )?(([A-Z]?[a-z]+|,|'|\.|\?|\!)| )+")
parenthetical_regex = re.compile("\(.+\)")
caps_regex = re.compile("[A-Z]+(\.|:)?")
prose_regex = re.compile("(([A-Z]?[a-z]+|,|'|\.|\?|!)| )+")


# sectionize a play or screenplay-type script (for theatre, TV, movies, ...)
def sectionize_play(script):
    # title, author, etc.
    # if title is preceded by "TITLE" or something similar, extract it
    # "START OF THIS _" = start of relevant material; before = metadata
    # line of just punctuation: probably a delimiter
    # prose: mostly normal-cased words
    # if more lines are of the form [A-Z]+.[whatever] than [A-Z]+:[whatever]:, "." is probably the delimiter
    # if we see no "X:Y" or "X.Y" lines, speakers and speech may be on separate lines (see alfred noyes' "rada")
    # these will have line-bigrams of the form "NAME, line", flanked by blank lines on either side
    # if () typically occurs outside of speech (e.g. "BELINDA (laughing). Yes, ma'am"), can disregard
    
    sections = []
    current_section = []
    current_section_name = None
    subsection = False
    subsubsection = False

    def add_section(last_section, subsection, subsubsection):
        if subsection:
            if subsubsection:
                sections[-1].subsections[-1].subsections.append(last_section)
            else:
                sections[-1].subsections.append(last_section)
        else:
            sections.append(last_section)
        return sections

    lines = script.split('\n')
    section_start = 0
    for line in lines:
        line = re.sub(parenthetical_regex, "", line).strip()
        # for section-detection purposes: actual script has ppl's names every couple of lines
        if speech_regex.match(line):
            if len(current_section) > 0 and current_section_name != "Speech":
                last_section = Section(current_section_name, section_start, section_start + len(current_section), '\n'.join(current_section))
                sections = add_section(last_section, subsection, subsubsection)
                current_section = []
                if current_section_name == 'Act' or current_section_name == 'Scene':
                    subsubsection = subsection
                    subsection = True
            current_section_name = "Speech"
            current_section.append(line)
        elif "persons" in line.lower() or "character" in line.lower() or 'personae' in line.lower():  # PERSONS/CHARACTERS = characters
            if len(current_section) > 0 and current_section_name != "Characters":  # if this closes the previous section
                last_section = Section(current_section_name, section_start, section_start + len(current_section), '\n'.join(current_section))
                sections = add_section(last_section, subsection, subsubsection)
                section_start += len(current_section)
                current_section = []
            current_section_name = "Characters"
            current_section.append(line)
        # title may be repeated; still part of metadata
        # detect 'ACT'/'SCENE' (scene goes within act, if \exists act)
        # 'SCENE' type stuff and stage directions often in [], ()
        elif "scene" in line.lower():
            if len(current_section) > 0 and current_section_name != "Scene":  # if this closes the previous section
                last_section = Section(current_section_name, section_start, section_start + len(current_section), '\n'.join(current_section))
                sections = add_section(last_section, subsection, subsubsection)
                section_start += len(current_section)
                current_section = []
                if sections[-1].category == "Act":
                    subsubsection = False
                    subsection = True
                if sections[-1].category == 'Scene':
                    subsubsection = False
                    subsection = False
                # add this section to act's subsections, if there is an act
            current_section_name = "Scene"
            current_section.append(line)
        elif act_regex.match(line.lower()):
            if len(current_section) > 0 and current_section_name != "Act":  # if this closes the previous section
                last_section = Section(current_section_name, section_start, section_start + len(current_section), '\n'.join(current_section))
                sections = add_section(last_section, subsection, subsubsection)
                section_start += len(current_section)
                current_section = []
                subsection = False
                subsubsection = False
            current_section_name = "Act"
            current_section.append(line)
        elif 'introduction' in line.lower():
            if len(current_section) > 0 and current_section_name != "Introduction":  # if this closes the previous section
                last_section = Section(current_section_name, section_start, section_start + len(current_section), '\n'.join(current_section))
                sections = add_section(last_section, subsection, subsubsection)
                section_start += len(current_section)
                current_section = []
            current_section_name = "Introduction"
            current_section.append(line)
        elif 'prologue' in line.lower():
            if len(current_section) > 0 and current_section_name != "Prologue":  # if this closes the previous section
                last_section = Section(current_section_name, section_start, section_start + len(current_section), '\n'.join(current_section))
                sections = add_section(last_section, subsection, subsubsection)
                section_start += len(current_section)
                current_section = []
            current_section_name = "Prologue"
            current_section.append(line)
        # TODO do the following if line's first real word is "enter" or "exit"
        elif line.startswith("[") and line.endswith("]") or line.startswith("(") and line.endswith(")") or line.startswith('_') and line.endswith('_'):
            if len(current_section) > 0 and current_section_name != "Setting":  # if this closes the previous section
                last_section = Section(current_section_name, section_start, section_start + len(current_section), '\n'.join(current_section))
                sections = add_section(last_section, subsection, subsubsection)
                section_start += len(current_section)
                current_section = []
                subsection = True
            current_section_name = "Setting"
            current_section.append(line)
        elif len([c for c in line if c.isalnum()]) < len(line):  # delimiter
            if len(current_section) > 0 and current_section_name != "Metadata":  # if this closes the previous section
                last_section = Section(current_section_name, section_start, section_start + len(current_section), '\n'.join(current_section))
                sections = add_section(last_section, subsection, subsubsection)            
                section_start += len(current_section)
                current_section = []
                if current_section_name == 'Act' or current_section_name == 'Scene':
                    subsubsection = subsection
                    subsection = True
            current_section_name = "Metadata"
            current_section.append(line)
   
    # consolidate duplicate sections
    out_sections = []
    last_section = sections[0]
    # TODO if there's a few speech/meta sections in a row, group hhem together
    for i in range(1, len(sections)):
        if sections[i].category == last_section.category:
            if sections[i].category not in ['Act', 'Scene']:  # it's ok for these to appear consecutively
                last_section = Section(last_section.category, last_section.start, sections[i].end, last_section.subsections + sections[i].subsections)
        else:
            out_sections.append(last_section)
            last_section = sections[i]
    out_sections.append(last_section)
    for section in sections:
        if len(section.subsections) > 0:
            for subsection in section.subsections:
                if len(subsection.subsections) > 0:
                    subsection.end = subsection.subsections[-1].end
            if len(section.subsections) > 0:
                section.end = section.subsections[-1].end

    return out_sections


class Section:
    def __init__(self, category, start, end, text):
        self.category = category
        self.start = start
        self.end = end
        self.text = text
        self.subsections = []


if __name__ == '__main__':
    in_dir = '../final_project/play_scripts'
    for fname in os.listdir(in_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(in_dir, fname), 'r', encoding='utf-8') as f:
                text = f.read()
            sectionize_play(text)