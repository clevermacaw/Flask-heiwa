"""Abstract classes for type hints."""

from __future__ import annotations

import abc
import typing

__all__ = ["SupportsLength"]
__version__ = "1.0.0"


# https://github.com/python/cpython/blob/3.8/Lib/typing.py
@typing.runtime_checkable
class SupportsLength(typing.Protocol):
	"""An abstract class which supports the ``__len__`` method."""

	@abc.abstractmethod
	def __len__(self: SupportsLength) -> int:
		pass
