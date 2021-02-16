if (runTest(new Test$num())) {
    passed_tests++;
    feedback += "$messageTest <span style=\"color:green\"><b>PASSED</b></span>$passed_data\n\n";
} else {
    feedback += "$messageTest <span style=\"color:red\"><b>FAILED</b></span>$failed_data\n";
    try {
       Object exp = Test$num.getExpectedVal();
       Object act = Test$num.getActualVal();
       feedback += "Expected: " + exp + "\n" + "but was: " + act + "\n\n";
    } catch (Exception | Error e) {
       feedback += e + "\n\n";
    }
}
