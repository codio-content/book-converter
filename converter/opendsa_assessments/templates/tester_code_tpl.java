import java.util.Objects;
import java.util.concurrent.Callable;

public class Tester {
   public static void main(String[] args) {
       int total_tests = $num;
       int passed_tests = 0;
       String feedback = "";
       String method_name = "$method_name";

$run_tests

       String total = "" + total_tests;
       String passed = "" + passed_tests;
       String output = total + "\n" + passed + "\n" + method_name + "\n" + feedback;
       System.out.println(output);
   }

   private static boolean runTest(Callable<Boolean> func) {
       try {
           return func.call();
       } catch (Exception | Error e) {
           return false;
       }
   }

$unit_tests

}
