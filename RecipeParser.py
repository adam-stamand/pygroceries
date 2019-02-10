import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from fractions import Fraction
import CategoriesDictionary as categories


ingredient_file = "C:\\Users\\adams\\Downloads\\Week 3.pdf"

unit_dict = \
{ \
"tsp":1, \
"tbsp":3, \
"cup":48, \
"oz":6, \
"lb":96, \
"whole":0, \
"can":0, \
"glass":0, \
"clove":0, \
"box":0, \
"package":0, \
"jar":0, \
"head":0, \
"stick":0, \
"crown":0, \
"slice":0, \
"bag":0, \
"loaf":0, \
"container":0, \
"carton":0 \
}




ingredients_output_file = open("ingredients_output.txt", "w+")




def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def find_letter(s):
    for index, letter in enumerate(s):
        if ((ord(letter) > 64) and (ord(letter) < 91)) or \
            ((ord(letter)) > 96 and (ord(letter) < 123)):
            return index
    return -1





def SearchIngredient(names, ingr_name):
    for name in names:
        rv = re.search(re.escape(name) + r's?', ingr_name, re.IGNORECASE)
        if rv:
            return True
    return False

def ParseInput():
    file_input = convert_pdf_to_txt(ingredient_file).split("\n")
    output_list = []
    for line in file_input:
        try:
            temp_list = line.split("PYTHON_INGREDIENT ",1)
            output_list.append(temp_list[1])
        except:
            continue
    return output_list

# Iterate through each line in input file
ingredient_lines = ParseInput()
for ingredient in ingredient_lines:

    # Split line into list; Make sure it's > minimum length
    ingredient_list = ingredient.split()
    if len(ingredient_list) < 3:
        print("--Inavlid Entry-- Expects at least three arguments per line. Entry: "  + ingredient[:-1])
        continue

    # Declare each of the components
    ingredient_quantity = None
    ingredient_unit = None
    ingredient_name = " ".join(ingredient_list[2:]).lower().strip()


    ## Extract each component
    # Extract Quantity
    try:
        temp_str = re.search(r'\d+(\.|\/)?\d*', ingredient_list[0]).group()
        ingredient_quantity = float(Fraction(temp_str))
    except:
        print("--Inavlid Entry-- Unexpected quantity format. Entry: "  + ingredient[:-1])
        continue

    # Exract Unit
    success = False
    ingredient_unit = ingredient_list[1].lower().replace(" ", "")
    for unit in unit_dict:
        rv = re.search(re.escape(unit) + r's?', ingredient_unit, re.IGNORECASE)
        if rv:
            ingredient_unit = unit
            success = True
            break
    if not success:
        print("--Invalid Entry-- Unknown unit. Entry: " + ingredient[:-1])
        continue

    # Convert Quantity if necessary
    if unit_dict[ingredient_unit] != 0:
        ingredient_quantity = round(ingredient_quantity * unit_dict[ingredient_unit], 1)
        ingredient_unit = "base"

    # Organize by Category
    ingredient_dict = dict()
    for category, content in categories.category_dict.items():
        names = content[0]
        ingredient_dict = content[1]
        success = SearchIngredient(names, ingredient_name)
        if success:
            break

    # Add ingredient to ingredient dictionary
    try:
        if ingredient_unit == "base":
            ingredient_dict[ingredient_name][0] = ingredient_dict[ingredient_name][0] + ingredient_quantity
        else:
            ingredient_dict[ingredient_name][2] = ingredient_dict[ingredient_name][2] + (" + " + str(ingredient_quantity) + " " + ingredient_unit)
    except:
        ingredient_dict[ingredient_name] = [ingredient_quantity, ingredient_unit, ingredient_name]

# Output Data to File
for category, content in categories.category_dict.items():
    ingredients_output_file.write("\n" + category +"\n")
    temp_list = content[1]

    for foo, item in temp_list.items():
        # Adjust base units
        if item[1] == "base":
            old_val = item[0]
            new_unit = ""
            for unit, conv in unit_dict.items():
                if conv == 0:
                    continue
                temp_val = item[0] / conv
                if temp_val <= old_val and temp_val >= 1:
                    old_val = temp_val
                    new_unit = unit

            item[0] = round(old_val, 1)
            item[1] = new_unit

        ingredients_output_file.write(str(item[0]) + " " + item[1] + " " + item[2] + "\n")

if len(categories.category_dict["Unknown"][1]) == 0:
    exit()

usr_input = input("Would you like to continue and identify Unknown entries? Y/N ")

if usr_input == "Y":
    new_dict = dict()
    # Build new dict
    for name, content in categories.category_dict.items():
        new_dict[name] = list(content[0])

    for foo, item_list in categories.category_dict["Unknown"][1].items():
        usr_input = None
        while not usr_input in categories.category_dict:
            for name, foo in new_dict.items():
                print (name)
            usr_input = input("What category is the following item? " + item_list[2] + "\n")
            if usr_input == "Unknown":
                break
        if usr_input != "Unknown":
            new_dict[usr_input].append(item_list[2])

    python_file = open("CategoriesDictionary.py", "r")
    data = python_file.readlines()
    for category, item_list in new_dict.items():
        for index, line in enumerate(data):
            if index > 50:
                break
            rv = re.search(r'.*' + re.escape(category) + '.*', line)
            if rv:
                data[index] = '"' + category + '":(' + str(tuple(item_list)) + ',{}), \\\n'
    python_file = open("CategoriesDictionary.py", "w+")
    python_file.writelines(data)

    # Check Name
    # if len(ingredient_name) < 1:
    #     print("--Invalid Entry-- Missing ingredient name. Entry: " + ingredient[:-1])
    #     continue

    # Check Unit
    # if ingredient_unit in unit_no_convert_list:
    #     ingredient_quantity = round(abs(float(ingredient_quantity)), 2)
    # elif ingredient_unit in unit_convert_dict:
    #     # Convert Quantity to base units
    #     ingredient_quantity = round(abs(float(ingredient_quantity)) / unit_convert_dict[ingredient_unit], 1)
    #     ingredient_unit = "base"
    # else:
    #     print("--Invalid Entry-- Invalid unit used. Entry: " + ingredient[:-1])
    #     continue

# Check Quantity
# ingredient_quantity = re.findall(r'-?\d+\.?\d*', ingredient_quantity)
# if len(ingredient_quantity) != 1:
#     print("--Invalid Entry-- One quantity required. Entry: " + ingredient[:-1])
#     continue
# ingredient_quantity = ingredient_quantity[0]


#for name, values in ingredient_dict.items():
#    ingredients_output_file.write(str(values[0]) + " " + values[1] + " " + name + "\n")

    ## Test if ingredient_unit is a unit; maybe using a dictionary

    #print("Ingredient Quantity: " + ingredient_quantity)
    #print("Ingredient Unit: " + ingredient_unit)
    #print("Ingredient Name: " + " ".join(ingredient_name))
    #temp_ingredient = re.search(ingredient)
    #
    #
        #if not is_number(ingredient_quantity[0]):
        #    print("--Invalid Entry-- Quantity must be valid number. Entry: " + ingredient[:-1])
        #    continue

    #    ingredient_quantity = ingredient_quantity.split("-", 1)
        #temp_list = ingredient.split("-", 1)
        #if len(temp_list) != 2:
        #    print("--Invalid Entry-- Must start with '-'. Entry: " + ingredient[:-1])
        #    continue
        #
        # temp_list = temp_list.split()
        # print(temp_list)
        # if len(temp_list) < 2:
        #     print("--Invalid Entry-- Too few arguments. Entry: " + ingredient[:-1])
        #     continue
        # ingredient_unit = temp_list[0]
        # ingredient_name = ' '.join(temp_list[1:])
