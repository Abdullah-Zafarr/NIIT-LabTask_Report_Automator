#include <iostream>
using namespace std;

// Check whether a number is even or odd
bool isEven(int n) {
    return n % 2 == 0;
}

int main() {
    int number;
    cout << "Enter a number: ";
    cin >> number;

    if (isEven(number)) {
        cout << number << " is even" << endl;
    } else {
        cout << number << " is odd" << endl;
    }

    // Print the first five multiples of the number
    for (int i = 1; i <= 5; i++) {
        cout << number << " x " << i << " = " << number * i << endl;
    }

    int sum = 0;
    for (int i = 1; i <= number; i++) {
        sum += i;
    }
    cout << "Sum from 1 to " << number << " is " << sum << endl;
    return 0;
}
