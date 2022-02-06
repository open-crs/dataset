import typing

import pandas

CWES_SEPARATOR = ","


class DatasetWorker:
    _filename: str = None
    _dataset: str = None

    def __init__(self, filename: str) -> None:
        self._filename = filename

        self._dataset = pandas.read_csv(self._filename)

    def __del__(self) -> None:
        self.dump()

    def add_new_source(self, name: str, cwes: typing.List[int],
                       parent_dataset: str) -> None:
        # Concatenate the CWEs
        cwes = CWES_SEPARATOR.join([str(cwe) for cwe in cwes])

        # Insert a new column into the dataframe
        self._dataset.loc[len(
            self._dataset.index)] = [name, cwes, parent_dataset, False]

    def mark_source_as_built(self, name: str) -> None:
        # Change the boolean indicating the status
        self._dataset.loc[self.dataset.name == name, "is_built"] = True

    def dump(self) -> None:
        self._dataset.to_csv(self._filename, index=False)

    def get_sources(self, dataset: str,
                    cwes: typing.List[int]) -> typing.List[str]:
        # Filter the dataset
        ids = []
        for _, row in self._dataset.iterrows():
            # Check the parent dataset
            if (row.parent_dataset != dataset):
                continue

            # Check the current CWEs
            if cwes:
                current_cwes = str(row.cwes).split(CWES_SEPARATOR)
                current_cwes = [int(element) for element in current_cwes]
                if (len(set(current_cwes).intersection(set(cwes))) == 0):
                    continue

            ids.append(row.name)

        return ids
