# graphics_texture.py

from __future__ import annotations

from typing import TYPE_CHECKING

from typing import Optional, Any
if TYPE_CHECKING:
    # Only imported for type hints; avoids circular import at runtime
    from graphics_library import GraphicsLibrary

class GraphicsTexture:
    def __init__(self) -> None:
        self.graphics: Optional["GraphicsLibrary"] = None
        self.texture_index: int = -1

        self.width: int = 0
        self.widthf: float = 0.0

        self.height: int = 0
        self.heightf: float = 0.0

        self.file_name: Optional[str] = None

    def load_from_file(self, graphics: Optional["GraphicsLibrary"], bitmap: Any, file_name: str) -> None:
        self.load_from_bitmap(graphics, bitmap, file_name)

    def load_from_bitmap(
        self,
        graphics: Optional["GraphicsLibrary"],
        bitmap: Optional[Any],
        file_name: Optional[str] = None,
    ) -> None:
        self.graphics = graphics
        self.file_name = file_name

        self.width = 0
        self.height = 0
        self.widthf = 0.0
        self.heightf = 0.0
        self.texture_index = -1

        if graphics is not None and bitmap is not None:
            # You will implement this in GraphicsLibrary:
            #   def texture_generate(self, bitmap) -> int: ...
            self.width = getattr(bitmap, "width", 0)
            self.height = getattr(bitmap, "height", 0)
            self.widthf = float(self.width)
            self.heightf = float(self.height)
            self.texture_index = graphics.texture_generate(bitmap)

    def load_empty(
        self,
        graphics: Optional["GraphicsLibrary"],
        width: int,
        height: int,
        file_name: Optional[str] = None,
    ) -> None:
        self.graphics = graphics
        self.file_name = file_name

        self.width = int(width)
        self.height = int(height)
        self.widthf = float(self.width)
        self.heightf = float(self.height)
        self.texture_index = -1

        if graphics is not None:
            # You will implement this in GraphicsLibrary:
            #   def texture_generate(self, width: int, height: int) -> int: ...
            self.texture_index = graphics.texture_generate(width, height)

    def load_existing(
        self,
        graphics: Optional["GraphicsLibrary"],
        texture_index: int,
        width: int,
        height: int,
        file_name: Optional[str] = None,
    ) -> None:
        self.graphics = graphics
        self.file_name = file_name

        self.width = int(width)
        self.height = int(height)
        self.widthf = float(self.width)
        self.heightf = float(self.height)
        self.texture_index = int(texture_index)
