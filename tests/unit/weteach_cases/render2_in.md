**Labs -- Part B** -- Unit 5 -- Writing Classes Topics 5.4, 5.5 and 5.6 -- Writing Methods
==========================================================================================

> **Lab 5.4.5 -- The Book Class**

Write a class called Book using the program shown in the image below, and run it using the Main class to achieve an output like the one shown at the bottom of the image. **The hash code may be different**, but the structure should be the same.
===================================================================================================================================================================================================================================================

![](media1/media/image4.png){width="6.407964785651793in" height="5.910937226596675in"}

Lab 5.4.6 -- The Book Class - First Expansion
---------------------------------------------

> ![](media1/media/image5.png){width="6.416816491688539in" height="3.7231244531933507in"}Add code to the Book class from the previous lab to enable the output shown below. New elements include a suitable constructor, accessor methods for each field, and a toString method to produce the output shown.

Lab 5.4.7 -- The Book Class -- Second Expansion
-----------------------------------------------

> ![](media1/media/image6.png){width="6.420034995625547in" height="3.4679166666666665in"}Further expanding the Book class from previous labs, add sufficient code to produce the output shown to the right. This will include a default constructor, one that sets all fields to default values, as well as \"setter\" methods, enabling changes to private instance fields.

Lab 5.4.8 -- The Book and Int Classes
-------------------------------------

> Using the Int class definition shown, adjust the Book class accordingly so that the private instance field **yearPub** is now of class Int instead of a primitive int data type.

![](media1/media/image7.png){width="1.552227690288714in" height="1.943332239720035in"}![](media1/media/image8.png){width="2.124362423447069in" height="2.236561679790026in"}

> ![](media1/media/image9.png){width="5.541935695538058in" height="2.7312489063867016in"}Use the Main class below to produce the outputs below. The first one is incorrect, and the second is correct. Be sure any adjustments you make to the Book class produce the second output, and not the first.

This first output shown below is incorrect. See how the publication year for the first book changed?
====================================================================================================

> ![](media1/media/image10.png){width="5.0288473315835525in" height="0.5082283464566929in"}
>
> ![](media1/media/image11.png){width="5.046149387576553in" height="0.5082283464566929in"}This second output is correct. The change to the year object did not affect the first book, which is what you want. Be sure your code does this.
