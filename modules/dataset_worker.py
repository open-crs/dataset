import pandas


class DatasetWorker:
    _filename = None
    _dataset = None

    def __init__(self, filename):
        self._filename = filename
        self.dataset = pandas.read_csv(self._filename)

    def add(self, name, cwes, parent_dataset):
        cwes = ",".join([str(cwe) for cwe in cwes])
        self.dataset.loc[len(
            self.dataset.index)] = [name, cwes, parent_dataset]

    def dump(self):
        self.dataset.to_csv(self._filename, index=False)