import numpy as np
from typing import List, Tuple, Dict
import math

class MelodyMatcher:
    def __init__(self):
        self.weights = {
            'dtw': 0.4,
            'levenshtein': 0.3,
            'lcs': 0.2,
            'cosine': 0.1
        }

    def dtw_distance(self, seq1: List[int], seq2: List[int]) -> float:
        """
        Dynamic Time Warping algorithm for tempo-independent melody matching
        """
        n, m = len(seq1), len(seq2)
        dtw_matrix = np.zeros((n + 1, m + 1))
        dtw_matrix.fill(float('inf'))
        dtw_matrix[0, 0] = 0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = abs(seq1[i-1] - seq2[j-1])
                dtw_matrix[i, j] = cost + min(
                    dtw_matrix[i-1, j],    # insertion
                    dtw_matrix[i, j-1],    # deletion
                    dtw_matrix[i-1, j-1]   # match
                )

        return dtw_matrix[n, m]

    def levenshtein_distance(self, seq1: List[int], seq2: List[int]) -> int:
        """
        Levenshtein Distance for note accuracy
        """
        n, m = len(seq1), len(seq2)
        dp = [[0 for _ in range(m + 1)] for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(
                        dp[i-1][j] + 1,    # deletion
                        dp[i][j-1] + 1,    # insertion
                        dp[i-1][j-1] + 1   # substitution
                    )

        return dp[n][m]

    def lcs_length(self, seq1: List[int], seq2: List[int]) -> int:
        """
        Longest Common Subsequence for sequence matching
        """
        n, m = len(seq1), len(seq2)
        dp = [[0 for _ in range(m + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        return dp[n][m]

    def cosine_similarity(self, seq1: List[int], seq2: List[int]) -> float:
        """
        Cosine Similarity for overall melody comparison
        """
        # Convert sequences to frequency vectors
        max_note = max(max(seq1), max(seq2)) + 1
        vec1 = np.zeros(max_note)
        vec2 = np.zeros(max_note)

        for note in seq1:
            vec1[note] += 1
        for note in seq2:
            vec2[note] += 1

        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def normalize_score(self, score: float, max_score: float) -> float:
        """
        Normalize scores to a 0-1 range
        """
        return 1 - (score / max_score) if max_score > 0 else 0

    def compare_melodies(self, melody1: List[int], melody2: List[int]) -> Dict[str, float]:
        """
        Compare two melodies using all algorithms and return weighted score
        """
        # Calculate individual scores
        dtw_score = self.dtw_distance(melody1, melody2)
        levenshtein_score = self.levenshtein_distance(melody1, melody2)
        lcs_score = self.lcs_length(melody1, melody2)
        cosine_score = self.cosine_similarity(melody1, melody2)

        # Normalize scores
        max_dtw = max(len(melody1), len(melody2)) * 127  # Assuming MIDI note range
        max_levenshtein = max(len(melody1), len(melody2))
        max_lcs = min(len(melody1), len(melody2))

        normalized_scores = {
            'dtw': self.normalize_score(dtw_score, max_dtw),
            'levenshtein': self.normalize_score(levenshtein_score, max_levenshtein),
            'lcs': lcs_score / max_lcs if max_lcs > 0 else 0,
            'cosine': cosine_score
        }

        # Calculate weighted final score
        final_score = sum(
            normalized_scores[algo] * weight 
            for algo, weight in self.weights.items()
        )

        return {
            'final_score': final_score,
            'individual_scores': normalized_scores
        } 