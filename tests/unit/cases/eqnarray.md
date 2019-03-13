The goal of this exercise is to translate a recursive definition into a Java method. The Ackermann function is defined for non-negative integers as follows:
$$
A(m, n) = \begin{cases}
              n+1 & \mbox{if } m = 0 \\
              A(m-1, 1) & \mbox{if } m > 0 \mbox{ and } n = 0 \\
              A(m-1, A(m, n-1)) & \mbox{if } m > 0 \mbox{ and } n > 0
\end{cases}
$$

Write a recursive method called `ack` that takes two `int`s as parameters and that computes and returns the value of the Ackermann function.

For example, the **factorial** of an integer $n$, which is written $n!$, is defined like this:

$$
0! = 1 \\
n! = n \cdot(n-1)!
$$

Don't confuse the mathematical symbol $!$, which means *factorial*, with the Java operator `!`, which means *not*.

$$
\sin \frac{\pi}{4} + \frac{\cos \frac{\pi}{4}}{2} \\
\log 10 + \log 20
$$
