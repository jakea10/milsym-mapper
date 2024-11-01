from pydantic_extra_types.coordinate import Latitude, Longitude
import sqlmodel
from typing import Literal, Optional, Annotated, Dict, List
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from geojson_pydantic import Feature, Point


# ------------------------------------------------------------------------------
#  Basic Unit models
# ------------------------------------------------------------------------------
class Unit(sqlmodel.SQLModel, table=True):
    """ Basic Unit class """
    # id: int | None = Field(default=None, primary_key=True)
    callsign: str | None = sqlmodel.Field(default=None, primary_key=True)
    affilitation: str  #Literal['friendly', 'neutral', 'hostile', 'unknown']
    latitude: Latitude
    longitude: Longitude


class UnitUpdate(sqlmodel.SQLModel):
    callsign: str
    affiliation: Literal['friendly', 'neutral', 'hostile', 'unknown'] | None = None
    latitude: Latitude | None = None
    longitude: Longitude | None = None


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
