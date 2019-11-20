#!/usr/bin/env sh
# -*- coding: utf8 -*-
#
#  Copyright (c) 2016 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Jesse Griffin <jesse@distantshores.org>
#  Caleb Maclennan <caleb@alerque.com>
#  Richard Mahn <rich.mahn@unfoldingword.org>

NOTES=/var/www/vhosts/door43.org/httpdocs/data/gitrepo/pages/en/bible/notes
BASEDIR=$(cd $(dirname "$0")/../ && pwd)

book_import () {
    # $1 is book short name
    # $2 is number of chapters

    if [ "$1" == "psa" ]; then
        for x in `seq -f "%03g" 1 $2`; do
            $BASEDIR/uwb/put_chunks_into_notes.py -l en -b $1 -c $x >/dev/null
        done
    else
        for x in `seq -f "%02g" 1 $2`; do
            $BASEDIR/uwb/put_chunks_into_notes.py -l en -b $1 -c $x >/dev/null
        done
    fi

    cd $NOTES/$1
    git add .
    git commit -am "Updated $1 notes"
    git push origin master

}

book_import luk 24
book_import rut 4
book_import tit 3
book_import 1ti 6
book_import 2ti 4
book_import act 28
book_import gen 50

# These added 2015-01-28
book_import jon 4
book_import rom 16
book_import gal 6
book_import eph 6
book_import php 4
book_import 1th 5
book_import 2th 3
book_import phm 1
book_import heb 13
book_import jas 5
book_import 1co 16
book_import 2co 13
book_import exo 40
book_import 1pe 5
book_import 2pe 3
book_import 1jn 5
book_import 2jn 1
book_import 3jn 1
book_import jud 1
book_import rev 22
book_import col 4

# These added 2015-02-05
book_import mat 28
book_import jhn 21
book_import mrk 16
book_import lev 27
book_import num 36
book_import deu 34
book_import jos 24

# These added 2015-02-11
book_import jdg 21
book_import 1sa 31
book_import job 42
book_import 1ki 22
book_import 2ki 25

# These added 2015-02-17
book_import 1ch 29
book_import 2ch 36
book_import lam 5
book_import jer 52
book_import oba 1
book_import hag 2
book_import zep 3
book_import hab 3
book_import nam 3
book_import mic 7
book_import mal 4
book_import jol 3
book_import amo 9
book_import zec 14
book_import ezr 10
book_import est 10
book_import neh 13
book_import ezk 48
book_import dan 12

# These added 2015-02-17
book_import hos 14
book_import sng 8
book_import ecc 12
book_import pro 31
book_import 2sa 24
book_import psa 150

# This added 2015-02-23
book_import isa 66

chown -R apache:apache /var/www/vhosts/door43.org/httpdocs/data/gitrepo/pages/en
