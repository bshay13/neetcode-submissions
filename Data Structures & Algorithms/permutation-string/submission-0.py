class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        # Handle the edge case where s1 is longer than s2
        if len(s1) > len(s2):
            return False

        # Create frequency arrays for s1 and the initial window of s2
        s1_freq = [0] * 26
        s2_freq = [0] * 26

        for i in range(len(s1)):
            s1_freq[ord(s1[i]) - ord('a')] += 1
            s2_freq[ord(s2[i]) - ord('a')] += 1

        # Check if the initial window is a permutation
        if s1_freq == s2_freq:
            return True

        # Slide the window across s2
        for i in range(len(s1), len(s2)):
            # Add the new character entering the window
            s2_freq[ord(s2[i]) - ord('a')] += 1
            # Remove the character leaving the window
            s2_freq[ord(s2[i - len(s1)]) - ord('a')] -= 1
            
            # Check for a match
            if s1_freq == s2_freq:
                return True

        # If the loop finishes, no permutation was found
        return False
        