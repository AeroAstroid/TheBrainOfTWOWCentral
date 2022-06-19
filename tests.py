from src.interpreter.function_deco import setupFunctions
from src.interpreter.globals import debug

from src.interpreter.run import runCodeSandbox


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
        correct = output == assumption
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
    """, "0.0")
    test("Basic Legacy Math", """
        [MATH 1 + [MATH 2 - [MATH 3 * [MATH 4 / 4]]]]
    """, "0.0")
    test("Basic Comparison", """
        [COMPARE 2 > 3]
    """, "False")
    test("Basic Logic", """
        [IF [COMPARE 2 < 3] "yes" "no"]
    """, "yes")
    test("Basic Functions", """
        [FUNC SQUARE [ARGS "x"]
            [MUL [VAR x] [VAR x]]
        ]
        [SQUARE 5]
    """, "25")

    test("J", "[J 5]", "jjjjj")


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
