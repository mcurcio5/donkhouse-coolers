import pandas as pd
import numpy as np

import os
import pickle

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from time import sleep
import time


def convert_text_to_list_of_hands(all_hands_text):
    """ converts the donk big text blob into individual hands """
    game_action_list = all_hands_text.text.split('\n')
    all_hands = []
    local_hand = []

    for i in range(len(game_action_list)):
        if 'SB' in game_action_list[i] and len(local_hand) != 0:
            all_hands.append(local_hand)
            local_hand = []
        local_hand.append(game_action_list[i])

    try:
        return all_hands[1:-1]
    except:
        return []


# def save_hands(hands, group_name):
#     """ saves the pickled list of hands in the correct directory by group name """
#     dest_dir = '/Users/mcurcio/Desktop/Notebooks/donk_hands/' + group_name
#
#     try:
#         os.makedirs(dest_dir)
#     except OSError:
#         pass  # already exists
#
#     file_name = dest_dir + '/' + str(int(time.time())) + '.txt'
#     with open(file_name, 'wb') as f:
#         pickle.dump(hands, f)


if __name__ == '__main__':
    max_delay = 15 # seconds

    driver = webdriver.Chrome('/Users/mcurcio/Downloads/chromedriver')
    driver.get('https://donkhouse.com/groups')
    # login
    try:
        e=WebDriverWait(driver, max_delay).until(EC.presence_of_element_located((By.NAME, 'name')))
        e=WebDriverWait(driver, max_delay).until(EC.presence_of_element_located((By.NAME, 'password')))
        e=WebDriverWait(driver, max_delay).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Login"]')))
    except TimeoutException:
        raise Exception('logging in took too much time')
    sleep(.1)
    # driver.find_element_by_name('name').send_keys('mcurcio')
    driver.find_element_by_name('name').send_keys('-you')
    sleep(.1)
    # driver.find_element_by_name('password').send_keys('qyjtid-3vingi-coSpaj')
    driver.find_element_by_name('password').send_keys('54321donk')
    driver.find_element(By.XPATH, '//button[text()="Login"]').click()

    # scrape both groups
    donkhouse_groups = ['https://donkhouse.com/group/100'] #, 'https://donkhouse.com/group/25332'] #,'https://donkhouse.com/group/42']
    # donkhouse_groups = ['https://donkhouse.com/group/28692'] # the test group
    output = {}
    for group_link in donkhouse_groups:
        driver.get(group_link)
        sleep(2)
        tables = driver.find_elements(By.XPATH,
                                      '//div[@class="columns"]/div[1]//form[@method="POST"]/a')

        # get the table data (number of people at tables)
        data = []
        for table in tables:
            data.append(table.text.split('\n') + [table.get_attribute('href')])

        group = pd.DataFrame(columns=['table', 'game_type', 'stakes', 'players', 'link'], data=data)
        # print(group)
        group['current_players'] = group['players'].apply(lambda x: int(x[0]))
        # group['table_size'] = group['players'].apply(lambda x: int(x[-1]))
        group = group.drop(columns=['players'])

        groups_of_interest = group.loc[group['current_players'] >= 2, 'table'].values
        links_of_interest = group.loc[group['current_players'] >= 2, 'link'].values

        # scrape all tables with two or more people
        for i, g in enumerate(groups_of_interest):
            driver.get(links_of_interest[i])
            try:
            	e=WebDriverWait(driver, max_delay).until(EC.presence_of_element_located((By.XPATH,
                                '//select[@id="mode"]/option[text()="hand histories only"]')))
            except:
            	raise Exception('loading hand histories option bar took too long')
            sleep(2)
            # switch to only view hand histories
            driver.find_elements(By.XPATH,
                                 '//select[@id="mode"]/option[text()="hand histories only"]')[0].click()
            sleep(2)
            try:
            	e=WebDriverWait(driver, max_delay).until(EC.presence_of_element_located((By.XPATH, '//div[@id="chat"]')))
            except:
            	raise Exception('loading hand histories took too long')

            sleep(5)

            all_hands_text = driver.find_elements(By.XPATH, '//div[@id="chat"]')
            all_hands = convert_text_to_list_of_hands(all_hands_text[0])
            # save_hands(all_hands, g)
            output[g] = all_hands
            sleep(1)
            # driver.execute_script("window.history.go(-1)")
            # sleep(1)

        # driver.execute_script("window.history.go(-1)")

    driver.quit()

    output['time'] = str(int(time.time()))

    return output

