import pandas as pd
import numpy as np
import os


standarcolumnnames = {
    "columnname": "standarname",
    'backers_count': "backers_count",
    'blurb': "blurb",
    'category': "category",
    'converted_pledged_amount': "converted_pledged_amount",
    'country': "country",
    'created_at': "created_at",
    'creator': "creator",
    'currency': "currency",
    'currency_symbol': "currency_symbol",
    'currency_trailing_code': "currency_trailing_code",
    'current_currency': "current_currency",
    'deadline': "deadline",
    'disable_communication': "disable_communication",
    'friends': "friends",
    'fx_rate': "fx_rate",
    'goal': "goal",
    'id': "id",
    'is_backing': "is_backing",
    'is_starrable': "is_starred",
    'is_starred': "is_starred",
    'launched_at': "launched_at",
    'location': "location",
    'name': "name",
    'permissions': "permissions",
    'photo': "photo",
    'pledged': "pledged",
    'profile': "profile",
    'slug': "slug",
    'source_url': "source_url",
    'spotlight': "spotlight",
    'staff_pick': "staff_pick",
    'state': "state",
    'state_changed_at': "state_changed_at",
    'static_usd_rate': "static_usd_rate",
    'urls': "urls",
    'usd_pledged': "usd_pledged",
    'usd_type': "usd_type",
    'country_displayable_name': 'country_displayable_name',  # Not in all files
    "unread_messages_count": "unread_messages_count",  # Not in all files
    'unseen_activity_count': 'unseen_activity_count'
}


def test_columns(columns, standarcolumnnames):
    for col in columns:
        if col not in standarcolumnnames.keys():
            raise ValueError(
                "ERROR at test_columns: Some of the columns name in file don't match ")


directory = '/home/alejandrocoronado/Dropbox/Github/Viridiantree/kickstarterdata/Input'
df_alldata = pd.DataFrame()

for yearfolder in ["2018"]:  # os.listdir(directory):
    print(yearfolder)
    directory_year = directory + "/" + yearfolder
    directory_year_output = directory_year.replace(
        "Input", "Output") + "/" + yearfolder + ".csv"
    for datafolder in os.listdir(directory_year):
        df_datafolder = pd.DataFrame()
        directory_year_datafolder = directory_year + "/" + datafolder

        try:  # Maybe we have it already
            df_datafolder = pd.read_csv(directory_year_output)
        except Exception as e:
            print("Exception")
            for dfname in os.listdir(directory_year_datafolder):
                directory_year_datafolder_dfname = directory_year_datafolder + "/" + dfname
                df = pd.read_csv(directory_year_datafolder_dfname)
                columns = df.columns
                print("\n\nyearfolder: {} \n\tdatafolder: {}\n\t\tdf_path {} \n\t\t\tdf columns:{}".format(
                    yearfolder, datafolder, dfname, len(columns)))
                test_columns(columns, standarcolumnnames)
                if len(df_datafolder) == 0:
                    df_datafolder = df
                else:
                    df_datafolder = df_datafolder.append(df)

    if len(df_alldata) == 0:
        df_datafolder.to_csv(directory_year_output)
        df_alldata = df_datafolder
    else:
        df_alldata = df_alldata.append(df_datafolder)

#We create a condensed database with all the information that we Downloaded.
df_alldata.to_csv(
    '/home/alejandrocoronado/Dropbox/Github/Viridiantree/kickstarterdata/Output/all_data.csv')
