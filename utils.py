import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import csv
import pathlib
from bs4 import BeautifulSoup
import logging
import shutil
import requests
import base64
import os
import pygsheets
import json
from google.oauth2 import service_account
import warnings
import math
from scipy.special import erf

#needed to connect to googlesheet db
SCOPES = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
service_account_info=st.secrets["gcp_service_account"]
my_credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
gc = pygsheets.authorize(custom_credentials=my_credentials)
DB_URL="https://docs.google.com/spreadsheets/d/1m0lG7b2Ze-Armz-C-5MLH960dk5v1I-mLyoaUk5WAyE/edit?usp=drive_link"

warnings.filterwarnings("ignore")

def clean_df(df):
    df_ok = df.copy()
    my_brand_low_freq = df_ok.brand.value_counts()[df_ok.brand.value_counts() < 5].index.tolist()
    df_ok = df_ok[df_ok.brand.isin(my_brand_low_freq) == False]
    df_ok['repair_barrier_if_end_of_life'] = df_ok['repair_barrier_if_end_of_life'].fillna('Unspecified')
    return df_ok

def build_pick_up_list(my_df, my_list_column):
    print(my_df[[my_list_column]].shape)
    my_df_valuecounts = my_df[[my_list_column]].iloc[:, 0].value_counts().reset_index()
    list_out = [str(my_df_valuecounts.iloc[i, 0]) + ' - ' + '({})'.format(my_df_valuecounts.iloc[i, 1]) for i in
                range(my_df_valuecounts.shape[0])]
    return my_df_valuecounts, list_out

def extract_info_machine(my_dataset, my_machine, my_brand, lang_var, pb_cat):
    if lang_var == 'UK':
        the_message = ' 🙄 Sorry, too few data to answer. Have a look in the statistics zone for more info ⏬. '
    elif lang_var == 'FR':
        the_message = " 🙄 Désolé, pas assez de data pour répondre, mais jette un oeil à l'onglet statistiques pour plus d'infos ⏬"
    else:
        st.write('error')
    my_useful_dataset = my_dataset
    my_useful_dataset_prodcat = my_useful_dataset[my_useful_dataset['product_category'] == my_machine]

    if pb_cat in ['U', 'G']:
        my_useful_dataset_pbCat = my_useful_dataset_prodcat
    else:
        my_useful_dataset_pbCat = my_useful_dataset_prodcat[my_useful_dataset_prodcat['problem_class_main'] == pb_cat]

    my_dataset_brand = my_dataset[my_dataset['brand'] == my_brand]

    my_useful_dataset_prodcat_brand = my_useful_dataset_prodcat[my_useful_dataset_prodcat['brand'] == my_brand]

    if my_useful_dataset_prodcat_brand.shape[0] > 0:
        my_number_of_machine_brand = my_useful_dataset_prodcat_brand.shape[0]
        my_age_mean_of_machine_brand = round(my_useful_dataset_prodcat_brand['product_age'].median(), 2)

    #compute percent_repair and CI
    PC_repair_brand,CI_repair_brand=PC_CI_repair_success(my_dataset_brand.shape[0],
                                                         my_dataset_brand[my_dataset_brand["repair_status"]=="Fixed"].shape[0], c_i=90)
    PC_repair_catprod,CI_repair_catprod=PC_CI_repair_success(my_useful_dataset_prodcat.shape[0],
                                                         my_useful_dataset_prodcat[my_useful_dataset_prodcat["repair_status"]=="Fixed"].shape[0], c_i=90)
    PC_repair_catprod_pbcat, CI_repair_catprod_pbcat = PC_CI_repair_success(my_useful_dataset_pbCat.shape[0],
                                                                my_useful_dataset_pbCat[my_useful_dataset_pbCat[
                                                                                              "repair_status"] == "Fixed"].shape[0], c_i=90)
    PC_repair, CI_repair = PC_CI_repair_success(my_useful_dataset_prodcat_brand.shape[0],
                                                my_useful_dataset_prodcat_brand[my_useful_dataset_prodcat_brand["repair_status"] == "Fixed"].shape[0], c_i=90)
    try:
        # print(PC_repair_brand, CI_repair_brand)
        # print(PC_repair, CI_repair)
        # final message
        if my_number_of_machine_brand > 10:
            magic_repair= magic_number( PC_repair_brand,CI_repair_brand,PC_repair_catprod,CI_repair_catprod, PC_repair_catprod_pbcat,
                  CI_repair_catprod_pbcat, PC_repair, CI_repair)
            if magic_repair > 0.55:
                if lang_var == 'UK':
                    the_message = ' 😍 YES! Run to repair !'
                elif lang_var == 'FR':
                    the_message = ' 😍 OUI! Cours faire réparer !'
                else:
                    st.write('error')
            elif 0.4<magic_repair<=0.55:
                if lang_var == 'UK':
                    the_message = '😙 YES! You should try to repair. '
                elif lang_var == 'FR':
                    the_message = " 😙 OUI! Tu peux essayer de faire réparer. "
                else:
                    st.write('error')
            elif 0.3<magic_repair<=0.4:
                if lang_var == 'UK':
                    the_message = '😎 YES, but you need an expert !'
                elif lang_var == 'FR':
                    the_message = '😎 OUI, mais il te faut un expert de la réparation !'
                else:
                    st.write('error')
            else:
                if lang_var == 'UK':
                    the_message = '😒 GIVE IT A TRY, with the help of an expert !'
                elif lang_var == 'FR':
                    the_message = "😒 A TENTER, avec l'aide d'un expert !"
                else:
                    st.write('error')
        else:
            if lang_var == 'UK':
                the_message = ' 😉 Very rare product in our base but try to repair !'
            elif lang_var == 'FR':
                the_message = ' 😉 Produit rare dans notre base mais pourquoi pas tenter !'
            else:
                st.write('error')
    except:
        my_number_of_machine_brand, my_age_mean_of_machine_brand, PC_repair, PC_repair_catprod = 'not found', 'not found', 'not found', 'not found'

    return my_number_of_machine_brand, my_age_mean_of_machine_brand, PC_repair, my_useful_dataset_prodcat_brand, PC_repair_catprod, PC_repair_brand, the_message, PC_repair_catprod_pbcat

def PC_CI_repair_success(n_product,n_repair, c_i=90):
    if n_product >0:
        if c_i == 90:
            z_factor=1.645
        elif c_i ==95:
            z_factor=1.96
        else:
            z_factor=1.645

        proba_success=round(n_repair/n_product,2)
        proba_interval= round(z_factor / (n_product * n_product **0.5)*(n_repair*(n_product-n_repair))**0.5,2)
        return proba_success, proba_interval
    else:
        return "not found","not found"

def magic_number( PC_repair_brand,CI_repair_brand,PC_repair_catprod,CI_repair_catprod, PC_repair_catprod_pbcat,
                  CI_repair_catprod_pbcat, PC_repair, CI_repair):
    vector=[0.335,0.4069,0.2356,0.01]
    magic_number=(PC_repair-CI_repair)*vector[0]+(PC_repair_brand-CI_repair_brand)*vector[1]+\
                 (PC_repair_catprod-CI_repair_catprod)*vector[2] + (PC_repair_catprod_pbcat-CI_repair_catprod_pbcat)*vector[3]
    magic_number=magic_number/sum(vector)
    print(magic_number)
    return magic_number

def lognormal_cdf(x, mu, sigma):
    if x <= 0:
        return 0.0  # CDF is 0 for x <= 0

    # Calculate the CDF for the lognormal distribution
    cdf = 0.5 * (1 + erf((math.log(x) - mu) / (math.sqrt(2) * sigma)))
    return cdf

def find_in_list(the_string, the_list):
    results = []
    proper_value = ""
    the_string_upper = the_string.upper()
    the_list = [str(my_val).upper().strip() for my_val in the_list]
    for i, my_place in enumerate(the_list):
        if the_string_upper in my_place:
            results.append(my_place)
        else:
            pass
    # we extract the proper place
    if len(results) == 1:
        proper_value = results[0]
    elif len(results) > 1:
        proper_value = 'pick in the list'
    else:
        proper_value = 'not found'
    return proper_value, results

def get_co2_water_bonus(the_data, the_product, lang_var):
    the_usefull_data = the_data[the_data.product_category == the_product]
    if lang_var == 'UK':
        the_co2 = str(the_usefull_data.CO2e.iloc[0]).replace(',', ' to ')
        the_water = str(the_usefull_data.water_L.iloc[0]).replace(',', ' to ')
        the_bonus = 'NO'
        if 'TBD' in the_co2:
            the_co2_message = "🌿 CO2: no data on CO2 yet 🙄"
        else:
            the_co2_message = "🌿 CO2: if repaired, you'll save {} kg of CO2. Planet Earth will thank you 🌍🌎🌏".format(
                str(the_co2)[1:-1])

        if 'TBD' in the_water:
            the_water_message = "💧 WATER: no data on water yet 🙄"
        else:
            the_water_message = "💧 WATER: if repaired, you'll save {} L of water. Planet Earth will thank you 🐬🐳🐋".format(
                str(the_water)[1:-1])
        the_bonus_message = ""
    elif lang_var == 'FR':
        the_co2 = str(the_usefull_data.CO2e.iloc[0]).replace(',', ' à ')
        the_water = str(the_usefull_data.water_L.iloc[0]).replace(',', ' à ')
        the_bonus = str(the_usefull_data.Bonus_euros.iloc[0])
        if 'TBD' in the_co2:
            the_co2_message = "🌿 CO2: pas encore de data dispo 🙄"
        else:
            the_co2_message = "🌿 CO2: si tu répares, {} kg de CO2 évités. La planète te dit merci 💛".format(
                str(the_co2)[1:-1])

        if 'TBD' in the_water:
            the_water_message = "💧 EAU: pas encore de data dispo 🙄"
        else:
            the_water_message = "💧 EAU: si tu répares, {} L d'eau évitées. La planète te dit merci 🐬🐳🐋".format(
                str(the_water)[1:-1])
        if the_bonus != 'nan':
            the_bonus_message = "💰 Eligible au bonus d'état réparation de {} euros*".format(str(the_bonus))
        else:
            the_bonus_message = "Cette réparation n'est pas encore éligible au bonus d'état*"
    else:
        the_co2_message, the_water_message, the_bonus_message = 'not found', 'not found', "not found"
    return the_co2_message, the_water_message, the_bonus_message

def crawl_query(query):
    req = requests.get(f"https://www.bing.com/search?q={query}" + "&answerCount=5&promote=webpages%2Cvideos", headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
    result_str = '<html><table style="border: none;">'  # Initializing the HTML code for displaying search results
    count_str = ''
    if req.status_code == 200:  # Status code 200 indicates a successful request
        bs = BeautifulSoup(req.content, features="html.parser")  # converting the content/text returned by request to a BeautifulSoup object
        search_result = bs.find_all("li",class_="b_algo")  # 'b_algo' is the class of the list object which represents a single result
        search_result = [str(i).replace("<strong>", "") for i in search_result]  # removing the <strong> tag
        search_result = [str(i).replace("</strong>", "") for i in search_result]  # removing the </strong> tag
        result_list = []

        for n, i in enumerate(search_result):  # iterating through the search results
            individual_search_result = BeautifulSoup(i, features="html.parser")  # converting individual search result into a BeautifulSoup object
            h2 = individual_search_result.find('h2')  # Finding the title of the individual search result
            href = h2.find('a').get('href')  # title's URL of the individual search result
            cite = f'{href[:50]}...' if len(href) >= 50 else href  # cite with first 20 chars of the URL
            url_txt = h2.find('a').text  # title's text of the individual search result
            # In a few cases few individual search results doesn't have a description. In such cases the description would be blank
            description = "" if individual_search_result.find('p') is None else individual_search_result.find('p').text[3:]
            # Appending the result data frame after processing each individual search result
            result_list.append({"Title": url_txt, "URL": href, "Description": description})
            ########################################################
            ######### HTML code to display search results ##########
            ########################################################
            description = description[:200] + '...'
            result_str += f'<tr style="border: none;"><h6><a href="{href}" target="_blank">{url_txt}</a></h6></tr><tr style="border: none;"><h7>{description}</h7></tr><tr style="border: none;"><h6>{""}</h6></tr>'
            if n > 10:
                break

        result_str += '</table></html>'
        count_str = f'<b style="font-size:12px;">Search returned {len(result_list)} results</b>'
        result_df = pd.DataFrame(result_list)
    else:
        result_df = pd.DataFrame({"Title": "", "URL": "", "Description": ""}, index=[0])
        result_str = '<html></html>'
        count_str = '<b style="font-size:20px;">Looks like an error!!</b>'

    return result_df, result_str, count_str

def build_data_dict_to_push(my_final_cat, my_final_object, my_final_brand, lang_var, my_age, my_pb_cat_selected,
                            other_inputs):
    data_dict = {'timestamp': [str(datetime.now())], 'category': [str(my_final_cat)], 'object': [str(my_final_object)],
                 'brand': [str(my_final_brand)], 'age': [str(my_age)], 'pb_category': [str(my_pb_cat_selected)],
                 'other_inputs': [str(other_inputs)], 'language': [str(lang_var)]}
    return data_dict

def write_data_in_gsheet_db(data_dict, DB_URL):
    try:
        sh = gc.open_by_url(DB_URL)
        new_data = pd.DataFrame(data_dict)
        new_data_values = new_data.values.tolist()
        sh[0].append_table(new_data_values, start='A1', end=None, dimension='ROWS', overwrite=False)
    except:
        print('error in pushing data to database')

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_img_with_href(local_img_path, target_url):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''<a href="{target_url}"><img src="data:image/{img_format};base64,{bin_str}" width="100%" height="auto"/></a>'''
    return html_code