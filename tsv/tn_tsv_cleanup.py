# -*- coding: utf-8 -*-
# This Python 3 script cleans up a few kinds of markdown formatting problems in column 9
# of the TSV tN files. It is only a partial solution.
# When translators alter the number of hash marks, they break the Markdown heading conventions.
# For example, the header jumps from level 1 with level 4 with no level 2 and 3 in between.
# This program intends to eliminate the jumps in heading levels by applying some
# informed guessing as to what the levels should have been. The algorithm is not perfect.
# The goal is to reduce the Errors and Warnings generated by the Door43 page builds
# while restoring the heading levels closer to their intended order.
# Correct operation of the algorithm depends on the consistency of the translator in assigning
# heading levels.
#
# This script also removes spaces before hash in each markdown line.
# Adds space after markdown header hash marks, if missing.
# Also removes double quotes that surround fields that should begin with just a markdown header.
# Fixes links of the form rc://en/...
# Untranslates SupportReference values that were mistakenly translated.
#
# This script was written for TSV notes files.
# Backs up the files being modified.
# Outputs files of the same name in the same location.

######################################################
# It is better to run this script on the source files
# before converting the files with tsv2rc.py.
######################################################

import re       # regular expression module
import io
import os
import sys
import tsv
import substitutions    # this module specifies the string substitutions to apply

# Globals
source_dir = r'C:\DCS\Kannada\TN.Dec-21\new'  # Where are the files located
language_code = 'kn'
max_files = 1     # How many files do you want to process
nProcessed = 0
filename_re = re.compile(r'.*\.tsv$')


def shortname(longpath):
    shortname = longpath
    if source_dir in longpath:
        shortname = longpath[len(source_dir)+1:]
    return shortname

# Calculates and returns the new header level.
# Updates the truelevel list.
def shuffle(truelevel, nmarks, currlevel):
    newlevel = currlevel
    if nmarks > currlevel and truelevel[nmarks] > currlevel:
        newlevel = currlevel + 1
    elif truelevel[nmarks] < currlevel:
        newlevel = truelevel[nmarks]
    
    # Adjust the array
    while nmarks > 1 and truelevel[nmarks] > newlevel:
        truelevel[nmarks] = newlevel
        nmarks -= 1
    return newlevel    

header_re = re.compile(r'(#+) ', flags=re.UNICODE)

# Converts and returns a single note
def fixHeadingLevels(note):
    currlevel = 0
    truelevel = [0,1,2,3,4,5,6,7,8,9]
    header = header_re.search(note, 0)
    while header:
        nmarks = len(header.group(1))
        newlevel = shuffle(truelevel, nmarks, currlevel)
        if newlevel != nmarks:
            note = note[0:header.start()] + '#' * newlevel + note[header.end()-1:]
        currlevel = newlevel
        header = header_re.search(note, header.start() + newlevel + 1)
    return note

hash_re = re.compile(r'#([^# \n].*)')    # missing space after #
blanklines_re = re.compile(r'[^\>]\<br\>#')     # less than two lines breaks before heading
# blankheading_re = re.compile(r'# *\<br\>')      # blank heading

# Removes space before # in markdown lines.
# Ensures at least one space after heading marks.
def fixSpacing(note):
    note = re.sub(r'\<br\> +#', "<br>#", note, 0)
    note = note.replace("# #", "##")
    while sub := hash_re.search(note):              # Add space after # where missing
        note = note[0:sub.start()] + "# " + sub.group(1)  # + u'\n'
    while sub := blanklines_re.search(note):
        note = note[0:sub.start()+1] + "<br>" + note[sub.start()+1:]

    # This was not safe because the next line might be another heading and the two headings would merge
    # while sub := blankheading_re.search(note):
        # note = note[0:sub.start()+1] + note[sub.end():]     # just remove the space(s) and <br>
    return note

# The fix applies if column 3 has more than four characters, and the row has exactly 8 columns to start.
# The fix assumes that the first four characters are valid and should have been followed by a tab.
# This output row should have 9 columns and column 3 should have four characters.
# This fixes a common problem with Gujarati and Nagamese tN files.
def fixID(row):
    if len(row) == 8 and len(row[3]) > 4:
        col4 = row[3][4:]
        row.insert(4, col4)
        row[3] = row[3][0:4]
    return row

# Makes corrections on the vernacular note field.
# Trailing spaces have already been removed.
def cleanNote(note):
    note = note.rstrip(" #[\\")
    replacement = "rc://" + language_code + "/"
    note = note.replace("rc://*/", replacement)
    note = note.replace("rc://en/", replacement)
    note = note.replace("rc://en_ta/", "rc://" + language_code + "/ta/")
    
    for pair in substitutions.subs:
        note = note.replace(pair[0], pair[1])
    note = fixSpacing(note)     # fix spacing around hash marks
    note = fixHeadingLevels(note)
    while note.endswith("<br>"):
        note = note[0:-4]
        note = note.rstrip(" #[\\")
    return note

# Combines rows that appear to be incorrectly broken.
# Where one row has 8 colummns, beginnning with the standard first column, and the next row has 1 column which is not standard.
# Coming in, the first row is headings, and the second row starts with the standard 3-character book abbreviation.
def mergeRows(data):
    nrows = len(data)
    standard = data[1][0]
    newdata = []
    newdata.append(data[0])
    i = 1
    while i < nrows - 1:
        row = data[i]
        while len(row) in {8,9} and row[0] == standard and i+1 < nrows and len(data[i+1]) == 1:
            fragment = data[i+1][0].rstrip()
            if len(fragment) > 0:
                if row[2] == "intro" and not row[-1].endswith('#'):   # intro rows have multiple "lines" and markdown syntax
                    row[-1] += "<br>"
                else:
                    row[-1] += " "
                row[-1] += fragment
            i += 1
        newdata.append(row)
        i += 1
    if i < nrows:
        newdata.append(data[i])
    return newdata

# Strips leading/trailing quotes and spaces from each column value in the row.
# Detects and repairs a few common ways in which one column is missing from the row.
# Makes a few fixes to the note column using cleanNote().
def cleanRow(row):
    i = 0
    while i < len(row):
        str = row[i].strip(' ')     # remove leading and trailing spaces  
        if len(str) > 0 and str[0] == '"' and str[-1] == '"':
            str = str[1:-1]
        row[i] = str
        i += 1
    if len(row) == 8:
        if len(row[3]) > 4: # A common problem, where the ID column is merged with the next column.
            row = fixID(row)
        elif not row[4].isascii():   # another common problem where the SupportReference column is omitted
            row.insert(4, "")
        elif len(row[4]) == 0 and row[5] in {'0','1'}:
            row.insert(4, "")
    if len(row) == 10 and row[9].strip() == "":
        row = row[0:9]
    if len(row) == 9:
        row[8] = cleanNote(row[8])
        row[4] = cleanSupportRef(row[4], row[8])
    return row

tapage_re = re.compile(r'\[\[.*?/ta/man/[\w]+/(.*?)]]', flags=re.UNICODE)

# Translates the value to the last tA article name in the note, if the value is non-ascii to begin with
def cleanSupportRef(value, note):
    if not value.isascii():
        if talink := tapage_re.search(note):
            value = talink.group(1)
    return value        

# Returns a value to be used in sorting the row
def rowValue(row):
    if row[0] == "Book":
        value = -1
    else:
        if row[1] == "front":
            value = 0
        else:
            value = 1000 * int(row[1])
        if row[2] != "intro":
            value += int(row[2])
    return value

def cleanFile(folder, fname):
    path = os.path.join(folder, fname)
    sys.stdout.write(shortname(path) + '\n')
    sys.stdout.flush()
    data = tsv.tsvRead(path)  # The entire file is returned as a list of lists of strings (rows); each row is a list of strings.

    if len(data) > 2 and data[0][0] == "Book" and len(data[1][0]) == 3:
        origdata = mergeRows(data)
    data = []
    for row in origdata:
        if len(row) > 1:
            row = cleanRow(row)
        data.append(row)
    data.sort(key=rowValue)

    bakpath = path.replace(".tsv", ".tsvorig")
    if not os.path.isfile(bakpath):
        os.rename(path, bakpath)
    if fname.startswith("en_"):
        path = os.path.join(folder, language_code + fname[2:])
    tsv.tsvWrite(data, path)

# Recursive routine to convert all files under the specified folder
def cleanFolder(folder):
    global nProcessed
    global max_files
    if nProcessed >= max_files:
        return
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        if os.path.isdir(path) and entry[0] != '.':
            cleanFolder(path)
        elif filename_re.match(entry):
            cleanFile(folder, entry)
            nProcessed += 1
        if nProcessed >= max_files:
            break

# Processes all .txt files in specified directory, one at a time
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != 'hard-coded-path':
        source_dir = sys.argv[1]

    if source_dir and os.path.isdir(source_dir):
        cleanFolder(source_dir)
        sys.stdout.write("Done. Processed " + str(nProcessed) + " files.\n")
    elif filename_re.match(source_dir) and os.path.isfile(source_dir):
        path = source_dir
        source_dir = os.path.dirname(path)
        cleanFile(source_dir, os.path.basename(path))
        sys.stdout.write("Done. Processed 1 file.\n")
    else:
        sys.stderr.write("Usage: python tsv_cleanup.py <folder>\n  Use . for current folder.\n")
