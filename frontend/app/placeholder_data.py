from typing import List
from models import Unit


sample_units: List[Unit] = [
    Unit(
        affilitation='friendly',
        callsign='ALPHA-1',
        latitude=35.2603,
        longitude=-116.8657
        
    ),
    Unit(
        affilitation='friendly',
        callsign='ALPHA-2',
        latitude=35.2539,
        longitude=-116.8591
    ),
    Unit(
        affilitation='hostile',
        callsign='HOSTILE-1',
        latitude=35.2812,
        longitude=-116.8045
    ),
    Unit(
        affilitation='unknown',
        callsign='UNKNOWN-1',
        latitude=35.2709,
        longitude=-116.8534
    )
]
