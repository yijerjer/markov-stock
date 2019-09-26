import pandas as pd
import numpy as np

class DiscreteMarkov:
    def __init__(self, ngram=1):
        self._ngram = ngram
        self._table = {}
        self.states = []
        self._normalised_table = {}

    def create_table(self, states_chain):
        self._states = list(set(states_chain))
        self._states.sort()

        for i in range(len(states_chain) - self._ngram):
            first = tuple(states_chain[i:i + self._ngram])
            second = states_chain[i + self._ngram]

            if first in self._table:
                self._table[first][second] = self._table[first][second] + 1 if second in self._table[first] else 1
            else:
                self._table[first] = {second: 1}
    
    def set_normalised_table(self):
        for first_state, row in self._table.items():
            self._normalised_table[first_state] = {second_state: val / sum(row.values()) for second_state, val in row.items()}


        return self._normalised_table

    @property
    def table(self):
        return self._table

    @property
    def normalised_table(self):
        return self._normalised_table


