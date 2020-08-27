# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 17:32:56 2020

@author: rejid4996
"""

import streamlit as st
import re
import os
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
import base64
from io import BytesIO
import time
import xlsxwriter
from SessionState import get

st.set_option('deprecation.showfileUploaderEncoding', False)
 
@st.cache()
def data_original(voc_data_orig, svoc_data_orig):
    voc_data = voc_data_orig[6:]
    svoc_data = svoc_data_orig[6:]
    
    return voc_data, svoc_data
  
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download file</a>' # decode b'abc' => abc      

#class tqdm:
#    def __init__(self, iterable, title=None):
#        if title:
#            st.write(title)
#        self.prog_bar = st.progress(0)
#        self.iterable = iterable
#        self.length = len(iterable)
#        self.i = 0
#
#    def __iter__(self):
#        for obj in self.iterable:
#            yield obj
#            self.i += 1
#            current_prog = self.i / self.length
#            self.prog_bar.progress(current_prog)

def main():
    """NLP App with Streamlit"""
    
    from PIL import Image
    logo = Image.open('ArcadisLogo.jpg')
    logo = logo.resize((300,90))
    
    st.sidebar.image(logo)
    
    st.sidebar.title("Tics Table Summarizer")
    st.sidebar.subheader("Table Manipulation")
    
    st.info("Summing all the relevant analytes")
    
    uploaded_file = st.sidebar.file_uploader("Choose the base file in the prescribed format", type="xlsx")
    
    if uploaded_file:
        #df = pd.read_excel(uploaded_file)
        
        # reading the files
        voc_data_orig = pd.read_excel(uploaded_file, sheet_name = "VOCs")
        svoc_data_orig = pd.read_excel(uploaded_file, sheet_name = "SVOCs")
        voc_list_df = pd.read_excel(uploaded_file, sheet_name = "VOC list")
        svoc_list_df = pd.read_excel(uploaded_file, sheet_name = "SVOC list")
        contamiants_df = pd.read_excel(uploaded_file, sheet_name = "List of Contaminents")
           
        voc_data, svoc_data = data_original(voc_data_orig, svoc_data_orig)
        
        # for all table manipulations
        #voc_data = voc_data_orig[6:]
        #svoc_data = svoc_data_orig[6:]
        
        # condition-1, matching voc table with voc list *
        voc_df_list = list(voc_data.iloc[:, 0])
        voc_list = list(voc_list_df.iloc[:, 0])
        
        svoc_df_list = list(svoc_data.iloc[:, 0])
        svoc_list = list(svoc_list_df.iloc[:, 0])
        
        st.sidebar.subheader("Criteria 1")
        
        st.markdown("### 🎲 Identify whether the TICs compounds (both VOCs and SVOCs) are target (TRG) compounds- For this, compare the TICs compounds with the TRG compounds in the lab report. If yes, insert a * along with the results throughout the compound results.")
        # token slider
        slider1 = st.sidebar.slider(label="choose the token sort ratio for voc",
                   min_value=50,
                   max_value=100,
                   value = 80,
                   step=5)
               
#        for i in tqdm(range(200), title=''):
#            time.sleep(0.05)
        
        #voc
        voc_id_list = []
        voc_ref_list = []
        for i in range(0, len(voc_df_list)):
            Str1 = voc_df_list[i]
            for j in range(0, len(voc_list)):
                Str2 = voc_list[j]
                Token_Sort_Ratio = fuzz.token_sort_ratio(Str1,Str2)
                if Token_Sort_Ratio > slider1: # <--- this can be tweaked
                    voc_id_list.append(i)
                    voc_ref_list.append(j)
        
        table_voc_df = []
        table_voc_list = []
        for i,j in zip(voc_id_list, voc_ref_list):
            table_voc_df.append(voc_df_list[i])
            table_voc_list.append(voc_list[j])
        
        table_voc_comparison = pd.DataFrame(list(zip(table_voc_df, table_voc_list)), columns = ["table value", "list value"])            
        table_voc_comparison.index = voc_id_list
        


        st.table(table_voc_comparison)
        
        #voc_id_list = st.sidebar.text_input("Select the index required from the voc table", "")
        
        
        
        voc_id_list = st.sidebar.multiselect("Select the index required from the voc table", 
                         voc_id_list)
        
        #voc_id_list = voc_id_list.split(",")
    
        voc_id_list = [int(i) for i in voc_id_list] 
            
        #run_button = st.sidebar.button(label='Run Extraction')
            
        voc_id_list = [i+6 for i in voc_id_list]          
        voc_data_orig = voc_data_orig.fillna(0)
        
        for i in voc_id_list:
            for j in range(4,len(voc_data_orig.columns)):    
                if (voc_data_orig.iloc[i, j] != 0):
                    voc_data_orig.iloc[i, j] = str(voc_data_orig.iloc[i, j]) +  '*'    
        
        #st.table(voc_data_orig.iloc[0:5, 0:5])
        
        # token slider
        slider2 = st.sidebar.slider(label="choose the token sort ratio for svoc",
                   min_value=50,
                   max_value=100,
                   value = 80,
                   step=5)
        
        #svoc
        svoc_id_list = []
        svoc_ref_list = []
        for i in range(0, len(svoc_df_list)):
            Str1 = svoc_df_list[i]
            for j in range(0, len(svoc_list)):
                Str2 = svoc_list[j]
                Token_Sort_Ratio = fuzz.token_sort_ratio(Str1,Str2)
                if Token_Sort_Ratio > slider2: # <--- this can be tweaked
                    svoc_id_list.append(i)
                    svoc_ref_list.append(j)
        
        table_svoc_df = []
        table_svoc_list = []
        for i,j in zip(svoc_id_list, svoc_ref_list):
            table_svoc_df.append(svoc_df_list[i])
            table_svoc_list.append(svoc_list[j])
        
        table_svoc_comparison = pd.DataFrame(list(zip(table_svoc_df, table_svoc_list)), columns = ["table value", "list value"])            
        table_svoc_comparison.index = svoc_id_list
        
        st.table(table_svoc_comparison)
        
        #svoc_id_list = st.sidebar.text_input("Select the index required from the svoc table", "")
        
        
        svoc_id_list = st.sidebar.multiselect("Select the index required from the svoc table", 
                         svoc_id_list)
        
        #svoc_id_list = svoc_id_list.split(",")
    
        svoc_id_list = [int(i) for i in svoc_id_list] 
        
        svoc_id_list = [i+6 for i in svoc_id_list]          
        svoc_data_orig = svoc_data_orig.fillna(0)
           
        for i in svoc_id_list:
            for j in range(4,len(svoc_data_orig.columns)):    
                if (svoc_data_orig.iloc[i, j] != 0):
                    svoc_data_orig.iloc[i, j] = str(svoc_data_orig.iloc[i, j]) +  '*'
        
        st.success("Criteria 1 has been successfully added to the tics table")
        
        st.sidebar.subheader("Criteria 2")
        
        st.markdown("### 🎲 Identify whether the TICs compounds are repeated in the VOC and SVOC table. If yes, insert ** along with the results throughout the row for the lowest value.")
                    
        # token slider
        slider3 = st.sidebar.slider(label="choose the token sort ratio for criteria 2",
                   min_value=80,
                   value = 95,
                   max_value=100,
                   step=2)
        
        # Criteria-2 **
        table_voc_value = []
        table_svoc_value = []
        voc_value = []
        svoc_value = []
        for i in range(0, len(voc_df_list)):
            Str1 = voc_df_list[i]
            for j in range(0, len(svoc_df_list)):
                Str2 = svoc_df_list[j]
                Token_Sort_Ratio = fuzz.token_sort_ratio(Str1,Str2)
                if Token_Sort_Ratio > slider3: #<---------------user tweaking
                    voc_value.append(i)
                    table_voc_value.append(voc_df_list[i])
                    svoc_value.append(j)
                    table_svoc_value.append(svoc_df_list[j])
        
        #table comparison
        table_comparison = pd.DataFrame(list(zip(table_voc_value, voc_value, table_svoc_value, svoc_value)), columns = ["voc value", "voc index", "svoc value", "svoc index"])            
        
        table_comparison['removal'] = table_comparison['voc value'].str.lower()
        table_comparison_cas = table_comparison[table_comparison['removal'].str.contains("unknown") == True]
        
        # cas comparison
        cas_voc_value = list(table_comparison_cas['voc index'])
        cas_svoc_value = list(table_comparison_cas['svoc index'])
        
        cas_voc_value = [i+6 for i in cas_voc_value] 
        cas_svoc_value = [i+6 for i in cas_svoc_value] 
        
        cas_no_voc = []
        for i in cas_voc_value:
            print(i)
            cas_no_voc.append(voc_data_orig.iloc[i, 1])
        
        cas_no_svoc = []
        for i in cas_svoc_value:
            print(i)
            cas_no_svoc.append(svoc_data_orig.iloc[i, 1])
        
        table_comparison_cas['cas voc'] = cas_no_voc
        table_comparison_cas['cas svoc'] = cas_no_svoc
        table_comparison_cas = table_comparison_cas[table_comparison_cas['cas voc']  == table_comparison_cas['cas svoc']]
        
        # tic table
        table_comparison =  table_comparison[table_comparison['removal'].str.contains("unknown") == False]
        table_comparison = table_comparison[(table_comparison['voc value'] != "Total Tic")]
        
        st.write(table_comparison)
        
        voc_value = list(table_comparison['voc index'])
        svoc_value = list(table_comparison['svoc index'])
        
        # appending cas values
        voc_value.extend(list(table_comparison_cas['voc index']))
        svoc_value.extend(list(table_comparison_cas['svoc index']))
        
        voc_value = [i+6 for i in voc_value] 
        svoc_value = [i+6 for i in svoc_value] 
        
        for id,jd in zip(voc_value,svoc_value):
            for i in range(4, len(voc_data_orig.columns)):
                
                if (voc_data_orig.iloc[id, i] != 0) and (svoc_data_orig.iloc[jd, i] != 0):
                
                    voc_data_orig.iloc[id, i] = str(voc_data_orig.iloc[id, i])
                    svoc_data_orig.iloc[jd, i] = str(svoc_data_orig.iloc[jd, i])              
                    
                    if(int(re.findall(r'\d+', voc_data_orig.iloc[id, i])[0]) < int(re.findall(r'\d+', svoc_data_orig.iloc[jd, i])[0])):
                        if "**" not in voc_data_orig.iloc[id, i]:
                            voc_data_orig.iloc[id, i] = str(voc_data_orig.iloc[id, i]) +  '**'
                    else:
                        if "**" not in svoc_data_orig.iloc[jd, i]:
                            svoc_data_orig.iloc[jd, i] = str(svoc_data_orig.iloc[jd, i]) +  '**'
        
        st.success("Criteria 2 has been successfully added to the tics table")
       
        
        st.sidebar.subheader("Criteria 3")
        
        st.markdown("### 🎲 Identify if any of the common lab contaminants (refer to pg. 45 NFG Organic Guidelines, October 1999) are present in the TICs compounds. If yes, insert *** along with the results throughout.")
                    
        # token slider
        slider4 = st.sidebar.slider(label="choose the token sort ratio for voc for criteria3",
                   min_value=50,
                   value = 80,
                   max_value=100,
                   step=5)
        
        contaminants_list = list(contamiants_df.iloc[:, 0])
    
        voc_3_list = []
        voc_ref_3_list = []
        table_voc_3_list = []
        table_voc_ref_3_list = []
        
        for i in range(0, len(voc_df_list)):
            Str1 = voc_df_list[i]
            for j in range(0, len(contaminants_list)):
                Str2 = contaminants_list[j]
                Token_Sort_Ratio = fuzz.token_sort_ratio(Str1,Str2)
                if Token_Sort_Ratio > slider4: # <--------------------------------------user input
                    voc_3_list.append(i)
                    table_voc_3_list.append(voc_df_list[i])
                    voc_ref_3_list.append(j)
                    table_voc_ref_3_list.append(contaminants_list[j])
        
        table_contaminant_voc_comparison = pd.DataFrame(list(zip(table_voc_3_list, table_voc_ref_3_list)), columns = ["voc value", "list contaminants"])            
        table_contaminant_voc_comparison.index = voc_3_list
        
        st.table(table_contaminant_voc_comparison)
        
        #voc_3_list = st.sidebar.text_input("Select the index required from the voc table for criteria 3", "")
        
        voc_3_list = st.sidebar.multiselect("Select the index required from the voc table for criteria 3", 
                         voc_3_list)
        
        #voc_3_list = voc_3_list.split(",")
    
        voc_3_list = [int(i) for i in voc_3_list] 
        
        voc_3_list = [i+6 for i in voc_3_list]
        
        for i in voc_3_list:
            for j in range(4,len(voc_data_orig.columns)):    
                if (voc_data_orig.iloc[i, j] != 0):
                    if "*" not in voc_data_orig.iloc[i, j]:
                        voc_data_orig.iloc[i, j] = str(voc_data_orig.iloc[i, j]) +  '***'
        
        # token slider
        slider5 = st.sidebar.slider(label="choose the token sort ratio for svoc for criteria3",
                   min_value=50,
                   value = 80,
                   max_value=100,
                   step=5)
        
        #svoc
        svoc_3_list = []
        svoc_ref_3_list = []
        table_svoc_3_list = []
        table_svoc_ref_3_list = []
        
        for i in range(0, len(svoc_df_list)):
            Str1 = svoc_df_list[i]
            for j in range(0, len(contaminants_list)):
                Str2 = contaminants_list[j]
                Token_Sort_Ratio = fuzz.token_sort_ratio(Str1,Str2)
                if Token_Sort_Ratio > slider5: #<--------- user input
                    svoc_3_list.append(i)
                    table_svoc_3_list.append(svoc_df_list[i])
                    svoc_ref_3_list.append(j)
                    table_svoc_ref_3_list.append(contaminants_list[j])
        table_contaminant_svoc_comparison = pd.DataFrame(list(zip(table_svoc_3_list, table_svoc_ref_3_list)), columns = ["svoc value", "list contaminants"])            
        table_contaminant_svoc_comparison.index = svoc_3_list
        
        st.table(table_contaminant_svoc_comparison)
        
        #svoc_3_list = st.sidebar.text_input("Select the index required from the svoc table for criteria 3", "")
        
        
        svoc_3_list = st.sidebar.multiselect("Select the index required from the svoc table for criteria 3", 
                         svoc_3_list)
        
        #svoc_3_list = svoc_3_list.split(",")
    
        svoc_3_list = [int(i) for i in svoc_3_list] 
        
        svoc_3_list = [i+6 for i in svoc_3_list]
         
        svoc_3_list = list(set(svoc_3_list)) # get unique
    
        for i in svoc_3_list:
            for j in range(4,len(svoc_data_orig.columns)):    
                if (svoc_data_orig.iloc[i, j] != 0):
                    if "*" not in svoc_data_orig.iloc[i, j]:
                        svoc_data_orig.iloc[i, j] = str(svoc_data_orig.iloc[i, j]) +  '***'
         
        st.success("Criteria 3 has been successfully added to the tics table")

        
        st.markdown("### 🎲 Do not include the (*,**,***) for summation of the total TICs.")
                    
        # final manipulation
        # creating copy for final appending
        actual_voc = voc_data_orig.copy() 
        actual_svoc = svoc_data_orig.copy() 
                       
        # removing total value rows
        voc_data_orig['removal'] = voc_data_orig.iloc[:, 0].str.lower()
        voc_data_orig = voc_data_orig[voc_data_orig['removal'].str.contains("total") == False]      
        voc_data_orig = voc_data_orig.drop(['removal'], axis=1)
    
        svoc_data_orig['removal'] = svoc_data_orig.iloc[:, 0].str.lower()
        svoc_data_orig = svoc_data_orig[svoc_data_orig['removal'].str.contains("total") == False]      
        svoc_data_orig = svoc_data_orig.drop(['removal'], axis=1)
    
        sum_list_voc = []
        for j in voc_data_orig.columns[4:]:
            values = []
            for i in voc_data_orig[j][5:]:
                if '*' not in str(i):
                    values.append(float(re.findall(r"[-+]?\d*\.\d+|\d+",str(i))[0]))
               
            sum_list_voc.append(sum(values))
    
        sum_list_svoc = []
        for j in svoc_data_orig.columns[4:]:
            values = []
            for i in svoc_data_orig[j][5:]:
                if '*' not in str(i):
                    values.append(float(re.findall(r"[-+]?\d*\.\d+|\d+",str(i))[0]))
               
            sum_list_svoc.append(sum(values))
    
        result_list = ["Result value", "-", "-", "-"] # for voc
        result_list.extend(sum_list_voc)
        actual_voc = actual_voc.append(pd.Series(result_list, index=actual_voc.columns), ignore_index=True)
    
    
        result_list = ["Result value", "-", "-", "-"] # for svoc
        result_list.extend(sum_list_svoc)
        actual_svoc = actual_svoc.append(pd.Series(result_list, index=actual_svoc.columns), ignore_index=True)
    
    
        cols = actual_voc.columns
        actual_voc[cols] = actual_voc[cols].replace({'0':np.nan, 0:np.nan})
    
        cols = actual_svoc.columns
        actual_svoc[cols] = actual_svoc[cols].replace({'0':np.nan, 0:np.nan})
        
        
        st.balloons()
        
        st.write(actual_voc)
                
        st.markdown(get_table_download_link(actual_voc), unsafe_allow_html=True)
        
        st.write(actual_svoc)
                
        st.markdown(get_table_download_link(actual_voc), unsafe_allow_html=True)
        
        st.success("process successful")
        #st.table(actual_svoc.iloc[0:5, 0:5])
        #st.markdown(get_table_download_link(actual_svoc), unsafe_allow_html=True)
              
#if __name__ == "__main__":
#    main()

session_state = get(password='')

if session_state.password != 'Aspirine':
    pwd_placeholder = st.empty()
    pwd = pwd_placeholder.text_input("Login to your Tics Calculator:", value="", type="password")
    session_state.password = pwd
    if session_state.password == '':
        st.info("please enter the valid password for user authentication")
    else:    
        if session_state.password == 'pwd123':
            pwd_placeholder.empty()
            main()
        else:
            st.error("the password you entered is incorrect")
else:
    main()
#
