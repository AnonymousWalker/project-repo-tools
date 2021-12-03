# -*- coding: utf-8 -*-
# In many Markdown files, the translators alter the number of hash marks, not realizing
# that by doing so they break the Markdown heading scheme.
# For example, the header jump from level 1 with level 4 with no level 2 and 3 in between.
# Or some files start out with a level 2 header.
# This program intends to eliminate the jumps in heading levels by applying some
# informed guessing as to what the levels should have been. The algorithm is not perfect.
# The goal is to reduce the Errors and Warnings generated by the Door43 page builds
# while restoring the heading levels closer to their intended order.
# The program promotes the first heading found to a level 1,
#   and normalizes the subsequent heading levels.
# The success of the algorithm is affected by the consistency of the translator in assigning
# the original heading levels.
# All the above program behavior is optional. Set suppress1 if you don't want it.
#
# Backs up the files being modified.
# Outputs files of the same name in the same location.
#
# Additional behavior:
#   Converts malformed heading marks "# #"
#   Removes blank lines between markdown list items.
#   Assures blank links before and after header lines.
#   Leading spaces before the asterisk are also removed.
#   Assures newline at the end of the file.
#   Removes gratutious formatting asterisks from header lines.
#
# Also expands incomplete references to tA articles.
# For example, expands Vidi: figs_metaphor to Vidi: [[rc://*/ta/man/translate/figs-metaphor]]

import re       # regular expression module
import io
import os
import string
import sys
from filecmp import cmp
import codecs

# Globals
source_dir = r'C:\DCS\Hindi\TA'
language_code = 'hi'
resource_type = 'ta'
server = 'DCS'     # DCS or WACS

nChanged = 0
max_files = 44444

placeholder_heading = ""
import substitutions    # change substitutions modules as necessary; generic one is just "substitutions"

suppress1 = False       # Suppress hash mark cleanup
suppress2 = True       # Suppress stdout informational messages 
suppress3 = False       # Suppress addition of blank lines after lists and removal of blank lines between list items
suppress4 = False       # Suppress addition of blank lines before lists. (should suppress for newer DCS resources)
if resource_type == 'ta':
    suppress1 = True

filename_re = re.compile(r'.*\.md$')
current_dir = ""
if resource_type == 'obs':
    filename_re = re.compile(r'\d+\.md$')

def shortname(longpath):
    shortname = longpath
    if source_dir in longpath:
        shortname = longpath[len(source_dir)+1:]
    return shortname

olistitem_re = re.compile(r'(\n[^#\n]*)\n+[ ]*?([1-6][\.\)] )', re.UNICODE)

# Applies to tN and tQ
# Folds ordered lists onto a single line
# Returns the fixed string.
def foldLists(alltext):
    found = olistitem_re.search(alltext)
    while found:
        alltext = alltext[:found.start()] + found.group(1) + " " + found.group(2) + alltext[found.end():]
        found = olistitem_re.search(alltext)
    return alltext

listinterrupt_re = re.compile('(\n *\* .*)\n(\n *\* )', flags=re.UNICODE)    # two list items with blank line between
listinterrupt2_re = re.compile('(\n *1\. .*)\n(\n *1\. )', flags=re.UNICODE)    # two ordered list items with blank line between
listOffset_re = re.compile(r'^ *[^\*1\n ][^\n]*\n *[\*1][\. ]', flags=re.UNICODE+re.MULTILINE)  # text line followed by list item
listOffset2_re = re.compile(r'^[\*] .*\n *[^\n\*1 ]', flags=re.UNICODE+re.MULTILINE)  # last list item not followed by blank line
ordered_re = re.compile(r'\n1\.[^ \n]')

# Applies to resource types other than tN and tQ
# Removes blank lines between list items.
# Ensures blank line before list items.
# Supplies missing space after ordered list item (1.)
# Multiple replacements per file
def fixLists(alltext):
    # The markdown dialect that DCS supports allows blank lines between list items.
    if not suppress3:
        found = listinterrupt_re.search(alltext)
        while found:        # remove blank lines between list items
            alltext = alltext[0:found.start()] + found.group(1) + found.group(2) + alltext[found.end():]
            found = listinterrupt_re.search(alltext)
        found = listinterrupt2_re.search(alltext)
        while found:        # remove blank lines between ordered list items
            alltext = alltext[0:found.start()] + found.group(1) + found.group(2) + alltext[found.end():]
            found = listinterrupt2_re.search(alltext)

        found = listOffset2_re.search(alltext)
        while found:        # add blank line after end of list
            alltext = alltext[0:found.end()-1] + '\n' + alltext[found.end()-1:]
            found = listOffset2_re.search(alltext)

    if not suppress4:
         found = listOffset_re.search(alltext)
         while found:
             alltext = alltext[0:found.end()-2] + '\n' + alltext[found.end()-2:]
             found = listOffset_re.search(alltext)

    # Change "1.foo" to "1. foo"
    found = ordered_re.search(alltext)
    while found:
        alltext = alltext[:found.start()+3] + ' ' + alltext[found.end()-1:]
        found = ordered_re.search(alltext)
    return alltext

# Calculates and returns the new header level.
# Updates the truelevel list.
def shuffle(truelevel, nmarks, currlevel):
    newlevel = currlevel
    if nmarks > len(truelevel) - 1:     # happens on lines with a lot of gratuitous ##### ## ## ## ##
        nmarks = len(truelevel) - 1
    if nmarks > currlevel and truelevel[nmarks] > currlevel:
        newlevel = currlevel + 1
    elif truelevel[nmarks] < currlevel:
        newlevel = truelevel[nmarks]
    
    # Adjust the array
    while nmarks > 1 and truelevel[nmarks] > newlevel:
        truelevel[nmarks] = newlevel
        nmarks -= 1
    return newlevel    

hash_re = re.compile(r' *(#+) +', flags=re.UNICODE)

# Removes asterisks from heading lines
def fixHeadingFormats(str):
    nChanges = 0
    text = ""
    lines = str.splitlines()
    for line in lines:
        header = hash_re.match(line, 0)
        if header:
            line = line.replace("*", "")
        text += line + '\n'
    return text

    # Normalizes markdown heading levels.
# Removes training blanks from header lines.
def fixHeadingLevels(str):
    nChanges = 0
    text = ""
    lines = str.splitlines()
    currlevel = 0
    truelevel = [0,1,2,3,4,5,6,7,8,9]
        # each position in the array represents the calculate true header level for that number of hash marks.
        # To start, the number of hash marks is assumed to be the true level.
        # This array is modified by the shuffle() function.

    for line in lines:
        header = hash_re.match(line, 0)
        if header:
            nmarks = len(header.group(1))
            newlevel = shuffle(truelevel, nmarks, currlevel)
            if newlevel != nmarks:
                line = '#' * newlevel + ' ' + line[header.end():]
                nChanges += 1
            currlevel = newlevel
        text += line.rstrip() + '\n'
    return text

validlink_re = re.compile(r'/([0-9][0-9])\.md$')

# Tries to modify an invalid link by decrementing the verse number
def verse2chunk(link):
    if goodlink := validlink_re.search(link):
        global current_dir
        referencedPath = os.path.join(current_dir, link)
        if not os.path.isfile(referencedPath):
            verse = int(goodlink.group(1))
            newlink = link[:goodlink.start()+1] + '{:02g}'.format(verse-1) + ".md"
            referencedPath = os.path.join(current_dir, newlink)
            if os.path.isfile(referencedPath):
                link = newlink
    return link

missingslash_re = re.compile(r'\.[0-9]')
missingdot_re = re.compile(r'[0-9/]md')
missingzero_re = re.compile(r'/[1-9][/\.]')

# Do surgery on the specified link
def fixMdLink(link):
    link =  link.replace(" ", "")   # remove spaces
    link =  link.replace("...", "..")
    link =  link.replace("///", "/")
    link =  link.replace("//", "/")
    link = link.lower()
    link =  link.replace("/md", ".md")
    link =  link.replace("..md", ".md")
    if miss := missingslash_re.search(link):
        link = link[:miss.start()+1] + "/" + link[miss.start()+1:]
    if miss := missingdot_re.search(link):
        link = link[:miss.start()+1] + "." + link[miss.start()+1:]
    if miss := missingzero_re.search(link):
        link = link[:miss.start()+1] + "0" + link[miss.start()+1:]
    # proper levels
    pos1 = link.rfind("./")
    if pos1 < 0:
        pos1 = 0
    nslash = link[pos1:].count("/")
    if nslash > 1 and link.startswith("./"):
        link = "." + link
    elif nslash == 1 and link.startswith(".."):
        link = link[1:]
    link = link.replace("/./", "/../")
    link = link.replace("/.md", ".md")
    link = verse2chunk(link)
    return link

mdlink_re = re.compile(r'\(([\.a-zA-Z0-9/ ]+[0-9/ ]+\.? ?[mM][dD] ?)(\).*)', flags=re.UNICODE+re.DOTALL)

# Make various corrections to md file references
def fixMdLinks(str):
    newstr = ""
    mdlink = mdlink_re.search(str)     # (../../luk/10/20.md)
    while mdlink:
        link = fixMdLink(mdlink.group(1))
        newstr += str[0:mdlink.start()+1] + link
        str = mdlink.group(2)
        mdlink = mdlink_re.search(str)
    newstr += str
    return newstr

inlinekey = []      # These are the strings that are actually replaced
#inlinekey.append( re.compile(r'[：\:\(/ ]figs_(\w*)', flags=re.UNICODE) )
#inlinekey.append( re.compile(r'[：\:\(/ ]translate_(\w*)', flags=re.UNICODE) )
#inlinekey.append( re.compile(r'[：\:\(/ ]writing_(\w*)', flags=re.UNICODE) )
#inlinekey.append( re.compile(r'[：\:\(/ ]guidelines_(\w*)', flags=re.UNICODE) )
#inlinekey.append( re.compile(r'[：\:\(/ ]bita_(\w*)', flags=re.UNICODE) )
inlinekey.append( re.compile(r'figs_(\w*)', flags=re.UNICODE) )
inlinekey.append( re.compile(r'translate_(\w*)', flags=re.UNICODE) )
inlinekey.append( re.compile(r'writing_(\w*)', flags=re.UNICODE) )
inlinekey.append( re.compile(r'guidelines_(\w*)', flags=re.UNICODE) )
inlinekey.append( re.compile(r'bita_(\w*)', flags=re.UNICODE) )
newstring = []
newstring.append( 'figs-' )
newstring.append( 'translate-' )
newstring.append( 'writing-' )
newstring.append( 'guidelines-' )
newstring.append( 'bita-' )

# Replaces primitive tA links (those that match something in inlinekey[])
def fixTaLinks(str):
    text = ""
    count = 0
    lines = str.splitlines()
    for line in lines:
        count += 1
        if not "://ufw.io/" in line:
            for i in range(len(inlinekey)):
                good_ref = ' [[rc://*/ta/man/translate/' + newstring[i]
                sub = inlinekey[i].search(line)
                while sub:
                    line = line[0:sub.start()] + good_ref + sub.group(1) + ']]' + line[sub.end():]
                    sub = inlinekey[i].search(line)
        text += line + '\n'
    return text
    
tnlink_re = re.compile(r'(rc://[ \*\w\-]+/tn/help/)(\w\w\w/\d+)/(\d+)', flags=re.UNICODE)

# Note links currently are not rendered on live site as links.
def fixTnLinks(str):
    newstr = ""
    notelink = tnlink_re.search(str)     # rc://.../tn/help/...
    while notelink:
        chunkmd = notelink.group(3)
        if len(chunkmd) == 1:
            chunkmd = "0" + chunkmd
        if notelink.group(2).startswith("psa") and len(chunkmd) == 2:
            chunkmd = "0" + chunkmd
        newstr += str[0:notelink.start()] + notelink.group(1) + notelink.group(2) + "/" + chunkmd
        str = str[notelink.end():]
        notelink = tnlink_re.search(str)
    newstr += str
    return newstr

def getChapterNumber(str):
    try:
        chapno = int(str)
    except ValueError as e:
        chapno = 0
    return chapno     
    
reflink_re = re.compile(r'\[+rc://[\*\w]+/bible/notes/(\w\w\w)/(\d+)/(\d+)\]+', flags=re.UNICODE)     # very old style bible/notes links

def fixRefLinks(path, str):
    chappath = os.path.dirname(path)
    mychap = getChapterNumber(os.path.basename(chappath))
    bookpath = os.path.dirname(chappath)
    mybook = os.path.basename(bookpath)
    newstr = ""
    reflink = reflink_re.search(str)   # rc://*/bible/notes/...
    while reflink:
        chunk = reflink.group(3)
        chap = reflink.group(2)
        book = reflink.group(1)
        newstr += str[0:reflink.start()] + "[" + book.upper() + " " + chap.lstrip('0') + ":" + chunk.lstrip('0') + "]"
        if book.lower() == mybook.lower():
            if getChapterNumber(chap) == mychap:
                newstr += "(./"
            else:
                newstr += "(../" + chap + "/"
        else:
            newstr += "../../" + book + "/" + chap + "/"
        newstr += chunk + ".md)"
        str = str[reflink.end():]
        reflink = reflink_re.search(str)
    newstr += str
    return newstr

blanks_re = re.compile('[\n \t]+')     # multiple newlines/ white space at beginning of string
hashblanks_re = re.compile('#  +')      # multiple spaces after hash mark
endblank_re = re.compile('[\n \t][\n \t]+\Z')     # multiple newlines/ white space at end of string
jams_re = re.compile(r'^#+[^ \t#]', re.UNICODE+re.MULTILINE)    # hash(es) at beginning of line not followed by space
multihash_re = re.compile(r'^[^\>\n#][^\n\\#]* #', re.UNICODE+re.MULTILINE)  # hash mark in the middle of a line that is not in a blockquote and IS preceded by a space
percenthash_re = re.compile(r'\n% ', re.UNICODE+re.MULTILINE)   # % symbol was once used to mark a H2 heading at beginning of a line but not at the beginning of a file (verify each time)
office_re = re.compile(r'<o\:p[^>\n]*?>', re.UNICODE)     # nasty MS Office codes
bibleq_re = re.compile(r'\[+rc:.*?bible[ /\:]+quest.*?\]+', flags=re.UNICODE)     # obsolete bible/questions links
reversedlink_re = re.compile(r'\)[ ]*?\[')
brokebracket = re.compile(r'(\[[^]]*?)[ \n]+\]', re.MULTILINE)

# Does some simple cleanup operations before starting the heavy conversions.
def preliminary_cleanup(text):
    if resource_type != 'ta':
        if found := blanks_re.match(text):
            text = text[found.end():] + '\n'    # remove blanks at beginning of string
    if found := endblank_re.search(text):
        text = text[0:found.start()] + '\n'     # remove blank lines at end of string
    text = text.replace("# #", "##")
    found = jams_re.search(text)
    while found:
        text = text[:found.end()-1] + ' ' + text[found.end()-1:]    # add space after hash mark(s) at beginning of lines
        found = jams_re.search(text)
    found = multihash_re.search(text)      # Hash group starting in the middle of a line
    while found:
        pos = found.start()
        text = text[:found.end()-1] + "\n\n" + text[found.end()-1:]
        found = multihash_re.search(text)

    text = re.sub(percenthash_re, "\n## ", text)
    text = re.sub(hashblanks_re, "# ", text)
    text = re.sub(office_re, "", text)
    text = re.sub(bibleq_re, "", text)
    text = re.sub(reversedlink_re, "), [", text)
    
    found = brokebracket.search(text)
    while found:
        text = text[:found.start()] + found.group(1) + text[found.end()-1:]
        found = brokebracket.search(text)

    return text

# Applies the substitutions found in substitutions.py, plus two that are language specific
def substitution(text):
    if language_code != 'en':
#        fromstr = "rc://" + language_code + "/"
#        text = text.replace(fromstr, "rc://*/")
#        fromstr = "rc://" + language_code + " /"
#        text = text.replace(fromstr, "rc://*/")
        substitutions.subs.append(	("rc://" + language_code + "/", "rc://*/") )
        substitutions.subs.append(	("rc://" + language_code + " /", "rc://*/") )
        substitutions.subs.append(	("rc:// " + language_code + "/", "rc://*/") )
        substitutions.subs.append(	("rc://en/", "rc://*/") )

    for pair in substitutions.subs:
        text = text.replace(pair[0], pair[1])
    return text

keystring = []      # These strings are searched to determine files that are candidates for change
keystring.append( re.compile(r'figs_', flags=re.UNICODE) )
keystring.append( re.compile(r'translate_', flags=re.UNICODE) )
keystring.append( re.compile(r'writing_', flags=re.UNICODE) )
keystring.append( re.compile(r'guidelines_', flags=re.UNICODE) )
keystring.append( re.compile(r'bita_', flags=re.UNICODE) )
extraBlankHeading_re = re.compile(r'^#+ *\n+(#+ +[\w\d])', flags=re.UNICODE+re.MULTILINE)

# Reads the entire source file as a string and converts it.
# If any change, writes target file.
def convertWholeFile(source, target):
    global suppress1
    fixHeadings = not suppress1
    input = io.open(source, "tr", encoding="utf-8-sig")
    text = input.read()
    input.close()
    nLeftParens = text.count("(")
    nRightParens = text.count(")")

    origtext = text
    text = substitution(text)   # Need to substitute HTML strings containing hash marks before doing header cleanup
    text = preliminary_cleanup(text)
    if source.endswith("title.md"):
        text = text.rstrip(" \n")   # lose trailing newline from title.md and sub-title.md files
    elif not text.endswith("\n"):
        text += "\n"            # ensure trailing newline in all other files
    
    if not text.startswith("# "):
        if not suppress2:
            sys.stdout.write(shortname(source) + " does not begin with level 1 heading, so no headings will be touched.\n")
        fixHeadings = False

    # Do the hash level fixes and TA references
    if not source.endswith("title.md"):
        if fixHeadings and "## " in text:
            text = fixHeadingLevels(text)
        text = fixHeadingFormats(text)

    if resource_type in {'tn','tq'} and "intro.md" not in source and server == 'DCS':
        text = foldLists(text)
    if resource_type not in {'tn','tq'} or server == 'WACS':
        text = fixLists(text)

    # Expand the TA links
    convertme = False
    for key in keystring:
        if key.search(text):
            convertme = True
            break
    if convertme:
        text = fixTaLinks(text)
    text = fixTnLinks(text)
    text = fixMdLinks(text)
    text = fixRefLinks(source, text)

    if ebh := extraBlankHeading_re.search(text):
        text = text[:ebh.start()] + ebh.group(1) + text[ebh.end():]
    
    changed = (text != origtext)
    if changed:
        if len(text) < 3:
            sys.stderr.write("Empty or almost empty file: " + shortname(source) + '\n')
#        elif len(origtext) - len(text) > 4 and len(text) < len(origtext) * 0.95:
#            sys.stderr.write("Error processing (>5% size reduction): " + shortname(source) + '\n')
#            changed = False
    if changed:
        output = io.open(target, "tw", encoding='utf-8', newline='\n')
        output.write(text)
        output.close()

paren_re = re.compile(r'[^)]\)$', re.UNICODE)   # ends with single but not double right paren

# Returns line with some corrections made
def cleanupLine(line):
    line = line.rstrip("\n\t \[\(\{")
    line = line.lstrip("\]\)\}")
    nBoldmarks = line.count("**")
    if nBoldmarks == 1 and line.count("*") % 2 == 0:   # orphaned '**' is a common error
        line = line.replace("**", "")
    elif nBoldmarks > 1 and nBoldmarks % 2 == 0:
        boldpos = line.find("**")      # finds the first ** in the line
        while boldpos >= 0:
            if line.find("** ", boldpos) == boldpos:      # the first ** is followed by a space
                line = line[:boldpos+2] + line[boldpos+3:]
            boldpos = line.find("**", boldpos+2)    # find the next ** in the line
            if boldpos > 0 and line[boldpos-1] == ' ':
                line = line[:boldpos-1] + line[boldpos:]
            boldpos = line.find("**", boldpos+2)    # finds the start of the next ** pair
    if line.count('(') > line.count(')') and paren_re.search(line):
        line += ')'
    return line

blankheading_re = re.compile(r'#+$')
listjam_re = re.compile(r'( *\*)([^\* ][^\*]+)$', re.UNICODE)     # asterisk not followed by space or another asterisk
tripleasterisk_re = re.compile(r'( *)\*\*\*([^\*]+\*\*.*)', re.UNICODE)     # line starts with triple asterisk and there is a double asterisk later in line

# Adds blank lines where needed before and after heading lines
# Supply placeholder heading if needed.
# Always writes target file, even if no changes.
def convertByLine(source, target):
    input = io.open(source, "tr", 1, encoding="utf-8-sig")
    lines = input.readlines()
    input.close()

    BLANK = 0       # blank line or top of file
    HEADER = 1
    TEXT = 2
    linetype = BLANK
    output = io.open(target, "tw", buffering=1, encoding='utf-8', newline='\n')
    for line in lines:
        line = cleanupLine(line)    # strips some whitespace, bad brackets, orphan **, and doubles right paren when needed
        prevlinetype = linetype
        if len(line) == 0:
            linetype = BLANK
        elif line[0] == '#':
            linetype = HEADER
            if blankheading_re.match(line) and len(placeholder_heading) > 0:
                line += " " + placeholder_heading
        else:
            linetype = TEXT
            if found := listjam_re.match(line):
                line = found.group(1) + " " + found.group(2)
            if found := tripleasterisk_re.match(line):
                line = found.group(1) + "* **" + found.group(2)
        if (linetype == HEADER and prevlinetype != BLANK) or (linetype == TEXT and prevlinetype == HEADER):
            output.write('\n')
        if not (linetype == BLANK and prevlinetype == BLANK):
            output.write(line + '\n')
    output.close

# Rewrites path without BOM if file has a UTF-8 Byte Order Mark.
# Backs up path to path.orig if any change and if path.orig does not already exist.
def removeBOM(path):
    bytes_to_remove = 0
    MAX = 60
    with open(path, 'rb') as f:
        raw = f.read(MAX + 3)
        while raw[bytes_to_remove:bytes_to_remove+3] == codecs.BOM_UTF8 and bytes_to_remove < MAX:
            bytes_to_remove += 3
        if bytes_to_remove > 0:
            f.seek(bytes_to_remove)
            raw = f.read()
    if bytes_to_remove > 0:
        bakpath = path + ".orig"
        if not os.path.isfile(bakpath):
            os.rename(path, bakpath)
        with open(path, 'wb') as f:
            f.write(raw)       

def convertFile(path):
    tmppath = path + ".tmp"
    convertWholeFile(path, tmppath)
    if not os.path.isfile(tmppath):
        tmppath = path
    if not path.endswith("title.md"):       # No further conversion is wanted for these one-line files
        tmppath2 = path + ".tmp2"
        convertByLine(tmppath, tmppath2)
    else:
        tmppath2 = tmppath
    changed = not cmp(tmppath2, path, shallow=False)
    if changed:
        global nChanged
        nChanged += 1
        sys.stdout.write("Converted " + shortname(path) + "\n")
        bakpath = path + ".orig"
        if not os.path.isfile(bakpath):
            os.rename(path, bakpath)
        else:
            os.remove(path)
        os.rename(tmppath2, path)
    if not changed and tmppath2 != path:
        os.remove(tmppath2)
    if tmppath != path and os.path.isfile(tmppath):
        os.remove(tmppath)
    removeBOM(path)

# Recursive routine to convert all files under the specified folder
def convertFolder(folder):
    global nChanged
    global max_files
    global current_dir
    current_dir = folder
    if nChanged >= max_files:
        return
    sys.stdout.write("Processing " + shortname(folder) + "\n")
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        if os.path.isdir(path) and entry[0] != '.':
            convertFolder(path)
        elif filename_re.match(entry) and not entry.startswith("LICENSE"):
            convertFile(path)
        if nChanged >= max_files:
            break
    sys.stdout.flush()

if __name__ == "__main__":
    if resource_type == 'tq':
        placeholder_heading = "??"
    elif resource_type == 'tn':
        placeholder_heading = "(note title)"

    if len(sys.argv) > 1 and sys.argv[1] != 'hard-coded-path':
        source_dir = sys.argv[1]

    if source_dir and os.path.isdir(source_dir):
        convertFolder(source_dir)
        sys.stdout.write("Done. Changed " + str(nChanged) + " files.\n")
    elif os.path.isfile(source_dir):
        path = source_dir
        source_dir = os.path.dirname(path)
        current_dir = source_dir
        convertFile(path)
        sys.stdout.write("Done. Changed " + str(nChanged) + " files.\n")
    else:
        sys.stderr.write("Usage: python md_cleanup.py <folder>\n  Use . for current folder or hard code the path.\n")
