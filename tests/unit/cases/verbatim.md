```code
public interface Comparable<T> {
    public int compareTo(T o);
}
```

For example, here's the source code for `java.lang.Integer`:

```code
public final class Integer extends Number implements Comparable<Integer> {

    public int compareTo(Integer anotherInteger) {
        int thisVal = this.value;
        int anotherVal = anotherInteger.value;
        return (thisVal<anotherVal ? -1 : (thisVal==anotherVal ? 0 : 1));
    }

    // other methods omitted
}
```