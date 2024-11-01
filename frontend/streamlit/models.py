from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from pydantic_extra_types.coordinate import Latitude, Longitude
from typing import Literal, Optional, Annotated, Dict, List
from geojson_pydantic import Feature, Point
import random


# ------------------------------------------------------------------------------
#  Basic Unit models
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
#  MIL-STD-2525D Unit Symbol models
# ------------------------------------------------------------------------------
PyObjectId = Annotated[str, BeforeValidator(str)]

class UnitFeatureModel(Feature[Point, Dict]):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [13.38272, 52.46385],
                },
                "properties": {
                    "sidc": "SFGPUCIZ--------",
                    "uniqueDesignation": "Friendly-1",
                }
            }
        }
    )


class UpdateUnitFeatureModel(Feature[Point, Dict]):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [13.38272, 52.46385],
                },
                "properties": {
                    "sidc": "SFGPUCIZ--------",
                    "uniqueDesignation": "Friendly-1",
                }
            }
        }
    )


class UnitFeatureCollection(BaseModel):
    features: List[UnitFeatureModel]
