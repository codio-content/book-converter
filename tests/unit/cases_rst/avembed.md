Each '0' bit indicates a left branch while each '1' bit indicates a right branch. The following slideshow shows an example for how to decode a message by traversing the tree appropriately.

<link rel="stylesheet" type="text/css" href=".guides/DataStructures/huffman.css"/>
<link rel="stylesheet" type="text/css" href=".guides/AV/Binary/huffmanCON.css"/>

<div id="huffmanDecodeCON" class="ssAV">
<span class="jsavcounter"></span>
<a class="jsavsettings" href="#">Settings</a>
<div class="jsavcontrols"></div>
<p class="jsavoutput jsavline"></p>
<div class="jsavcanvas"></div>
</div>
<script type="text/javascript" src=".guides/DataStructures/huffman.js"></script>
<script type="text/javascript" src=".guides/AV/Binary/huffmanDecodeCON.js"></script>
<br/>



<div id="HuffmanDecodePRO" class="embedContainer" data-exer-name="HuffmanDecodePRO" data-long-name="HuffmanDecodePRO" data-short-name="HuffmanDecodePRO" data-frame-src=".guides/opendsa_v1/Exercises/Binary/HuffmanDecodePRO.html?selfLoggingEnabled=false&localMode=true&module=BasicPointers2&JXOP-debug=true&JOP-lang=en&JXOP-code=java" data-frame-width="660"data-frame-height="600" data-external="false" data-points="1.0" data-required="True" data-showhide="show" data-threshold="1" data-type="ka"data-exer-id=""><div class="center"> <div id="HuffmanDecodePRO_iframe"></div></div>





### How efficient is Huffman coding?

In theory, Huffman coding is an optimal coding method whenever the true frequencies are known, and the frequency of a letter is independent of the context of that letter in the message.

.. slide:: Mid-Square Method

```   .. odsafig:: Images/MidSquare.png```
      :width: 100
      :align: center
      :capalign: justify
      :figwidth: 90%
      :alt: Mid-square method example

<div id="MidSquare" class="embedContainer" data-exer-name="MidSquare" data-long-name="MidSquare" data-short-name="MidSquare" data-frame-src=".guides/opendsa_v1/AV/Hashing/MidSquare.html?selfLoggingEnabled=false&localMode=true&module=BasicPointers2&JXOP-debug=true&JOP-lang=en&JXOP-code=java" data-frame-width="660"data-frame-height="600" data-external="false" data-points="1.0" data-required="True" data-showhide="show" data-threshold="1" data-type="pe"data-exer-id=""><div class="center"> <div id="MidSquare_iframe"></div></div>



<div id="MidSquare1" class="embedContainer" data-exer-name="MidSquare1" data-long-name="MidSquare1" data-short-name="MidSquare1" data-frame-src=".guides/opendsa_v1/AV/Hashing/MidSquare1.html?selfLoggingEnabled=false&localMode=true&module=BasicPointers2&JXOP-debug=true&JOP-lang=en&JXOP-code=java" data-frame-width="660"data-frame-height="600" data-external="false" data-points="1.0" data-required="True" data-showhide="show" data-threshold="1" data-type="pe"data-exer-id=""><div class="center"> <div id="MidSquare1_iframe"></div></div>

