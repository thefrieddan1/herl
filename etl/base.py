from abc import ABC, abstractmethod
from typing import Any

class Extractor(ABC):
    """Abstract base class for data extraction."""
    
    @abstractmethod
    def extract(self) -> Any:
        """Extracts data from a source."""
        pass

class Transformer(ABC):
    """Abstract base class for data transformation."""
    
    @abstractmethod
    def transform(self, data: Any) -> Any:
        """Transforms the extracted data."""
        pass

class Loader(ABC):
    """Abstract base class for data loading."""
    
    @abstractmethod
    def load(self, data: Any) -> None:
        """Loads data into a target."""
        pass
