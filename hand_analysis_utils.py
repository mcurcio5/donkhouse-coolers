import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path


def get_unique_hands_in_order(files):
    all_hands = []
    for file in files:  # adds unique hands while preserving order in which they occured
        local_hands = pd.read_pickle(file)
        hands_as_strings = ['\n'.join(hand) for hand in local_hands]  # make list hashable
        new_hands = [hand for hand in hands_as_strings if hand not in all_hands]
        all_hands += new_hands

    return [hand.split('\n') for hand in all_hands]

def get_all_donk_flips():
    """ gets all the flips scraped from donk """
    all_hands = []

    for i in range(1, 9):
        path_name = '/Users/mcurcio/Desktop/Notebooks/donk_hands/donk_' + str(i)
        path = Path(path_name).glob('**/*')
        files = [x for x in path if x.is_file() and '.DS_Store' not in str(x)]
        all_hands += get_unique_hands_in_order(files)

    return all_hands

def get_pot_size(hand):
    return sum([float(line.split('won ')[1].split(' chips')[0]) for line in list(
        filter(lambda x: 'won' in x, hand))])

def get_pot_winners(hand):
    return [winner.split(' ')[0] for winner in list(filter(lambda x: 'won' in x, hand))]

def won_at_showdown(hand):
    return bool(sum(list(map(lambda x: 'showed' in x, hand))))

def get_all_shown_cards(hand):
    cards_shown = list(filter(lambda x: 'showed' in x, hand))
    parsed_lists = list(map(lambda x: x.split(' '), cards_shown))

    output_dict = {}
    for l in parsed_lists:
        output_dict[l[0]] = ''.join(l[2:4])

    return output_dict

def get_runout(hand):
    runouts = list(filter(lambda x: 'board' in x, hand))
    try:
        return runouts[-1].split('board: ')[1]
    except:
        return ""


def is_all_in_runout(row):
    try:
        line_is_board = np.array(list(map(lambda x: int('board' in x), row['hand'])))
        line_after_last_board = row['hand'][np.where(line_is_board == 1)[0][-1] + 1]
        if row['won_at_showdown'] and (('mucked' in line_after_last_board) or
                                       ('showed' in line_after_last_board)):
            return True
    except:
        pass  # hand ended early or no board seen

    return False


def get_cards_before_all_in(row):
    if row['is_all_in_runout']:
        line_is_board = np.array(list(map(lambda x: int('board' in x), row['hand'])))
        board_indices = np.where(line_is_board == 1)[0]
        index = board_indices[-1]
        while 'board' in row['hand'][index]:
            index -= 1
        indices_of_cards_before_all_in = board_indices[:-(board_indices[-1] - index)]

        if len(indices_of_cards_before_all_in) == 0:
            return ""

        return row['hand'][indices_of_cards_before_all_in[-1]].split('board: ')[1]

    return pd.NA

def get_hands_as_df(all_hands):
    session = pd.DataFrame({'pot_winners': list(map(get_pot_winners, all_hands)),
              'pot_size': list(map(get_pot_size, all_hands)),
              'won_at_showdown': list(map(won_at_showdown, all_hands)),
              'cards_shown': list(map(get_all_shown_cards, all_hands)),
              'runout': list(map(get_runout, all_hands)),
              'hand': all_hands})

    session['is_all_in_runout'] = session.apply(lambda x: is_all_in_runout(x), axis=1)
    session['cards_before_all_in'] = session.apply(lambda x: get_cards_before_all_in(x), axis=1)
    session['double_board'] = session['runout'].apply(lambda x: True if ' / ' in x else False)
    session['n_cards_seen'] = session['runout'].apply(lambda x: int(np.round(len(x) / 3)))
    session['n_cards_seen'] = session['n_cards_seen'].apply(lambda x: x // 2 if x > 5 else x)

    return session