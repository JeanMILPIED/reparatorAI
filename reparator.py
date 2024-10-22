import streamlit as st
import pygsheets
from google.oauth2 import service_account
import time

from utils import *

warnings.filterwarnings("ignore")

#needed to connect to googlesheet db
SCOPES = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
service_account_info=st.secrets["gcp_service_account"]
my_credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
gc = pygsheets.authorize(custom_credentials=my_credentials)
DB_URL="https://docs.google.com/spreadsheets/d/1m0lG7b2Ze-Armz-C-5MLH960dk5v1I-mLyoaUk5WAyE/edit?usp=drive_link"

# Create a button with custom styles
def custom_button(the_link, the_text, the_bkgd_color):
    button_html = f"""
    <style>
    .raizuum-button {{
        background-color: {the_bkgd_color}; /* Blue default background */
        color: white !important; /* White font with important to override other styles */
        padding: 5px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px; /* Rounded square shape */
        border: none; /* Remove border */
    }}
    </style>
    <a href="{the_link}" target="_blank" class="raizuum-button">{the_text}</a>
    """
    return button_html

def local_css(filename):
    with open(filename) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

emoji_list=["🎸","📻","🛠","📠","☎","🖨","💻","🖥","🖱","📸","📺","⌚","🕹","🎮","🎤","🎧","😎","🌎"]

######---- main front code here ---
st.image("images/bannerTop.jpg")
col10, col11, col12=st.columns([1,20,4])
lang_var = col12.radio("",('FR','UK'))
col11.title('REPARATOR.AI')

if lang_var=='UK':
    col11.write('#### *`In less than 1 minute`, we will be the first to tell you if you can `repair`. For `free`, of course !*')
    st.write('')
elif lang_var=='FR':
    col11.write("#### *`En moins d'1 minute`, le premier site à te dire si ça peut se `réparer`. Et c'est `gratuit` !*")
    st.write('')
else:
    st.write('error language')

dict_screen_all={"UK":
                     {"selectBox0":"1️⃣ **CATEGORY**",
                     "selectBox1":"2️⃣ **OBJECT TYPE**",
                     "textInput1":"BRAND",
                     "selectBox2":'3️⃣ **BRAND**',
                     "textInput2":'NOT FOUND !',
                     "textInput3": "4️⃣ **AGE** (years)",
                     "button1": "**Let's find repairs !** 🛠 ",
                     "button2": "Best repair tutorials on the web 🚀",
                     "textInput4":'THE STATISTICS BEHIND IT in our database',
                     "textInput5":'# FAILED {} {}',
                     "textInput6":'MEAN AGE of failures (years)',
                     "textInput7": 'REPAIR SUCCESS RATE (%)',
                     "textInput8":'# {} {} OF SAME AGE',
                     "textInput9":'REPAIR SUCCESS RATE (%) FOR {}',
                     "textInput10":"🦄 Send me a comment!",
                     "textInput11":"🐓 French Actors for Repair",
                     "textInput12":"⚠ Age is missing",
                     "textInput13" : "6️⃣ **OTHER USEFUL INFO** here",
                     "textInput14" : "#### About ReparatorAI 👓",
                     "textInput15" : "#### Should I repair or should I throw ? ⁉",
                     "textInput16": "Created in 2022, **ReparatorAI** is a **free tool** based on opendata. A database of more than 190'000 repairs is analysed at every request to offer you **best advice** about your broken object. Today, more than 1000 people use it worldwide.",
                     "textInput17": "5️⃣ **THE PROBLEM** looks like :",
                     "textInput18": '{} REPAIR SUCCESS RATE (%)',
                     "textInput19": 'SAME AGE',
                     "textInput20": 'Today in our database, you will find **{} repair events on {} equipment types from {} different brands**. Go for an exploration ⏬',
                     "textInput21": "YOUR PRODUCT",
                     "textInput22": "**I want to contribute 🚀**"
                     },
                 "FR":
                    {"selectBox0":"1️⃣ **CATEGORIE**",
                     "selectBox1":"2️⃣ **TYPE D'OBJET** ",
                     "textInput1":"MARQUE",
                     "selectBox2":"3️⃣ **MARQUE**",
                     "textInput2":'PAS TROUVé !',
                     "textInput3": "4️⃣ **AGE** (en années)",
                     "button1": "**Voyons si c'est réparable !** 🛠 ",
                     "button2": "Les meilleurs Tutos du Web 🚀",
                     "textInput4": 'STATISTIQUES DE PANNES dans notre database',
                     "textInput5": "{} {} EN PANNE",
                     "textInput6": "AGE moyen des pannes (années)",
                     "textInput7": "% DE SUCCES DES REPARATIONS",
                     "textInput8": "{} {} DU MÊME AGE",
                     "textInput9": "% DE SUCCES DES REPARATIONS DE {}",
                     "textInput10": " 🦄 Envoie-moi un avis!",
                     "textInput11": " 🐓 Les acteurs Français de la réparation",
                     "textInput12" : "⚠ Indiquez l'Age de la machine",
                     "textInput13" : "6️⃣ **AUTRE INFO UTILE** ici",
                     "textInput14" : "#### Tout sur ReparatorAI 👓",
                     "textInput15" : "#### Dis-moi que je peux réparer mon objet en panne ! ⁉",
                     "textInput16" : "Conçu en 2022, **ReparatorAI** est un outil **gratuit** basé sur de l'opendata. Une base de donnée de plus de 190'000 réparations est analysée à chaque requète pour t'informer du **meilleur choix face à une panne**. Il est aujourd'hui utilisé par plus de 1000 personnes dans le monde.",
                     "textInput17": "5️⃣ **LA PANNE** a l'air d'être d'origine :",
                     "textInput18": "% DE SUCCES DE REPARATION {} ",
                     "textInput19": "AU MEME AGE",
                     "textInput20": "Aujourd'hui, dans notre base de données, tu trouveras **{} réparations portant sur {} types d'équipements de {} marques différentes**. L'exploration c'est par là ⏬",
                     "textInput21": "TON PRODUIT",
                     "textInput22": "**Je veux contribuer 🚀**"
                     }
                 }

topCategory={"UK":['BATHROOM', 'ELECTRONICS', 'HOME', 'IMAGE', 'KITCHEN', 'OFFICE', 'OTHER', 'SOUND'],
             "FR":['SALLE DE BAIN','ELECTRONIQUE','MAISON','IMAGE','CUISINE','BUREAU','AUTRES','SON']}

pb_category={"UK":["Mechanical","Electric/Electronic","Fire/leaks/dirt","I don't know"],
             "FR":["Mécanique","Electrique/Electronique","Feu/Fuite/Saleté","Je ne sais pas"],
             "values":['M','E','O','U']}

selectObjectList={"UK": ['POWER TOOL', 'TOY', 'HAIR DRYER', 'DECORATIVE OR SAFETY LIGHTS', 'LAMP',
                         'PORTABLE RADIO', 'HANDHELD ENTERTAINMENT DEVICE', 'FOOD PROCESSOR', 'SMALL HOME ELECTRICAL',
                         'HAIR & BEAUTY ITEM', 'MISC', 'SEWING MACHINE', 'WATCH/CLOCK', 'HI-FI SEPARATES',
                         'DESKTOP COMPUTER', 'BATTERY/CHARGER/ADAPTER', 'SMALL KITCHEN ITEM', 'VACUUM',
                         'TV AND GAMING-RELATED ACCESSORIES', 'COFFEE MAKER', 'KETTLE', 'IRON',
                         'DIGITAL COMPACT CAMERA', 'PRINTER/SCANNER', 'LAPTOP', 'HI-FI INTEGRATED',
                         'PAPER SHREDDER', 'TOASTER', 'FLAT SCREEN', 'MOBILE', 'TABLET', 'DSLR/VIDEO CAMERA',
                         'HEADPHONES', 'LARGE HOME ELECTRICAL', 'MUSICAL INSTRUMENT', 'PROJECTOR',
                         'PC ACCESSORY', 'AIRCON/DEHUMIDIFIER', 'FAN', 'GAMES CONSOLE'],
                    "FR": ['OUTIL BRICOLAGE', 'JOUET', 'SÈCHE CHEVEUX', 'LUMINAIRES ET GUIRLANDES DÉCO',
                           'LAMPE', 'RADIO PORTABLE', 'APPAREIL DE DIVERTISSEMENT PORTABLE', 'ROBOT DE CUISINE',
                           'PETIT ÉLECTROMÉNAGER DE MAISON', 'ÉQUIPEMENT POUR CHEVEUX & BEAUTÉ', 'DIVERS',
                           'MACHINE À COUDRE', 'MONTRE / RÉVEIL', 'COMPOSANTS HI-FI', 'ORDINATEUR DE BUREAU',
                           'BATTERIE / CHARGEUR / ADAPTATEUR', 'PETIT ÉLECTROMÉNAGER DE CUISINE', 'ASPIRATEUR',
                           'ACCESSOIRE TV ET JEUX VIDEOS', 'MACHINE À CAFÉ', 'BOUILLOIRE', 'FER À REPASSER',
                           'APPAREIL PHOTO NUMÉRIQUE', 'IMPRIMANTE / SCANNER', 'ORDINATEUR PORTABLE', 'HI-FI',
                           'BROYEUSE À PAPIER', 'GRILLE PAINS', 'ECRAN PLAT', 'TÉLÉPHONE PORTABLE', 'TABLETTE',
                           'CAMESCOPE', 'ECOUTEURS', 'GROS ÉLECTROMÉNAGER', 'INSTRUMENT DE MUSIQUE',
                           'VIDÉO PROJECTEUR', 'ACCESSOIRE PC', 'CLIMATISEUR / DÉSHUMIDIFICATEUR', 'VENTILATEUR',
                           'CONSOLE DE JEUX VIDÉO']}

#nettoyage de dataset source
my_data=pd.read_csv('data/OpenRepairData_v0.3_aggregate_202407.csv')
my_data=clean_df(my_data)
my_top_cat=''
my_final_object=''
my_final_brand=''
my_co2_w_data=pd.read_csv('data/df_water_CO2_goods_fill.csv', sep=';', encoding='latin',index_col=0)
my_co2_w_data['product_category'] = [str(my_val).upper().strip() for my_val in my_co2_w_data.index]
my_logN_data=pd.read_csv('data/lognormal_fit_cat_202312.csv', index_col=0)
my_quotes_data=pd.read_csv('data/quotes.csv', sep=';', encoding='latin')

#qui sommes nous
with st.container(border = True):
    st.write(dict_screen_all[lang_var]["textInput14"])
    st.write(dict_screen_all[lang_var]["textInput16"])
    st.write(dict_screen_all[lang_var]["textInput20"].format(my_data.shape[0], len(my_data.product_category.unique()),
                                               len(my_data.brand.unique())))

st.divider()
# partie sur les infos de réparation
st.write(dict_screen_all[lang_var]["textInput15"])

with st.container(border=True):

    dict_useful={"TopCategory":{"UK":"TopCategory","FR":"TopCategory_FR"},
                 "product_category":{"UK":"product_category","FR":"product_category_FR"}}

    _, topCategory_list = build_pick_up_list(my_data, dict_useful["TopCategory"][lang_var])
    my_final_cat = st.selectbox(dict_screen_all[lang_var]["selectBox0"], tuple(topCategory_list))
    my_final_cat = my_final_cat.split(' -')[0]
    index_in_list = topCategory[lang_var].index(my_final_cat)
    my_final_cat = topCategory["UK"][index_in_list]

    _, selectObjectList_cat_list = build_pick_up_list(my_data[my_data.loc[:,dict_useful["TopCategory"]["UK"]] == my_final_cat],
                                                         dict_useful["product_category"][lang_var])
    my_final_object = st.selectbox(dict_screen_all[lang_var]["selectBox1"], tuple(selectObjectList_cat_list))
    my_final_object = my_final_object.split(' -')[0]
    index_in_list = selectObjectList[lang_var].index(my_final_object)
    my_final_object = selectObjectList["UK"][index_in_list]
    my_final_object_FR = selectObjectList["FR"][index_in_list]

    _, selectBrandList = build_pick_up_list(my_data[(my_data.loc[:,dict_useful["TopCategory"]["UK"]] == my_final_cat)
                                                    & (my_data.loc[:,dict_useful["product_category"]["UK"]] == my_final_object)],
                                                             'brand')
    my_final_brand = st.selectbox(dict_screen_all[lang_var]["selectBox2"], tuple(selectBrandList))
    my_final_brand = my_final_brand.split(' -')[0]
    my_age=st.number_input(dict_screen_all[lang_var]["textInput3"], value=0, min_value=0, max_value=99, key=None, step=1)

    if my_age=="":
        st.write(dict_screen_all[lang_var]['textInput12'])

    my_pb_cat_selected = st.selectbox(dict_screen_all[lang_var]["textInput17"], tuple(pb_category[lang_var]))
    my_pb_cat_val = pb_category["values"][pb_category[lang_var].index(my_pb_cat_selected)]

    other_inputs = st.text_input(dict_screen_all[lang_var]['textInput13'], value=" ",max_chars=None, key=None, type="default")

col1, col3, col2=st.columns([2,1,2])
if col1.button(dict_screen_all[lang_var]["button1"], type="primary"):
    st.write('-----------------------------------')
    the_author, the_quote = get_quote(my_quotes_data, my_final_object, lang_var)
    bot_style(the_quote)
    st.write(the_author)
    with st.spinner('Wait for it...'):
        # write in db googlesheet
        data_dict = build_data_dict_to_push(my_final_cat, my_final_object, my_final_brand, lang_var, my_age,
                                            my_pb_cat_selected, other_inputs)
        write_data_in_gsheet_db(data_dict, DB_URL)

        my_number_of_machine_brand, my_age_mean_of_machine_brand, my_percent_of_repair, useful_data , my_percent_of_repair_product, my_percent_of_repair_brand, the_message, my_percent_of_repair_product_pbCat= extract_info_machine(my_data, my_final_object, my_final_brand, lang_var, my_pb_cat_val)
        proba_fail=compute_proba_fail(my_final_object,my_age,my_logN_data)
        the_co2_message, the_water_message, the_bonus_message = get_co2_water_bonus(my_co2_w_data, my_final_object, lang_var)


    st.write('-----------------------------------')
    st.write('**REPARATOR.AI**')
    if lang_var=="UK":
        if float(my_age) == 0:
            the_letter = ''
            my_age_print = 'less than 1'
        elif float(my_age) > 1:
            the_letter = 's'
            my_age_print = my_age
        else:
            the_letter = ''
            my_age_print = my_age
        bot_style('#### Worth trying to repair your {} {} of {} year{} old ?'.format(my_final_brand, my_final_object, my_age_print, the_letter))
        bot_style(the_message)
        bot_style(the_bonus_message)
        bot_style("##### INFO: computed probability of failure at this age is {}%".format(proba_fail))
    elif lang_var=='FR':
        if float(my_age) == 0:
            the_letter=''
            my_age_print = 'moins de 1'
        elif float(my_age) > 1:
            the_letter = 's'
            my_age_print=my_age
        else:
            the_letter = ''
            my_age_print=my_age
        bot_style('#### Réparer ta/ton {} {} de {} an{}, ça se tente ?'.format(my_final_object_FR, my_final_brand, my_age_print, the_letter))
        bot_style(the_message)
        bot_style(the_bonus_message)
        bot_style("##### INFO: la probabilité de tomber en panne à cet âge est de {}%".format(proba_fail))
        st.caption("(* toutes les infos sur https://www.ecosystem.eco/fr/article/qualirepar-equipements-concernes)")
    bot_style(the_co2_message)
    bot_style(the_water_message)

    if lang_var=='FR':
        my_final_object=my_final_object_FR

    with st.expander(dict_screen_all[lang_var]["textInput4"]):
        col5, col6, col7= st.columns([3,1,3])
        col5.metric(dict_screen_all[lang_var]["textInput7"], round(my_percent_of_repair*100,1), delta=None, delta_color="normal")
        col7.metric(dict_screen_all[lang_var]["textInput5"].format(my_final_object, my_final_brand), my_number_of_machine_brand, delta=None, delta_color="normal")
        col5.metric(dict_screen_all[lang_var]["textInput6"], my_age_mean_of_machine_brand, delta=None, delta_color="normal")

        useful_data=useful_data.dropna(axis=0, subset=['product_age'])
        useful_data_age=useful_data[abs(useful_data.product_age - int(my_age))<=1]
        col7.metric(dict_screen_all[lang_var]["textInput8"].format(my_final_object, my_final_brand), useful_data_age.shape[0], delta=None, delta_color="normal")

        if useful_data_age.shape[0]>0:
            my_own_pc_repair=round(useful_data_age[useful_data_age['repair_status']=='Fixed'].shape[0] / useful_data_age.shape[0], 2)
        else:
            my_own_pc_repair='not found'


        repair_data=[my_percent_of_repair,my_percent_of_repair_product_pbCat,my_own_pc_repair,my_percent_of_repair_product,my_percent_of_repair_brand]
        labels=[dict_screen_all[lang_var]["textInput21"],my_pb_cat_selected, dict_screen_all[lang_var]["textInput19"],my_final_object, my_final_brand]
        df_repair=pd.DataFrame([round(my_pc * 100,1) for my_pc in repair_data])
        df_repair[dict_screen_all[lang_var]["textInput7"]]=labels
        df_repair.columns=[" ",dict_screen_all[lang_var]["textInput7"]]
        st.vega_lite_chart(
            df_repair,
            {
                "mark": {"type": "bar","cornerRadiusEnd": 4},
                "encoding": {
                    "x": {"field": " ", "type": "quantitative"},
                    "y": {"field": dict_screen_all[lang_var]["textInput7"], "type": "nominal"},
                },
            }, use_container_width=True
        )

stripe_payment_url_good = "https://buy.stripe.com/4gw16x8yqckc1nGeUU"
col2.markdown(custom_button(stripe_payment_url_good, dict_screen_all[lang_var]["textInput22"], "#23c448"),
                        unsafe_allow_html=True)

st.write("-----------------------------------------------")

SC_hop="https://www.produitsdurables.fr"
hop_html = get_img_with_href('images/Produits-Durables_logo.png', SC_hop)
col12, col13 = st.columns(2)
col13.markdown(hop_html, unsafe_allow_html=True)

if lang_var=='UK':
    col12.write("You want to know more on repair and durability, let's meet on")
elif lang_var=='FR':
    col12.write("Pour plus de conseils pour réparer et faire durer ses objets, rendez-vous sur")
else:
    st.write ('error')

with st.expander(dict_screen_all[lang_var]["textInput11"]):
    st.write('1001PIECES: https://www.1001pieces.com/')
    st.write('ENVIE: https://www.envie.org/sequiper-reparer/')
    st.write('iFIXIT: https://fr.ifixit.com/')
    st.write('LeSitedeLaPiece: https://www.lesitedelapiece.com/content/8-tous-nos-appareils')
    st.write('LONGUE VIE AUX OBJETS (ADEME): https://longuevieauxobjets.ademe.fr/')
    st.write('MURFY: https://murfy.fr/')
    st.write('PRODUITS DURABLES: https://www.produitsdurables.fr/')
    st.write('REPAIR CAFE: https://www.repaircafe.org/fr/')
    st.write('REPAIR CAFE PARIS: https://www.repaircafeparis.fr/')
    st.write('REEVIVE: https://www.reevive.fr/')
    st.write('SOS-ACCESSOIRE: https://atelier.sos-accessoire.com/')
    st.write('SOSAV: https://www.sosav.fr/guides/electromenager/petit-electromenager/')
    st.write('SPAREKA: https://www.spareka.fr/')

if st.button(dict_screen_all[lang_var]["textInput10"]):
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

# insert ebay banner
SC_ebay = 'https://ebay.us/ZUNSOp'

#ebay banner
gif_html = get_img_with_href('images/CertifiedRefurb_980x400.jpg', SC_ebay)
st.markdown(gif_html, unsafe_allow_html=True)

st.image("images/bannerBottom.jpg")
st.caption('Version 22/10/2024 - ')
if lang_var=='UK':
    st.caption('Data source is : https://openrepair.org/open-data/downloads/')
    st.caption('Made with 💛 with Streamlit and Python')
    st.caption("Banner images generated with https://lexica.art")
elif lang_var=='FR':
    st.caption('Lien vers les données sources : https://openrepair.org/open-data/downloads/')
    st.caption('Fait avec 💛 avec Streamlit et Python')
    st.caption("Images générées par LexicaArt : https://lexica.art")
else:
    st.write ('error')

#insert stat_counter
SC_JS="""
<a title="Web Analytics" href="https://statcounter.com/" target="_blank"><img src="https://c.statcounter.com/12751623/0/9447ca5b/1/" alt="Web Analytics" ></a>
"""
st.components.v1.html(SC_JS)






