class ResumeLine:
    def __init__(self, text: str, startX: float, endX: float, startY: float, endY: float):
        self._text = text
        self._startX = startX
        self._endX = endX
        self._startY = startY
        self._endY = endY

    def __str__(self):
        return f'"{self._text}", start: ({self._startX}, {self._startY}), end: ({self._endX}, {self._endY})'

    @property
    def text(self) -> str:
        return self._text

    @property
    def startX(self) -> float:
        return self._startX

    @property
    def endX(self) -> float:
        return self._endX

    @property
    def startY(self) -> float:
        return self._startY

    @property
    def endY(self) -> float:
        return self._endY
