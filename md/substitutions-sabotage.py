# -*- coding: utf-8 -*-
# This version of substitutions.py corrects many instances of what appears to be
# extensive, deliberate corruption of TA links.
# substitutions.py is used by md_cleanup.py.
# An ordered list of tuples to be used for string substitutions.
#

subs = [
	("http://ufw.io/[[rc://", "[[rc://"),
	
	# HTML / V-MAST section
	("&nbsp;", " "),
	("&#34;", "\""),
	("&#39;", "'"),
	("<o:p>", ""),
	("</o:p>", ""),
	
	("rc://en/", "rc://*/"),
	("rc://*/obe/", "rc://*/tw/bible/"),

    ("figs-_idiom", "figs-idiom"),
    ("figs-123pperson", "figs-123person"),
    ("figs-abbstractnouns", "figs-abstractnouns"),
    ("figs-abstactnouns", "figs-abstractnouns"),
    ("figs-abstaractnouns", "figs-abstractnouns"),
    ("figs-abstarctnouns", "figs-abstractnouns"),
    ("figs-abstrac]", "figs-abstractnouns"),
    ("figs-abstracnouns", "figs-abstractnouns"),
    ("figs-abstractions", "figs-abstractnouns"),
    ("figs-abstractnoun]", "figs-abstractnouns]"),
    ("figs-abstractnounss", "figs-abstractnouns"),
    ("figs-asbtractnouns", "figs-abstractnouns"),
    ("figs-acctivepassive", "figs-activepassive"),
    ("figs-acitivepassive", "figs-activepassive"),
    ("figs-acitvepassive", "figs-activepassive"),
    ("figs-acivepassive", "figs-activepassive"),
    ("figs-actiepassive", "figs-activepassive"),
    ("figs-actionpassive", "figs-activepassive"),
    ("figs-active]", "figs-activepassive]"),
    ("figs-activep]", "figs-activepassive]"),
    ("figs-activepasive", "figs-activepassive"),
    ("figs-activepassi]", "figs-activepassive]"),
    ("figs-activepassice", "figs-activepassive"),
    ("figs-activepassiv]", "figs-activepassive]"),
    ("figs-activepasssive", "figs-activepassive"),
    ("figs-activepav", "figs-activepassive"),
    ("figs-activepe", "figs-activepassive"),
    ("figs-activepv", "figs-activepassive"),
    ("figs-actviepassive", "figs-activepassive"),
    ("figs-acvtivepassive", "figs-activepassive"),
    ("figs-ametonymy", "figs-metonymy"),
    ("figs-apostrphe", "figs-apostrophe"),
    ("figs-daublet", "figs-doublet"),
    ("figs-decalarative", "figs-declarative"),
    ("figs-ellipses", "figs-ellipsis"),
    ("figs-ellipsisi", "figs-ellipsis"),
    ("figs-euphemsism", "figs-euphemism"),
    ("figs-event]", "figs-events]"),
    ("figs-exclamation]", "figs-exclamations]"),
    ("figs-exclusiv]", "figs-exclusive]"),
    ("figs-expicit", "figs-explicit"),
    ("figs-explcit", "figs-explicit"),
    ("figs-explict", "figs-explicit"),
    ("figs-genderanotations", "figs-gendernotations"),
    ("figs-hebrewmonths", "translate-hebrewmonths"),
    ("figs-hypebole", "figs-hyperbole"),
    ("figs-hyperbe", "figs-hyperbole"),
    ("figs-hyperbloe", "figs-hyperbole"),
    ("figs-hypoand", "figs-hypo"),
    ("figs-idioms]", "figs-idiom]"),
    ("figs-idion", "figs-idiom"),
    ("figs-idom", "figs-idiom"),
    ("figs-ifiom", "figs-idiom"),
    ("figs-implicit", "figs-explicit"),
    ("figs-maetonymy", "figs-metonymy"),
    ("figs-meonymy", "figs-metonymy"),
    ("figs-meronymy", "figs-metonymy"),
    ("figs-meta]", "figs-metaphor]"),
    ("figs-metahor", "figs-metaphor"),
    ("figs-metanymy", "figs-metonymy"),
    ("figs-metaohor", "figs-metaphor"),
    ("figs-metaph]", "figs-metaphor]"),
    ("figs-metaphior", "figs-metaphor"),
    ("figs-metapho]", "figs-metaphor]"),
    ("figs-metaphoir", "figs-metaphor"),
    ("figs-metaphorand", "figs-metaphor"),
    ("figs-metapor", "figs-metaphor"),
    ("figs-methaphor", "figs-metaphor"),
    ("figs-metomymy", "figs-metonymy"),
    ("figs-metonomy", "figs-metonymy"),
    ("figs-metonumy", "figs-metonymy"),
    ("figs-metonym]", "figs-metonymy]"),
    ("figs-metophor", "figs-metaphor"),
    ("figs-mettonymy", "figs-metonymy"),
    ("figs-mmetaphor", "figs-metaphor"),
    ("figs-mrtonymy", "figs-metonymy"),
    ("figs-nomialadj", "figs-nominaladj"),
    ("figs-nomiladj", "figs-nominaladj"),
    ("figs-numbers", "translate-numbers"),
    ("figs-paralelism", "figs-parallelism"),
    ("figs-paralism", "figs-parallelism"),
    ("figs-paralleism", "figs-paralleism"),
    ("figs-parallesim", "figs-parallelism"),
    ("figs-parellelism", "figs-parallelism"),
    ("figs-pastoffurture", "figs-pastforfuture"),
    ("figs-pastorfutre", "figs-pastforfuture"),
    ("figs-pastorfuture", "figs-pastforfuture"),
    ("figs-peersonification", "figs-personification"),
    ("figs-personfication", "figs-personification"),
    ("figs-personificatio]", "figs-personification]"),
    ("figs-personifiction", "figs-personification"),
    ("figs-personitication", "figs-personification"),
    ("figs-prersonification", "figs-personification"),
    ("figs-proverbs", "writing-proverbs"),
    ("figs-question", "figs-rquestion"),
    ("figs-questions", "figs-rquestion"),
    ("figs-quotation]", "figs-quotations]"),
    ("figs-quotationquotes", "figs-quotations"),
    ("figs-quoteinquotes", "figs-quotesinquotes"),
    ("figs-quotesinqotes", "figs-quotesinquotes"),
    ("figs-rqeustion", "figs-rquestion"),
    ("figs-rquesion", "figs-rquestion"),
    ("figs-rquestio]", "figs-rquestion]"),
    ("figs-rquestions", "figs-rquestion"),
    ("figs-rquetion", "figs-rquestion"),
    ("figs-rqustion", "figs-rquestion"),
    ("figs-sctivepassive", "figs-activepassive"),
    ("figs-sumile", "figs-simile"),
    ("figs-symaction", "translate-symaction"),
    ("figs-eynecdoche", "figs-synecdoche"),
    ("figs-syneadoche", "figs-synecdoche"),
    ("figs-synecdoache", "figs-synecdoche"),
    ("figs-synecdoch]", "figs-synecdoche]"),
    ("figs-synecdohe", "figs-synecdoche"),
    ("figs-synecoche", "figs-synecdoche"),
    ("figs-synedoche", "figs-synecdoche"),
    ("translate-bweght", "translate-bweight"),
    ("translate-dbistance", "translate-bdistance"),
    ("translate-explicit", "figs-explicit"),
    ("translate-frcation", "translate-fraction"),
    ("translate-hebrewsmonth", "translate-hebrewmonths"),
    ("translate-manuscript]", "translate-manuscripts]"),
    ("translate-money", "translate-bmoney"),
    ("translate-name]", "translate-names]"),
    ("translate-namesand", "translate-names"),
    ("translate-nominal]", "translate-nominaladj]"),
    ("translate-number]", "translate-numbers]"),
    ("translate-numbers0", "translate-numbers"),
    ("translate-numbres", "translate-numbers"),
    ("translate-proverbs", "writing-proverbs"),
    ("translate-symlanguage", "writing-symlanguage"),
    ("translate-synmation", "translate-symaction"),
    ("translate-unknow]", "translate-unknown]"),
    ("translate-unknwn", "translate-unknown"),
    ("translate-unknwown", "translate-unknown"),
    ("translate-unkwon", "translate-unknown"),
    ("writing-backgraound", "writing-background"),
    ("writing-proverb", "writing-proverbs"),
    ("writing-proverbss", "writing-proverbs"),

 	("\\ [", "["),
 	("\\ ]", "]"),
 	("\\[", "["),
 	("\\]", "]"),
 	(" ]", "]"),
 	("]]]]", "]]"),
 	("]])]]", "]])"),
	(") [", "), ["),
	(" \( ", " ("),
	("/ )", "/)"),
	("____", "__"),
	("___", "__"),
	("..md", ".md"),
	(".jpg?direct&", ".jpg")    # OBS image links
]