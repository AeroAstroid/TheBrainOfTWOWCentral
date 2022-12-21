from Commands.bstar.interpreter.function_deco import setupFunctions

from Commands.bstar.interpreter.run import runCodeSandbox


# stolen from https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
# muhahahahahahaha 😈
class Colours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Stats:
    num = 0
    correctTests = 0
    failedTestNames = []
    failedTests = 0


# def disableUselessPrints():
#     debug.print_debug = False
#     debug.print_error = False


def attempt(code, assumption, amount=50):
    attemptResults = []
    failedAttemptOutput = ""
    for i in range(amount):
        output = runCodeSandbox(code)
        correct = output.strip() == assumption
        attemptResults.append(correct)
        if not correct:
            failedAttemptOutput = output

    perfect = all(attemptResults)

    return [perfect, failedAttemptOutput]


def test(name, code, assumption):
    results = attempt(code, assumption)
    if results[0]:
        print(Colours.OKGREEN + Colours.BOLD + "✔", name, Colours.ENDC)
        Stats.correctTests += 1
    else:
        print(Colours.FAIL + Colours.BOLD + "✘", name, end="")
        print(f" (Wanted '{assumption}', Got '{results[1]}')")
        Stats.failedTestNames.append(name)
        Stats.failedTests += 1
    Stats.num += 1


def testAll():
    test("Hello, World!", "Hello, World!", "Hello, World!")
    test("Simple Define", "[DEFINE x 10][VAR x]", "10")
    test("Basic Math", """
        [ADD 1 [SUB 2 [MUL 3 [DIV 4 4]]]]
    """, "0")
    test("Basic Legacy Math", """
        [MATH 1 + [MATH 2 - [MATH 3 * [MATH 4 / 4]]]]
    """, "0")
    test("Basic Comparison", """
        [COMPARE 2 > 3]
    """, "0")
    test("Basic Logic", """
        [IF [COMPARE 2 < 3] "yes" "no"]
    """, "yes")
    test("Basic Functions", """
        [FUNC SQUARE [ARGS "x"]
            [MUL [VAR x] [VAR x]]
        ]
        [SQUARE 5]
    """, "25")
    test("Map Test (Functions, Arrays)", """
        [FUNC MAP_SET [ARRAY "map" "key" "val"] [BLOCK
        [DEFINE ind [FIND [INDEX [VAR map] 0] [VAR key]]]
        [IF [COMPARE [VAR ind] == -1] [BLOCK
            [DEFINE keys [CONCAT [INDEX [VAR map] 0] [ARRAY [VAR key]]]]
            [DEFINE vals [CONCAT [INDEX [VAR map] 1] [ARRAY [VAR val]]]]
            [RETURN [ARRAY [VAR keys] [VAR vals]]]
        ] ""]
        [DEFINE vals [SETINDEX [INDEX [VAR map] 1] [VAR ind] [VAR val]]]
        [RETURN [SETINDEX [VAR map] 1 [VAR vals]]]
        ]]
        [FUNC MAP_GET [ARRAY "map" "key"] [BLOCK
        [DEFINE ind [FIND [INDEX [VAR map] 0] [VAR key]]]
        [RETURN [INDEX [INDEX [VAR map] 1] [VAR ind]]]
        ]]
        [DEFINE map [ARRAY {} {}]]
        [DEFINE map [MAP_SET [VAR map] "a" "1"]]
        [DEFINE map [MAP_SET [VAR map] "a" "2"]]
        [MAP_GET [VAR map] "a"]
    """, "2")

    test("Array Syntax", "{[J 10], [J 50]}", "['jjjjjjjjjj', 'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj'}")
    test("Array Syntax 2", "[INDEX {[J 10], [J 50]} 1]", "jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
    test("J", "[J 5]", "jjjjj")
    test("Built-in MAP", '[MAP [LENGTH [var "map.iterator"]] {1, 21, 101}]', "[1, 2, 3]")
    test("Built-in MAP 2", '[MAP [MUL [var "map.iterator"] 5] {1, 2, 3}]', "[5, 10, 15]")


if __name__ == "__main__":
    setupFunctions()
    # disableUselessPrints()
    print(Colours.WARNING + "Starting test..." + Colours.ENDC)
    testAll()

    print(Colours.ENDC + "\n\n==== TEST RESULTS ====")
    if Stats.failedTests == 0:
        print(Colours.OKGREEN + Colours.BOLD + f"All {Stats.num} tests passed!" + Colours.ENDC)
    elif Stats.failedTests < Stats.correctTests:
        print(Colours.WARNING + Colours.BOLD + f"{Stats.correctTests} / {Stats.num} passed..." + Colours.ENDC)
    else:
        print(Colours.FAIL + Colours.BOLD + f"{Stats.correctTests} / {Stats.num} passed..." + Colours.ENDC)

    print()  # newline
    for name in Stats.failedTestNames:
        print(Colours.FAIL + Colours.BOLD + "✘", name + Colours.ENDC)
