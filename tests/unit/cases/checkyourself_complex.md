|||challenge
Suppose you mix <b>Enumerable</b> into a class <b>Foo</b> that does not provide the <b>each</b> method.  What error will be raised when you call <b>Foo.new.map { |elt| puts elt }</b>? 
<p><details><summary>Check yourself</summary>

The <b>map</b> method in <b>Enumerable</b> will attempt to call <b>each</b> on its receiver, but since the new <b>Foo</b> object doesn't define <b>each</b>, Ruby will raise an Undefined Method error.</details></p>

|||