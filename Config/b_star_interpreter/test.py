from Config.b_star_interpreter.function_deco import setupFunctions
from Config.b_star_interpreter.run import runCode

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Test:
    def __init__(self, name: str, code: str, expected: str):
        self.name = name
        self.code = code
        self.expected = expected

    def correct(self):
        return self.output() == self.expected

    def output(self):
        return runCode(self.code).strip()

class TestManager:
    def __init__(self):
        self.tests = []

    def add(self, tests: list[Test]):
        self.tests.extend(tests)

    def run(self):
        for test in self.tests:
            correct = test.correct()
            output = test.output()

            if correct:
                print(bcolors.HEADER + test.name + bcolors.OKGREEN, ":", "SUCCESS!")
            elif output is Exception:
                print(bcolors.HEADER + test.name + bcolors.FAIL, ":", output)
            else:
                print(bcolors.HEADER + test.name + bcolors.WARNING, ":", "Failure...", output, "!=", test.expected)


if __name__ == "__main__":
    setupFunctions()
    main = TestManager()
    main.add([
        Test("10 J's", "[J 10]", "jjjjjjjjjj")
    ])

    main.run()