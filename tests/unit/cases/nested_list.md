* *Specific.* Here are examples of a vague feature paired with a specific version: 
**source:ch_bdd/code/vaguefeature.rb**
```code
ch_bdd/code/vaguefeature.rb
```

* *Measurable.* Adding Measurable to Specific means that each story should be testable, which implies that there are known expected results for some good inputs. An example of a pair of an unmeasurable versus measurable feature is 
**source:ch_bdd/code/unmeasurablefeature.rb**
```code
ch_bdd/code/unmeasurablefeature.rb
```
 Only the second case can be tested to see if the system fulfills the requirement.
* *Achievable.* Ideally, you implement the user story in one Agile iteration. If you are getting less than one story per iteration, then they are too big and you need to subdivide these stories into smaller ones. As mentioned above, the tool _**Pivotal Tracker**_ measures _**Velocity**_, which is the rate of completing stories  of varying difficulty.
* *Relevant.* A user story must have business value to one or more stakeholders. To drill down to the real business value, one technique is to keep asking “Why.” Using as an example a ticket-selling app for a regional theater, suppose the proposal is to add a Facebook linking feature. Here are the “Five Whys” in action with their recursive questions and answers: 

1. Why add the Facebook feature? As box office manager, I think more people will go with friends and enjoy the show more.
1. Why does it matter if they enjoy the show more? I think we will sell more tickets.
1. Why do you want to sell more tickets? Because then the theater makes more money.
1. Why does theater want to make more money? We want to make more money so that we don't go out of business.
1. Why does it matter that theater is in business next year? If not, I have no job. (We're pretty sure the business value is now apparent to at least one stakeholder!)
* *Timeboxed.* Timeboxing means that you stop developing a story once you've exceeded the time budget. Either you give up, divide the user story into smaller ones, or reschedule what is left according to a new estimate. If dividing looks like it won't help, then you go back to the customers to find the highest value part of the story that you can do quickly. The reason for a time budget per user story is that it is extremely easy to underestimate the length of a software project. Without careful accounting of each iteration, the whole project could be late, and thus fail. Learning to budget a software project is a critical skill, and exceeding a story budget and then refactoring it is one way to acquire that skill.