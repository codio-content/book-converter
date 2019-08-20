|||challenge

  Suppose you mix **Enumerable** into a class **Foo** that does not
  provide the **each** method.  What error will be raised when you
  call **Foo.new.map { |elt| puts elt }**?
  <details><summary>Check yourself</summary>The **map** method in **Enumerable** will attempt to call **each** on its receiver, but since the new **Foo** object doesn't define **each**, Ruby will raise an Undefined Method error.</details>

|||