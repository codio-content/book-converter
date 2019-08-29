In contrast to a native app, which is designed to render a particular user interface associated with only one SaaS service, we can think of a desktop or mobile browser as a *universal client*, because any site the browser visits can deliver all the information necessary to render that site's user interface. Both browsers and native apps are used by millions of people, so we call them *production clients*.


Indeed, modern practice suggests that even when creating a user-facing SaaS app designed to be used via a browser, we should design the app as a collection of resources accessible via RESTful APIs, but then provide a Web browser-based user interface “on top of” those API calls.


If the Web browser is the universal client, _**HTML**_, the HyperText Markup Language, is the universal language. A _**markup language**_ combines text with markup (annotations about the text) in a way that makes it easy to syntactically distinguish the two.

HTML consists of a hierarchy of nested elements, each of which consists of an opening tag such as **<p>**, a content part (in some cases), and a closing tag such as **</p>**. Most opening tags can also have attributes, as in **$<$a href="http://..."$>$**. Some tags that don't have a content part are self-closing, such as **<br clear="both"/>** for a line break that clears both left and right margins.


  

|||info
The use of angle brackets for tags comes from _**SGML**_ (Standard Generalized Markup Language), a codified standardization of IBM's Generalized Markup Language, developed  in the 1960s for encoding computer-readable project documents.

|||



There is an unfortunate and confusing mess of terminology surrounding the [lineage of HTML](http://www.w3.org/TR/html5/introduction.html#history-1).  HTML 5 includes features of both its predecessors (HTML versions 1 through 4) and XHTML (eXtended HyperText Markup Language), which is a subset of _**XML**_, an eXtensible Markup Language that can be used both to represent data and to describe other markup languages.  Indeed, XML is a common data representation for exchanging information *between* two services in a Service-Oriented Architecture, as we'll see in Chapter chap:tdd when we extend RottenPotatoes to retrieve movie information from a separate movie database service.  The differences among the variants of XHTML and HTML are difficult to keep straight, and not all browsers support all versions.  Unless otherwise noted, from now on when we say HTML we mean HTML 5, and we will try to avoid using features that aren't widely supported.


Of particular interest are the HTML tag attributes **id** and **class**, because they figure heavily into connecting the HTML structure of a page with its visual appearance.  The following screencast illustrates the use of Firefox's Web Developer toolbar to quickly identify the ID's and Classes of HTML elements on a page.

<hr>

**Screencast: Inspecting the ID and Class attributes**

<iframe width="560" height="315" src="//www.youtube.com/embed/X5ArSbUea_o" frameborder="0" allowfullscreen></iframe>


CSS uses _**selector notations**_ such as **div#***name* to indicate a **div** element whose **id** is *name* and **div.***name* to indicate a **div** element with class *name*. Only one element in an HTML document can have a given **id**, whereas many elements (even of different tag types) can share the same **class**. All three aspects of an element---its tag type, its **id** (if it has one), and its **class** attributes (if it has any)---can be used to identify an element as a candidate for visual formatting.

<hr>




|||info
For an extreme example of how much can be done with CSS, visit the [CSS Zen Garden](http://csszengarden.com).

|||


As the next screencast shows, the _**CSS**_ (_**Cascading Style Sheets**_) standard allows us to associate visual “styling” instructions with HTML elements by using the elements' classes and IDs. The screencast covers only a few basic CSS constructs, which are summarized in Figure fig:css_cheat.  The Resources section at the end of the chapter lists sites and books that describe CSS in  great detail, including how to use CSS for aligning content on a page, something designers used to do manually with HTML tables.



<hr>

**Screencast: Introduction to CSS**

<iframe width="560" height="315" src="//www.youtube.com/embed/E5ZVorHn_fs" frameborder="0" allowfullscreen></iframe>


There are four basic mechanisms by which a selector in a CSS file can match an HTML element: by tag name, by class, by ID, and by hierarchy. If multiple selectors match a given element, the rules for which properties to apply are complex, so most designers try to avoid such ambiguities by keeping their CSS simple.  A useful way to see the “bones” of a page is to select \Sf{CSS>-Disable Styles>-All Styles} from the Firefox Web Developer toolbar; most developer-friendly browsers offer a “developer mode” featuring similar behaviors. Disabling styles will display the page with all CSS formatting turned off, showing the extent to which CSS can be used to separate visual appearance from logical structure.

<hr>



ch_arch/tables/css_cheat

**Figure 1.1**

 A few CSS constructs, including those explained in Screencast css-intro.  The top table shows some CSS *selectors*, which identify the elements to be styled; the bottom table shows a few of the many attributes, whose names are usually self-explanatory, and example values they can be assigned.  Not all attributes are valid on all elements.


Using this new information, Figure fig:10k  expands steps 2 and 3 from the previous section's summary of how SaaS works.

![SaaS from 10,000 feet.  Compared to Figure fig:50k, step 2 has been expanded to describe the content returned by the Web server, and step 3 has been expanded to describe the role of CSS in how the Web browser renders the content.](ch_arch/figs/saas10k.jpg)
**Figure 1.3**
SaaS from 10,000 feet.  Compared to Figure fig:50k, step 2 has been expanded to describe the content returned by the Web server, and step 3 has been expanded to describe the role of CSS in how the Web browser renders the content.

CSS provides for sophisticated layout behaviors, but can be tricky to use in 2 regards. First, some background in layout and graphic design is helpful in deciding how to style site elements - spacing, typography, color palette. Second, even if you know what you want the site to look like, it can be tricky to write the necessary CSS to achieve complex layouts, in which elements may "float" to the far left or far right of the page while text flows around them, or rearrange themselves responsively when the screen geometry changes (browser window resized, phone rotates) to provide a defensible user experience on both desktop and mobile devices.

Front-end frameworks use two mechanisms to "package" both aesthetic choices about visual styling and the coding required to achieve that styling.

CSS classes - define complex behaviors, provide reasonable default choices about typography and layout. By following certain rules about page structure - for example, which elements should be nested inside which others - and attaching the appropriate CSS classes to the elements, a variety of common element layouts can be achieved.

JavaScript - more sophisticated behaviors such as animations, collapsing menus, and drag-and-drop also require some JavaScript code. In many cases, you need never directly call this code: instead, you annotate page elements with yet other CSS classes, and the framework arranges to trigger the correct JavaScript code when the user interacts with elements having those classes. (Section [binding JavaScript to the DOM] explains the mechanics of how this is done.)

Rather than delving deeply into the aesthetics of graphic design, our goal for you as a well-rounded full-stack developer is that you should know how to provide well-structured pages with proper element nesting and clean CSS class tags, for two reasons. First, with a good front-end framework, just doing this will be enough to provide an AURA site (aesthetic, usable, responsive, accessible). Second, a clean site layout and classing allows designers to refine, customize, or work separately on the site's visual appearance.

There are 2 principles to using front-end frameworks successfully in this way: semantic styling and grid layout. Semantic styling means First, think of your page's visual elements not in terms of their visual characteristics ("This message should appear in a red box with bold text") but in terms of their function ("This message signals an error", "This text is the page title", "This list of items is a menu of navigation options"). A good front-end framework names its styles according to the function they enable an element to fulfill, rather than according to their visual appearance.

## SPA or MPA?
SPA vs MPA: Are you building something that's more like a website (transactional? lots of different possible screens? user navigates large amounts of data in a typical session? multi-screen workflows?) or more like a desktop app (few screens? continuous interaction vs transactional, eg something like Pivotal Tracker? user navigates modest amounts of data in a typical session? short workflows or interactions typically limited to 1 screen?)  If it's primarily a website, use HTML5 + jQuery where needed. If primarily an app, may be better off using a framework. [Need a checklist like "when to use agile" for "when to build a SPA vs MPA"].  Examples of popular SPAs: Gmail, Google Docs, Pivotal Tracker.  Popular MPAs: IMDb, Amazon.com, Google Search.  *MPA vs SPA is primarily a user experience question, not a technical one!*



---
**Summary**
  

* An _**HTML**_ (HyperText Markup Language) document consists of a hierarchically nested collection of elements. Each element begins with a  _**tag**_ in <angle brackets> that may have optional _**attributes**_.  Some elements enclose content.
* A _**selector**_ is an expression that identifies one or more HTML elements in a document by using a combination of the element name (such as **body**), element **id** (an element attribute that must be unique on a page), and element **class** (an attribute that need not be unique on a page).
* _**Cascading Style Sheets**_ (CSS) is a stylesheet language describing visual attributes of elements on a Web page.  A stylesheet associates sets of visual properties with  selectors.  A special **link** element inside the **head** element of an HTML document associates a stylesheet with that document.
* The “developer tools” in each browser, such as the Firefox Web Developer toolbar, are invaluable in peeking under the hood to examine both the structure of a page and its stylesheets.



---



|||challenge

  True or false: every HTML element must have an ID.

  <details><summary>Check yourself</summary>False---the ID is optional, though must be unique if provided.</details>

|||




|||info
**GitHub Gists** make it easy to copy-and-paste the code.
|||




|||challenge

  
  Given the following HTML markup:

  
**source:ch_arch/code/htmlexercise.html**
```code
ch_arch/code/htmlexercise.html
```

  Write down a CSS selector that will select *only* the word
  *Mondays* for styling.
  <details><summary>Check yourself</summary>Three possibilities, from most specific to least specific, are: **#i span**, **p.x span**, and **.x span**. Other selectors are possible but redundant or over-constrained; for example, **p#i span** and **p#i.x span** are redundant with respect to this HTML snippet since at most one element can have the ID **i**.</details>

|||



|||challenge

  In Self-Check ex:css1, why are **span**
  and  **p span** *not* valid answers?
  <details><summary>Check yourself</summary>Both of those selector also match *Tuesdays*, which is a **span** inside a **p**.</details>

|||



|||challenge

  What is the most common way to associate a CSS stylesheet with an HTML
  or HTML document? (HINT: refer to the earlier screencast example.)

  <details><summary>Check yourself</summary>Within the **HEAD** element of the HTML or HTML document, include a **LINK** element with at least the following three attributes: **REL="STYLESHEET"**, **TYPE="text/css"**, and **HREF="*uri*"**, where ***uri*** is the full or partial URI of  the stylesheet.  That is, the stylesheet must be accessible as a resource named by a URI.</details>

|||