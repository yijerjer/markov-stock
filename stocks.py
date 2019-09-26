import csv
import numpy as np
from datetime import datetime, timedelta

class Stocks:
    def __init__(self, csv_file_dir):
        self._stock_prices = {}
        csv_reader = csv.DictReader(open(csv_file_dir, 'r'))
        date = None
        for row in csv_reader:
            date = datetime.strptime(row["Date"], "%Y-%m-%d")
            row.pop("Date")
            self._stock_prices[date] = {name: float(val) for name, val in row.items()}

        self._latest_date = date
        self._quantisation = [
            (-np.inf, -3), (-3, -2.5), (-2.5, -2), (-2, -1.5), (-1.5, -1), (-1, 0.5), (-0.5, 0),
            (0, 0.5), (0.5, 1), (1, 1.5), (1.5, 2), (2, 2.5), (2.5, 3), (3, np.inf)
        ]
    
    def from_period(self, period):
        if period == "1Y":
            days_delta = 365

        start_date = self._latest_date - timedelta(days=days_delta)
        period_prices = {date: row for date, row in self._stock_prices.items() if date > start_date}
        return period_prices

    def before_period(self, period):
        if period == "1Y":
            days_delta = 365
        
        end_date = self._latest_date - timedelta(days=days_delta)
        period_prices = {date: row for date, row in self._stock_prices.items() if date < end_date}
        return period_prices

    def apply_naive_method(self):
        prev_prev_row = {}
        prev_row = {}
        for row in self._stock_prices.values():
            if prev_row:
                if prev_prev_row:
                    row["prev_day_return"] = prev_row["Close"] - prev_prev_row["Close"]
                    row["naive_method"] = prev_row["Close"] + row["prev_day_return"]
                prev_prev_row = prev_row

            prev_row = row

    def apply_discrete_markov_chain(self, proba_table):
        prev_rows = []
        ngram = len(list(proba_table.keys())[0])

        for row in self._stock_prices.values():
            if len(prev_rows) == ngram:
                prev_states = tuple([row["quantised_prev_day_return"] for row in prev_rows if "quantised_prev_day_return" in row])
                if len(prev_states) == ngram:
                    next_probas = proba_table.get(prev_states, {})
                    # next_state = [key for key, proba in next_probas.items() if proba == max(next_probas.values())][0]
                    # if next_state == 0:
                    #     row["markov_method"] = prev_row["Close"] + self._quantisation[next_state][1] + 0.25
                    # elif next_state == (len(self._quantisation) - 1):
                    #     row["markov_method"] = prev_row["Close"] + self._quantisation[next_state][0] + 0.25
                    # else:
                    #     row["markov_method"] = prev_row["Close"] + sum(self._quantisation[next_state]) / 2

                    change = 0
                    if next_probas:
                        for idx, proba in next_probas.items():
                            price_range = self._quantisation[idx]
                            if idx == 0:
                                change += proba * (price_range[1] + 0.25)
                            elif idx == (len(self._quantisation) - 1):
                                change += proba * (price_range[0] + 0.25)
                            else:
                                change += proba * (sum(price_range) / 2)
                        
                    row["markov_method"] = prev_rows[-1]["Close"] + change

                prev_rows.pop(0)
            prev_rows.append(row)
    
    def quantise_prev_day_return(self):
        for row in self._stock_prices.values():
            if "prev_day_return" in row:
                for idx, q_range in enumerate(self._quantisation):
                    if row["prev_day_return"] >= q_range[0] and row["prev_day_return"] < q_range[1]:
                        row["quantised_prev_day_return"] = idx

    def mape(self, method):
        pred_method_diff = [np.absolute(row["Close"] - row[method]) / row["Close"] for row in self._stock_prices.values() if method in row]
        mape = sum(pred_method_diff) / len(pred_method_diff)
        return mape
        
    def get_predict_returns(self, method):
        start_price = 1

        for i in range(len(self._stock_prices.values()) - 1):
            rows = list(self._stock_prices.values())
            if method in rows[i + 1] and method in rows[i]:
                percentage_pred_return = (rows[i + 1][method] - rows[i][method]) / rows[i][method]
                if percentage_pred_return > 0:
                    percentage_actual_return = (rows[i + 1]["Close"] - rows[i]["Close"]) / rows[i]["Close"]
                    start_price *= (1 + percentage_actual_return)
    
        return start_price



    @property
    def latest_date(self):
        return self._latest_date
    
    @property
    def prices(self):
        return self._stock_prices
