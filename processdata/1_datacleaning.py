
import pandas as pd
import ast
import json
import numpy as np
import sys
import math
from tqdm import tqdm
from datetime import datetime
import seaborn as sns
# In this script we will transform all the Data that we colected
# in 0_joinfiles.py from previous kickstarter campaigns from 2016 to 2020.
# We will analize the data and see what are the things we need to change before
#"working" with the date an create models:


def read_args():
    args = sys.argv
    first_arg = args[1]
    second_arg = args[2]
    return first_arg, second_arg
# First we import the dataset and use pandas library to handle all the data.


def load_data(path):
    """
    Loads all the appended Data in 0_joinfiles.py
    """
    print("********** STAGE ONE: load_data - START ")

    # this function takes some time to execute
    df = pd.read_csv(path)
    print("********** STAGE ONE: load_data - COMPLETED ")
    return df


path_all_data = "/home/alejandrocoronado/Dropbox/Github/Viridiantree/kickstarterdata/Output/all_data.csv"
path_sample_date = "/home/alejandrocoronado/Dropbox/Github/Viridiantree/kickstarterdata/Output/all_data_sample.csv"

df = load_data(path_sample_date)

# At this moment all_data only contains infromation for 2019, however we expact that data in the future
# will have the same format. Using a smaller DataSet allow us to fail faster. At first it doesn't seem
# really important but it's fundamental to save time and save days of processing.


def convert_observation_fromjson(df, column):
    """
    This fucntion allow us to iteare over a DataFrame, using column as
    reference.  To each osbservation we will transalte the json format to python format
    and finally we will transform that jeson into a dataframe row to attach it to
    the DataFrame
    """
    print("\n\nSTAGE TWO: convert_observation_fromjson - START ")
    ignore_count = 0
    for i in tqdm(range(len(df))):
        json_obs = df.loc[i, column]
        if isinstance(json_obs, float):
            ignore_count += 1
            print("\tignore_count: {}".format(ignore_count))
            continue  # Ignore it
        else:
            dict_obs = json.loads(json_obs)
            for key in dict_obs.keys():
                if key != "urls":
                    if key not in df.columns:
                        # Create a column empty
                        df[key] = np.nan
                    # We iterate over the dictionary and insert the value
                    df.loc[i, key] = dict_obs[key]

    # This fucntion doesn't seem too efficient (it could be better with lambdas or matrix operations)
    # but for now it allows me continue.
    print("********** STAGE ONE: convert_observation_fromjson - COMPLETED ")

    return df


df_json = convert_observation_fromjson(df, "location")


def get_categoricalvariables(df):
    """
    # Let's start with one of the most important startegies for identify problems with
    # our data. Let's check the type and unique values of a each variable.
    # This will tell us two things identify "categorical variables", identify errors
    # like two different types of data in  single variable.
   """
    print("\n\nSTAGE THREE: get_categoricalvariables - START ")

    lowerbound_categoricalvariables = 50
    categoricalvariables = dict()
    categoricalvariables[50] = list()
    categoricalvariables[100] = list()
    categoricalvariables[25] = list()
    categoricalvariables[10] = list()
    # We didn't need to use categoricalvariables with lower or upper bound because
    # the analysis show that most categorical groups have less than 20 elements. And we can
    # live with that. Rember is not about making the best but to make it fast

    for col in df.columns:
        # Visual is good for first test. Don't forget to print.
        uniqueelements = df[col].unique()
        lengthunqiue = len(uniqueelements)

        if lengthunqiue < lowerbound_categoricalvariables:  # Lets start with 50
            print("\n\nColumn: {}".format(col))
            print("\n\tCategorical Variable: {} ".format(col))
            for i, val in enumerate(uniqueelements):
                print("\n\t\t {} -  {}".format(i, val))
            categoricalvariables[lowerbound_categoricalvariables].append(col)
    print("********** STAGE THREE: get_categoricalvariables - COMPLETED ")

    return categoricalvariables


categoricalvariables = get_categoricalvariables(df)
# OBSERVATIONS:
# LOOK like categorical but it isn't: fx_rate
# state - unique(): failed, successful, live, canceled, suspended
# usd_type <-????
# We can delete = freinds
# COLUMNS: 'country', 'currency', 'currency_symbol', 'currency_trailing_code','current_currency',
#'disable_communication','is_starrable','spotlight','staff_pick',
#'state','usd_type','friends','is_backing','is_starred','permissions']


def filter_categorical(df, categoricalvariables):
    print("\n\nSTAGE FOUR: filter_categorical - START ")

    categoricalvariables = categoricalvariables[50]
    # We delete the variable that is an intruder.
    filter_columns = ["fx_rate"]
    categoricalvariables = [
        x for x in categoricalvariables if x not in filter_columns]
    # The reason is that we dont have enough data to make it move enough through the year.
    print("********** STAGE FOUR: filter_categorical - COMPLETED ")
    selected_columns = [x for x in df.columns if x not in filter_columns]
    df = df[selected_columns]
    return df, categoricalvariables


df, categoricalcolumns = filter_categorical(df, categoricalvariables)

# CHAPTER 2: -- How to choose the variables that work for the prjects.


print("\n\n\nWe ara analizing: {} variable with {} categoricalvariables and {} numerical variables".format(
    len(df.columns), len(categoricalcolumns), len(df.columns) - len(categoricalcolumns)))
print("*** Starting NA analysis  ***")


def get_navariables(df, upperbound_na=.01):
    """
    Returns a list of the variables that have more than x% na variables
    """
    print("\n\nSTAGE FIVE: get_navariables - START ")

    navariables = dict()
    navariables[.1] = list()
    navariables[.01] = list()
    # We can to select the variables that have enough information to be used in the analysis. The question here
    # is how many observations do I need to make the analysis. I would say than 70% of the observations but lets
    # try with 90% just to be sure and see wich variables we cut with this bound.

    upperbound_na = .1
    upperbound_na = .01  # 90%

    for col in df.columns:
        # Visual is good for first test. Don't forget to print.
        uniqueelements = df[col].unique()
        print("\n\nColumn: {}".format(col))
        naobservations = df[col].isna().sum()
        pct_na = naobservations / len(df)

        if pct_na > upperbound_na:  # If more that 90% of observations are na then we delete
            print("\n\tNA Variable: {} ".format(col))
            for i, val in enumerate(uniqueelements):
                print("\n\t\t {} -  {}".format(i, val))
            navariables[upperbound_na].append(col)
    print("********** STAGE FIVE: get_navariables - COMPLETED ")

    return navariables


def filter_navariables(df, navariables):
    print("\n\nSTAGE FIVE: filter_navariables - START ")

    navariables = navariables[.01]
    selected_columns = [x for x in df.columns if x not in navariables]
    df = df[selected_columns]
    print("\n\nSTAGE FIVE: filter_navariables - COMPLETED ")

    return df, navariables


navariables = get_navariables(df)
df, filter_navariables = filter_navariables(df, navariables)

#{0.9: ['friends', 'is_backing', 'is_starred', 'permissions'],
# 0.5: ['friends', 'is_backing', 'is_starred', 'permissions']}
# Our analysis show that we have really high quality information. Most of data is complete
# Let's get more strict about the na and see hoy much can we increase the upperbound_na

# if I delete all the variables that has more than 50 % of na oservations I will delete ONLY three variables.
# if I delete all the variables that has more than 10 % of na oservations I will delete ONLY three variables.
#    How many can we delete??
# if I delete all the variables that has more than 1 % of na oservations I will delete ONLY three variables.

# WE KEEP ALL INFORMATION! That's great


# CHAPTER 3:
# Cleaning Data (SPECIAL CASE) what to do if we find a json format variables.
# A problem ad hoc of kickstarter webdatabase.

# Numerical distribution

def get_datevariables(df):
    """ Return all variables that should be transformed to dates.
    """

    print("\n\nSTAGE SIX: get_datevariables - START ")
    print("\n\nSTAGE SIX: get_datevariables - COMPLETED ")
    datevariables = ["created_at", "deadline",
                     "launched_at", "state_changed_at"]
    return datevariables


datevariables = get_datevariables(df)


def get_numericalobjectvariables(df, categoricalcolumns, datevariables):
    """
    Divides all the noncategoricalvariables (have many different elements
    to be considered categorical) in two new groups:

    numericalvariables: If variable can be converted to numeric i.e all
    variables are numeric
    objectvariables: There strings or combination of numeric + string
    """
    print("\n\nSTAGE SEVEN: get_numericalobjectvariables - START ")
    kpis = dict()
    noncategoricalvariables = [
        x for x in df.columns if x not in categoricalcolumns]
    noncategoricalnondatevariables = [
        x for x in noncategoricalvariables if x not in datevariables]
    numerical_statistics = dict()
    numericalvariables = list()
    objectvariables = list()
    for col in noncategoricalnondatevariables:
        try:
            df[col] = pd.to_numeric(df[col])
            numericalvariables.append(col)
        except Exception as e:
            objectvariables.append(col)
    print("********** STAGE SEVEN: get_numericalobjectvariables - COMPLETED ")
    return numericalvariables, objectvariables


numericalvariables, objectvariables = get_numericalobjectvariables(
    df, categoricalcolumns, datevariables)


# CHAPTER 4: Disribution of Variables
# WE already talk about navalues, categorical columns. So far everything is all right.
# We can skip directly to the next sesion wich will be analyzing the distributions of
# numerical columns
# The distribution of numerical values gruped in categories.

# This scenario will be much easier to do if we just read the columns and just figure our the meaning
# but for the sake of the argument I will pretend that this columns are in latin and I don't
# understand them. This is a nice test tu run because if you identify pattern and connect it with the name
# of a variable you will be leanring directly of the data instead of making asumptions. Also
# is mor fun

# RETAKING ....

def get_numericalvariable_statistics(df, numericalvariables, n):
    """
    We want to filter our data using the variance of the numerical variables.
    There are many ways to this. This process is called atypical values identification
    The idea is that there are many point in your data that have atypical values, sometimes
    it is caused by typos or events that were really weird and alter the data.

    There is a lot of people that say tha is important to keep or label this observations
    but this only makes sense in a competition, we are only trying to get a good estimation
    of the kickstarter pledged amounts

    n is a metrics that tell us how much coverage do we want to include in our function.
    If n is too large we will be accepting more osbservations in our dataset since it will
    be more difficult  to be classified as atypical valur.

    A good expermient is to test how low you can make n without affecting the integrity of the information (completeness)
    """
    print("\n\nSTAGE EIGHT: get_numericalvariable_statistics - START \n---------------------------- numerical_statistics -------------------------")
    kpis = dict()
    numerical_statistics = dict()
    for col in numericalvariables:
        uniqueelements = df[col].unique()
        numerical_statistics[col] = dict()
        description = df[col].describe()
        for element in description.keys():
            numerical_statistics[col][element] = description[element]
        mean = numerical_statistics[col]["mean"]
        std = numerical_statistics[col]["std"]
        numerical_statistics[col]["unique"] = len(df[col].unique())
        numerical_statistics[col]["unique_pct"] = len(
            df[col].unique()) / len(df)
        numerical_statistics[col]["upper_bound"] = mean + (n * std)
        numerical_statistics[col]["lower_bound"] = mean - (n * std)
        upper_bound = numerical_statistics[col]["upper_bound"]
        lower_bound = numerical_statistics[col]["lower_bound"]
        numerical_statistics[col]["typical_obs"] = len(df[(df[col]
                                                           > lower_bound) & (df[col] < upper_bound)])
        numerical_statistics[col]["atypical_obs"] = len(
            df) - numerical_statistics[col]["typical_obs"]
        numerical_statistics[col]["atypical_pct"] = numerical_statistics[col]["atypical_obs"] / \
            len(df)

        print("\ncol: {} \n\tatypical_pct: {} \n\t unique_pct: {}".format(
            col, numerical_statistics[col]["atypical_pct"], numerical_statistics[col]["unique_pct"]))
    print("********** STAGE EIGHT: get_numericalvariable_statistics - COMPLETED ")

    return numerical_statistics


numerical_statistics = get_numericalvariable_statistics(
    df, numericalvariables, 1.5)
# TO DO: check this values with ALL DATA


# After executing get_numericalobjectvariables with different values of n cut == 1. I can choose the once
# that I think is a good mesurement to exclude values. I decided it to be 1.5
# first beacuse is a good rule of thomb and becuase if I reduce it to 1 std I eliminated 5% of
# my data points (taking usd_pledged as reference).
# By levaing it at 1.5 I only delete 3% and if I increase n to 2 I'll eliminate 2% of the Data.


# Start length: 1000
# End length: 710
# WE delete 30% of the observations!!! but how??
# Simple remeber that some of the variables where date variables? we dont have to include those variables
# in the filter_categorical


def filter_numericalvalues(df, numerical_statistics, numerical_control):
    """
    Delete all observations that fall outside a certian range defined by mean +- (N*std)
    numerical_control: List of variables that will be used to filter data using atypical values.

    """
    print("\n\nSTAGE TEN: filter_numericalvalues - START ")
    print("\tStart length: " + str(len(df)))
    for col in numerical_statistics.keys():
        if col in numerical_control:
            df = df[(df[col] > numerical_statistics[col]["lower_bound"]) &
                    (df[col] < numerical_statistics[col]["upper_bound"])]
    print("\tEnd length: " + str(len(df)))

    print("********** STAGE TEN: filter_numericalvalues - COMPLETED ")
    return df


numerical_control = ["usd_pledged", "backers_count"]
df = filter_numericalvalues(df, numerical_statistics, numerical_control)


def transform_datevariables(df, datevariables):
    """ Trandsform all dates to the correct format pd.DateTime()
    The Dates of the database are reported in UNIX format.
    We need to applu the fromtimestamp function to each observation.

    """
    print("\n\nSTAGE ELEVEN: transform_datevariables - START ")
    for col in datevariables:
        df[col] = df[col].apply(lambda x: datetime.fromtimestamp(
            x).strftime('%Y-%m-%d %H:%M:%S'))
        df[col] = pd.to_datetime(df[col])
    print(df[datevariables].head())
    print("\n\nSTAGE ELEVEN: transform_datevariables - START ")

    return df


# CHAPTER 5: Plots and distribution of data
date_column = "created_at"
df = transform_datevariables(df, datevariables)
sns.lineplt(df[date_column], df["usd_pledged"])
