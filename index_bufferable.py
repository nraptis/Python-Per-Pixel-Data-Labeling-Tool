from abc import ABC, abstractmethod

class IndexBufferable(ABC):

    @abstractmethod
    def write_to_buffer(self, buffer) -> None:
        """Write this object's integer data into the buffer."""
        raise NotImplementedError

    @abstractmethod
    def size(self) -> int:
        """Return number of indices written."""
        raise NotImplementedError