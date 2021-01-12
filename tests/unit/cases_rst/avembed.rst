Each '0' bit indicates a left branch while each '1' bit indicates a
right branch.
The following slideshow shows an example for how to decode a message
by traversing the tree appropriately.

.. inlineav:: :figure_number:0.0.1: huffmanDecodeCON ss
   :long_name: Huffman Coding Tree Slideshow: Decoding
   :links: DataStructures/huffman.css AV/Binary/huffmanCON.css
   :scripts: DataStructures/huffman.js AV/Binary/huffmanDecodeCON.js
   :output: show

.. avembed:: Exercises/Binary/HuffmanDecodePRO.html ka
   :long_name: Huffman Decoding Proficiency Exercise


How efficient is Huffman coding?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In theory, Huffman coding is an optimal coding method whenever the
true frequencies are known, and the frequency of a letter is
independent of the context of that letter in the message.

.. slide:: Mid-Square Method

   .. odsafig:: :figure_number:0.0.1: Images/MidSquare.png
      :width: 100
      :align: center
      :capalign: justify
      :figwidth: 90%
      :alt: Mid-square method example

   .. avembed:: AV/Hashing/MidSquare.html pe
      :long_name: MidSquare
      :test_name: MidSquare


   .. avembed:: AV/Hashing/MidSquare1.html pe
