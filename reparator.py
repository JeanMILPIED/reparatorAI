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

col10, col11, col12=st.columns([2,3,1])
lang_var = col12.radio("",('UK','FR'))
col11.title('REPARATOR.AI ')

if lang_var=='UK':
    col10.title('🔮🧠😻🌎🛠🙏')
    col11.write('In 1 minute, we will tell you if you can repair. For free, of course !')
    st.write('')
    st.subheader('Can anybody repair my machine please ? 😰')

elif lang_var=='FR':
    col11.write("En 1 minute, le premier site à te dire si ça peut se réparer. Et c'est gratuit !")
    col10.title('🔮🧠😻🌎🛠🙏')
    st.write('')
    st.subheader('Mon objet est-il réparable ? 😰')

else:
    st.write('error language')

def local_css(filename):
    with open(filename) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def clean_df(df):
    df_ok=df[df.year_of_manufacture>1950]
    my_brand_low_freq=df_ok.brand.value_counts()[df_ok.brand.value_counts()<10].index.tolist()
    df_ok=df_ok[df_ok.brand.isin(my_brand_low_freq)==False]
    df_ok=df_ok[df_ok.repair_status!='Unknown']
    df_ok['repair_barrier_if_end_of_life']=df_ok['repair_barrier_if_end_of_life'].fillna('Unspecified')
    return df_ok

def extract_info_machine(my_dataset,my_machine, my_brand, lang_var):
    if lang_var=='UK':
        the_message='Oups too few data for reparatorAI to answer 🙄'
    elif lang_var=='FR':
        the_message = 'Oups pas assez de données pour que reparatorAI te réponde 🙄'
    else:
        st.write('error')
    my_useful_dataset = my_dataset
    my_useful_dataset = my_useful_dataset[my_useful_dataset['product_category'] == my_machine]
    if my_useful_dataset.shape[0]>0:
        my_percent_of_repair_product = round(
            my_useful_dataset[my_useful_dataset['repair_status'] == 'Fixed'].shape[0] / my_useful_dataset.shape[0], 2)
    else:
        my_percent_of_repair_product='not found'

    my_useful_dataset = my_useful_dataset[my_useful_dataset['brand_ok'] == my_brand]
    if my_useful_dataset.shape[0] > 0:
        my_number_of_machine_brand = my_useful_dataset.shape[0]
        my_percent_of_repair = round(my_useful_dataset[my_useful_dataset['repair_status']=='Fixed'].shape[0] / my_number_of_machine_brand, 2)
        my_age_mean_of_machine_brand = round(my_useful_dataset['product_age'].median(), 2)
        
    #final message
        if my_number_of_machine_brand>10:
            if my_percent_of_repair >0.5:
                if lang_var=='UK':
                    the_message='Run to repair ! 😍'
                elif lang_var=='FR':
                    the_message='Cours le faire réparer ! 😍'
                else: st.write('error')
            elif ((my_percent_of_repair <0.5) & (my_percent_of_repair_product>0.5)):
                if lang_var=='UK':
                    the_message='You should try to repair it 😙'
                elif lang_var=='FR':
                    the_message = "Ca vaut le coup d'essayer de le réparer 😙"
                else:
                    st.write('error')
            else:
                if lang_var=='UK':
                    the_message='Contact an expert! 😎'
                elif lang_var=='FR':
                    the_message = 'Il te faut un expert de la réparation! 😎'
                else:
                    st.write('error')
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

def get_co2_water(the_data,the_product, lang_var):
    the_usefull_data=the_data[the_data.product_category==the_product]
    if lang_var=='UK':
        the_co2=str(the_usefull_data.CO2e.iloc[0]).replace(',',' to ')
        the_water=str(the_usefull_data.water_L.iloc[0]).replace(',',' to ')
        if 'TBD' in the_co2:
            the_co2_message = "CO2: no data on CO2 yet 🙄"
        else:
            the_co2_message = "CO2: if repaired, you'll save {} kg of CO2. Planet Earth will thank you 🌍🌎🌏".format(str(the_co2)[1:-1])

        if 'TBD' in the_water:
            the_water_message = "WATER: no data on water yet 🙄"
        else:
            the_water_message = "WATER: if repaired, you'll save {} L of water. Planet Earth will thank you 🐬🐳🐋".format(
                str(the_water)[1:-1])
    elif lang_var=='FR':
        the_co2 = str(the_usefull_data.CO2e.iloc[0]).replace(',', ' à ')
        the_water = str(the_usefull_data.water_L.iloc[0]).replace(',', ' à ')
        if 'TBD' in the_co2:
            the_co2_message = "CO2: pas encore de data dispo 🙄"
        else:
            the_co2_message = "CO2: si tu répares,  {} kg de CO2 évitées. La planète te dit merci 🌍🌎🌏".format(
                str(the_co2)[1:-1])

        if 'TBD' in the_water:
            the_water_message = "EAU: pas encore de data dispo 🙄"
        else:
            the_water_message = "EAU: si tu répares, {} L d'eau évitées. La planète te dit merci 🐬🐳🐋".format(
                str(the_water)[1:-1])
    else:
        the_co2_message, the_water_message = 'not found', 'not found'
    return the_co2_message, the_water_message

def crawl_query(query):
    req = requests.get(f"https://www.bing.com/search?q={query}", headers={"user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'})
    result_str = '<html><table style="border: none;">' #Initializing the HTML code for displaying search results
    if req.status_code == 200: #Status code 200 indicates a successful request
        bs = BeautifulSoup(req.content, features="html.parser") #converting the content/text returned by request to a BeautifulSoup object
        search_result = bs.find_all("li", class_="b_algo") #'b_algo' is the class of the list object which represents a single result
        search_result = [str(i).replace("<strong>","") for i in search_result] #removing the <strong> tag
        search_result = [str(i).replace("</strong>","") for i in search_result] #removing the </strong> tag
        result_df = pd.DataFrame() #Initializing the data frame that stores the results

        for n,i in enumerate(search_result): #iterating through the search results
            individual_search_result = BeautifulSoup(i, features="html.parser") #converting individual search result into a BeautifulSoup object
            h2 = individual_search_result.find('h2') #Finding the title of the individual search result
            href = h2.find('a').get('href') #title's URL of the individual search result
            cite = f'{href[:50]}...' if len(href) >= 50 else href # cite with first 20 chars of the URL
            url_txt = h2.find('a').text #title's text of the individual search result
            #In a few cases few individual search results doesn't have a description. In such cases the description would be blank
            description = "" if individual_search_result.find('p') is None else individual_search_result.find('p').text
            #Appending the result data frame after processing each individual search result
            result_df = result_df.append(pd.DataFrame({"Title": url_txt, "URL": href, "Description": description}, index=[n]))
            count_str = f'<b style="font-size:20px;">Bing Search returned {len(result_df)} results</b>'
            ########################################################
            ######### HTML code to display search results ##########
            ########################################################
            result_str += f'<tr style="border: none;"><h3><a href="{href}" target="_blank">{url_txt}</a></h3></tr>'+\
            f'<tr style="border: none;"><strong style="color:green;">{cite}</strong></tr>'+\
            f'<tr style="border: none;">{description}</tr>'+\
            f'<tr style="border: none;"><td style="border: none;"></td></tr>'
        result_str += '</table></html>'

    #if the status code of the request isn't 200, then an error message is displayed along with an empty data frame
    else:
        result_df = pd.DataFrame({"Title": "", "URL": "", "Description": ""}, index=[0])
        result_str = '<html></html>'
        count_str = '<b style="font-size:20px;">Looks like an error!!</b>'

    return result_df, result_str, count_str

if lang_var=='UK':
    dict_screen={"selectBox1":"OBJECT name - chose the right one",
                 "textInput1":"BRAND",
                 "selectBox2":'the BRAND',
                 "textInput2":'NOT FOUND !',
                 "textInput3": "the AGE (years)",
                 "button1": "let's find repairs! 🧠 ",
                 "button2": "Best websites to find repair 🚀",
                 "textInput4":'THE STATISTICS BEHIND IT',
                 "textInput5":'# FAILED {} {}',
                 "textInput6":'MEAN AGE (years)',
                 "textInput7": 'REPAIR SUCCESS RATE (%)',
                 "textInput8":'# {} {} OF SAME AGE',
                 "textInput9":'REPAIRS SUCCESS RATE (%) FOR {}',
                 "textInput10":"Send me a comment! 🦄",
                 "textInput11":"French Actors for Repair 🚀"}
elif lang_var=='FR':
    dict_screen={"selectBox1":"L'OBJET que tu souhaites réparer ",
                 "textInput1":"MARQUE",
                 "selectBox2":"la MARQUE",
                 "textInput2":'PAS TROUVé !',
                 "textInput3": "Quel AGE a-t-il ? (en années)",
                 "button1": "Allons trouver si c'est réparable ! 🧠 ",
                 "button2": "Le meilleur du Web 🚀",
                 "textInput4": 'STATISTIQUES DE PANNES',
                 "textInput5": "NOMBRE DE {} {} EN PANNE",
                 "textInput6": "AGE MOYEN (années)",
                 "textInput7": "% DES REPARATIONS REUSSIES",
                 "textInput8": "NOMBRE DE {} {} DU MÊME AGE QUE LE MIEN",
                 "textInput9": "% DES REPARATIONS REUSSIES DANS CETTE CATEGORIE {}",
                 "textInput10": "Envois-moi un avis! 🦄",
                 "textInput11": "Les acteurs Français de la réparation 🚀"
                 }
selectObjectList_UK=['POWER TOOL', 'TOY', 'HAIR DRYER', 'DECORATIVE OR SAFETY LIGHTS', 'LAMP',
 'PORTABLE RADIO', 'HANDHELD ENTERTAINMENT DEVICE', 'FOOD PROCESSOR', 'SMALL HOME ELECTRICAL',
 'HAIR & BEAUTY ITEM', 'MISC', 'SEWING MACHINE', 'WATCH/CLOCK', 'HI-FI SEPARATES',
 'DESKTOP COMPUTER', 'BATTERY/CHARGER/ADAPTER', 'SMALL KITCHEN ITEM', 'VACUUM',
 'TV AND GAMING-RELATED ACCESSORIES', 'COFFEE MAKER', 'KETTLE', 'IRON',
 'DIGITAL COMPACT CAMERA', 'PRINTER/SCANNER', 'LAPTOP', 'HI-FI INTEGRATED',
 'PAPER SHREDDER', 'TOASTER', 'FLAT SCREEN', 'MOBILE', 'TABLET', 'DSLR/VIDEO CAMERA',
 'HEADPHONES', 'LARGE HOME ELECTRICAL', 'MUSICAL INSTRUMENT', 'PROJECTOR',
 'PC ACCESSORY', 'AIRCON/DEHUMIDIFIER', 'FAN', 'GAMES CONSOLE']

selectObjectList_FR=['Outil Bricolage', 'Jouet', 'Sèche cheveux', 'Luminaires et guirlandes déco',
 'Lampe', 'Radio portable', 'Appareil de divertissement portable', 'Robot de cuisine', 'Petit électroménager de maison',
 'équipement pour cheveux & beauté', 'Divers', 'Machine à coudre', 'Montre / Réveil', 'Composants HI-Fi', 'Ordinateur de Bureau',
 'Batterie / chargeur / adaptateur', 'Petit électroménager de cuisine', 'Aspirateur', 'accessoire TV et jeux videos', 'Machine à café',
 'Bouilloir', 'Fer à repasser', 'Appareil photo numérique', 'Imprimante / scanner', 'Ordinateur portable', 'Hi-Fi', 'Broyeuse à papier',
 'Grille pains', 'Ecran plat', 'Téléphone portable', 'Tablette', 'Camescope', 'Ecouteurs', 'Gros électroménager',
 'Instrument de musique', 'Vidéo projecteur', 'Accessoire PC', 'Climatiseur / déshumidificateur', 'Ventilateur', 'Console de jeux vidéo']
selectObjectList_FR=[my_str.upper() for my_str in selectObjectList_FR]

my_data=pd.read_csv('OpenRepairData_v0.3_aggregate_202204.csv')
my_data['brand']=[str(my_val).upper().strip() for my_val in my_data.brand]
my_data['product_category']=[str(my_val).upper().strip() for my_val in my_data.product_category]
my_data=clean_df(my_data)
my_final_object=''
my_final_brand=''

my_co2_w_data=pd.read_csv('df_water_CO2_goods_fill.csv', index_col=0)
my_co2_w_data['product_category'] = [str(my_val).upper().strip() for my_val in my_co2_w_data.index]

if lang_var=='UK':
    my_final_object = st.selectbox(dict_screen["selectBox1"], tuple(sorted(selectObjectList_UK)))
elif lang_var=='FR':
    my_final_object_FR = st.selectbox(dict_screen["selectBox1"], tuple(sorted(selectObjectList_FR)))
    index_in_list=selectObjectList_FR.index(my_final_object_FR)
    my_final_object=selectObjectList_UK[index_in_list]

my_final_brand = st.selectbox(dict_screen["selectBox2"], tuple(pd.Series(my_data[my_data.product_category==my_final_object].brand_ok.unique()).sort_values().tolist()))
my_age=st.text_input(dict_screen["textInput3"], value=0, max_chars=None, key=None, type="default")

col1, col3, col2=st.columns([2,1,2])
if col1.button(dict_screen["button1"]):
    try:
        my_number_of_machine_brand, my_age_mean_of_machine_brand, my_percent_of_repair, useful_data , my_percent_of_repair_product, the_message= extract_info_machine(my_data, my_final_object, my_final_brand, lang_var)
        if lang_var=="UK":
            st.subheader('for {} {} of {} years old'.format(my_final_object, my_final_brand, my_age))
            st.subheader(the_message)
        elif lang_var=='FR':
            st.subheader('pour {} {} de {} ans'.format(my_final_object_FR, my_final_brand, my_age))
            st.subheader(the_message)
        the_co2_message, the_water_message=get_co2_water(my_co2_w_data,my_final_object, lang_var)
        st.write(the_co2_message)
        st.write(the_water_message)

        if lang_var=='FR':
            my_final_object=my_final_object_FR

        with st.expander(dict_screen["textInput4"]):
            col5, col6, col7= st.columns(3)
            st.metric(dict_screen["textInput5"].format(my_final_object, my_final_brand), my_number_of_machine_brand, delta=None, delta_color="normal")
            st.metric(dict_screen["textInput6"], my_age_mean_of_machine_brand, delta=None, delta_color="normal")
            st.metric(dict_screen["textInput7"], round(my_percent_of_repair*100,1), delta=None, delta_color="normal")

            useful_data=useful_data.dropna(axis=0, subset=['product_age'])
            useful_data_age=useful_data[np.abs(useful_data.product_age - int(my_age))<=1]
            col8,col9=st.columns(2)
            st.metric(dict_screen["textInput8"].format(my_final_object, my_final_brand), useful_data_age.shape[0], delta=None, delta_color="normal")

            if useful_data_age.shape[0]>0:
                my_own_pc_repair=round(useful_data_age[useful_data_age['repair_status']=='Fixed'].shape[0] / useful_data_age.shape[0], 2)
                st.metric(dict_screen["textInput7"], round(my_own_pc_repair * 100,1),
                            delta=round(my_own_pc_repair * 100 - my_percent_of_repair * 100,1), delta_color="normal")
            else:
                my_own_pc_repair='Not found any'
                st.metric(dict_screen["textInput7"], my_own_pc_repair)

            if ((my_percent_of_repair_product != 'not found') & (my_own_pc_repair != 'not found')):
                st.metric(dict_screen["textInput9"].format(my_final_object), round(my_percent_of_repair_product * 100, 1),
                            delta=round(my_percent_of_repair_product * 100 - my_percent_of_repair * 100, 1), delta_color="normal")
        #         #we save logs
    #         this_is_now=datetime.now()
    #         list_info=[this_is_now,my_final_object, my_final_brand, my_age]
    #         with open('reparator_logs.csv', 'a', newline='\n') as f:
    #             writer =csv.writer(f)
    #             writer.writerow(list_info)
    except:
        if lang_var=='UK':
            st.write('MISSING INFO')
        elif lang_var=='FR':
            st.write('INFORMATION MANQUANTE')
        else:
            st.write ('error')

if col2.button(dict_screen["button2"]):
    if lang_var == 'UK':
        query='repair {} {} fixit tutorial'.format(my_final_object, my_final_brand).replace(' ','+')
    elif lang_var == 'FR':
        query='réparation {} {} tuto comment faire réparer'.format(my_final_object, my_final_brand).replace(' ','+')
    try:
        result_df, result_str, count_str=crawl_query(query)
        st.markdown(f'{count_str}', unsafe_allow_html=True)
        st.markdown(f'{result_str}', unsafe_allow_html=True)
    except:
        st.write('OOOps  - no internet connexion maybe')
    #st.markdown('<h3>Data Frame of the above search result</h3>', unsafe_allow_html=True)
    #st.dataframe(result_df)

st.write("-----------------------------------------------")

from PIL import Image
PD_img= Image.open('Produits-Durables_logo.png')
col12,col13=st.columns(2)
col12.image(PD_img, width=300)
if lang_var=='UK':
    col13.write("You want to know more on repair and durability, let's meet on  https://www.produitsdurables.fr")
elif lang_var=='FR':
    col13.write("Pour plus de conseils pour réparer et faire durer ses objets, rendez-vous sur https://www.produitsdurables.fr")
else:
    st.write ('error')

with st.expander(dict_screen["textInput11"]):
    st.write('1001PIECES: https://www.1001pieces.com/')
    st.write('ENVIE: https://www.envie.org/sequiper-reparer/')
    st.write('iFIXIT: https://fr.ifixit.com/')
    st.write('LeSitedeLaPiece: https://www.lesitedelapiece.com/content/8-tous-nos-appareils')
    st.write('MURFY: https://murfy.fr/')
    st.write('PRODUITS DURABLES: https://www.produitsdurables.fr/')
    st.write('REPAIR CAFE: https://www.repaircafe.org/fr/')
    st.write('REPAIR CAFE PARIS: https://www.repaircafeparis.fr/')
    st.write('REEVIVE: https://www.reevive.fr/')
    st.write('SOSAV: https://www.sosav.fr/guides/electromenager/petit-electromenager/')
    st.write('SPAREKA: https://www.spareka.fr/')

if st.button(dict_screen["textInput10"]):
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

st.caption('Version 16/11/2022')
if lang_var=='UK':
    st.caption('data source is : https://openrepair.org/open-data/downloads/')
    st.caption('you want to contribute ? I am a huge coffee fan! https://www.buymeacoffee.com/jeanmilpied ')

elif lang_var=='FR':
    st.caption('lien vers les données sources : https://openrepair.org/open-data/downloads/')
    st.caption("tu veux contribuer ? ça tombe bien, j'adore le café: ! https://www.buymeacoffee.com/jeanmilpied ")
else:
    st.write ('error')

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





