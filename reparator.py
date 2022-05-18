import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import csv
import pathlib
from bs4 import BeautifulSoup
import logging
import shutil

col10, col11=st.columns(2)
col11.title('REPARATOR.AI ')

#col10.image('Mr_reparator.png')
col10.title('🔮🧠😻🌎')
col10.subheader(' 🚀 free.open.share 🚀')
st.write('')
st.subheader('Can anybody repair my machine please ? 😰')

def local_css(filename):
    with open(filename) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

def get_co2_water(the_data,the_product):
    the_usefull_data=the_data[the_data.product_category==the_product]
    the_co2=str(the_usefull_data.CO2e.iloc[0]).replace(',',' to ')
    the_water=str(the_usefull_data.water_L.iloc[0]).replace(',',' to ')
    if 'TBD' in the_co2:
        the_co2_message = "CO2: no data on CO2 yet 🙄"
    else:
        the_co2_message = "CO2: if repaired, you'll save {} kg of CO2. Planet Earth will thank you 🌍🌎🌏".format(the_co2)

    if 'TBD' in the_water:
        the_water_message = "WATER: no data on water yet 🙄"
    else:
        the_water_message = "WATER: if repaired, you'll save {} L of water. Planet Earth will thank you 🐬🐳🐋".format(
            the_water)
    return the_co2_message, the_water_message


my_data=pd.read_csv('OpenRepairData_v0.3_aggregate_202110.csv')
my_data['brand']=[str(my_val).upper().strip() for my_val in my_data.brand]
my_data['product_category']=[str(my_val).upper().strip() for my_val in my_data.product_category]
my_final_object=''
my_final_brand=''

my_co2_w_data=pd.read_csv('df_water_CO2_goods_fill.csv', index_col=0)
my_co2_w_data['product_category'] = [str(my_val).upper().strip() for my_val in my_co2_w_data.index]

my_final_object = st.selectbox("OBJECT name - chose the right one", tuple(pd.Series(my_data.product_category.unique()).sort_values().tolist()))

col3, col4=st.columns(2)
my_brand=col3.text_input("BRAND", value="", max_chars=None, key=None, type="default")
my_final_brand, my_final_brand_best_results=find_in_list(my_brand, pd.Series(my_data[my_data.product_category==my_final_object].brand.unique()).sort_values().tolist())
if my_final_brand !='not found':
    my_final_brand = col4.selectbox('chose the right one', tuple(my_final_brand_best_results))
else:
    col4.write('NOT FOUND !')

my_age=st.text_input("object age (years)", value=0, max_chars=None, key=None, type="default")

if st.button("let's find repairs! 🧠 "):
    try:
        my_number_of_machine_brand, my_age_mean_of_machine_brand, my_percent_of_repair, useful_data , my_percent_of_repair_product, the_message= extract_info_machine(my_data, my_final_object, my_final_brand)
        st.subheader('for {} {} of {} years old'.format(my_final_object, my_final_brand, my_age))
        st.subheader('RESULT: ' + the_message)
        the_co2_message, the_water_message=get_co2_water(my_co2_w_data,my_final_object)
        st.write(the_co2_message)
        st.write(the_water_message)
        
        with st.expander('THE STATISTICS BEHIND IT'):
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
#         #we save logs
#         this_is_now=datetime.now()
#         list_info=[this_is_now,my_final_object, my_final_brand, my_age]
#         with open('reparator_logs.csv', 'a', newline='\n') as f:
#             writer =csv.writer(f)
#             writer.writerow(list_info)
    except:
        st.write('MISSING INFO')


st.write("Send me a comment! 🦄")
if st.button("GO!"):
    contact_form="""
    <form action="https://formsubmit.co/c66fb24c1e59b02bd2b4cf68f974cd89" method="POST">
         <input type="hidden" name="_captcha" value="false">
         <input type="text" name="name" placeholder="Your Name" required>
         <input type="email" name="email" placeholder="Your email" required>
         <textarea name="message" placeholder="your gentle words"></textarea>
         <button type="submit">Send</button>
    </form>
    """
    st.markdown(contact_form, unsafe_allow_html=True)
    local_css("style/style.css")

st.caption('data source is : https://openrepair.org/open-data/downloads/')
st.caption('you want to contribute ? I am a huge coffee fan! https://www.buymeacoffee.com/jeanmilpied ')

#insert the google analytics or stat_counter
GA_JS = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-MGD4ES78W6"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-MGD4ES78W6');
    </script>
    """

SC_JS="""
<a title="Web Analytics" href="https://statcounter.com/" target="_blank"><img src="https://c.statcounter.com/12751623/0/9447ca5b/1/" alt="Web Analytics" ></a>
"""

def inject_ga(GA_JS):
    GA_ID = "google_analytics"

    # Note: Please replace the id from G-XXXXXXXXXX to whatever your
    # web application's id is. You will find this in your Google Analytics account
    
    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):  # if cannot find tag
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # recover from backup
        else:
            shutil.copy(index_path, bck_index)  # keep a backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)

#inject_ga()
st.components.v1.html(SC_JS)





