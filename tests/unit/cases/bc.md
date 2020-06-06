<b>Summary of legacy code exploration</b>

<b>Voucher</b>

jQuery defines a global function <b>jQuery()</b> (aliased as <b><span>\$</span>()</b>) that, when passed a CSS selector (examples of which we saw in Figure fig:css_cheat), returns all of the current page's DOM elements matching that selector.  For example, <b>jQuery('#movies')</b> or <b><span>\$</span>('#movies')</b> would return the single element whose ID is <b>movies</b>, if one exists on the page; <b><span>\$</span>('h1.title')</b> would return all the <b>h1</b> elements whose CSS class is <b>title</b>. A more general version of this functionality is <b>.find(</b><i>selector</i><b>)</b>, which only searches the DOM subtree rooted at the target.  To illustrate the distinction, <b><span>\$</span>('p span')</b> finds <i>any</i> <b>span</b> element that is contained inside a <b>p</b> element, whereas if <b>elt</b> already refers to a <i>particular</i> <b>p</b> element, then <b>elt.find('span')</b> only finds <b>span</b> elements that are descendants of <b>elt</b>.


|||info
The call <b>jQuery.noConflict()</b> “undefines” the <b><span>\$</span></b> alias, in case your app uses the browser's built-in <b><span>\$</span></b> (usually an alias for <b>document.-getElementById</b>) or loads another JavaScript library such as [Prototype](http://prototypejs.org) that also tries to define <b><span>\$</span></b>.

|||
