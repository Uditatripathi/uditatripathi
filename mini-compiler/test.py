# Generated Python code
import sys

def main():
    x = None
    y = None
    result = None
    x = 10
    y = 5
    result = (x + (y * 2))
    print("Initial result: %f\n" % (result))
    if (result > 20):
        result = (result - 10)
        print("Result was > 20, subtracted 10: %f\n" % (result))
    else:
        result = (result + 5)
        print("Result was <= 20, added 5: %f\n" % (result))
    while (x > 0):
        x = (x - 1)
        result = (result + 1)
        print("In while loop, x = %d, result = %f\n" % (x, result))

if __name__ == "__main__":
    main()