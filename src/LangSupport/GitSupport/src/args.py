import sys

from src.io_write import error


class Args:
    def __init__(self, arg_list):
        self.arg_list = arg_list
        self.process_args()

    def process_args(self):
        args = iter(self.arg_list)
        arg_dict = {}
        for arg in args:
            try:
                arg_dict[arg] = next(args)
            except StopIteration:
                error("Invalid Arguments")
                sys.exit(1)  # If the args are not specified like "-a b", it will be Invalid

        self.arg_list = arg_dict

    def define_action(self):
        pass


if __name__ == '__main__':
    Args(sys.argv[1:])
