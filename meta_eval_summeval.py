from dotenv import load_dotenv
from prettytable import PrettyTable
from scipy.stats import spearmanr, pearsonr, kendalltau
import json
import re
import argparse
import os


def calculate_correlation(pred_score, human_score):
    assert len(pred_score) == len(human_score)
    result = {'pearson': 0, 'spearman': 0, 'kendalltau': 0}

    if (len(result) == 0):
        result = {'pearson': 0, 'spearman': 0, 'kendalltau': 0}
    result['pearson'] = pearsonr(pred_score, human_score).statistic
    result['spearman'] = spearmanr(pred_score, human_score).statistic
    result['kendalltau'] = kendalltau(pred_score, human_score).statistic

    return result


def print_correlations(result):
    table = PrettyTable(['Pearson', 'Spearman', 'Kendall'])
 
    table.add_row(
        [round(result['pearson'], 4), round(result['spearman'], 4), round(result['kendalltau'], 4)])
    print(table)


def parse_output(output):
    matched = re.search("^ ?([\d\.]+)", output)
    if (matched):
        try:
            score = float(matched.group(1))
        except:
            score = 0
    else:
        score = 0
    return score


if __name__ == '__main__':
# ====================================== SETUP ====================================== #
    load_dotenv(".env")
    input_file_path = os.getenv("input_file_path")
    dimension = os.getenv("dimension")
# =================================================================================== #

    jobj = json.load(open(input_file_path))
    pred_scores, human_scores = [], []

    print("Calculating correlation for G-Eval")
    print("File Path::", input_file_path)

    for item in jobj:
        all_responses = item["all_responses"]
        all_scores = [parse_output(x) for x in all_responses]
        p1, p2, p3, p4, p5 = all_scores.count(1), all_scores.count(2), all_scores.count(3), all_scores.count(4), all_scores.count(5)

        score = (1*p1 + 2*p2 + 3*p3 + 4*p4 + 5*p5) / len(all_scores)

        pred_scores.append(score)
        human_scores.append(item['scores'][dimension])

    print('len(pred_scores): {}'.format(len(pred_scores)))
    print('len(human_scores): {}'.format(len(human_scores)))

    results = calculate_correlation(pred_scores, human_scores)
    print_correlations(results)
