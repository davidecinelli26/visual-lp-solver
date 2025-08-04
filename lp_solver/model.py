"""Linear program data models.

This module provides simple dataclasses to represent a linear program and its
constraints. The goal is to validate the structure of an LP before passing it
along to a solver.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Sequence, Iterable, Literal

import numpy as np


class Inequality(str, Enum):
    """Enumeration of supported inequality operators for constraints."""

    LE = "<="
    GE = ">="
    EQ = "="


@dataclass
class Constraint:
    """Represents a single linear constraint.

    Attributes
    ----------
    coefficients: Sequence[float]
        Coefficients of the constraint left-hand side.
    inequality: Inequality
        Type of inequality (<=, >=, =).
    value: float
        Right-hand side constant of the constraint.
    """

    coefficients: Sequence[float]
    inequality: Inequality
    value: float

    def __post_init__(self) -> None:  # pragma: no cover - simple validation
        # Allow passing inequality as string; convert to Enum to validate.
        try:
            self.inequality = Inequality(self.inequality)
        except ValueError as exc:  # invalid inequality type
            valid = ", ".join(i.value for i in Inequality)
            raise ValueError(f"Invalid inequality '{self.inequality}'. Must be one of {valid}.") from exc


@dataclass
class LinearProgram:
    """A linear program consisting of an objective and a set of constraints."""

    objective: Sequence[float]
    constraints: List[Constraint] = field(default_factory=list)
    sense: Literal["max", "min"] = "min"

    def __post_init__(self) -> None:  # pragma: no cover - simple validation
        if self.sense not in {"max", "min"}:
            raise ValueError("sense must be either 'max' or 'min'")

        obj_len = len(self.objective)
        for c in self.constraints:
            if len(c.coefficients) != obj_len:
                raise ValueError(
                    "All constraints must have the same number of coefficients as the objective"
                )

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the linear program after validating its size."""

        obj_len = len(self.objective)
        if len(constraint.coefficients) != obj_len:
            raise ValueError(
                "Constraint coefficient length must match the number of objective coefficients"
            )
        self.constraints.append(constraint)

    @property
    def num_variables(self) -> int:
        """Return the number of variables of the LP inferred from the objective."""

        return len(self.objective)

    def iter_matrix(self) -> Iterable[Sequence[float]]:
        """Yield the coefficient vectors for each constraint.

        This can be useful for building matrix representations (A matrix) of the
        linear program.
        """

        for c in self.constraints:
            yield c.coefficients

    def A_matrix(self) -> np.ndarray:
        """Return the matrix of constraint coefficients."""

        return np.array([c.coefficients for c in self.constraints], dtype=float)

    def b_vector(self) -> np.ndarray:
        """Return the vector of constraint right-hand sides."""

        return np.array([c.value for c in self.constraints], dtype=float)

    def c_vector(self) -> np.ndarray:
        """Return the vector of objective function coefficients."""

        return np.array([c for c in self.objective], dtype=float)

    def sense_vector(self) -> list[str]:
        """Return the list of inequality symbols for each constraint."""

        return [c.inequality.value for c in self.constraints]
