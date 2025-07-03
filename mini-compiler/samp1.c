void main() {

    // Example 1: Basic arithmetic and control flow

    int x;

    int y;

    float result;



    x = 10;

    y = 5;

    result = x + y * 2;

    printf("Example 1 - Initial result: %f\n", result);



    if (result > 20) {

        result = result - 10;

        printf("Result was > 20, subtracted 10: %f\n", result);

    } else {

        result = result + 5;

        printf("Result was <= 20, added 5: %f\n", result);

    }



    while (x > 0) {

        x = x - 1;

        result = result + 1;

        printf("In while loop, x = %d, result = %f\n", x, result);

    }



    // Example 2: Palindrome number checker

    int num;

    int reversed;

    int remainder;

    int original;

    

    reversed = 0;

    printf("\nExample 2 - Palindrome Checker\n");

    printf("Testing number: ");

    num = 121;  // Testing with palindrome number 121

    printf("%d\n", num);

    

    original = num;

    

    while (num != 0) {

        remainder = num % 10;

        reversed = reversed * 10 + remainder;

        num = num / 10;

    }

    

    if (original == reversed) {

        printf("%d is a palindrome.\n", original);

    } else {

        printf("%d is not a palindrome.\n", original);

    }

}
