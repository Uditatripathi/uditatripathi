void main() {
    int num;
    int reversed;
    int remainder;
    int original;
    
    reversed = 0;
    
    printf("Enter an integer: ");
    num = 5;  // Since we don't support scanf, I'm setting a default value
    
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
