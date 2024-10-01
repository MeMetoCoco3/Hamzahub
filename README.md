# HamzaHub
## A complete and automatized management system for dangerous goods on a indexed warehouse written in Python and SQL.

### What is it?
HamzaHub is a working management system inspired by years of having to deal with dangerous goods in the logistics field. My main objective was make it fully functional, easy to use and easily customizable so anybody could start to use it on their workspace. The main features that HamzaHub has are:
- Database creation over customizable user characteristics representing real Warehouse. 
- Customizable Tkinter GUI.
- Fully manageable Inbound and Outbound characteristics. 
- Bulk Locations and automatized moves for release of orders. 
- Login.
- Input orders and inbound information via .csv

It is, also, my final project for *CS50 Introduction with Python*.

### Why?
I found that some of the work that we use to do at my warehouse could be automatized, like the moving from bulk locations to floor locations, and the program was not friendly with workers that just wanted to do their job quickly without having to press to much buttons for so little action. 

### Usage
1. We will clone the repo: 
```shell
    git clone hamzahub repository link
```
2. Set the parameters as we want on *.config/config_database.json*, you will requiere a connection on MySQL workbench.
3. Run *warehouse_creation.py* with python command:
```shell
    python warehouse_creation.py 
```
4. Now that our MySQL database has been created, we will start the program with:
```shell
    python main.py
```
5. You can use user *Admin* and password *Admin* to enter and register more users using the top bar dropdown menu.


