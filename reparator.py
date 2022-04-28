import streamlit as st
import pandas as pd
import numpy as np

col10, col11=st.columns(2)
col11.title('REPARATOR.AI ')

#col10.image('Mr_reparator.png')
col10.title('🔮🧠😻')
col10.subheader(' 🚀 free.open.share 🚀')
st.write('')
st.subheader('Can anybody repair my machine please ? 😰')

def extract_info_machine(my_dataset,my_machine, my_brand):
    the_message='Oups too few data for reparatorAI to answer 🙄'
    my_useful_dataset = my_dataset
    my_useful_dataset = my_useful_dataset[my_useful_dataset['product_category'] == my_machine]
    if my_useful_dataset.shape[0]>0:
        my_percent_of_repair_product = round(
            my_useful_dataset[my_useful_dataset['repair_status'] == 'Fixed'].shape[0] / my_useful_dataset.shape[0], 2)
    else:
        my_percent_of_repair_product='not found'

    my_useful_dataset = my_useful_dataset[my_useful_dataset['brand'] == my_brand]
    if my_useful_dataset.shape[0] > 0:
        my_number_of_machine_brand = my_useful_dataset.shape[0]
        my_percent_of_repair = round(my_useful_dataset[my_useful_dataset['repair_status']=='Fixed'].shape[0] / my_number_of_machine_brand, 2)
        my_age_mean_of_machine_brand = round(my_useful_dataset['product_age'].median(), 2)
        
    #final message
        if my_number_of_machine_brand>10:
            if my_percent_of_repair >0.5:
                the_message='run to repair ! 😍'
            elif ((my_percent_of_repair <0.5) & (my_percent_of_repair_product>0.5)):
                the_message='you should try to repair it 😙'
            else:
                the_message='contact an expert! 😎'
    else:
        my_number_of_machine_brand, my_age_mean_of_machine_brand, my_percent_of_repair, my_percent_of_repair_product='not found', 'not found', 'not found','not found'
    

    
    return my_number_of_machine_brand, my_age_mean_of_machine_brand, my_percent_of_repair, my_useful_dataset, my_percent_of_repair_product, the_message

def find_in_list(the_string, the_list):
    results=[]
    proper_value=""
    the_string_upper = the_string.upper()
    the_list = [str(my_val).upper().strip() for my_val in the_list]
    for i, my_place in enumerate(the_list):
        if the_string_upper in my_place:
            results.append(my_place)
        else:
            pass
    #we extract the proper place
    if len(results)==1:
        proper_value=results[0]
    elif len(results)>1:
        proper_value='pick in the list'
    else:
        proper_value='not found'
    return proper_value, results



my_data=pd.read_csv('OpenRepairData_v0.3_aggregate_202110.csv')
my_data['brand']=[str(my_val).upper().strip() for my_val in my_data.brand]
my_data['product_category']=[str(my_val).upper().strip() for my_val in my_data.product_category]
my_final_object=''
my_final_brand=''

col1, col2=st.columns(2)
my_object=col1.text_input("object name", value="", max_chars=None, key=None, type="default")
my_final_object, my_final_object_best_results=find_in_list(my_object, pd.Series(my_data.product_category.unique()).sort_values().tolist())
if my_final_object !='not found':
    my_final_object = col2.selectbox('chose the right one', tuple(my_final_object_best_results))
else:
    col2.write ('NOT FOUND !')

col3, col4=st.columns(2)
my_brand=col3.text_input("object brand", value="", max_chars=None, key=None, type="default")
my_final_brand, my_final_brand_best_results=find_in_list(my_brand, pd.Series(my_data[my_data.product_category==my_final_object].brand.unique()).sort_values().tolist())
if my_final_brand !='not found':
    my_final_brand = col4.selectbox('chose the right one', tuple(my_final_brand_best_results))
else:
    col4.write ('NOT FOUND !')

my_age=st.text_input("object age (years)", value=0, max_chars=None, key=None, type="default")

if st.button("let's find repairs! 🧠 "):
    try:
        my_number_of_machine_brand, my_age_mean_of_machine_brand, my_percent_of_repair, useful_data , my_percent_of_repair_product, the_message= extract_info_machine(my_data, my_final_object, my_final_brand)
        st.subheader('RESULT FOR {} {}'.format(my_final_object,my_final_brand))
        st.subheader(the_message)
        st.subheader('THE STATISTICS BEHIND IT')
        col5, col6, col7= st.columns(3)
        col5.metric('# FAILED OBJECTS', my_number_of_machine_brand, delta=None, delta_color="normal")
        col6.metric('MEAN AGE (years)', my_age_mean_of_machine_brand, delta=None, delta_color="normal")
        col7.metric('REPAIRS SUCCESS RATE (%)', round(my_percent_of_repair*100,1), delta=None, delta_color="normal")

        useful_data=useful_data.dropna(axis=0, subset=['product_age'])
        useful_data_age=useful_data[np.abs(useful_data.product_age - int(my_age))<=1]
        col8,col9=st.columns(2)
        col8.metric('# OBJECTS OF MY AGE', useful_data_age.shape[0], delta=None, delta_color="normal")

        if useful_data_age.shape[0]>0:
            my_own_pc_repair=round(useful_data_age[useful_data_age['repair_status']=='Fixed'].shape[0] / useful_data_age.shape[0], 2)
            col9.metric('REPAIRS SUCCESS RATE (%)', round(my_own_pc_repair * 100,1),
                        delta=round(my_own_pc_repair * 100 - my_percent_of_repair * 100,1), delta_color="normal")
        else:
            my_own_pc_repair='Not found any'
            col9.metric('REPAIRS SUCCESS RATE (%)', my_own_pc_repair)

        if ((my_percent_of_repair_product != 'not found') & (my_own_pc_repair != 'not found')):
            st.metric('REPAIRS SUCCESS RATE (%) FOR THIS PRODUCT CATEGORY', round(my_percent_of_repair_product * 100, 1),
                        delta=round(my_percent_of_repair_product * 100 - my_percent_of_repair * 100, 1), delta_color="normal")
    except:
        st.write('MISSING INFO')


st.caption('data source is : https://openrepair.org/open-data/downloads/')
st.caption('you want to contribute ? I am a huge coffee fan! https://www.buymeacoffee.com/jeanmilpied ')



