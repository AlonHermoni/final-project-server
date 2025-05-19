import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.melody_matcher import MelodyMatcher

class TestMelodyMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = MelodyMatcher()
        
        # Sample melodies for testing
        self.melodies = {
            'twinkle_twinkle': [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60],  # Twinkle Twinkle Little Star
            'happy_birthday': [60, 60, 62, 60, 65, 64, 60, 60, 62, 60, 67, 65],  # Happy Birthday
            'jingle_bells': [67, 67, 67, 67, 67, 67, 67, 69, 60, 62, 64],  # Jingle Bells
            'mary_had_little_lamb': [64, 62, 60, 62, 64, 64, 64, 62, 62, 62, 64, 67, 67],  # Mary Had a Little Lamb
            'ode_to_joy': [67, 67, 69, 71, 71, 69, 67, 65, 64, 64, 65, 67, 67, 65, 65]  # Ode to Joy
        }

    def test_identical_melodies(self):
        """Test that identical melodies get a perfect score"""
        result = self.matcher.compare_melodies(
            self.melodies['twinkle_twinkle'],
            self.melodies['twinkle_twinkle']
        )
        self.assertAlmostEqual(result['final_score'], 1.0, places=2)
        self.assertAlmostEqual(result['individual_scores']['dtw'], 1.0, places=2)
        self.assertAlmostEqual(result['individual_scores']['levenshtein'], 1.0, places=2)
        self.assertAlmostEqual(result['individual_scores']['lcs'], 1.0, places=2)
        self.assertAlmostEqual(result['individual_scores']['cosine'], 1.0, places=2)

    def test_similar_melodies(self):
        """Test that similar melodies get high scores"""
        # Test with transposed melody (same melody, different key)
        original = self.melodies['twinkle_twinkle']
        transposed = [note + 2 for note in original]  # Transpose up by 2 semitones
        result = self.matcher.compare_melodies(original, transposed)
        self.assertGreater(result['final_score'], 0.7)  # Should be quite similar

    def test_different_melodies(self):
        """Test that different melodies get lower scores"""
        result = self.matcher.compare_melodies(
            self.melodies['twinkle_twinkle'],
            self.melodies['happy_birthday']
        )
        self.assertLess(result['final_score'], 0.5)  # Should be quite different

    def test_empty_melodies(self):
        """Test handling of empty melodies"""
        result = self.matcher.compare_melodies([], [])
        self.assertEqual(result['final_score'], 0.0)

    def test_different_lengths(self):
        """Test melodies of different lengths"""
        short_melody = self.melodies['twinkle_twinkle'][:5]
        long_melody = self.melodies['twinkle_twinkle']
        result = self.matcher.compare_melodies(short_melody, long_melody)
        self.assertGreater(result['final_score'], 0.0)
        self.assertLess(result['final_score'], 1.0)

    def test_all_melody_pairs(self):
        """Test all possible pairs of our sample melodies"""
        melody_names = list(self.melodies.keys())
        for i in range(len(melody_names)):
            for j in range(i + 1, len(melody_names)):
                melody1 = self.melodies[melody_names[i]]
                melody2 = self.melodies[melody_names[j]]
                result = self.matcher.compare_melodies(melody1, melody2)
                
                # Verify score is between 0 and 1
                self.assertGreaterEqual(result['final_score'], 0.0)
                self.assertLessEqual(result['final_score'], 1.0)
                
                # Verify all individual scores are between 0 and 1
                for score in result['individual_scores'].values():
                    self.assertGreaterEqual(score, 0.0)
                    self.assertLessEqual(score, 1.0)

    def test_single_note_melodies(self):
        """Test melodies with single notes"""
        result = self.matcher.compare_melodies([60], [60])
        self.assertEqual(result['final_score'], 1.0)
        
        result = self.matcher.compare_melodies([60], [72])
        self.assertLess(result['final_score'], 1.0)

if __name__ == '__main__':
    unittest.main() 