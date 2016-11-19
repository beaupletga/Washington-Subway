#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import Tkinter
import pickle
import time
import csv
from threading import Thread
import tkFileDialog
from tkMessageBox import *
import ttk
import glob
from Tkinter import *
import PIL
from PIL import ImageTk, Image
import httplib, urllib, base64
from scipy import *
import networkx as nx
import numpy as np
from lxml import etree
import xml.etree.ElementTree as ET

global api_key
api_key='6b700f7ea9db408e9745c207da7ca827'

def changer():
    api_key= e.get()

def changer_api():#Change la valeur de l'API
    global e
    seconde=Tk()
    window.title("API")
    window.configure(background='grey')
    Label(seconde, text="API-key").grid(row=0)
    e = Entry(seconde).grid(row=0,column=1)
    b = Button(seconde, text="Valider", width=10, command=changer).grid(row=0,column=2)
    seconde.mainloop()


global r
window = Tk()
l= PanedWindow(window, orient=VERTICAL)
r=PanedWindow(window, orient=VERTICAL)
l.pack(side=LEFT, fill=BOTH, pady=2, padx=2)
r.pack(side=RIGHT,expand=Y, fill=BOTH, pady=2, padx=2)

image = Image.open("depart.png")
photo1 = ImageTk.PhotoImage(image)

image2 = Image.open("arrive.png")
photo2 = ImageTk.PhotoImage(image2)

image = Image.open("retard.gif")
photo3 = ImageTk.PhotoImage(image)

image = Image.open("ne_pas_ouvrir.jpg")#faut pas tricher !
photo4 = ImageTk.PhotoImage(image)

image = Image.open("ne_pas_ouvrir.png").resize((700,650))#faut pas tricher !
photo5 = ImageTk.PhotoImage(image)


def afficher_carte():#affiche la carte

    image = Image.open("map.png").resize((700,700))
    photo = ImageTk.PhotoImage(image)



    canvas = Canvas(l, width = image.size[0], height = image.size[1])
    canvas.create_image(0,0, anchor = NW, image=photo)
    #canvas.pack(side=LEFT)
    l.add(canvas)
    bouton4=Button(window, text="Parcours sur la map",command=lecture,bd=5)
    l.pack()
    bouton4.pack()
    l.mainloop()

    """
    Frame3 = Frame(window, bg="white", borderwidth=2,height=300,width=300)
    Frame3.pack(side=RIGHT)

    image = Image.open("map.png").resize((600,600))
    photo = ImageTk.PhotoImage(image)
    panel1 = Label(Frame3, image = photo,width=300, height=300)
    panel1.pack()

    window.mainloop()
    """


def creation_liste(liste_stations):
    tree = etree.parse("station_list.xml")
    compteur=0
    for user in tree.xpath("//Name"):
        liste_stations.append(user.text)
        compteur+=1

def creation_liste3():
    tree = etree.parse("station_list.xml")
    for user in tree.xpath("//StationTogether1"):
        if (user.text):
            print user.text

def creation_liste2(liste_code_stations):
    tree = etree.parse("station_list.xml")
    for user in tree.xpath("//Code"):
        liste_code_stations.append(user.text)

def get_code_from_name(name,liste_stations,liste_code_stations):
    for i in range(0,len(liste_stations)):
        if (liste_stations[i]==name):
            return liste_code_stations[i]


def temps_entre_deux_stations(station1,station2):#calcul le temps entre deux stations
    headers = {'api_key': api_key,}
    params = urllib.urlencode({'FromStationCode': station1,'ToStationCode': station2,})
    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/Rail.svc/SrcStationToDstStationInfo?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        #print data

        root=ET.fromstring(data)
        #child=root.find('.//RailTime')
        caca=root[0]
        deux=caca[0]
        quatre=deux[3].text
        return quatre
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_indice(liste,arret):
    for i in range(0,len(liste)):
        if (liste[i]==arret):
            return i


def affecter_matrice(station1,station2,tab,liste):
    temps=temps_entre_deux_stations(station1,station2)
    indice_station1=get_indice(liste,station1)
    indice_station2=get_indice(liste,station2)
    tab[indice_station1][indice_station2]=temps


def definir_graphe(station1,station2,liste):#Defini le graphe
    headers = {'api_key': api_key,}
    params = urllib.urlencode({'FromStationCode': station1,'ToStationCode': station2,})

    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/Rail.svc/Path?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        root=ET.fromstring(data)
        #child=root.find('.//RailTime')
        caca=root[0]

        for i in range(0,len(caca)):#len(caca)-1
            deux=caca[i]
            quatre=deux[4].text
            liste.append(quatre)

        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def envoyer(liste1,liste2,liste3,liste4,liste5,liste6):
    definir_graphe('N06','G05',liste1)
    definir_graphe('B11','A15',liste2)
    definir_graphe('K08','D13',liste3)
    definir_graphe('G05','J03',liste4)
    definir_graphe('C15','E06',liste5)
    definir_graphe('E10','F11',liste6)



def symetrique(tab):
    for i in range(0,len(tab)):
        for j in range(0,len(tab)):
            if (tab[j][i]!=0 and tab[i][j]==0):
                tab[i][j]=tab[j][i]
            if (tab[i][j]!=0 and tab[j][i]==0):
                tab[j][i]=tab[i][j]
            if (tab[i][j]!=0 and tab[j][i]!=0):
                if (tab[i][j]>tab[j][i]):
                    tab[i][j]=tab[j][i]
                else:
                    tab[j][i]=tab[i][j]


def callback():
    if askyesno('Metro', 'Une connection internet est requise'):
        main()


global tab,liste_code_stations

def main():#Raffraichi la carte depuis le site de Washington
    liste_stations=[]
    liste_code_stations=[]
    creation_liste(liste_stations)
    creation_liste2(liste_code_stations)
    dimension=len(liste_stations)

    tab=zeros((dimension, dimension))

    liste1=[]#SV
    liste2=[]#RD
    liste3=[]#OR
    liste4=[]#BL
    liste5=[]#YL
    liste6=[]#GR


    envoyer(liste1,liste2,liste3,liste4,liste5,liste6)

    for i in range(0,len(liste1)-1):
        tmp1=get_code_from_name(liste1[i],liste_stations,liste_code_stations)
        tmp2=get_code_from_name(liste1[i+1],liste_stations,liste_code_stations)
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste2)-1):
        tmp1=get_code_from_name(liste2[i],liste_stations,liste_code_stations)
        tmp2=get_code_from_name(liste2[i+1],liste_stations,liste_code_stations)
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste3)-1):
        tmp1=get_code_from_name(liste3[i],liste_stations,liste_code_stations)
        tmp2=get_code_from_name(liste3[i+1],liste_stations,liste_code_stations)
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste4)-1):
        tmp1=get_code_from_name(liste4[i],liste_stations,liste_code_stations)
        tmp2=get_code_from_name(liste4[i+1],liste_stations,liste_code_stations)
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste5)-1):
        tmp1=get_code_from_name(liste5[i],liste_stations,liste_code_stations)
        tmp2=get_code_from_name(liste5[i+1],liste_stations,liste_code_stations)
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste6)-1):
        tmp1=get_code_from_name(liste6[i],liste_stations,liste_code_stations)
        tmp2=get_code_from_name(liste6[i+1],liste_stations,liste_code_stations)
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    symetrique(tab)


    np.savetxt(
    'tab.csv',           # file name
    tab,                # array to save
    fmt='%.2f',             # formatting, 2 digits in this case
    delimiter=',',          # column delimiter
    newline='\n',           # new line character
    footer='end of file',   # file footer
    comments='# ',          # character to use for comments
    header='Data generated by numpy')


compteur=0
def clic2(evt):#Calcul un trajet bis
    liste_stations=[]
    tree = etree.parse("station_list.xml")
    for user in tree.xpath("//Name"):
        liste_stations.append(user.text)
    global var1,var2,var3
    global compteur
    compteur+=1
    try:
        i=l1.curselection()  ## Récupération de l'index de l'élément sélectionné
        var1= l1.get(i)  ## On retourne l'élément (un string) sélectionné
    except:
        try:
            i=l2.curselection()  ## Récupération de l'index de l'élément sélectionné
            var2=l2.get(i)
        except:
            i=l3.curselection()  ## Récupération de l'index de l'élément sélectionné
            var3=l3.get(i)
            var3_int=get_indice(liste_stations,var3)
            del liste_stations[var3_int]
            M=np.delete(thedata, var3_int, 0)
            N=np.delete(M, var3_int, 1)
            G = nx.from_numpy_matrix(N, create_using=nx.DiGraph())
            var1_int=get_indice(liste_stations,var1)
            var2_int=get_indice(liste_stations,var2)

            try :
                resultat=nx.dijkstra_path(G, var1_int, var2_int)
                Label(r, text='0 min',bg="red").grid(row=0, column=0,columnspan=1, rowspan=1)
                Label(r, text='Départ',bg="red").grid(row=0, column=1,columnspan=1, rowspan=1)
                Label(r, text=var1,bg="red").grid(row=0, column=2,columnspan=1, rowspan=1)
                r.pack()
                precedent=get_indice(liste_stations,var1)
                compteur=1
                temps_int=0
                for i in range(0,len(resultat)-2):
                    if (get_ligne_from_name(liste_stations[resultat[i]],liste_stations[resultat[i+2]])==False):
                        temps_int+=nx.dijkstra_path_length(G,precedent,resultat[i+1])
                        precedent=resultat[i+1]
                        texte1=str(temps_int)+' min'
                        Label(r, text=texte1).grid(row=compteur, column=0,columnspan=1, rowspan=1)
                        Label(r, text='Changement '+str(compteur)).grid(row=compteur,column=1,columnspan=1, rowspan=1)
                        Label(r, text=liste_stations[resultat[i+1]]).grid(row=compteur, column=2,columnspan=1, rowspan=1)
                        r.pack()
                        compteur+=1
                temps_int+=nx.dijkstra_path_length(G,precedent,resultat[len(resultat)-1])

                Label(r, text=str(temps_int)+' min',bg="green").grid(row=compteur, column=0,columnspan=1, rowspan=1)
                Label(r, text='Arrivée',bg="green").grid(row=compteur, column=1,columnspan=1, rowspan=1)
                Label(r, text=var2,bg="green").grid(row=compteur, column=2,columnspan=1, rowspan=1)

                Label(r,text="").grid(row=compteur+5)
                Label(r,text="").grid(row=compteur+5)
                Label(r,text="Liste des stations",bg="yellow").grid(row=compteur+5)
                r.pack()
                for i in resultat:
                    Label(r,text=liste_stations[i]).grid(row=compteur+7)
                    compteur+=1
                    r.pack()
            except:
                Label(r,text="Les deux stations ne sont pas atteignables").grid(row=0)
                r.pack()
            window.mainloop()

def trajet_bis():
    global l1,l2,l3
    liste_tmp=[]
    tree = etree.parse("station_list.xml")
    compteur=0
    f1 = Frame(window)
    s1 = Scrollbar(f1)
    l1 = Listbox(f1)
    l1.bind('<ButtonRelease-1>',clic2)

    s2 = Scrollbar(f1)
    l2= Listbox(f1)
    l2.bind('<ButtonRelease-1>',clic2)

    s3 = Scrollbar(f1)
    l3= Listbox(f1)
    l3.bind('<ButtonRelease-1>',clic2)
    for user in tree.xpath("//Name"):
        liste_tmp.append(user.text)
    liste_tmp.sort()
    for i in liste_tmp:
        compteur+=1
        l1.insert(compteur, i)
        l2.insert(compteur, i)
        l3.insert(compteur,i)
    s1.config(command = l1.yview)
    l1.config(yscrollcommand = s1.set)
    l1.pack(side = LEFT, fill = Y)
    s1.pack(side = RIGHT, fill = Y)

    s2.config(command = l2.yview)
    l2.config(yscrollcommand = s2.set)
    l2.pack(side = LEFT, fill = Y)
    s2.pack(side = RIGHT, fill = Y)

    s3.config(command = l3.yview)
    l3.config(yscrollcommand = s3.set)
    l3.pack(side = LEFT, fill = Y)
    s3.pack(side = RIGHT, fill = Y)
    f1.pack()


def charger():#Charge la map depuis le fichier tab (pour eviter de toujours l'impoorter)
    global thedata
    thedata = np.genfromtxt(
    'tab.csv',           # file name
    skip_header=0,          # lines to skip at the top
    skip_footer=0,          # lines to skip at the bottom
    delimiter=',',          # column delimiter
    dtype='float32',        # data type
    filling_values=0)
    window.update()
    bouton2=Button(window, text="Trouver un trajet",command=trajet,bd=5)
    bouton5=Button(window, text="Trouver un trajet bis",command=trajet_bis,bd=5)
    bouton4=Button(window, text="Afficher la map",command=afficher_carte,bd=5)
    bouton2.pack()
    bouton4.pack()
    bouton5.pack()
    window.mainloop()

def get_ligne_from_name(arret1,arret2):
    liste_tmp1=[]
    liste_tmp2=[]
    tree = etree.parse("station_list.xml")
    for user in tree.xpath("//Station"):
        if (user[8].text==arret1):
            liste_tmp1.append(user[3].text)
            liste_tmp1.append(user[4].text)
            liste_tmp1.append(user[5].text)
            liste_tmp1.append(user[6].text)
    for user in tree.xpath("//Station"):
        if (user[8].text==arret2):
            liste_tmp2.append(user[3].text)
            liste_tmp2.append(user[4].text)
            liste_tmp2.append(user[5].text)
            liste_tmp2.append(user[6].text)

    for i in liste_tmp1:
        for j in liste_tmp2:
            if (j==i and i!=None):
                return True
    return  False

def get_ligne_from_name2(arret1,arret2):
    liste_tmp1=[]
    liste_tmp2=[]
    tree = etree.parse("station_list.xml")
    for user in tree.xpath("//Station"):
        if (user[8].text==arret1):
            liste_tmp1.append(user[3].text)
            liste_tmp1.append(user[4].text)
            liste_tmp1.append(user[5].text)
            liste_tmp1.append(user[6].text)
    for user in tree.xpath("//Station"):
        if (user[8].text==arret2):
            liste_tmp2.append(user[3].text)
            liste_tmp2.append(user[4].text)
            liste_tmp2.append(user[5].text)
            liste_tmp2.append(user[6].text)

    for i in liste_tmp1:
        for j in liste_tmp2:
            if (j==i and i!=None):
                return i

compteur=0
def clic(evt):#Calcul simplement le trajet
    liste_stations=[]
    liste_code_stations=[]
    tree = etree.parse("station_list.xml")
    for user in tree.xpath("//Name"):
        liste_stations.append(user.text)
    for user in tree.xpath("//Code"):
        liste_code_stations.append(user.text)
    global var1,var2
    global compteur
    compteur+=1
    try:
        i=l1.curselection()  ## Récupération de l'index de l'élément sélectionné
        var1= l1.get(i)  ## On retourne l'élément (un string) sélectionné
    except:
        i=l2.curselection()  ## Récupération de l'index de l'élément sélectionné
        var2=l2.get(i)
        G = nx.from_numpy_matrix(thedata, create_using=nx.DiGraph())
        var1_int=get_indice(liste_stations,var1)
        var2_int=get_indice(liste_stations,var2)
        try:
            resultat=nx.dijkstra_path(G, var1_int, var2_int)
            Label(r, image=photo1).grid(row=0, column=0,columnspan=1, rowspan=1)
            Label(r, text='0 min',bg="green").grid(row=0, column=1,columnspan=1, rowspan=1)
            Label(r, text='Départ',bg="green").grid(row=0, column=2,columnspan=1, rowspan=1)
            Label(r, text=var1,bg="green").grid(row=0, column=3,columnspan=1, rowspan=1)

            compteur=1
            precedent=get_indice(liste_stations,var1)
            temps_int=0
            for i in range(0,len(resultat)-2):
                if (get_ligne_from_name(liste_stations[resultat[i]],liste_stations[resultat[i+2]])==False):
                    temps_int+=nx.dijkstra_path_length(G,precedent,resultat[i+1])

                    texte1=str(temps_int)+' min'
                    #Label(r, text='',bg="red").grid(row=0, column=0,columnspan=1, rowspan=1)
                    #abel(r, text=get_ligne_from_name2(liste_stations[precedent],liste_stations[resultat[i]])).grid(row=compteur+1, column=0)
                    Label(r, text=texte1).grid(row=compteur+2, column=1)
                    Label(r, text='Changement '+str(compteur)).grid(row=compteur+2,column=2)
                    Label(r, text=liste_stations[resultat[i+1]]).grid(row=compteur+2, column=3)

                    precedent=resultat[i+1]
                    compteur+=1
            temps_int+=nx.dijkstra_path_length(G,precedent,resultat[len(resultat)-1])

            Label(r, image=photo2).grid(row=compteur+2, column=0)
            Label(r, text=str(temps_int)+' min',bg="red").grid(row=compteur+2, column=1)
            Label(r, text='Arrivée',bg="red").grid(row=compteur+2, column=2)
            Label(r, text=var2,bg="red").grid(row=compteur+2, column=3)
            Label(r,text="Liste des stations",bg="yellow").grid(row=compteur+5)
            for i in resultat:
                Label(r,text=liste_stations[i]).grid(row=compteur+7)
                compteur+=1
        except:
            Label(r,text="Les deux stations ne sont pas atteignables").grid()
        window.mainloop()


def trajet():
    liste_tmp=[]
    global l1,l2
    tree = etree.parse("station_list.xml")
    compteur=0
    f1 = Frame(window)
    s1 = Scrollbar(f1)
    l1 = Listbox(f1)
    l1.bind('<ButtonRelease-1>',clic)

    s2 = Scrollbar(f1)
    l2= Listbox(f1)
    l2.bind('<ButtonRelease-1>',clic)
    for user in tree.xpath("//Name"):
        liste_tmp.append(user.text)
    liste_tmp.sort()
    for i in liste_tmp:
        compteur+=1
        l1.insert(compteur, i)
        l2.insert(compteur, i)

    s1.config(command = l1.yview)
    l1.config(yscrollcommand = s1.set)
    l1.pack(side = LEFT, fill = Y)
    s1.pack(side = RIGHT, fill = Y)

    s2.config(command = l2.yview)
    l2.config(yscrollcommand = s2.set)
    l2.pack(side = LEFT, fill = Y)
    s2.pack(side = RIGHT, fill = Y)
    f1.pack()



compteur_tmp=0
liste_tmp=[]
def motion(event):#Calcule le trajet en cliquant sur deux stations de la carte
    liste_stations=[]
    liste_code_stations=[]
    tree = etree.parse("station_list.xml")
    for user in tree.xpath("//Name"):
        liste_stations.append(user.text)
    for user in tree.xpath("//Code"):
        liste_code_stations.append(user.text)
    global compteur_tmp,liste_tmp
    compteur_tmp+=1
    x, y = event.x, event.y
    liste_tmp.append(x)
    liste_tmp.append(y)
    if (abs(x-632)<8 and abs(y-670)<8):#On ferme les yeux !
        Label(r, image=photo4).grid(row=0)
        Label(r, text="Femme ou mulet ?").grid(row=1)
        Label(r,image=photo5).grid(row=2)
        Label(r, text="Je préfère la Femme").grid(row=3)
    if (compteur_tmp==2):
        x1=liste_tmp[0]
        y1=liste_tmp[1]
        x2=liste_tmp[2]
        y2=liste_tmp[3]
        station1=""
        station2=""
        cr = csv.reader(open("wesh.csv","rb"))
        for i in cr:
            if (abs(x1-int(i[1]))<8 and abs(y1-int(i[2]))<8):
                station1=i[0]
        c=csv.reader(open("wesh.csv","rb"))
        for h in c:
            if (abs(x2-int(h[1]))<8 and abs(y2-int(h[2]))<8):
                station2=h[0]

        if (station1!="" and station2!=""):
            var1_int=get_indice(liste_stations,station1)
            var2_int=get_indice(liste_stations,station2)
            G = nx.from_numpy_matrix(thedata, create_using=nx.DiGraph())
            resultat=nx.dijkstra_path(G, var1_int, var2_int)


            Label(r, image=photo1).grid(row=0, column=0,columnspan=1, rowspan=1)
            Label(r, text='0 min',bg="green").grid(row=0, column=1,columnspan=1, rowspan=1)
            Label(r, text='Départ',bg="green").grid(row=0, column=2,columnspan=1, rowspan=1)
            Label(r, text=station1,bg="green").grid(row=0, column=3,columnspan=1, rowspan=1)

            compteur=1
            precedent=get_indice(liste_stations,station1)
            temps_int=0
            for i in range(0,len(resultat)-2):
                if (get_ligne_from_name(liste_stations[resultat[i]],liste_stations[resultat[i+2]])==False):
                    if (compteur==1):
                        code_station1=get_code_from_name(station1,liste_stations,liste_code_stations)
                        code_station2=liste_code_stations[resultat[i+1]]

                        x=prochain_train(code_station1,code_station2,1)
                        y=prochain_train(code_station1,code_station2,2)
                        Label(r, text="        ").grid(row=0, column=4,columnspan=1, rowspan=1)
                        Label(r, text="Prochain train : "+str(x),bg="green").grid(row=0, column=5,columnspan=1, rowspan=1)
                        Label(r, text="         ").grid(row=0, column=6,columnspan=1, rowspan=1)
                        Label(r, text="Train suivant : "+str(y),bg="green").grid(row=0, column=7,columnspan=1, rowspan=1)


                    temps_int+=nx.dijkstra_path_length(G,precedent,resultat[i+1])

                    texte1=str(temps_int)+' min'
                    #Label(r, text='',bg="red").grid(row=0, column=0,columnspan=1, rowspan=1)
                    #abel(r, text=get_ligne_from_name2(liste_stations[precedent],liste_stations[resultat[i]])).grid(row=compteur+1, column=0)
                    Label(r, text=texte1).grid(row=compteur+2, column=1)
                    Label(r, text='Changement '+str(compteur)).grid(row=compteur+2,column=2)
                    Label(r, text=liste_stations[resultat[i+1]]).grid(row=compteur+2, column=3)
                    precedent=resultat[i+1]
                    compteur+=1
            if (compteur==1):

                x=prochain_train(liste_code_stations[var1_int],liste_code_stations[var2_int],1)
                y=prochain_train(liste_code_stations[var1_int],liste_code_stations[var2_int],2)
                Label(r, text="        ").grid(row=0, column=4,columnspan=1, rowspan=1)
                Label(r, text="Prochain train : "+str(x),bg="green").grid(row=0, column=5,columnspan=1, rowspan=1)
                Label(r, text="         ").grid(row=0, column=6,columnspan=1, rowspan=1)
                Label(r, text="Train suivant : "+str(y),bg="green").grid(row=0, column=7,columnspan=1, rowspan=1)

            temps_int+=nx.dijkstra_path_length(G,precedent,resultat[len(resultat)-1])

            Label(r, image=photo2).grid(row=compteur+2, column=0)
            Label(r, text=str(temps_int)+' min',bg="red").grid(row=compteur+2, column=1)
            Label(r, text='Arrivée',bg="red").grid(row=compteur+2, column=2)
            Label(r, text=station2,bg="red").grid(row=compteur+2, column=3)
            Label(r,text="Liste des stations",bg="yellow").grid(row=compteur+5)
            for i in resultat:
                Label(r,text=liste_stations[i]).grid(row=compteur+7)
                compteur+=1
        else:
            Label(r,text="Tu sais pas cliquer !").grid(row=0)

def lecture():
    window.bind('<Button-1>', motion)

def prochain_train(station_code1,station_code2,choix):#Affiche le prochain train et le train suivant
    headers = {'api_key': api_key}
    params = urllib.urlencode({'StationCodes': station_code1,'DestinationCode': station_code2})
    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        tmp="/StationPrediction.svc/GetPrediction/"+station_code1+"?Destinationcode="+station_code2
        conn.request("GET", tmp, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        root=ET.fromstring(data)
        #child=root.find('.//RailTime')
        if choix==1:
            premier=root[0]
            deux=premier[0]
            trois=deux[8].text
            if trois=="BRD":
                return "Train à quai"
            if trois=="ARR":
                return "Train proche"
            else:
                return (trois+" min")
        else:
            premier=root[0]
            deux=premier[1]
            trois=deux[8].text
            if trois=="BRD":
                return "Train à quai"
            if trois=="ARR":
                return "Train proche"
            else:
                return (trois+" min")
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def voir_incidents():#Affiche les incidents sur les lignes
    headers = {'api_key': api_key,}

    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/Incidents.svc/Incidents", "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        root=ET.fromstring(data)
        try:
                    premier=root[0]
                    deux=premier[0]
                    trois=deux[0].text
                    quatre=deux[2].text
                    cinq=deux[7].text
                    Label(r, image="Update : "+trois).grid(row=0, column=0,columnspan=1, rowspan=1)
                    Label(r, text="Description : "+quatre).grid(row=1, column=0,columnspan=1, rowspan=1)
                    Label(r, text="Lignes affectées : "+cinq).grid(row=2, column=0,columnspan=1, rowspan=1)
                    r.pack()
        except:
            Label(r, text="Aucun incident", bg="blue").grid(row=2, column=0,columnspan=1, rowspan=1)#
            Label(r, image=photo3).grid(row=0, column=0,columnspan=1, rowspan=1)

            conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

#voir_incidents()


def choix():#Menu principal
    bouton1=Button(window, text="Charger la map",command=charger,bd=5)
    bouton3=Button(window, text="Définir la map",command=callback,bd=5)
    bouton2=Button(window, text="Voir incidents",command=voir_incidents,bd=5)
    bouton4=Button(window, text="Changer API key",command=changer_api,bd=5)
    bouton1.pack()
    bouton3.pack()
    bouton2.pack()
    bouton4.pack()
    window.mainloop()

window.title("Metro")
window.geometry("1920x1920")
window.configure(background='grey')

choix()
