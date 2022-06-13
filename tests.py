from src.interpreter.function_deco import setupFunctions

from src.interpreter.run import runCode


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
    failedTests = 0


def test(name, code, assumption):
    result = runCode(code)
    correct = result == assumption
    if correct:
        print(Colours.OKGREEN + Colours.BOLD + "✔", name, Colours.ENDC)
        Stats.correctTests += 1
    else:
        print(Colours.FAIL + Colours.BOLD + "✘", name, end="")
        print(f" (Wanted '{assumption}', Got '{result}')")
        Stats.failedTests += 1
    Stats.num += 1


def testAll():
    test("J", "[J 2]", "jj")
    test("J Pt. 2", "[J 0]", "j")
    test("J Pt. 3", "[J -9]", "j")
    test("J Final Boss", "[J 100]",
         "jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")


if __name__ == "__main__":
    setupFunctions()
    print(Colours.WARNING + "Starting test..." + Colours.ENDC)
    testAll()

    print()
    if Stats.failedTests == 0:
        print(Colours.OKGREEN + Colours.BOLD + f"All {Stats.num} tests passed!" + Colours.ENDC)
    elif Stats.failedTests < Stats.correctTests:
        print(Colours.WARNING + Colours.BOLD + f"{Stats.correctTests} / {Stats.num} passed..." + Colours.ENDC)
    else:
        print(Colours.FAIL + Colours.BOLD + f"{Stats.correctTests} / {Stats.num} passed..." + Colours.ENDC)

