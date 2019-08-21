**Summary of legacy code exploration**

**Voucher**

jQuery defines a global function **jQuery()** (aliased as **<span>\$</span>()**) that, when passed a CSS selector (examples of which we saw in Figure fig:css_cheat), returns all of the current page's DOM elements matching that selector.  For example, **jQuery('#movies')** or **<span>\$</span>('#movies')** would return the single element whose ID is **movies**, if one exists on the page; **<span>\$</span>('h1.title')** would return all the **h1** elements whose CSS class is **title**. A more general version of this functionality is **.find(***selector***)**, which only searches the DOM subtree rooted at the target.  To illustrate the distinction, **<span>\$</span>('p span')** finds *any* **span** element that is contained inside a **p** element, whereas if **elt** already refers to a *particular* **p** element, then **elt.find('span')** only finds **span** elements that are descendants of **elt**.


|||info
The call **jQuery.noConflict()** “undefines” the **<span>\$</span>** alias, in case your app uses the browser's built-in **<span>\$</span>** (usually an alias for **document.-getElementById**) or loads another JavaScript library such as [Prototype](http://prototypejs.org) that also tries to define **<span>\$</span>**.

|||