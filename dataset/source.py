import typing


class Source:
    identifier: str
    full_filename: str
    cwes: typing.List[int]
    additional_files: typing.List[str]

    def __init__(
        self,
        identifier: str,
        full_filename: str,
        cwes: typing.Union[int, typing.List[int]],
        additional_files: typing.List[str] = None,
    ) -> None:
        self.identifier = identifier
        self.full_filename = full_filename
        self.additional_files = additional_files

        if isinstance(cwes, int):
            self.cwes = [cwes]
        else:
            self.cwes = cwes
