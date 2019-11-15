# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------
"""
    General_tools module
    ====================

    Developped by: L. Ravera

    Project: Athena X-IFU / DRE-DEMUX

    General purpose tools needed for the DRE data processing

    """

# -----------------------------------------------------------------------
# Imports
import os, csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------------------------------------------------
def checkdir(dirname):
    r"""
        This function checks if a directory exists. If not it creates it.

        Parameters:
        -----------
        dirname: String
        Name of the directory to be verified / created.

        Returns
        -------
        Nothing

        """
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    return()

# -----------------------------------------------------------------------
def get_csv(filename):
    r"""
        This function reads a dictionnary from a csv file.

        Parameters:
        -----------
        filename: string
        The name of the csv file

        Returns
        -------
        dictionnary: dictionnary

        """

    dictionnary={}

    if not os.path.exists(os.path.join(filename)):
        print("File "+filename+" not found.")
    else:
        with open(filename, newline='') as csvfile:
            dict_reader = csv.reader(csvfile, delimiter='=', quotechar='|')
            for row in dict_reader:
                try:    # for numbers
                    dictionnary[row[0]]=float(row[1].replace(',','.'))
                except: # for strings
                    dictionnary[row[0]]=row[1]
    return(dictionnary)

# -----------------------------------------------------------------------
def print_dict(the_dict, the_dictname):
    r"""
        This function prints a set of parameter values from a dictionnary .

        Parameters:
        ----------
        dict: dictionnary
        Contains the parameters

        dictname: string
        Name of the dictionnary (used to prompt the user)

        Returns
        -------
        Nothing

        """

    print('The ', the_dictname, ' parameters are the following:')
    for key in the_dict.keys():
        print('  ', key, ': ', the_dict[key])    
    return()

# -----------------------------------------------------------------------
def non_empty_lines(table):
    r"""
        This function looks for empty lines in an 2 dimensionnal array.
    """
    n_lines = len(table[0,:])
    non_empty_lines = np.ones((n_lines), dtype=bool)
    for line in range(n_lines):
        if np.abs(table[:,line]).max()==0:
            non_empty_lines[line]=False
    return(non_empty_lines)

# ---------------------------------------------------------------------------

