#Importation des packages necessaires
import pandas as pd
import networkx as nx
from bokeh.layouts import column,row
from bokeh.plotting import curdoc
from bokeh.models import BoxZoomTool, Circle, HoverTool,Plot, ResetTool,CheckboxGroup,Select,Slider,Button
from collections import OrderedDict
from bokeh.plotting import from_networkx
from bokeh.models.widgets import TextInput
from tornado.ioloop import IOLoop


global degre
degre=1

global segmentation
segmentation="All"

global garantie
garantie=0

global etats
etats=[0,1,2]

global contrepartie
contrepartie=""


def crea_graphe(g,data,list_nd,list_emp,list_gar):
    g.add_nodes_from(list_nd) #On ajoute les noeuds au graphes

    for i in data_garant.index: #On ajoute les étiquettes aux noeuds
        #Libellé
        g.nodes[str(data_garant["Identifiant garant"][i])]["Libelle"]=data_garant["Libellé court garant"][i]
        g.nodes[str(data_garant["Identifiant emprunteur"][i])]["Libelle"]=data_garant["Libellé court emprunteur"][i]
        
        #Etat
        g.nodes[str(data_garant["Identifiant garant"][i])]["Etat"]=data_garant["Libellé état garant"][i]
        g.nodes[str(data_garant["Identifiant emprunteur"][i])]["Etat"]=data_garant["Libellé état  emprunteur"][i]
        
        #Id
        g.nodes[str(data_garant["Identifiant garant"][i])]["Identifiant"]=data_garant["Identifiant garant"][i]
        g.nodes[str(data_garant["Identifiant emprunteur"][i])]["Identifiant"]=data_garant["Identifiant emprunteur"][i]
        
        #Role
        g.nodes[str(data_garant["Identifiant garant"][i])]["Role"]="Garant"
        g.nodes[str(data_garant["Identifiant emprunteur"][i])]["Role"]="Emprunteur"
        
        #Segemnts
        g.nodes[str(data_garant["Identifiant garant"][i])]["Segment"]=data_garant["Segment garant"][i]
        g.nodes[str(data_garant["Identifiant emprunteur"][i])]["Segment"]=data_garant["Segment risque emprunteur"][i]
        
        #Encours
        #g.nodes[str(data_garant["Identifiant garant"][i])]["Encours comptable"]=data_garant["Encours comptable"][i]
        
        
        ### On ajoute les arrètes avec la regle suivante : est de garant de 
        g.add_edges_from([(str(data_garant["Identifiant garant"][i]),str(data_garant["Identifiant emprunteur"][i]))])
        
    #On spécifie les noeuds qui sont garant et emprunteur    
    for i in list(set(data_garant["Identifiant emprunteur"].unique())&set(data_garant["Identifiant garant"].unique())):
        g.nodes[str(i)]["Role"]="Emprunteur\Garant"
    
    return g

def get_neighbors(G,noeuds): #Fonction qui renvoie les voisins des noeuds du graphe G
    #G est un graphe, noeuds est une liste de noeuds du graphe G
    res=[]
    for noeud in noeuds:
        res+=[n for n in G.neighbors(noeud)]
    return res

def subgraph_etat(G,lst_noeud):
    etats_act=[]
    if(segmentation=="All"):
        etats_seg=["Non renseigné","Collectivités locales","Contreparties diverses","Etablissement de crédit","Financements spécialisés","OLS","Sanitaire et SMS"]
    else:
        etats_seg=["Non renseigné",segmentation]
    #print(etats_seg)
    res=[]
    if(0 in etats):
        etats_act.append("Sain")
    if(1 in etats):
        etats_act.append("Sous surveillance")
    if(2 in etats):
        etats_act.append("En défaut")
    for i in range(len(lst_noeud)):
        if(G.nodes[lst_noeud[i]]["Etat"] in etats_act and G.nodes[lst_noeud[i]]["Segment"] in etats_seg):
            res.append(lst_noeud[i])
    return res
  
def subgraph_nd_deg(G,noeud,deg): #Calcul le sous graphe de G de degré deg pour noeud
    #G est un graphe, noeud un noeud de G et degré un entier
    res=[noeud]
    for i in range(deg):
            res+=get_neighbors(G,res)
    
    res=subgraph_etat(G,res)    
    return G.subgraph(res+[noeud])

def color_graph(G): #Colorie le graphe G
    # En défaut=rouge, Sous surveillance=jaune et sain=vert
    dict_color={}
    for node in G.nodes(): #On parcourt les noeuds de G
        if(G.nodes[node]["Etat"]=="En défaut"): #Si en défaut --> Rouge
             dict_color[node]="red"
        elif(G.nodes[node]["Etat"]=="Sous surveillance"):#Si sous surveillance --> Jaune
             dict_color[node]="yellow"
        else:                                         #Si Sain --> Vert
            dict_color[node]="green"
    nx.set_node_attributes(G,dict_color,"node_color") #On ajoute les couleurs au graphe
    return 

def update_graph(): #Callback du TextInput pour la recherche de Contrepartie
    #New correspond au nouvel input rentré par l'utilisateur
    
    if(contrepartie in list_nd): #Si new est dans liste des noeuds on affiche son graphe
    
        name_ctr=g.nodes[contrepartie]["Libelle"] #On récupère le nom de la contrepartie pour le titre
        sub_g=subgraph_nd_deg(g,contrepartie,degre) #On calcul le sous graphe de G avec new comme noeud et le degré choisi
        color_graph(sub_g) #On colorie le Graphe
        
        plot.title.text = "Contagion de la contrepartie "+name_ctr #Titre
        plot.tools=[]
        #Etiquettes et fonctionnalités graphiques
        node_hover_tool = HoverTool(tooltips=[("Libellé", "@Libelle"),("Identifiant","@Identifiant"),("État","@Etat"),("Rôle","@Role"),("Segment","@Segment")])
        plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())
        
        #Affichage du graphe
        graph_renderer = from_networkx(sub_g,nx.spring_layout,center=(0, 0))
        
        #Couleur des noeuds
        graph_renderer.node_renderer.glyph = Circle(size=15,fill_color="node_color")
        plot.renderers=[]
        plot.renderers.append(graph_renderer)
        return
    
    return

def ctr_callback(attr, old, new):
    global contrepartie
    contrepartie=new
    #debug_global()
    update_graph()
    return

def etat_callback(attr, old, new):
    global etats
    etats=new
    #debug_global()
    update_graph()
    return

def deg_callback(attr, old, new):
    global degre
    degre=int(new)
    #debug_global()
    update_graph()
    return

def encours_callback(attr, old, new):
    global garantie
    garantie=new
    #debug_global()
    update_graph()
    return

def seg_callback(attr, old, new):
    global segmentation
    segmentation=new
    update_graph()
    return

def stop_server(): #Boutton pour eteindre le serveur
    IOLoop.current().stop()
button = Button(label="Fermer le serveur",button_type="danger",margin=(15,5,5,25),height=50)
button.on_click(stop_server)


def debug_global():
    print("Id_tiers : ",contrepartie,",états : ",etats,",degré : ",degre,", seuil garantie : ",garantie," et segmentation : ",segmentation)
    return


# On charge la base pickle
data_garant=pd.read_pickle("Data/BaseContagion.pkl")

list_emp=list(data_garant["Identifiant emprunteur"].unique()) #On recupere tout les emprunteurs
list_gar=list(data_garant["Identifiant garant"].unique())#On recupere tout les garants

list_nd = list(OrderedDict.fromkeys(list_emp+list_gar)) #On fusionne les listes pour obtenir la liste des noeuds
#On enleve les doublons
list_nd=[str(i) for i in list_nd] #On convertit en str pour l'affichage Bokeh

g=nx.Graph() #On crée notre graphe
g=crea_graphe(g,data_garant,list_nd,list_emp,list_gar)


#Création du plot
plot = Plot(width=550, height=550) 
plot.title.text = " " #Titre

#Recherche par tiers
find_tiers= TextInput(title='Recherche par numéros tiers : ',value='')
find_tiers.on_change('value',ctr_callback)

#Séléction des états
checkBox_etat=CheckboxGroup(labels=["Sain","Sous Surveillance", "En défaut"],active=[0,1,2],margin=(28,5,5,25))
checkBox_etat.on_change('active',etat_callback)


#Selection du degré
deg=Select(title="Sélectionner le degré",value="1",options=["1","2","3","4"],margin=(5,5,5,25))
deg.on_change('value',deg_callback)

#Selection de l'encours
encours=Slider(start=0, end=10000, value=0, step=2000, title="Encours comptable (en €)",margin=(10,5,5,25))
encours.on_change('value',encours_callback)

#Selection de la segmentation
str_seg=["All","Collectivités locales","Contreparties diverses","Etablissement de crédit","Financements spécialisés","OLS","Sanitaire et SMS"]
seg=Select(title="Sélectionner un segment",value="All",options=str_seg,margin=(5,5,5,25))
seg.on_change('value',seg_callback)


options=column(checkBox_etat,deg,encours,seg,button)
#Partie création de l'application
curdoc().add_root(column(find_tiers,row(plot,options)))
 
import os
os.system(r'cd U:\DG\DGDR\50.RISQUES FINANCIERS\550. Pilotage et Innovation\C_DEVELOPPEMENT\Contagion & conda activate base & bokeh serve --show AppV1.py')
