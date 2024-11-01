from pydantic import BaseModel, Field
from pydantic_extra_types.coordinate import Latitude, Longitude
from typing import Literal
import random


class Unit(BaseModel):
    id: int | None = Field(default=None)
    affilitation: Literal['friendly', 'hostile', 'unknown', 'neutral']
    # TODO: dimension: Literal['air', 'space', 'ground', 'sea_surface', 'sea_subsurface']  # defines the primary mission area for the operational object within the battlespace
    callsign: str | None = Field(examples=['ALPHA-1', 'BRAVO-2', 'CHARLIE-3'])
    latitude: Latitude
    longitude: Longitude

    # Sorting
    def __lt__(self, other):
        if self.affilitation != other.affiliation:
            # Sort by affilitation first
            affiliation_order = {'friendly': 0, 'hostile': 1, 'unknown': 2, 'neutral': 3}
            return affiliation_order[self.affilitation] < affiliation_order[other.affilitation]
        else:
            # If same affiliation, sort by callsign
            return self.callsign < other.callsign
        
    def simulate_movement(self):
        # Simulate a small random movement within a 0.01 degree range
        self.latitude += random.uniform(-0.01, 0.01)
        self.longitude += random.uniform(-0.01, 0.01)
