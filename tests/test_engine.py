"""
Unit tests for Roommie — covers:
  • DefaultScoringStrategy  (habit, language, vibe scoring)
  • MatchingEngine           (budget filter, tier labels, ordering)
  • UserFactory              (correct types, invalid role)
  • Encapsulation validators (age, monthly_rent, max_budget)
"""

import unittest

from models import HouseOwner, HouseSeeker, UserFactory
from models.scoring_strategy import DefaultScoringStrategy
from engine import MatchingEngine


# ---------------------------------------------------------------------------
# Helpers — build minimal valid users without repeating boilerplate
# ---------------------------------------------------------------------------

def _owner(**overrides) -> HouseOwner:
    defaults = dict(
        user_id=1, name="Owner", age=30, gender="male",
        occupation="Artist", bio="bio", avatar_url="",
        habits=["Clean", "Quiet"],
        languages=["English"],
        neighborhood="Užupis",
        monthly_rent=600,
    )
    defaults.update(overrides)
    return HouseOwner(**defaults)


def _seeker(**overrides) -> HouseSeeker:
    defaults = dict(
        user_id=2, name="Seeker", age=24, gender="female",
        occupation="Designer", bio="bio", avatar_url="",
        habits=["Clean", "Creative"],
        languages=["English"],
        max_budget=650,
        preferred_neighborhoods=["Užupis"],
    )
    defaults.update(overrides)
    return HouseSeeker(**defaults)


# ---------------------------------------------------------------------------
# DefaultScoringStrategy
# ---------------------------------------------------------------------------

class TestHabitScore(unittest.TestCase):
    def setUp(self):
        self.s = DefaultScoringStrategy()

    def test_full_overlap(self):
        o = _owner(habits=["Clean", "Quiet"])
        sk = _seeker(habits=["Clean", "Quiet"])
        # shared=2, union=2 → 2/2 * 70 = 70
        self.assertAlmostEqual(self.s.habit_score(o, sk), 70.0)

    def test_partial_overlap(self):
        o = _owner(habits=["Clean", "Quiet", "Non-smoker"])
        sk = _seeker(habits=["Clean", "Creative"])
        # shared={"Clean"}, union=4 → 1/4 * 70 = 17.5
        self.assertAlmostEqual(self.s.habit_score(o, sk), 17.5)

    def test_no_overlap(self):
        o = _owner(habits=["Quiet"])
        sk = _seeker(habits=["Social"])
        self.assertAlmostEqual(self.s.habit_score(o, sk), 0.0)

    def test_empty_habits_both(self):
        o = _owner(habits=[])
        sk = _seeker(habits=[])
        self.assertAlmostEqual(self.s.habit_score(o, sk), 0.0)


class TestLanguageScore(unittest.TestCase):
    def setUp(self):
        self.s = DefaultScoringStrategy()

    def test_full_overlap(self):
        o = _owner(languages=["English", "Lithuanian"])
        sk = _seeker(languages=["English", "Lithuanian"])
        # 2/2 * 20 = 20
        self.assertAlmostEqual(self.s.language_score(o, sk), 20.0)

    def test_partial_overlap(self):
        o = _owner(languages=["English", "Lithuanian"])
        sk = _seeker(languages=["English", "German"])
        # shared={"English"}, union=3 → 1/3 * 20 ≈ 6.666
        self.assertAlmostEqual(self.s.language_score(o, sk), 20 / 3, places=3)

    def test_no_overlap(self):
        o = _owner(languages=["Lithuanian"])
        sk = _seeker(languages=["German"])
        self.assertAlmostEqual(self.s.language_score(o, sk), 0.0)


class TestVibeScore(unittest.TestCase):
    def setUp(self):
        self.s = DefaultScoringStrategy()

    def test_same_category_earns_bonus(self):
        # Artist + Designer are both "creative"
        o = _owner(occupation="Artist")
        sk = _seeker(occupation="Designer")
        self.assertAlmostEqual(self.s.vibe_score(o, sk), 10.0)

    def test_same_tech_category(self):
        o = _owner(occupation="Software Developer")
        sk = _seeker(occupation="Engineer")
        self.assertAlmostEqual(self.s.vibe_score(o, sk), 10.0)

    def test_different_categories_no_bonus(self):
        o = _owner(occupation="Chef")       # food
        sk = _seeker(occupation="Designer") # creative
        self.assertAlmostEqual(self.s.vibe_score(o, sk), 0.0)

    def test_unknown_occupations_no_bonus(self):
        o = _owner(occupation="Astronaut")
        sk = _seeker(occupation="Astronaut")
        self.assertAlmostEqual(self.s.vibe_score(o, sk), 0.0)

    def test_composite_capped_at_100(self):
        # Construct users where raw sum would exceed 100
        o = _owner(habits=["A", "B"], languages=["X"], occupation="Artist")
        sk = _seeker(habits=["A", "B"], languages=["X"], occupation="Designer")
        self.assertLessEqual(self.s.score(o, sk), 100.0)


# ---------------------------------------------------------------------------
# MatchingEngine
# ---------------------------------------------------------------------------

class TestBudgetFilter(unittest.TestCase):
    def setUp(self):
        self.engine = MatchingEngine()

    def test_seeker_too_poor_excluded(self):
        # rent=600, budget=400 → 400 < 600-100=500 → excluded
        o = _owner(monthly_rent=600)
        sk = _seeker(max_budget=400)
        self.assertEqual(self.engine.find_matches(sk, [o]), [])

    def test_seeker_at_margin_boundary_included(self):
        # rent=600, budget=500 → 500 == 600-100 → included
        o = _owner(monthly_rent=600)
        sk = _seeker(max_budget=500, preferred_neighborhoods=["Užupis"])
        matches = self.engine.find_matches(sk, [o])
        self.assertEqual(len(matches), 1)

    def test_seeker_above_rent_included(self):
        o = _owner(monthly_rent=500)
        sk = _seeker(max_budget=700, preferred_neighborhoods=["Užupis"])
        self.assertEqual(len(self.engine.find_matches(sk, [o])), 1)


class TestTierLabels(unittest.TestCase):
    def setUp(self):
        self.engine = MatchingEngine()

    def test_preferred_neighbourhood_is_perfect(self):
        o = _owner(neighborhood="Užupis")
        sk = _seeker(preferred_neighborhoods=["Užupis"], max_budget=650)
        _, _, label = self.engine.find_matches(sk, [o])[0]
        self.assertEqual(label, "Perfect")

    def test_non_preferred_neighbourhood_is_suggested(self):
        o = _owner(neighborhood="Šnipiškės")
        sk = _seeker(preferred_neighborhoods=["Užupis"], max_budget=650)
        _, _, label = self.engine.find_matches(sk, [o])[0]
        self.assertEqual(label, "Suggested")

    def test_perfect_ranked_before_suggested(self):
        perfect_o   = _owner(user_id=1, neighborhood="Užupis",    monthly_rent=600)
        suggested_o = _owner(user_id=2, name="O2", neighborhood="Šnipiškės", monthly_rent=600)
        sk = _seeker(preferred_neighborhoods=["Užupis"], max_budget=700)
        matches = self.engine.find_matches(sk, [suggested_o, perfect_o])
        self.assertEqual(matches[0][2], "Perfect")
        self.assertEqual(matches[1][2], "Suggested")

    def test_same_role_returns_empty(self):
        o1 = _owner(user_id=1)
        o2 = _owner(user_id=2, name="O2")
        self.assertEqual(self.engine.find_matches(o1, [o2]), [])

    def test_custom_strategy_is_used(self):
        class ZeroStrategy(DefaultScoringStrategy):
            def score(self, a, b) -> float:
                return 0.0

        engine = MatchingEngine(strategy=ZeroStrategy())
        o  = _owner()
        sk = _seeker(preferred_neighborhoods=["Užupis"])
        matches = engine.find_matches(sk, [o])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0][1], 0.0)


# ---------------------------------------------------------------------------
# UserFactory
# ---------------------------------------------------------------------------

class TestUserFactory(unittest.TestCase):
    def test_creates_house_owner(self):
        user = UserFactory.create(
            "House Owner",
            user_id=10, name="Test", age=30, gender="male",
            occupation="Chef", bio="bio", avatar_url="",
            habits=["Clean"], languages=["English"],
            neighborhood="Užupis", monthly_rent=500,
        )
        self.assertIsInstance(user, HouseOwner)

    def test_creates_house_seeker(self):
        user = UserFactory.create(
            "House Seeker",
            user_id=11, name="Test", age=22, gender="female",
            occupation="Designer", bio="bio", avatar_url="",
            habits=["Quiet"], languages=["English"],
            max_budget=600, preferred_neighborhoods=["Užupis"],
        )
        self.assertIsInstance(user, HouseSeeker)

    def test_owner_has_correct_attributes(self):
        user = UserFactory.create(
            "House Owner",
            user_id=12, name="Eglė", age=24, gender="female",
            occupation="Artist", bio="bio", avatar_url="",
            habits=["Quiet"], languages=["Lithuanian"],
            neighborhood="Užupis", monthly_rent=600,
        )
        self.assertEqual(user.neighborhood, "Užupis")
        self.assertEqual(user.monthly_rent, 600)

    def test_seeker_has_correct_attributes(self):
        user = UserFactory.create(
            "House Seeker",
            user_id=13, name="Domas", age=25, gender="male",
            occupation="Engineer", bio="bio", avatar_url="",
            habits=["Quiet"], languages=["Lithuanian"],
            max_budget=700, preferred_neighborhoods=["Šnipiškės"],
        )
        self.assertEqual(user.max_budget, 700)
        self.assertEqual(user.preferred_neighborhoods, ["Šnipiškės"])

    def test_invalid_role_raises_value_error(self):
        with self.assertRaises(ValueError):
            UserFactory.create("Visitor", user_id=1, name="X", age=20)


# ---------------------------------------------------------------------------
# Encapsulation validators
# ---------------------------------------------------------------------------

class TestAgeValidation(unittest.TestCase):
    def test_age_below_minimum_raises(self):
        with self.assertRaises(ValueError):
            _owner(age=15)

    def test_age_above_maximum_raises(self):
        with self.assertRaises(ValueError):
            _owner(age=121)

    def test_age_at_lower_boundary_valid(self):
        self.assertEqual(_owner(age=16).age, 16)

    def test_age_at_upper_boundary_valid(self):
        self.assertEqual(_owner(age=120).age, 120)

    def test_age_property_setter_rejects_update(self):
        u = _owner(age=25)
        with self.assertRaises(ValueError):
            u.age = 5


class TestMonthlyRentValidation(unittest.TestCase):
    def test_zero_rent_raises(self):
        with self.assertRaises(ValueError):
            _owner(monthly_rent=0)

    def test_negative_rent_raises(self):
        with self.assertRaises(ValueError):
            _owner(monthly_rent=-100)

    def test_positive_rent_valid(self):
        self.assertEqual(_owner(monthly_rent=1).monthly_rent, 1)


class TestMaxBudgetValidation(unittest.TestCase):
    def test_zero_budget_raises(self):
        with self.assertRaises(ValueError):
            _seeker(max_budget=0)

    def test_negative_budget_raises(self):
        with self.assertRaises(ValueError):
            _seeker(max_budget=-50)

    def test_positive_budget_valid(self):
        self.assertEqual(_seeker(max_budget=1).max_budget, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
