# -*- coding: utf-8 -*-

# Script for verifying proper Markdown format and links. Should check the following:
# Remove empty .md files.
# Blank line before and after header lines.
# Single space after hash on header line.
# No closed headers.
# Standard format of ordered lists (lists whose items are arranged on separate lines)
#      blank lines before and after list
#      period not paren after the number
#      space after period
# References are properly formed: [[rc://ur-deva/ta/man/translate/figs-hyperbole]]
# References in headings (warning)
# References to tA entries are valid.

# Globals
language_code = u'id'
resource_type = 'tq'
ta_dir = r'C:\DCS\English\en_ta'    # English tA
obs_dir = r'C:\DCS\English\en_obs\content'   # Target language OBS content folder, needed if OBS links are to be checked
# tn_dir = r'C:\DCS\Kannada\kn_tn'    # Target language tN, needed if note links are to be checked
nChecked = 0

suppress1 = False    # Suppress warnings about text before first heading
suppress2 = False    # Suppress warnings about blank headings
suppress3 = False    # Suppress warnings about no period after numbers at start of line
suppress4 = False    # Suppress warnings about closed headings
suppress5 = False    # Suppress warnings about invalid passage links (needed for OBS)
suppress6 = False    # Suppress warnings about invalid OBS links
suppress7 = False    # Suppress warnings about file starting with blank line
suppress8 = False    # Suppress warnings about invalid list style
if resource_type == "ta":
    suppress1 = True
    suppress7 = True
    suppress8 = True

# Markdown line types
HEADING = 1
BLANKLINE = 2
TEXT = 3
LIST_ITEM = 4
ORDEREDLIST_ITEM = 5

import sys
import os

# Set Path for files in support/
# rootdiroftools = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(rootdiroftools,'support'))

import io
import codecs
import re

listitem_re = re.compile(r'[ \t]*[\*\-][ \t]')
olistitem_re = re.compile(r'[ \t]*[0-9]+\. ')
badolistitem_re = re.compile(r'[ \t]*[0-9]+[\)]')
badheading_re = re.compile(r' +#')

class State:
    path = ""
    linecount = 0  
    headingcount = 0
    headinglevel = 0
    linetype = []
    # prevlinetype = None
    currlinetype = None
        
    def setPath(self, path):
        State.path = path
        State.linecount = 0
        State.headingcount = 0
        State.prevheadinglevel = 0
        State.currheadinglevel = 0
        State.prevlinetype = None
        State.currlinetype = None
        State.linetype = []
        # sys.stdout.write(shortname(path) + "\n")
        
    def addLine(self, line):
        # State.prevline = State.currline
        # State.currline = line
        State.prevlinetype = State.currlinetype
        State.linecount += 1
        if line and line[0] == u'#' or badheading_re.match(line):
            State.currlinetype = HEADING
            State.headingcount += 1
            State.prevheadinglevel = State.currheadinglevel
            State.currheadinglevel = line.count(u'#', 0, 5)
        elif not line:
            State.currlinetype = BLANKLINE
        elif listitem_re.match(line):
            State.currlinetype = LIST_ITEM
        elif olistitem_re.match(line) or badolistitem_re.match(line):
            State.currlinetype = ORDEREDLIST_ITEM
        else:
            State.currlinetype = TEXT
        State.linetype.append(State.currlinetype)
        # sys.stdout.write(str(State.linecount) + ": line length: " + str(len(line)) + ". headingcount is " + str(State.headingcount) + "\n")

def reportError(msg):
    state = State()
    try:
        sys.stderr.write(shortname(state.path) + " line " + str(state.linecount) + ": " + msg + ".\n")
    except UnicodeEncodeError as e:
        sys.stderr.write(shortname(state.path) + " line " + str(state.linecount) + ": (Unicode...)\n")
        
 
# Reports empty file 
def verifyNotEmpty(mdPath):
    if os.path.isfile(mdPath):
       statinfo = os.stat(mdPath)
       if statinfo.st_size == 0:
           sys.stderr.write("Empty file: " + shortname(mdPath) + "\n")

heading_re = re.compile(r'#+[ \t]')
closedHeading_re = re.compile(r'#+[ \t].*#+[ \t]*$', re.UNICODE)
badclosedHeading_re = re.compile(r'#+[ \t].*[^# \t]#+[ \t]*$', re.UNICODE)  # closing hash without preceding space

def take(line):
    state = State()
    state.addLine(line)
    if not line:
        if state.linecount == 1 and not suppress7:
            reportError("starts with blank line")
        return
    if state.prevlinetype == HEADING and state.currlinetype != BLANKLINE:
        reportError("missing blank line after heading.")
    if state.currlinetype != HEADING and state.headingcount == 0 and not suppress1:
        reportError("has text before first heading")
    if state.currlinetype == HEADING:
        if state.linecount > 1 and state.prevlinetype != BLANKLINE:
            reportError("missing blank line before heading")
        if badheading_re.match(line):
            reportError("space(s) before heading")
        elif len(line) > 1 and not heading_re.match(line):
            reportError("missing space after hash symbol(s)")
        elif closedHeading_re.match(line):
            if not suppress4:
                reportError("closed heading")
            if badclosedHeading_re.match(line):
                reportError("no space before closing hash mark")
        elif len(line) == 1 and not suppress2:
            reportError("blank heading")
        if state.currheadinglevel > state.prevheadinglevel + 1:
            if resource_type != "ta" or state.prevheadinglevel > 0:
                reportError("heading level incremented by more than one level")
    if state.currlinetype == LIST_ITEM:
        if state.prevlinetype in { TEXT, HEADING }:
            reportError("invalid list syntax")
        i = state.linecount - 1
        if i > 1 and state.linetype[i-1] == BLANKLINE and state.linetype[i-2] == LIST_ITEM and not suppress8:
            reportError("invalid list style")
    if state.currlinetype == ORDEREDLIST_ITEM:
        if badolistitem_re.match(line) and not suppress3:
            reportError("item number not followed by period")
        if olistitem_re.match(line):
            if state.prevlinetype in { TEXT, HEADING }:
                reportError("missing blank line before ordered list")
            i = state.linecount - 1
# At least in the English tA, there are numerous violations of this rule, and yet
# the lists render beautifully. I am commenting out this rule check, 1/29/19.
#            if i > 1 and state.linetype[i-1] == BLANKLINE and state.linetype[i-2] == ORDEREDLIST_ITEM:
#                reportError("invalid ordered list style")
    if line.find(u'# #') != -1:
        reportError('probable heading syntax error')
    if len(line) > 2 and line[0:2] == u'% ':
        reportError("% used to mark a heading")

tapage_re = re.compile(r'\[\[.*/ta/man/(.*?)]](.*)', flags=re.UNICODE)
talink_re = re.compile(r'(\(rc://[\w\-]+/ta/man/)(.+?/.+?)(\).*)', flags=re.UNICODE)
obslink_re = re.compile(r'(rc://)([\w\-]+)(/tn/help/obs/)(\d+)(/\d+)(.*)', flags=re.UNICODE)
notelink_re = re.compile(r'(rc://)([\w\-]+)(/tn/help/)(\w\w\w/\d+/\d+)(.*)', flags=re.UNICODE)
passagelink_re = re.compile(r']\(([^\)]+)\)(.*)', flags=re.UNICODE)

# Parse tA manual page names from the link.
# Verifies the existence of the referenced page.
def checkTALinks(line):
    found = False
    page = tapage_re.search(line)
    while page:
        found = True
        if line and line[0] == u'#':
            reportError("tA page reference in heading")
        manpage = page.group(1)
        path = os.path.join(ta_dir, manpage)
        if not os.path.isdir(path):
            reportError("invalid tA page reference")
        page = tapage_re.search(page.group(2))

    if not found:
        link = talink_re.search(line)
        while link:
            found = True
            if line and line[0] == u'#':
                reportError("tA link in heading")
            manpage = link.group(2)
            manpage = manpage.replace(u'_', u'-')
            path = os.path.join(ta_dir, manpage)
            if path[-3:].lower() == '.md':
                path = path[:-3]
            if not os.path.isdir(path):
                reportError("invalid tA link: " + manpage)
            link = talink_re.search(link.group(3))
    return found          


# Parse tA links, note links, OBS links and passage links to verify existence of referenced .md file.
def checkMdLinks(line, fullpath):
    foundTA = checkTALinks(line)
    foundOBS = checkOBSLinks(line)
    if not foundOBS:        # because note links match OBS links
        foundTN = checkNoteLinks(line)
    if not foundTA and not foundOBS and not foundTN:    # because passagelink_re could match any of these
        checkPassageLinks(line, fullpath)

# Returns True if any OBS links were found and checked.
def checkOBSLinks(line):
    found = False
    link = obslink_re.search(line)
    while link:
        found = True
        if link.group(2) != language_code:
            reportError("invalid language code in OBS link")
        elif not suppress6:
            obsPath = os.path.join(obs_dir, link.group(4)) + ".md"
            if not os.path.isfile(obsPath):
                reportError("invalid OBS link: " + link.group(1) + link.group(2) + link.group(3) + link.group(4) + link.group(5))
        link = obslink_re.search(link.group(6))
    return found

# Returns True if any notes links were found.
# I am not checking note links currently because they are not rendered on live site as links anyway.
def checkNoteLinks(line):
    found = False
    notelink = notelink_re.search(line)
#     while notelink:
#         found = True
#         if notelink.group(2) != language_code:
#             reportError("invalid language code in note link")
#         else:
#             notePath = os.path.join(tn_dir, notelink.group(4)) + ".md"
#             notePath = os.path.normcase(notePath)
#             if not os.path.isfile(notePath):
#                 reportError("invalid note link: " + notelink.group(1) + notelink.group(2) + notelink.group(3) + notelink.group(4))
#         notelink = notelink_re.search(notelink.group(5))

    if notelink:
        found = True
    return found
    
def checkPassageLinks(line, fullpath):
    passage = passagelink_re.search(line)
    while passage:
        referencedPath = os.path.join( os.path.dirname(fullpath), passage.group(1) )
        if not suppress5 and not os.path.isfile(referencedPath):
            reportError("invalid passage link: " + passage.group(1))
        passage = passagelink_re.search(passage.group(2))

prefix_re = re.compile(r'C:\\DCS')

def shortname(longpath):
    shortname = longpath
    if prefix_re.match(longpath):
        shortname = "..." + longpath[6:]
    return shortname

# Markdown file verification
def verifyFile(path):
    # detect file encoding
    enc = detect_by_bom(path, default="utf-8")
    input = io.open(path, "tr", 1, encoding=enc)
    lines = input.readlines(-1)
    input.close

    verifyNotEmpty(path)
    state = State()
    state.setPath(path)
    for line in lines:
        line = line.rstrip()
        take( line )
        checkMdLinks(line, path)
    sys.stderr.flush()
    global nChecked
    nChecked += 1

def detect_by_bom(path, default):
    with open(path, 'rb') as f:
        raw = f.read(4)
    for enc,boms in \
            ('utf-8-sig',(codecs.BOM_UTF8)),\
            ('utf-16',(codecs.BOM_UTF16_LE,codecs.BOM_UTF16_BE)),\
            ('utf-32',(codecs.BOM_UTF32_LE,codecs.BOM_UTF32_BE)):
        if any(raw.startswith(bom) for bom in boms):
            return enc
    return default

def verifiable(path, fname):
    v = False
    if os.path.isfile(path) and fname[-3:].lower() == '.md':
        if resource_type == "ta":
            v = (fname == "01.md")
        else:
            v = True
    return v
    
def verifyDir(dirpath):
    sys.stdout.flush()
    for f in os.listdir(dirpath):
        path = os.path.join(dirpath, f)
        if os.path.isdir(path) and path[-4:] != ".git":
            # It's a directory, recurse into it
            verifyDir(path)
        elif verifiable(path, f):
            verifyFile(path)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == 'hard-coded-path':
        source = r'C:\DCS\Indonesian\id_tq'
    else:
        source = sys.argv[1]

    if resource_type == "ta":
        sys.stdout.write("Checking only files named 01.md.\n\n")
        sys.stdout.flush()

    if os.path.isdir(source):
        verifyDir(source)
    elif os.path.isfile(source):
        verifyFile(source)
    else:
        sys.stderr.write("File not found: " + source + '\n')

    print "Done. Checked " + str(nChecked) + " files.\n"