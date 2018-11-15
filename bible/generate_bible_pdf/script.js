if (!String.prototype.startsWith) {
    String.prototype.startsWith = function(searchString, position) {
        position = position || 0;
        return this.indexOf(searchString, position) === position;
    };
}

if (!String.prototype.includes) {
    Object.defineProperty(String.prototype, 'includes', {
        value: function(search, start) {
          if (typeof start !== 'number') {
               start = 0
          }
          if (start + search.length > this.length) {
               return false
          } else {
              return this.indexOf(search, start) !== -1
          }
        }
    })
}

$(document).ready(function(){
    var books = $('.bible-book-text');
    books.each(function(bookIdx) {
        var book = books[bookIdx];
        var contents = $(book).contents();
        console.log(contents);
        var footnotes = {}

        contents.each(function(contentIdx) {
            var content = this;
            console.log(content.localName+' '+content.className);
            if (content.localName === 'div' && content.className === 'footnotes') {
                console.log(content.childNodes.length);
                for (var i = 0; i < content.childNodes.length; ++i) {
                    childNode = content.childNodes[i];
                    if (childNode.id.startsWith('fn-')) {
                        footnotes[childNode.id] = $(childNode).detach();
                    }
                }
                $(content).detach();
            }
        });
        console.log(footnotes);
        
        var pageIdx = 0;
        var colIdx = 0;
        var page = $('<div id="page'+pageIdx+'" class="page"></div>');
        page.appendTo(book);
        var col1 = $('<div id="col'+colIdx+'" class="col left"></div>');
        col1.appendTo(page);
        var col2 = $('<div id="col'+(colIdx+1)+'" class="col right"></div>');
        col2.appendTo(page);
        var footnotesSection1 = $('<div id="footnotesSection'+colIdx+'" class="footnotesSection left footnotes"></div>');
        footnotesSection1.appendTo(page);
        var footnotesSection2 = $('<div id="footnotesSection'+(colIdx+1)+'" class="footnotesSection right footnotes"></div>');
        footnotesSection2.appendTo(page);
        col = page.find('#col'+colIdx);
        var footnotesSection = page.find('#footnotesSection'+colIdx);
        console.log(footnotesSection.length);
        console.log(contents.clone());
        console.log(contents);
        contents.each(function(contentIdx) {
            var content = this;
            var $content = $(this);
            console.log('Got content of tag <'+content.localName+' '+content.id+' '+content.className+'>');
            if (content.localName == 'p' || content.localName == 'h1' || content.localName == 'h2') {
                $content.detach();
                var items = [];
                var lastItemWasVerseNum = false;
                console.log('CHILD NODES LENGTH: '+content.childNodes.length);
                for (var i = 0; i < content.childNodes.length; i++) {
                    var childNode = content.childNodes[i];
                    console.log("TYPE: "+childNode.nodeType);
                    if (childNode.nodeType === 3) {
                        if (childNode.nodeValue.trim().length) {
                            var words = childNode.nodeValue.trim().split(/ +/g).map(function(val){return val+' '});
                            if (lastItemWasVerseNum) {
                                items[items.length-1] = items[items.length-1].trim()+words.shift();
                                lastItemWasVerseNum = false;
                            }
                            items = items.concat(words);
                        }
                    } 
                    else if(childNode.nodeType === 1) {
                        if (childNode.className == 'v-num') {
                            lastItemWasVerseNum = true;
                            items.push(childNode.outerHTML+' ');
                        }
                        else if(childNode.id.startsWith('ref-fn-')) {
                            items[items.length-1] = items[items.length-1].trim()+childNode.outerHTML+' ';
                        }
                        else if(content.localName === 'div' && content.className === 'footnotes') {
                            // do nothing, already have footnotes
                        }
                        else if(content.localName === 'div') {
                            items.push(childNode.outerHTML+' ');
                        }
                        else if (childNode.className == 'chunk-break') {
                            // do nothing
                        }
                        else {
                            console.log('=========> GOT THIS FUNKY THING: '+childNode.outerHTML);
                        }
                    }
                    else {
                        console.log(childNode.nodeType);
                        console.log("================> Have a node of "+childNode.nodeType+" -> "+childNode.outerHTML);
                    }
                }
    
                wrapper = $content.clone().empty();
                wrapper.appendTo(col);
                while(items.length) {
                    var item = items.shift();
                    // console.log("our item is: "+item);
                    var element = $('<span>'+item+'</span>');
                    element.appendTo(wrapper);
                    var itemFootnotes = [];
                    if (item.includes('ref-fn-')) {
                        if (! footnotesSection.contents().length) {
                            itemFootnotes.push($('<hr class="footnotes-hr"/>'));
                        }
                        var re = /ref-(fn-\d+-\d+-\d+-\d+)/g;
                        while (match = re.exec(item)) {
                            var idx = match[1];
                            if (footnotes[idx]) {
                                itemFootnotes.push($(footnotes[idx]));
                            }
                        }
                        itemFootnotes.forEach(function(element) {
                            element.appendTo(footnotesSection);
                        });
                    }
                    var colHeight = col.height() + footnotesSection.height();
                    var pageHeight = page.height();
                    if (colHeight > pageHeight) {
                        ++colIdx;
                        element.detach();
                        itemFootnotes.forEach(function(element) {
                            element.detach();
                        });
                        if (wrapper.is(':empty')) {
                            wrapper.detach();
                        } else {
                            wrapper = $content.clone().empty();
                        }
                        if (colIdx % 2 === 0) {
                            ++pageIdx;
                            page = $('<div id="page'+pageIdx+'" class="page"/>');
                            page.appendTo(book);
                            col1 = $('<div id="col'+colIdx+'" class="col left"/>');
                            col1.appendTo(page);
                            col2 = $('<div id="col'+(colIdx+1)+'" class="col right"/>');
                            col2.appendTo(page);
                            footnotesSection1 = $('<div id="footnotesSection'+colIdx+'" class="footnotesSection left footnotes"></div>');
                            footnotesSection1.appendTo(page);
                            footnotesSection2 = $('<div id="footnotesSection'+(colIdx+1)+'" class="footnotesSection right footnotes"></div>');
                            footnotesSection2.appendTo(page);
                        }
                        col = page.find('#col'+colIdx);
                        footnotesSection = page.find('#footnotesSection'+colIdx);
                        console.log(footnotesSection.length);
                        wrapper.appendTo(col);
                        items.unshift(item);
                    }
                    else {
                        element.detach();
                        wrapper.html(wrapper.html() + element.html());
                        //console.log("all is good for "+colIdx);
                        //console.log(wrapper.html());
                    }
                }
            }
        });
    });
});