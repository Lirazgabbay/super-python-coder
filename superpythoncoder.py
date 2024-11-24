#superpythoncoder.py
import random
import subprocess
import os

from chat_app import  process_and_execute_code

def suggest_random_program():
    """Suggest a random program idea if the user doesn't provide one."""
    # List of programming problems to solve
    PROGRAMS_LIST = [
        # # Problem 1: String Interleaving
        # """Create a program that prints all interleavings of two given strings.
        # Requirements:
        # - Take two input strings str1 and str2
        # - Print all possible interleavings of the strings
        # - Assume all characters in both strings are different
        # Example:
        # Input: str1 = "AB", str2 = "CD"
        # Output:
        # ABCD
        # ACBD
        # ACDB
        # CABD
        # CADB
        # CDAB""",

        # # Problem 2: Palindrome Number
        # """Create a program that checks if a number is a palindrome.
        # Requirements:
        # - Take a number as input
        # - Return True if it's a palindrome, False otherwise
        # - Handle negative numbers and edge cases""",

        # # Problem 3: BST K-th Element
        # """Create a program that finds the kth smallest element in a binary search tree.
        # Requirements:
        # - Implement a binary search tree
        # - Find the kth smallest element
        # - Handle edge cases (empty tree, k > tree size)
        # - Use efficient traversal methods"""

        #problem 4: shortest-path-in-a-grid-with-obstacles-elimination
        """ You are given an m x n integer matrix grid where each cell is either 0 (empty) or 1 (obstacle). You can move up, down, left, or right from and to an empty cell in one step.
            Return the minimum number of steps to walk from the upper left corner (0, 0) to the lower right corner (m - 1, n - 1) given that you can eliminate at most k obstacles. If it is not possible to find such walk return -1.
            
            Example 1:
            Input: grid = [[0,0,0],[1,1,0],[0,0,0],[0,1,1],[0,0,0]], k = 1
            Output: 6
            Explanation: 
            The shortest path without eliminating any obstacle is 10.
            The shortest path with one obstacle elimination at position (3,2) is 6. Such path is (0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2) -> (3,2) -> (4,2).

            Example 2:
            Input: grid = [[0,1,1],[1,1,1],[1,0,0]], k = 1
            Output: -1
            Explanation: We need to eliminate at least two obstacles to find such a walk.""",

        # #problem 5:  Find Median from Data Stream
        # """The median is the middle value in an ordered integer list. If the size of the list is even, there is no middle value, and the median is the mean of the two middle values.
        # For example, for arr = [2,3,4], the median is 3.
        # For example, for arr = [2,3], the median is (2 + 3) / 2 = 2.5.
        # Implement the MedianFinder class:

        # MedianFinder() initializes the MedianFinder object.
        # void addNum(int num) adds the integer num from the data stream to the data structure.
        # double findMedian() returns the median of all elements so far. Answers within 10-5 of the actual answer will be accepted.
        
        # Example 1:
        # Input
        # ["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"]
        # [[], [1], [2], [], [3], []]
        # Output
        # [null, null, null, 1.5, null, 2.0]

        # Explanation
        # MedianFinder medianFinder = new MedianFinder();
        # medianFinder.addNum(1);    // arr = [1]
        # medianFinder.addNum(2);    // arr = [1, 2]
        # medianFinder.findMedian(); // return 1.5 (i.e., (1 + 2) / 2)
        # medianFinder.addNum(3);    // arr[1, 2, 3]
        # medianFinder.findMedian(); // return 2.0
        # """
    ]

    return random.choice(PROGRAMS_LIST)

def super_python_coder():
    print(f"Welcome to Super Python Coder. Tell me, which program you would like me to code for you? If you don't have an idea, just press enter and I will choose a random progeam to code")
    user_input = input("Your program idea: ").strip()
    if not user_input:
        chosen_program = suggest_random_program()
        print(f"Here's an idea: {chosen_program}")
        return chosen_program
    else:
        print(f"Great! Let's create a program for: {user_input}")
        return user_input
    
if __name__ == "__main__":
    filename = "generatedcode.py"
    prompt = super_python_coder()
    if process_and_execute_code(prompt, filename):
        print("Code creation completed successfully!")
    try:
        file_path = os.path.abspath(filename)
        if os.path.exists(filename):
            subprocess.call(["start","", file_path], shell=True)
        else:
            print(f"Error: The file {filename} was not created.")
    except Exception as e:
        print(f"Could not open the file: {e}")   