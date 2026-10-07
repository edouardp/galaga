"""Small physical-unit conversions for normalized spacetime coordinates.

Constants follow SI, IAU astronomical units, and Julian years. This is a
bounded conversion backend, not a general dimensional-expression parser.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real
from types import MappingProxyType
from typing import Literal

CoordinateUnits = Literal["natural", "si"] | tuple[str, str]

SPEED_OF_LIGHT = 299_792_458.0
ASTRONOMICAL_UNIT = 149_597_870_700.0
JULIAN_YEAR = 365.25 * 86_400
STANDARD_GRAVITY = 9.80665


@dataclass(frozen=True, slots=True)
class _Unit:
    symbol: str
    factor: float
    aliases: tuple[str, ...] = ()


def _index(units: tuple[_Unit, ...]) -> MappingProxyType[str, _Unit]:
    return MappingProxyType({name.lower(): unit for unit in units for name in (unit.symbol, *unit.aliases)})


_TIME_UNITS = (
    _Unit("ns", 1e-9, ("nanosecond", "nanoseconds")),
    _Unit("μs", 1e-6, ("us", "µs", "microsecond", "microseconds")),
    _Unit("ms", 1e-3, ("millisecond", "milliseconds")),
    _Unit("s", 1, ("second", "seconds")),
    _Unit("min", 60, ("minute", "minutes")),
    _Unit("h", 3600, ("hour", "hours")),
    _Unit("day", 86_400, ("days",)),
    _Unit("week", 7 * 86_400, ("weeks",)),
    _Unit("month", JULIAN_YEAR / 12, ("months",)),
    _Unit("year", JULIAN_YEAR, ("years", "yr")),
)
_DISTANCE_UNITS = (
    _Unit("nm", 1e-9, ("nanometer", "nanometre", "nanometers", "nanometres")),
    _Unit("μm", 1e-6, ("um", "µm", "micrometer", "micrometre")),
    _Unit("mm", 1e-3, ("millimeter", "millimetre")),
    _Unit("cm", 1e-2, ("centimeter", "centimetre")),
    _Unit("m", 1, ("meter", "metre", "meters", "metres")),
    _Unit("km", 1000, ("kilometer", "kilometre", "kilometers", "kilometres")),
    _Unit("light-second", SPEED_OF_LIGHT, ("light-seconds", "ls")),
    _Unit("AU", ASTRONOMICAL_UNIT, ("astronomical_unit",)),
    _Unit("ly", SPEED_OF_LIGHT * JULIAN_YEAR, ("light-year", "light-years")),
)
_SPEED_UNITS = (
    _Unit("m/s", 1),
    _Unit("km/h", 1000 / 3600),
    _Unit("km/s", 1000),
    _Unit("c", SPEED_OF_LIGHT),
    _Unit("% c", SPEED_OF_LIGHT / 100, ("%c", "percent_c")),
)
_ACCELERATION_UNITS = (
    _Unit("m/s²", 1, ("m/s^2", "m/s2")),
    _Unit("g", STANDARD_GRAVITY),
)
_TIME = _index(_TIME_UNITS)
_DISTANCE = _index(_DISTANCE_UNITS)
_SPEED = _index(_SPEED_UNITS)
_ACCELERATION = _index(_ACCELERATION_UNITS)


def _real(value: object, name: str = "value") -> float:
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _convert(value: float, factor: float) -> float:
    return _real(_real(value) * factor, "converted value")


def _unit(name: str, table: MappingProxyType[str, _Unit], quantity: str) -> _Unit:
    if not isinstance(name, str):
        raise TypeError(f"{quantity} unit must be a string")
    try:
        return table[name.strip().lower()]
    except KeyError as error:
        supported = ", ".join(dict.fromkeys(unit.symbol for unit in table.values()))
        raise ValueError(f"unsupported {quantity} unit {name!r}; choose {supported}") from error


def normalize_coordinate_units(value: CoordinateUnits) -> Literal["natural"] | tuple[str, str]:
    """Resolve a coordinate policy to natural units or explicit time/distance units."""

    if isinstance(value, str) and value == "natural":
        return "natural"
    if isinstance(value, str) and value == "si":
        return ("s", "m")
    if not isinstance(value, tuple) or len(value) != 2:
        raise ValueError("coordinate units must be 'natural', 'si', or a (time_unit, distance_unit) tuple")
    return (_unit(value[0], _TIME, "time").symbol, _unit(value[1], _DISTANCE, "distance").symbol)


def _auto(value: float, units: tuple[_Unit, ...], zero_unit: _Unit) -> _Unit:
    if value == 0:
        return zero_unit
    return next((unit for unit in reversed(units) if abs(value) >= unit.factor), units[0])


def _format(value: float, unit: _Unit, precision: int) -> str:
    if not isinstance(precision, int) or isinstance(precision, bool) or not 1 <= precision <= 15:
        raise ValueError("precision must be an integer from 1 to 15")
    number = value / unit.factor
    if not math.isfinite(number):
        raise ValueError("converted value exceeds floating-point range")
    text = format(0.0 if number == 0 else number, f".{precision}g")
    return f"{text}% c" if unit.symbol == "% c" else f"{text} {unit.symbol}"


@dataclass(frozen=True, slots=True)
class SpacetimeUnits:
    """Physical scale for coordinates with ``c=1``.

    One natural time unit is ``time_scale_seconds`` seconds; one natural
    length unit is ``c * time_scale_seconds`` metres. Years are Julian years
    and months are one twelfth of a Julian year, not calendar durations.
    """

    time_scale_seconds: float = 1.0

    def __post_init__(self) -> None:
        scale = _real(self.time_scale_seconds, "time_scale_seconds")
        if scale <= 0 or not math.isfinite(SPEED_OF_LIGHT * scale) or not math.isfinite(SPEED_OF_LIGHT / scale):
            raise ValueError("time_scale_seconds must be positive and give finite length and acceleration scales")
        object.__setattr__(self, "time_scale_seconds", scale)

    @classmethod
    def for_acceleration(cls, value: float = 1, *, unit: str = "g") -> SpacetimeUnits:
        """Choose the scale where one natural proper acceleration has this magnitude."""

        acceleration = _real(value, "acceleration") * _unit(unit, _ACCELERATION, "acceleration").factor
        if acceleration <= 0 or not math.isfinite(acceleration):
            raise ValueError("acceleration must be positive and finite")
        return cls(SPEED_OF_LIGHT / acceleration)

    @property
    def length_scale_meters(self) -> float:
        return SPEED_OF_LIGHT * self.time_scale_seconds

    def coordinate_factors(self, units: CoordinateUnits) -> tuple[float, float]:
        """Multipliers converting physical time/distance coordinates to natural units."""

        selected = normalize_coordinate_units(units)
        if selected == "natural":
            return 1.0, 1.0
        factors = (
            _unit(selected[0], _TIME, "time").factor / self.time_scale_seconds,
            _unit(selected[1], _DISTANCE, "distance").factor / self.length_scale_meters,
        )
        if any(not math.isfinite(factor) or factor <= 0 for factor in factors):
            raise ValueError("coordinate conversion exceeds floating-point range")
        return factors

    def time_from(self, value: float, unit: str = "s") -> float:
        """Convert a physical duration to natural time units."""
        return _convert(value, _unit(unit, _TIME, "time").factor / self.time_scale_seconds)

    def time_in(self, value: float, unit: str = "s") -> float:
        """Convert a natural duration to the selected physical time unit."""
        return _convert(value, self.time_scale_seconds / _unit(unit, _TIME, "time").factor)

    def distance_from(self, value: float, unit: str = "m") -> float:
        return _convert(value, _unit(unit, _DISTANCE, "distance").factor / self.length_scale_meters)

    def distance_in(self, value: float, unit: str = "m") -> float:
        return _convert(value, self.length_scale_meters / _unit(unit, _DISTANCE, "distance").factor)

    def speed_from(self, value: float, unit: str = "m/s") -> float:
        """Convert physical coordinate velocity to a fraction of c."""
        return _convert(value, _unit(unit, _SPEED, "speed").factor / SPEED_OF_LIGHT)

    def speed_in(self, value: float, unit: str = "m/s") -> float:
        return _convert(value, SPEED_OF_LIGHT / _unit(unit, _SPEED, "speed").factor)

    def acceleration_from(self, value: float, unit: str = "m/s^2") -> float:
        return _convert(
            value, _unit(unit, _ACCELERATION, "acceleration").factor * self.time_scale_seconds / SPEED_OF_LIGHT
        )

    def acceleration_in(self, value: float, unit: str = "m/s^2") -> float:
        return _convert(
            value, SPEED_OF_LIGHT / self.time_scale_seconds / _unit(unit, _ACCELERATION, "acceleration").factor
        )

    def format_time(self, value: float, unit: str = "auto", *, precision: int = 3) -> str:
        physical = _real(self.time_in(value))
        selected = _auto(physical, _TIME_UNITS, _TIME["s"]) if unit == "auto" else _unit(unit, _TIME, "time")
        return _format(physical, selected, precision)

    def format_distance(self, value: float, unit: str = "auto", *, precision: int = 3) -> str:
        physical = _real(self.distance_in(value))
        if unit != "auto":
            selected = _unit(unit, _DISTANCE, "distance")
        elif abs(physical) >= 0.1 * _DISTANCE["ly"].factor:
            selected = _DISTANCE["ly"]
        elif abs(physical) >= 0.01 * ASTRONOMICAL_UNIT:
            selected = _DISTANCE["au"]
        else:
            everyday = tuple(
                candidate for candidate in _DISTANCE_UNITS if candidate.symbol not in {"cm", "light-second", "AU", "ly"}
            )
            selected = _auto(physical, everyday, _DISTANCE["m"])
        return _format(physical, selected, precision)

    def format_speed(self, value: float, unit: str = "auto", *, precision: int = 3) -> str:
        physical = _real(self.speed_in(value))
        if unit == "auto":
            selected = (
                _SPEED["%c"] if abs(value) >= 0.01 else _SPEED["km/s"] if abs(physical) >= 1000 else _SPEED["m/s"]
            )
        else:
            selected = _unit(unit, _SPEED, "speed")
        return _format(physical, selected, precision)

    def format_acceleration(self, value: float, unit: str = "g", *, precision: int = 3) -> str:
        return _format(_real(self.acceleration_in(value)), _unit(unit, _ACCELERATION, "acceleration"), precision)


__all__ = ["CoordinateUnits", "SpacetimeUnits"]
