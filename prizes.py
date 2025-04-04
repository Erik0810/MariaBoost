from datetime import datetime, timedelta
from typing import Optional, Dict

class Prize:
    def __init__(self, name: str, description: str, image: str = None):
        self.name = name
        self.description = description
        self.image = f'/static/images/{image}' if image else "blank"

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

class PrizeManager:
    def __init__(self):
        self._prizes: Dict[str, Prize] = {}
        self._load_default_prizes()

    def add_prize(self, year: int, week: int, prize: Prize) -> None:
        """Add a prize for a specific week"""
        if not 1 <= week <= 53:
            raise ValueError("Week number must be between 1 and 53")
        
        week_key = f"{year}-{week:02d}"
        self._prizes[week_key] = prize

    def get_prize(self, date: Optional[datetime] = None) -> Optional[Prize]:
        """Get prize for a specific date (defaults to current date)"""
        if date is None:
            date = datetime.now()
        
        # Get ISO week number (1-53)
        week_key = date.strftime("%Y-%V")
        return self._prizes.get(week_key)

    def get_week_key(self, date: Optional[datetime] = None) -> str:
        """Get the ISO week key for a date"""
        if date is None:
            date = datetime.now()
        return date.strftime("%Y-%V")

    def _load_default_prizes(self) -> None:
        """Load some default prizes for testing"""
        default_prizes = {
            (2025, 14): Prize(
                name="Kveld med Netflix",
                description="Sett deg ned og kos deg med en god film eller serie",
                image="Prize_Cinema.gif"
            ),
            (2025, 15): Prize(
                name="Spermageddon",
                description="Greit vi kan se spermageddon (om den fortsatt går, hvis ikke noe anna). + slush",
                image="Prize_Cinema.gif"
            ),
            (2025, 16): Prize(
                name="YT protein shake",
                description="El gains de bimbini",
                image="Prize.gif"
            ),
            (2025, 17): Prize(
                name="Strikkekveld",
                description="En kveld hvor du lærer meg å strikke",
                image="Prize_Knit.gif"
            ),
            (2025, 18): Prize(
                name="Pasta night",
                description="Vi cookåh pasta, my treat",
                image="Prize_Pasta.gif"
            ),
            (2025, 19): Prize(
                name="Massasje",
                description="30 minutters massasje når det passer deg",
                image="Prize_Massage.gif"
            ),
            (2025, 20): Prize(
                name="YT Protein Shake",
                description="Må huske på å la deg bli bøs også",
                image="Prize.gif"
            ),
            (2025, 21): Prize(
                name="Bakekveld",
                description="Vi baker noe digg, du velger hva",
                image="Prize_Baking.gif"
            ),
            (2025, 22): Prize(
                name="Spa-kveld",
                description="Ansiktsmaske, cream soda, søt-film, og snacks",
                image="Prize_Spa.gif"
            ),
            (2025, 23): Prize(
                name="YT Protein Shake",
                description="munch munch",
                image="Prize.gif"
            ),
            (2025, 24): Prize(
                name="Tur på museum",
                description="Du velgåh hvilket",
                image="Prize.gif"
            ),
            (2025, 25): Prize(
                name="Digital detox kveld",
                description="Sett deg ned med en god bok og en kopp te. Vi bruker ikke tlf hele kvelden",
                image="Prize.gif"
            ),
            (2025, 26): Prize(
                name="Fototur i botanisk hage",
                description="Vi tar en tur sammen og viser hverandre bildene når vi er ferdige",
                image="Prize.gif"
            ),
            (2025, 27): Prize(
                name="Hjemmetrening",
                description="Vi trener sammen hjemme",
                image="Prize.gif"
            ),
            (2025, 28): Prize(
                name="Matlaging",
                description="Lag en ny oppskrift sammen",
                image="Prize.gif"
            ),
            (2025, 29): Prize(
                name="Vin og ost",
                description="Smaking av forskjellige viner og oster",
                image="Prize.gif"
            ),
            (2025, 30): Prize(
                name="DIY-prosjekt",
                description="Start på et kreativt prosjekt hjemme",
                image="Prize.gif"
            )
        }

        for (year, week), prize in default_prizes.items():
            self.add_prize(year, week, prize)

    def list_all_prizes(self) -> Dict[str, Prize]:
        """Get all prizes (for admin purposes)"""
        return self._prizes.copy()

    def add_prizes_for_next_weeks(self, start_date: datetime, num_weeks: int, prize: Prize) -> None:
        """Add the same prize for multiple future weeks"""
        current_date = start_date
        for _ in range(num_weeks):
            year = current_date.year
            week = int(current_date.strftime("%V"))
            self.add_prize(year, week, prize)
            current_date += timedelta(weeks=1)

# Create a singleton instance
prize_manager = PrizeManager()

# Example usage:
if __name__ == "__main__":
    # Add a specific prize
    special_prize = Prize(
        name="Special Weekend",
        description="Spa day",
        image="spa.jpg"
    )
    
    # Get current week's prize
    current_prize = prize_manager.get_prize()
    if current_prize:
        print(f"This week's prize: {current_prize}")
    
    # Add same prize for next 4 weeks
    start_date = datetime.now() + timedelta(weeks=1)
    prize_manager.add_prizes_for_next_weeks(
        start_date,
        num_weeks=4,
        prize=special_prize
    )