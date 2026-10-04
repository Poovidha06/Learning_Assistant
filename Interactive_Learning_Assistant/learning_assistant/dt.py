# The program must accept a string S and an integer X as the input. The program must print two string values based on the following conditions.

# - For each 1s from MSB in the binary representation of X, the program must toggle the characters in the same position to upper case and for each Os, the program must toggle the characters to lower case. The remaining characters in the string S must not be altered. Then the program must print the modified string in the first line of output.

# - For each 1s from LSB in the binary representation of X, the program must toggle the characters in the same position to upper case and for each Os, the program must toggle the characters to lower case. The remaining characters in the string S must not be altered. Then the program must print the modified string in the second line of output

# Note: The length of the string S is always greater than or equal to the number of bits in the binary representation of X

# Boundary Condition(s):

# 1 <= Length of S <= 100

# 1 < X <= 10^8
# Input Format:

# The first line contains S.

# The second line contains X.

# Output Format:

# The first line contains a string value.

# The second line contains a string value.

# Example Input/Output 1:

# Input

# BasketBall

# 23

# Output

# BaSKEtBall

# BaskeTbALL

# Explanation:

# Here the given string is BasketBall and the value of K is 23.

# The binary representation of 23 is 10111.

# BasketBall -> BaSKEtBall

# BasketBall -> BaskeTbALL

# Example Input/Output 2:

# Input

# PAPER

# 10

# Output:

# PaPeR

# PApEr

s = input()
x = int(input())

# Get the binary representation of X and remove the '0b' prefix
binary_x = bin(x)[2:]

# --- First Condition: MSB (Most Significant Bit) to LSB (Least Significant Bit) ---

# Create a list from the string to easily modify characters
result1 = list(s)

# Iterate through the binary representation of X
for i in range(len(binary_x)):
    # The character in the string to be modified is at the same index as the bit
    if binary_x[i] == '1':
        # If the bit is '1', convert the character to uppercase
        result1[i] = result1[i].upper()
    else:
        # If the bit is '0', convert the character to lowercase
        result1[i] = result1[i].lower()

# Join the list of characters back into a string and print it
print("".join(result1))

# --- Second Condition: LSB (Least Significant Bit) to MSB (Most Significant Bit) ---

# Create a new list from the original string for the second modification
result2 = list(s)

# Calculate the starting index for modification from the right side of the string
start_index = len(s) - len(binary_x)

# Iterate through the binary representation of X
for i in range(len(binary_x)):
    # The character to modify is at the start_index plus the current loop index
    if binary_x[i] == '1':
        # If the bit is '1', convert the character to uppercase
        result2[start_index + i] = result2[start_index + i].upper()
    else:
        # If the bit is '0', convert the character to lowercase
        result2[start_index + i] = result2[start_index + i].lower()

# Join the modified list of characters back into a string and print it
print("".join(result2))