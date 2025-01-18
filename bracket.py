from competitor import Competitor
from match import Match
import math

class Bracket:
    def __init__(self, competitors):
        self.competitors = competitors
        self.rounds = []  # List of all rounds
        self.current_round = 0  # Current round index
        self.generate_bracket()

    def generate_bracket(self):
        """Generate the tournament bracket."""
        competitors = [Competitor(name, "") for name in self.competitors]

        # Ensure competitors count is a power of 2
        next_power_of_2 = 2 ** math.ceil(math.log2(len(competitors)))
        while len(competitors) < next_power_of_2:
            competitors.append(Competitor("TBD", ""))

        # First round
        self.rounds.append([Match(competitors[i], competitors[i + 1]) for i in range(0, len(competitors), 2)])

    def get_current_round_matches(self):
        """Return the matches for the current round."""
        return self.rounds[self.current_round]

    def advance_to_next_round(self):
        """Move to the next round with the current round's winners."""
        current_matches = self.get_current_round_matches()
        winners = [match.get_winner() for match in current_matches if match.get_winner()]

        if len(winners) < 2:
            return None  # Tournament is over

        next_round_matches = [Match(winners[i], winners[i + 1] if i + 1 < len(winners) else None) for i in range(0, len(winners), 2)]
        self.rounds.append(next_round_matches)
        self.current_round += 1
        return next_round_matches
