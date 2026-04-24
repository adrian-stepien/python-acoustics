"""
Quantities and units
====================

The Quantity module provides two classes to work with quantities and units.

"""

from typing import TypeAlias

from acoustics.standards.iso_tr_25417_2007 import REFERENCE_PRESSURE

UnitSpec: TypeAlias = tuple[str, str, str]
QuantitySpec: TypeAlias = tuple[str, str, bool, str | None, str | None, float]

quantities: dict[str, QuantitySpec] = {
    'pressure': ('Pressure', 'pascal', True, 'p', '$p$', REFERENCE_PRESSURE),
}
"""
Dictionary with quantities. Each quantity is stored as a tuple.
"""

units: dict[str, UnitSpec] = {
    'meter': ('meter', 'm', '$m$'),
    'pascal': ('pascal', 'Pa', '$Pa$'),
}
"""
Dictionary with units. Each unit is stored as a tuple.
"""


class Unit:
    """
    Unit of quantity.

    .. note:: Perhaps inherit from tuple or :class:`collections.namedTuple`?

    """

    def __init__(self, name, symbol, symbol_latex):

        self.name = name
        """
        Name of the unit.
        """
        self.symbol = symbol
        """
        Symbol of the unit.
        """

        self.symbol_latex = symbol_latex
        """
        Symbol of the unit in LaTeX.
        """

    def __repr__(self):
        return f"Unit({self.name})"

    def __str__(self):
        return self.name


class Quantity:
    """
    Quantity.
    """

    def __init__(self, name, unit, dynamic, symbol=None, symbol_latex=None, reference=1.0):

        self.name = name
        """
        Name of the quantity.
        """

        self.symbol = symbol
        """
        Symbol of the quantity.
        """

        self.symbol_latex = symbol_latex
        """
        Symbol of the unit in LaTeX.
        """

        self.unit = unit
        """
        Unit. See :class:`Unit`.
        """

        self.dynamic = dynamic
        """
        Dynamic quantity (`True`) or energetic (`False`).
        """

        self.reference = reference
        """
        Reference value of the quantity.
        """

    def __repr__(self):
        return f"Quantity({self.name})"

    def __str__(self):
        return self.name

    @property
    def energetic(self):
        """
        Energetic quantity (`True`) or dynamic (`False`).
        """
        return not self.dynamic


def get_quantity(name):
    """
    Get quantity by name. Returns instance of :class:`Quantity`.

    :param name: Name of the quantity.

    """
    try:
        quantity_name, unit_name, dynamic, symbol, symbol_latex, reference = quantities[name]
    except KeyError as err:
        raise ValueError("Unknown quantity. Quantity is not yet specified.") from err
    try:
        unit_args = units[unit_name]
    except KeyError as err:
        raise RuntimeError("Unknown unit. Quantity has been specified but unit has not.") from err

    return Quantity(quantity_name, Unit(*unit_args), dynamic, symbol, symbol_latex, reference)
