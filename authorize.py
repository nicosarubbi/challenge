import sys
import accounts
import business_logic


if __name__ == '__main__':
    for line in sys.stdin:
        line = line.strip()
        operation = accounts.Operation.parse(line)
        if operation:
            print(operation)

