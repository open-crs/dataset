import typing

import pandas

from .configuration import Configuration


class DatasetWorker:
    """Class for working with the dataset of vulnerable programs"""
    _filename: str = None
    _dataset: str = None

    def __init__(self, filename: str) -> None:
        """Initializes a DatasetWorker instance.

        Args:
            filename (str): Name of the CSV dataset
        """
        self._filename = filename

        self._dataset = pandas.read_csv(self._filename)

    def __del__(self) -> None:
        """Destroys a DatasetWorker instance."""
        self.dump()

    def add_new_source(self, name: str, cwes: typing.List[int],
                       parent_dataset: str) -> None:
        """Adds a new source into the dataset

        Args:
            name (str): Name (identifier) of the sources
            cwes (typing.List[int]): CWEs that the source includes
            parent_dataset (str): Parent datasets
        """
        # Concatenate the CWEs
        cwes = Configuration.CWES_SEPARATOR.join([str(cwe) for cwe in cwes])

        # Insert a new column into the dataframe
        self._dataset.loc[len(
            self._dataset.index)] = [name, cwes, parent_dataset, False]

    def mark_source_as_built(self, name: str) -> None:
        # Change the boolean indicating the status
        self._dataset.loc[self._dataset.name == name, "is_built"] = True

    def dump(self) -> None:
        """Dumps the dataset from memory to disk."""
        self._dataset.to_csv(self._filename, index=False)

    def get_sources(self,
                    dataset: str = None,
                    cwes: typing.List[int] = None,
                    is_built: bool = None,
                    only_names: bool = False) -> list:
        """Gets specific sources from dataset.

        Args:
            dataset (str, optional): Parent dataset. Defaults to None.
            cwes (typing.List[int], optional): CWEs that the sources include.
                Defaults to None.
            is_built (bool, optional): Boolean indicating if the sources are
                compiled (an executable already exists). Defaults to None.
            only_names (bool, optional): Boolean indicating if only the names
                should be returned. Defaults to False, meaning that the function
                will return a panda's DataFrame.

        Returns:
            list: List with sources (or only their names)
        """
        # Filter the dataset
        sources = []
        for _, row in self._dataset.iterrows():
            # Check the parent dataset
            if dataset and row.parent_dataset != dataset:
                continue

            # Check if the sources are built
            if is_built != None and row.is_built != is_built:
                continue

            # Check the current CWEs
            if cwes:
                current_cwes = str(row.cwes).split(
                    Configuration.CWES_SEPARATOR)
                current_cwes = [int(element) for element in current_cwes]
                if (len(set(current_cwes).intersection(set(cwes))) == 0):
                    continue

            # If the above checks passed, then return the entry's name
            if only_names:
                sources.append(row["name"])
            else:
                sources.append(row.tolist())

        return sources
