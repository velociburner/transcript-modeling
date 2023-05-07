import os
import re


# act_regex = re.compile("(?i)act(?-i) (((I)?(V|X))|(V)?I{1,3}|X{1,3}I{0,3}[X]?)")
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
    sections = []
    current_section = []
    current_section_name = None
    section_threshold = 0  # line at the start of the current section
    subsection = False
    subsubsection = False

    def add_section(last_section, subsection, subsubsection):
        # last_section = Section(current_section_name, len(current_section), '\n'.join(current_section))
        if subsection:
            if subsubsection:
                sections[-1].subsections[-1].subsections.append(last_section)
                # subsection = False
            else:
                sections[-1].subsections.append(last_section)
                # subsection = False
        else:
            sections.append(last_section)

    for line in script:
        line = re.sub(parenthetical_regex, "", line).strip()
        if "INTRODUCTION" in line:  # INTRODUCTION
            if len(current_section) > 0:  # if this closes the previous section
                # TODO ensure previous section name is not None
                sections.append(Section(current_section_name, len(current_section), '\n'.join(current_section)))
                section_threshold += len(current_section)
                current_section = []
            current_section_name = "Introduction"
        elif "PERSONS" in line or "CHARACTER" in line:  # PERSONS/CHARACTERS = characters
            if len(current_section) > 0:  # if this closes the previous section
                # TODO ensure previous section name is not None
                sections.append(Section(current_section_name, len(current_section), '\n'.join(current_section)))
                section_threshold += len(current_section)
                current_section = []
            current_section_name = "Characters"
        # title may be repeated; still part of metadata
        # detect 'ACT'/'SCENE' (scene within act, if \exists act)
        if act_regex.match(line):
            if len(current_section) > 0:  # if this closes the previous section
                # TODO ensure previous section name is not None
                last_section = Section(current_section_name, len(current_section), '\n'.join(current_section))
                if subsection:
                    if subsubsection:
                        sections[-1].subsections[-1].subsections.append(last_section)
                        subsection = False
                    else:
                        sections[-1].subsections.append(last_section)
                        subsection = False
                else:
                    sections.append(last_section)
                section_threshold += len(current_section)
                current_section = []
            current_section_name = "Act"
        elif "SCENE" in line:
            if len(current_section) > 0:  # if this closes the previous section
                last_section = Section(current_section_name, len(current_section), '\n'.join(current_section))
                add_section()
                section_threshold += len(current_section)
                current_section = []
                if sections[-1].category == "Act":
                    subsection = True
                # add this section to act's subsections, if there is an act
                current_section_name = "Scene"
        # 'SCENE' type stuff and stage directions often in [], ()
        elif line.startswith("[") and line.endswith("]") or line.startswith("(") and line.endswith(")"):
            last_section = Section(current_section_name, len(current_section), '\n'.join(current_section))
            if subsection:
                if subsubsection:
                    sections[-1].subsections[-1].subsections.append(last_section)
                    subsection = False
                else:
                    sections[-1].subsections.append(last_section)
                    subsection = False
            else:
                sections.append(last_section)
            section_threshold += len(current_section)
            current_section = []
            subsection = True
            current_section_name = "Setting"
        # for section-detection purposes: actual script has ppl's names every couple of lines
        elif speech_regex.match(line):
            if not subsubsection:
                last_section = Section(current_section_name, len(current_section), '\n'.join(current_section))
                if subsection:
                    sections[-1].subsections.append(last_section)
                    # keep subsection True so we can add speech to subsection
                else:
                    sections.append(last_section)
            current_section_name = "Speech"
            subsubsection = True

        # prose: mostly normal-cased words
        # if more lines are of the form [A-Z]+.[whatever] than [A-Z]+:[whatever]:, "." is probably the delimiter
        # if we see no "X:Y" or "X.Y" lines, speakers and speech may be on separate lines (see alfred noyes' "rada")
        # these will have line-bigrams of the form "NAME, line", flanked by blank lines on either side
        # if () typically occurs outside of speech (e.g. "BELINDA (laughing). Yes, ma'am"), can disregard
        if len([c for c in line if c.isalphanum()]) < len(line):  # delimiter
            sections.append(Section("Metadata", len(current_section), '\n'.join(current_section)))
            section_threshold += len(current_section)
            current_section = []
    return sections


# check for number of lines of the form CAPS PUNCT NormalCase
# if there are few/none, the play is probably of the form "NAME\nLine"
def exploratory_sectioning(script):
    lines = script.split('\n')
    typical_speech_lines = [line for line in lines if speech_regex.match(line)]
    print(len(typical_speech_lines) / len(lines))
    if len(typical_speech_lines) < len(lines)/4:
        line_bigrams = [(lines[i], lines[i+1]) for i in range(len(lines) - 1)]
        contentful_bigrams = [bigram for bigram in line_bigrams if bigram[0] and bigram[1]]
        twoline_lines = [bigram for bigram in contentful_bigrams if caps_regex.match(bigram[0]) and prose_regex.match(bigram[1])]
        print(len(twoline_lines) / len(contentful_bigrams))


class Section:
    def __init__(self, category, line_span, text):
        self.category = category
        self.line_span = line_span
        self.text = text
        self.subsections = []

