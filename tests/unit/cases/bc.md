**Summary of legacy code exploration**

__Voucher__

jQuery defines a global function __jQuery()__ (aliased as __<span>\$</span>()__) that, when passed a CSS selector (examples of which we saw in Figure fig:css_cheat), returns all of the current page's DOM elements matching that selector.  For example, __jQuery('#movies')__ or __<span>\$</span>('#movies')__ would return the single element whose ID is **movies**, if one exists on the page; __<span>\$</span>('h1.title')__ would return all the **h1** elements whose CSS class is **title**. A more general version of this functionality is __.find(__*selector*__)__, which only searches the DOM subtree rooted at the target.  To illustrate the distinction, __<span>\$</span>('p span')__ finds *any* **span** element that is contained inside a **p** element, whereas if __elt__ already refers to a *particular* **p** element, then __elt.find('span')__ only finds **span** elements that are descendants of __elt__.


|||info
The call __jQuery.noConflict()__ “undefines” the __<span>\$</span>__ alias, in case your app uses the browser's built-in __<span>\$</span>__ (usually an alias for __document.-getElementById__) or loads another JavaScript library such as [Prototype](http://prototypejs.org) that also tries to define __<span>\$</span>__.

|||
