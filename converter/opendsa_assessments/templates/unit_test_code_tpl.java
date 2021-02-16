public static class Test$num implements Callable<Boolean>{
   private static final $class_name instance = new $class_name();

   public Test$num() {
   }

   public static Object getExpectedVal() {
      return $expected;
   }

   public static Object getActualVal() {
      return instance.$method_name($actual);
   }

   public Boolean call() {
      return Objects.equals(getExpectedVal(), getActualVal());
   }
}
