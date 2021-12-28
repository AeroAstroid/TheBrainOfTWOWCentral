from typing import List, Dict


class UserFunction:
    def __init__(self, name: str, args: Dict[int, str], block: List[str], global_func: bool, codebase):
        self.args = args
        self.block = block
        self.codebase = codebase

        if global_func:
            codebase.functions[name] = self

    def run(self, args: List[str]):
        print(f"{args} > {self.args} > {self.block} > {self.block[0]} > {self.block[0][0]}")

        # TODO: There is definitely a faster way to do this (3 nested for loops is terrible)
        # TODO: Use numpy for arrays and stuff
        # for example maybe creating a lambda that already knows where to replace the variables
        # instead iterating through the entire code block
        # (interpreting within interpreting)
        # main_buffer = []
        main_buffer = self.enumerateList(self.block, args)
        # if len(block_buffer) > 1:
        #     main_buffer.append(block_buffer)
        # else:
        #     main_buffer.append(block_buffer[0])
        return main_buffer

    def enumerateList(self, block: List[str], args: List[str]):
        block_buffer = []
        for part in block:
            # recursion moment
            if isinstance(part, List):
                block_buffer.append(self.enumerateList(part, args))

            isarg = False
            for i, argument in self.args.items():
                if part == argument:
                    isarg = True
                    block_buffer.append(str(args[i]))
            if not isarg:
                block_buffer.append(part)
        return block_buffer
