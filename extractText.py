# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 23:35:10 2022

@author: mabin
"""
import json
import glob
import re

# Dictionary initialization
carrier_information = {"shipper_info": list(), "receipt_info": list(), "Carrier": None, "MC#": None, "attention": None, "carrier_phone": None}
# Load Json Files
def load_text_file(f):    
    with open(f, 'r') as file:
        json_map = json.load(file)
        return json_map

# Function to clean data
def data_clean(text):
    try:
        strip_po = [i.strip() for i in text.split('\n')]
        remove_space = [i for i in strip_po if i not in [' ', '']]
        remove_space_between = [i.split('  ') for i in remove_space]
        cleaned_data = list()
        count = 0
        for i in remove_space_between:
            cleaned_data.append([])
            for j in i:
                if j not in ['']:
                    cleaned_data[count].append(j.strip())
            count += 1
        
        return cleaned_data

    except Exception as e:
        print("kvt data clean exception")
        print(e)
        return None


# Get text between lines
def get_lines_between(origtmp, str1, str2):
    start_index = 0
    stop_index = 0
    for ele_nos, ele in enumerate(origtmp):
        for stchar in ele:
            if str1 in stchar.lower():
                start_index = ele_nos

            if str2 in stchar.lower():
                stop_index = ele_nos
                return origtmp[start_index:stop_index+1]
    return([])
# function for extraction
def get_receipt_information(receiver_info):
    deliv_date = r"^Delivery Date: ((?:[A-Z][a-z]+[ ]?)+\d{2},[ ]?\d{4})"
    deliv_date_compile_re = re.compile(deliv_date)
    
    regex_addr_line1 = r'\d+ \w+.*'
    raddr_line1_compile_re = re.compile(regex_addr_line1)
    
    regex_raddr_line2 = r"(?:[A-Z]+[ ]?)+,[ ][A-Z][A-Z][ ]\d{5}"
    raddr_line2_compile_re = re.compile(regex_raddr_line2)
    stop_idx = 0
    y = get_lines_between(receiver_info, "consignee:","delivery date:")
    addr_lookup_state = 'NoLook'
    for line in y:
        for x in line:
            if x.find('Consignee:') >= 0:
                carrier_information["receipt_info"].append({"Consignee": line[1], "Cons_ref": line[3],})
                stop_idx = stop_idx + 1
                addr_lookup_state = 'look1'
            elif addr_lookup_state == 'look1':
                addr_line_1 = raddr_line1_compile_re.findall(x)
                if len(addr_line_1) > 0:
                    #print(addr_line_1)
                    carrier_information["receipt_info"][stop_idx-1]["addr_line_1"] = addr_line_1[0]
                    addr_lookup_state = 'look2'
            elif addr_lookup_state == 'look2':
                addr_line_2 = raddr_line2_compile_re.findall(x)
                if len(addr_line_2) > 0:
                    carrier_information["receipt_info"][stop_idx-1]["addr_line_2"] = addr_line_2[0]
                    addr_lookup_state = 'Deliv_date_look'
            elif addr_lookup_state == 'Deliv_date_look':
                deliv_date_info = deliv_date_compile_re.findall(x)
                if len(deliv_date_info) > 0:
                    carrier_information["receipt_info"][stop_idx-1]["Delivery_date"] = deliv_date_info[0]
                    addr_lookup_state = 'NoLook'
def get_shipper_information(shiper_info):
    
    pick_date = r"^Pickup Date: ((?:[A-Z][a-z]+[ ]?)+\d{2},[ ]?\d{4})"
    pick_date_compile_re = re.compile(pick_date)
    
    regex_saddr_line1 = r'\d+ \w+.*'
    saddr_line1_compile_re = re.compile(regex_saddr_line1)
    
    regex_saddr_line2 = r"(?:[A-Z]+[ ]?)+,[ ][A-Z][A-Z][ ]\d{5}"
    saddr_line2_compile_re = re.compile(regex_saddr_line2)
    stop_idx = 0
    y = get_lines_between(shiper_info, "shipper:","consignee:")
    addr_lookup_state = 'NoLook'
    for line in y:
        for x in line:
            if x.find('Shipper:') >= 0:
                carrier_information["shipper_info"].append({"Shipper": line[1], "Shipping_ref": line[3],})
                stop_idx = stop_idx + 1
                addr_lookup_state = 'look_for_addr_line_1'
            elif addr_lookup_state == 'look_for_addr_line_1':
                addr_line_1 = saddr_line1_compile_re.findall(x)
                if len(addr_line_1) > 0:
                    carrier_information["shipper_info"][stop_idx-1]["addr_line_1"] = addr_line_1[0]
                    addr_lookup_state = 'look_for_addr_line_2'
            elif addr_lookup_state == 'look_for_addr_line_2':
                addr_line_2 = saddr_line2_compile_re.findall(x)
                if len(addr_line_2) > 0:
                    carrier_information["shipper_info"][stop_idx-1]["addr_line_2"] = addr_line_2[0]
                    addr_lookup_state = 'Pickup_date_look'
            elif addr_lookup_state == 'Pickup_date_look':
                pick_date_info = pick_date_compile_re.findall(x)
                if len(pick_date_info) > 0:
                    carrier_information["shipper_info"][stop_idx-1]["Ship_date"] = pick_date_info[0]

def get_carrier_name(carrier_info):
    carr_info = get_lines_between(carrier_info, "carrier:","carrier:")
    #print(carr_info)
    if len(carr_info) == 0:
        return 'Carrier name not found'
    if len(carr_info[0]) > 2:
        carrier_info = carr_info[0][1]
        carrier_information["Carrier"] = carrier_info
    else:
        return carr_info[0][-1]

def get_mc_number(mc_info):
    m_info = get_lines_between(mc_info, "mc#","mc#")
    # print(m_info)
    if len(m_info) == 0:
        return 'MC not found'
    if len(m_info[0]) > 2:
        mc = m_info[0][1]
        carrier_information["MC#"] = mc
    else:
        return m_info[0][-1]
    
def get_attention(attention_info):    
    att_info = get_lines_between(attention_info, "attention:","attention:")
    # print(att_info)
    if len(att_info) == 0:
        return 'Attention not found'
    if len(att_info[0]) > 1:
        att_person = att_info[0][1] 
        carrier_information["attention"] = att_person
    else:
        return att_info[0][-1]


def get_equipment(equipment_info):
    equ_info = get_lines_between(equipment_info, "equipment:","equipment:")
    #print(equ_info)
    if len(equ_info) == 0:
        return 'Equipment not found'
    if len(equ_info[0]) > 2:
        eq = equ_info[0][1]
        carrier_information["equip"] = eq
    else:
        return equ_info[0][-1]
    pass

def get_carrier_phone(carr_phone_info):
    phone_info = get_lines_between(carr_phone_info, "phone:","phone:")
    # print(phone_info)
    if len(phone_info) == 0:
        return 'Phone not found'
    if len(phone_info[0]) > 1:
        phone = phone_info[0][1]
        carrier_information["carrier_phone"] = phone
    else:
        return phone_info[0][-1]


def get_pro_number():
    pass

# Extract  Information
def kvt_extract(text_data):
    
    cleaned_data = data_clean(text_data)

    get_carrier_phone(cleaned_data)
    get_carrier_name(cleaned_data)
    get_shipper_information(cleaned_data)
    get_mc_number(cleaned_data)
    
    get_attention(cleaned_data)
    
    get_equipment(cleaned_data)
    
    get_carrier_phone(cleaned_data)
    
    get_receipt_information(cleaned_data)
    
    
    return carrier_information

extracted_info = []

# Main
for file_path in glob.glob('C:/Users/mabin/Desktop/gc apply/Generation-Student/Documents/TEXT Files/fitzmark_2.json'):
    #print(file_path)
    text_map = load_text_file(file_path)
    text = "\n\n\n".join(text_map['text'].values())
    
    
    # print(text)
    details = kvt_extract(text)
    extracted_info.append(details)
for items in extracted_info:
    print(items)
