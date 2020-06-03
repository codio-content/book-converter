###  Software as a Service


The power of SOA combined with the power of the Internet led to a special case of SOA with its own name: ___Software as a Service (SaaS)___. It delivers software and data as a service over the Internet, usually via a thin program such as a browser that runs on local client devices instead as an application binary that must be installed and runs wholly on that device.  Examples that many use every day include searching, social networking, and watching videos. The advantages for the customer and for the software developer are widely touted:



1. Since customers do not need to install the application, they don't have to worry whether their hardware is the right brand or fast enough, nor whether they have the correct version of the operating system.
2. The data associated with the service is generally kept with the service, so customers need not worry about backing it up, losing it due to a local hardware malfunction, or even losing the whole device, such as a phone or tablet.
3. When a group of users wants to collectively interact with the same data, SaaS is a natural vehicle.
4. When data is large and/or updated frequently, it may make more sense to centralize data and offer remote access via SaaS.
5. Only a single copy of the server software runs in a uniform, tightly-controlled hardware and operating system environment selected by the developer, which avoids the compatibility hassles of distributing binaries that must run on wide-ranging computers and operating systems. In addition, developers can test new versions of the application on a small fraction of the real customers temporarily without disturbing most customers. (If the SaaS client runs in a browser, there still are compatibility challenges, which we describe in Chapter chap:arch.) 

|||info
**SaaS: Innovate or Die?** Lest you think the perceived need to improve a successful service is just software engineering paranoia, the most popular search engine used to be AltaVista and the most popular social networking site used to be MySpace.
|||


6. SaaS companies compete regularly on bringing out new features to help ensure that their customers do not abandon them for a competitor who offers a better service.
7. Since only developers have a copy of the software, they can upgrade the software and underlying hardware frequently as long as they don't violate the external application program interfaces (API). Moreover, developers don't need to annoy users with the seemingly endless requests for permission to upgrade their applications.



Combining the advantages to the customer and the developer together explains why SaaS is rapidly growing and why traditional software products are increasingly being transformed to offer SaaS versions. An example of the latter is Microsoft Office 365, which allows you to use the popular Word, Excel, and PowerPoint productivity programs as a remote service by paying for use rather than pre-purchasing software and installing it on your local computer. Another example is TurboTax Online, which offers the same deal for another shrink-wrap standard-bearer.

file content

**<p style="font-size: 10px">Figure 1.1:  Examples of SaaS programming frameworks and the programming languages they are written in</p>**



Unsurprisingly, given the popularity of SaaS, Figure fig:SaaS_frameworks lists the many programming frameworks that claim to help.   In this book, we use Ruby on Rails (“Rails”), although the ideas we cover will work with other programming frameworks as well. We chose Rails because it came from a community that had already embraced the Agile lifecycle, so the tools support Agile particularly well.

Ruby is typical of modern scripting languages in including automatic memory management and dynamic typing. By including important advances in programming languages, Ruby goes beyond languages like Perl in supporting multiple programming paradigms such as object oriented and functional programming.


Useful additional features that help productivity via reuse include ___mix-ins___, which collect related behaviors and make it easy to add them to many different classes, and ___metaprogramming___, which allows Ruby programs to synthesize code at runtime. Reuse is also enhanced with Ruby's support for ___closures___ via ___blocks___ and ___yield___. Chapter chap:ruby_intro is a short description of Ruby for those who already know Java, and Chapter chap:rails_intro introduces Rails.

In addition to our view of Rails being technically superior for Agile and SaaS, Ruby and Rails are widely used. For example, Ruby routinely appears among top 10 most popular programming languages. A well-known SaaS app associated with Rails is Twitter, which began as a Rails app in 2006 and grew from 20,000 tweets per day in 2007 to 200,000,000 in 2011, during which time other frameworks replaced various parts of it.

software engineering skill: use the right tool for the job, even if it means learning a new tool or new language! Indeed, an attractive feature of the Rails community is that its contributors routinely improve productivity by inventing new tools to automate tasks that were formerly done manually.

Note that frequent upgrades of SaaS---due to only having a single copy of the software---perfectly align with the Agile software lifecycle. Hence, Amazon, eBay, Facebook, Google, and other SaaS providers all rely on the Agile lifecycle, and traditional software companies like Microsoft are increasingly using Agile in their product development. The Agile process is an excellent match to the fast-changing nature of SaaS applications.


---
**Summary:** ___Software as a Service (SaaS)___ is attractive to both customers and providers because the universal client (the Web browser) makes it easier for customers to use the service and the single version of the software at a centralized site makes it easier for the provider to deliver and improve the service. Given the ability and desire to frequently upgrade SaaS, the Agile software development process is popular for SaaS, and so there are many frameworks to support Agile and SaaS. This book uses Ruby on Rails.

---



|||challenge
Which of the  examples of Google SaaS apps---Search, Maps, News, Gmail, Calendar, YouTube, and Documents---is the best match to each of the six arguments given in this section for SaaS, reproduced below. 
<p><details><summary>Check yourself</summary>

While you can argue the mappings, below is our answer. (Note that we cheated and put some apps in multiple categories) 

1. No user installation: Documents
2. Can't lose data: Gmail, Calendar.
3. Users cooperating: Documents.
4. Large/changing datasets: Search, Maps, News, and YouTube.
5. Software centralized in single environment: Search.
6. No field upgrades when improve app: Documents.

</details></p>
|||



|||challenge
True or False: If you are using the Agile development process to develop SaaS apps, you could use Python and Django or languages based on the Microsoft's .NET framework and ASP.NET instead of Ruby and Rails. 
<p><details><summary>Check yourself</summary>

True. Programming frameworks for Agile and SaaS include Django and ASP.NET.</details></p>
|||


Given the case for SaaS and the understanding that it relies on a Service Oriented Architecture, we are ready to see the underlying hardware that makes SaaS possible.
