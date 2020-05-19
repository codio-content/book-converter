|||challenge
Suppose you mix __Enumerable__ into a class __Foo__ that does not provide the __each__ method.  What error will be raised when you call __Foo.new.map { |elt| puts elt }__? 
<details><summary>Check yourself</summary>The __map__ method in __Enumerable__ will attempt to call __each__ on its receiver, but since the new __Foo__ object doesn't define __each__, Ruby will raise an Undefined Method error.</details>
|||