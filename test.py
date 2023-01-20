import argparse

parser = argparse.ArgumentParser(description="The ArchCraftsman installer.")
parser.add_argument('-t', '--test', action='store_const', const=True, default=False,
                    help='Used to test the installer. No command will be executed.')
args = parser.parse_args()
print(args)
print(args.test)
