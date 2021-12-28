from typing import List, Dict, Callable


class UserFunction:
    def __init__(self, name: str, args: Dict[int, str], block: List[str], codebase):
        self.args = args
        self.block = block
        self.codebase = codebase

        codebase.functions[name] = self

    def run(self, args: List[str]):
        print(f"{args} > {self.args} > {self.block} > {self.block[0]} > {self.block[0][0]}")

        # TODO: There is definitely a faster way to do this
        # TODO: Use numpy for arrays and stuff
        # for example maybe creating a lambda that already knows where to replace the variables
        # instead iterating through the entire code block
        # (interpreting within interpreting)
        buffer = []
        for part in self.block[0]:
            isarg = False
            for i, argument in self.args.items():
                if part == argument:
                    isarg = True
                    buffer.append(args[i])
            if not isarg:
                buffer.append(part)
        return buffer
