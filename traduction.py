# ------------------ Credits --------------------
"""
Auteur : Récitasse
Date : 29/08/2023
Description : Traduction online avec toutes les informations (russe) -> français

Les arguments utilisables :
   m mot seulement
   d déclinaison ou conjugaison
   e les exemples

Ils peuvent être mis dans le désordre mais doivent être attaché

"""

import requests
from bs4 import BeautifulSoup
import sys
import enchant
from prettytable import PrettyTable
bs = "\033[1m"; bf = "\033[0m"

# ------------------ Info ----------------------
langue_defaut = "russe"
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
# ----------------------------------------------

class traduction:
   def __init__(self, langue:str, headers:str="", affi:str="menac") -> None:
      """
      Ininitialise la traduction

      Args:
         langue (str) : définit la langue à traduire

      Exemple:
         russe
      """
      list_langue = ["espagnol","russe",'chinois',"japonais",'allemand','italien','portugais','grecque','hindi','anglais','coréen','turc','arabe']
      self.langue = langue
      self.url_trad = f"https://www.online-translator.com/traduction/{self.langue}-français/"
      self.html_parser = ""
      self.headers = {'User-Agent' : headers}
      self.DECL_A = ""
      self.CONJ = ""
      self.DECL_N = ""
      self.DATA_M = ""
      self.longue = ""
      self.affi = list(affi[0])

      if ''.join(self.affi) in list_langue:
         tempo = self.langue
         self.langue = ''.join(self.affi)
         self.affi = tempo

      for el in self.affi:
         if el not in ["m","d","e"]:
            print(f"""\033[91mx Erreur\033[0m. Argument {el} invalide.""")
            exit(1)

   def verification(self, mot:str, aff:bool=False):
      list_langue = ["espagnol","russe",'chinois',"japonais",'allemand','italien','portugais','grecque','hindi','anglais','coréen','turc','arabe']
      """
      Permet de vérifier un mot pour ne pas le réécrire plusieurs fois

      Args: 
         mot (str) : Le mot à vérifier
      """
      if self.langue == "russe":
         url_v = f"https://speller.yandex.net/services/spellservice.json/checkText?text={mot}&lang=ru"
         response = requests.get(url_v, headers=self.headers)
         if response.status_code == 200:
            suggestions = [error['s'][0] for error in response.json()]
            if aff and suggestions:
               print(f"\033[91mERREUR !\033[0m {mot} \033[91mn'existe pas.\033[0m")
               print("Correction : ")
               for suggestion in suggestions:
                  print(f"   -> \033[3;92m\033[3m{suggestion}\033[0m")
            return suggestions

      elif self.langue == "anglais":
         dictionary_en = enchant.Dict("en_US")
         if not dictionary_en.check(mot) and not dictionary_en.check(mot):
            suggestions = dictionary_en.suggest(mot) + dictionary_en.suggest(mot)
            print(f"Mot: {mot}, Suggestions: {suggestions}")
      else:
         print(f"/!\ : langue -> {self.langue}, n'est pas admise.")
        
   def aspect(self, mot:str) -> ["",""]:
      """
      Fonction donnant l'aspect d'un verbe (uniquement pour le russe)

      Args:
         mot (str) : verbe dont il faut connaitre l'aspect
      """
      url= f"https://conjugueur.reverso.net/conjugaison-russe-verbe-{mot}.html"

      reponse2 = requests.get(url, headers=self.headers)
      if reponse2.status_code == 200:
         data_asp2 = reponse2.text
         html_parser = BeautifulSoup(data_asp2, "html.parser")

         # L'aspect actuel
         asa = html_parser.find("span", class_="perfective-verb")
         asa = asa.get_text(strip=True)

         # L'autre
         asd = html_parser.find("span", id="ch_linkedForm")
         asd = asd.get_text(strip=True)

         return [asa, asd]
         
      else:
         print("Le verbe sélectionné n'existe pas.")
         return ["",""]

   def connexion(self, mot:str)->str:
      """
      Renvoie les informations de la page web de la traduction
      """
      self.url_trad = f"https://www.online-translator.com/traduction/{self.langue}-français/{mot}"

      reponse = requests.get(self.url_trad, headers=self.headers)
      if reponse.status_code == 200:
         return reponse.text
      else:
         print("\033[91mERREUR !\033[0m")
         exit(1)

   def trad(self, mot:str) -> dict:
      langue = self.langue
      """
      Traduction du mot dans une langue donnée

      Args:
         mot (str) : le mot à traduire
         langue (str) : langue dans laquelle il doit être traduit
      """
      DATA = {'mot': mot, 'type':"", 'detail':"", 'trad':[], 'exemple':[], 'genre':"", 'aspect':{'perfectif':"", 'imperfectif':""}}
      self.langue = langue
      self.verification(mot,True)
      data = self.connexion(mot)
      self.html_parser = BeautifulSoup(data, "html.parser")

      if self.html_parser.find("span", class_="source_only sayWord"):

         if not mot == self.html_parser.find("span", class_="source_only sayWord").get_text(strip=True):
            sugg = self.verification(mot)
            print("\n")
            if sugg:
               mot = sugg[0]
               DATA['mot'] = mot
            data = self.connexion(mot)
            self.html_parser = BeautifulSoup(data, "html.parser")

      # Obtention des informations
      detail = self.html_parser.find("div", class_="otherImportantForms")
      if detail:
         detail = detail.get_text(strip=True)
         DATA['detail'] = detail

      #Obtention du genre
      try:
         genre = self.html_parser.find("span", class_="ref_info")
         genre = genre.get_text(strip=True)
         DATA['genre'] = genre 
      except AttributeError as e:
         DATA['genre'] = ""

      #Obtention du type (nom, verbe, adj)
      try:
         type = self.html_parser.find("span", class_="ref_psp")
         type = type.get_text(strip=True)
         DATA['type'] = type
      except AttributeError as e:
         DATA['type'] = ""


      # Si c'est un verbe on doit avoir les aspects
      if type == "verbe" and self.langue == "russe":
         info = self.aspect(mot)
         if info[0] == "(imperfectif)":
            DATA['aspect']['imperfectif'] = mot
            DATA['aspect']['perfectif'] = info[1].replace("- perfectif","").replace(";",", ").replace(",",", ")
         elif info[0] == "(perfectif)":
            DATA['aspect']['perfectif']=mot
            DATA['aspect']['imperfectif'] = info[1].replace("- imperfectif", "").replace(";",", ").replace(",",", ")
         self.CONJ = self.conjugaison(mot)
      elif type == "nom" and self.langue == "russe":
         self.DECL_N = self.declinaison_nom(mot)
      elif type == "adjectif" and self.langue == "russe":
         self.DECL_A = self.declinaison_adj(mot)
      else:
         pass
      
      # Les traductions
      trad_list = {"trad": [], "detail": []}
      trads = self.html_parser.find_all("div", class_="cforms_result")
      for trad in trads:
         mots = trad.find_all("span", class_="result_only sayWord")
         for mot in mots:
            DATA['trad'].append(mot.get_text().replace("\n",""))
         detailss = trad.find_all("div", class_="samplesList")
         for details in detailss:
            DATA['exemple'].append(details.get_text().replace("\n",""))
      
      # Si aucune traduction trouvée
      if not DATA['trad']:
         print(f"Aucune traduction trouvée pour {bs}'{mot}'{bf}.")
         exit(1)


      self.DATA_M = DATA

   def declinaison_adj(self, mot:str) -> dict:
      """
      Renvoie les déclinaisons de l'adjectif (mot)
      """
      clean = ["Именительный падеж (Какой? Чей?)", "Родительный падеж (Какого? Чьего?)", "Дательный падеж (Какому? Чьему?)", "Винительный падеж, одуш. (Какого? Чьего?)","Винительный падеж, неодуш. (Какой? Чей?)", "Творительный падеж (Каким? Чьим?)", "Предложный падеж (О каком? О чьем?)","Мужской род",'Женский род',"Средний род","Множественное число"]
      rep = ["Nominatif", "Génitif", "Datif", "Accusatif An.","Accusatif In.", "Instrumental", "Locatif",'Masculin','Féminin','Neutre',"Pluriel"]

      DATA_L = {'Nominatif':{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, "Accusatif An.":{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""},"Accusatif In.":{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, 'Génitif':{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, 'Datif':{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, "Instrumental":{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, "Locatif":{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}}

      DATA_S = {'Nominatif':{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, "Accusatif An.":{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""},"Accusatif In.":{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, 'Génitif':{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, 'Datif':{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, "Instrumental":{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}, "Locatif":{"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}}

      DATA_C = {"Masculin":"","Féminin":"", "Neutre":"", "Pluriel":""}

      L = ["Masculin","Féminin", "Neutre", "Pluriel"]

      url = f"https://www.online-translator.com/conjugaison et déclinaison/{self.langue}/{mot}"
      response = requests.get(url, headers=self.headers)
      if response.status_code == 200:
         data = response.text
         html_parser = BeautifulSoup(data, "html.parser")

         text = html_parser.find("div", class_="cc wordforms table ajective g-table cform_group full-forms")

         # Forme longue
         infos = text.find_all("div", class_="tr desk")
         for info in infos:
            els = info.find_all("span", class_="transl_form tr_f")
            cas = info.find("div", class_="td transl_form_des")
            if cas:
               cas = cas.get_text(strip=True)
               for i in range(len(clean)):
                  cas = cas.replace(clean[i], rep[i])
               for i,el in enumerate(els):
                  DATA_L[cas][L[i]] = el.get_text()
            else:
               els = info.find_all("span", class_="transl_form tr_f")
               cas = info.find("div", class_="td transl_form_des nob")
               cas = cas.get_text(strip=True)
               for i in range(len(clean)):
                  cas = cas.replace(clean[i], rep[i])
               for i,el in enumerate(els):
                  DATA_L[cas][L[i]] = el.get_text()
         self.longue = DATA_L

         # Forme superlatif /!\ cette forme n'existe pas toujours
         try:
            text = html_parser.find("div", class_="cc wordforms table ajective g-table cform_group superlative")

            infos = text.find_all("div", class_="tr desk")
            for info in infos:
               els = info.find_all("span", class_="transl_form tr_f")
               cas = info.find("div", class_="td transl_form_des")
               if cas:
                  cas = cas.get_text(strip=True)
                  for i in range(len(clean)):
                     cas = cas.replace(clean[i], rep[i])
                  for i,el in enumerate(els):
                     DATA_S[cas][L[i]] = el.get_text()
               else:
                  els = info.find_all("span", class_="transl_form tr_f")
                  cas = info.find("div", class_="td transl_form_des nob")
                  cas = cas.get_text(strip=True)
                  for i in range(len(clean)):
                     cas = cas.replace(clean[i], rep[i])
                  for i,el in enumerate(els):
                     DATA_S[cas][L[i]] = el.get_text()
         except AttributeError as e:
            pass

         # Forme courte /!\ cette forme n'existe pas toujours
         try:
            text = html_parser.find("div", class_="cc wordforms table ajective g-table cform_group sm-table short-forms")

            infos = text.find_all("div", class_="tr desk")
            for info in infos:
               els = info.find_all("span", class_="transl_form tr_f")
               cas = info.find("div", class_="td transl_form_des")
               if cas:
                  cas = cas.get_text(strip=True)
                  for i in range(len(clean)):
                     cas = cas.replace(clean[i], rep[i])
                  for i,el in enumerate(els):
                     DATA_C[cas] = el.get_text()
               else:
                  els = info.find_all("span", class_="transl_form tr_f")
                  cas = info.find("div", class_="td transl_form_des nob")
                  cas = cas.get_text(strip=True)
                  for i in range(len(clean)):
                     cas = cas.replace(clean[i], rep[i])
                  for i,el in enumerate(els):
                     DATA_C[cas] = el.get_text()
         except AttributeError as e:
            pass
         
         # Forme superlatif /!\ cette forme n'existe pas toujours
         sup =""
         try:
            text = html_parser.find("div", class_="cc wordforms table ajective g-table cform_group sm-table comparative")
            sup = text.get_text(strip=True)
         except AttributeError as e:
            pass

         ADJ_DICT = {"longue":DATA_L , "comparatif":DATA_S, "courte":DATA_C, "superlatif":sup}

         return ADJ_DICT
         
   def conjugaison(self, mot:str) -> dict:
      """
      Renvoie les conjugaisons du verbe (mot)
      """
      DATA = {'indicatif':{'présent':[], 'passé':[], 'futur':[]}, 'conditionnel':[], 'impératif':[], 'participes':{'actif':{'présent':"", 'passé':{}}, "passif":{'présent':"", 'passé':""}}, 'gérondif':""}

      clean = ["Я ","Ты ","Он/она/оно ","Мы ","Вы ","Они ","(ты) ","(вы) ",'-','Он/она ']

      url = f"https://www.online-translator.com/conjugaison et déclinaison/{self.langue}/{mot}"
      response = requests.get(url, headers=self.headers)
      if response.status_code == 200:
         data = response.text
         html_parser = BeautifulSoup(data, "html.parser")

         indicatif = html_parser.find_all("span", class_="wfSpan indicative")
         subjonctif = html_parser.find_all("span", class_="wfSpan subjunctive")
         imperatif = html_parser.find_all("span", class_="wfSpan imperative")
         participes = html_parser.find_all("span", class_="wfSpan participations entirely")

         t = ['présent', 'passé', 'futur']
         for i, ind in enumerate(indicatif):
            temps = ind.find("p", class_="phdr").get_text()
            pers = ind.find_all("span", class_="tr_f")
            for per in pers:
               if per.get_text() == '-':
                  DATA['indicatif'][t[i]] = ['-']*6
               else:
                  p = per.get_text()
                  for el in clean:
                     p = p.replace(el,'')
                  DATA['indicatif'][t[i]].append(p)

         for ind in subjonctif:
            pers = ind.find_all("span", class_="tr_f")
            for per in pers:
               p = per.get_text()
               for el in clean:
                  p = p.replace(el,'')
               DATA['conditionnel'].append(p)

         for ind in imperatif:
            pers = ind.find_all("span", class_="tr_f")
            for per in pers:
               if per.get_text() == '-':
                  DATA['impératif'][t[i]] = ['']*2
               else:
                  p = per.get_text()
                  for el in clean:
                     p = p.replace(el,'')
                  DATA['impératif'].append(p)

         for ind in participes:
            pers = ind.find_all("span", class_="tr_f")
            temps = ind.find("p", class_="phdr").get_text()
            voix = ind.find_all("span", class_="tr_d")
            if voix:
               for i in range(len(voix)):
                  if "Действительный залог" in voix[i].get_text():
                     try:
                        DATA['participes']['actif']['présent'] = pers[0].get_text()
                     except AttributeError as e:
                        DATA['participes']['actif']['présent'] = ""
                     
                     try:
                        DATA['participes']['actif']['passé'] = pers[1].get_text()
                     except IndexError as e:
                        DATA['participes']['actif']['passé'] = ""

                  elif "Страдательный залог" in voix[i].get_text():
                     try:
                        DATA['participes']['passif']['présent'] = pers[0].get_text()
                     except AttributeError as e:
                        DATA['participes']['passif']['présent'] = ""
                     try:
                        DATA['participes']['passif']['passé'] = pers[1].get_text()
                     except IndexError as e:
                        DATA['participes']['passif']['passé'] = ""

            # Pour le gérondif
            pers = participes[1].find("span", class_="tr_f")
            if pers.get_text() != "":
               DATA['gérondif'] = pers.get_text()

            return DATA

      else:
         print("Erreur")
         exit(1)

   def declinaison_nom(self, mot:str) -> dict:
      """
      Renvoie la déclinaison du nom commun (mot)
      """
      clean = ["Именительный падеж(Кто? Что?)", "Родительный падеж(Кого? Чего?)", "Дательный падеж(Кому? Чему?)", "Винительный падеж(Кого? Что?)", "Творительный падеж(Кем? Чем?)", "Предложный падеж(О ком? О чем?)"]
      rep = ["Nominatif", "Génitif", "Datif", "Accusatif", "Instrumental", "Locatif"]
      DATA = {'singulier' : {'nominatif':"", 'accusatif':"", 'génitif':"", 'datif':"", "instrumental":"", "locatif":""}, 'pluriel' : {'nominatif':"-", 'accusatif':"-", 'génitif':"-", 'datif':"-", "instrumental":"-", "locatif":"-"}}
      url = f"https://www.online-translator.com/conjugaison et déclinaison/{self.langue}/{mot}"
      response = requests.get(url, headers=self.headers)
      Tempo = []
      if response.status_code == 200:
         data = response.text
         html_parser = BeautifulSoup(data, "html.parser")

         texts = html_parser.find_all("div", class_="tr desk")
         for text in texts:
            cas = text.find("div", class_="td des")
            lignes = text.find_all("span", class_="transl_form tr_f")
            cas = cas.get_text(strip=True)
            for i in range(len(clean)):
               cas = cas.replace(clean[i],rep[i])
            Tempo.append([cas, lignes[0].get_text(strip=True), lignes[1].get_text(strip=True)])
      else:
         print("Erreur, le site est innacessible.")
         exit(1)
      
      # Attribition
      DATA['singulier']['Nominatif'] = Tempo[0][1]
      DATA['pluriel']['Nominatif'] = Tempo[0][2]

      DATA['singulier']['Génitif'] = Tempo[1][1]
      DATA['pluriel']['Génitif'] = Tempo[1][2]

      DATA['singulier']['Accusatif'] = Tempo[3][1]
      DATA['pluriel']['Accusatif'] = Tempo[3][2]

      DATA['singulier']['Datif'] = Tempo[2][1]
      DATA['pluriel']['Datif'] = Tempo[2][2]

      DATA['singulier']['Instrumental'] = Tempo[4][1]
      DATA['pluriel']['Instrumental'] = Tempo[4][2]

      DATA['singulier']['Locatif'] = Tempo[5][1]
      DATA['pluriel']['Locatif'] = Tempo[5][2]

      return DATA
            
   def afficher(self):
      """
      Permet d'afficher sous forme de table les informations (traduction, déclinaison/conjugaison)
      """
      #Pour le mot
      table = PrettyTable()
      # si le mot est un nom
      if self.DATA_M['type'] == "nom":

         if "m" in self.affi:
            table.field_names = [f"{bs}Mot{bf}", f"{bs}Traduction{bf}",f"{bs}genre{bf}",f"{bs}Détails{bf}"]
            table.add_row([self.DATA_M['mot'], self.DATA_M['trad'][0], self.DATA_M['genre'], self.DATA_M['detail']])
            print(f"Information :")
            print(f"{table}\n")

         cond = True
         if "d" in self.affi:
            try:
               table_decl = PrettyTable()
               table_decl.field_names = [f"{bs}Cas{bf}", f"{bs}Singulier{bf}",f"{bs}Pluriel{bf}"]

               rep = ["Nominatif", "Génitif", "Datif", "Accusatif", "Instrumental", "Locatif"]

               for i in range(6):
                  table_decl.add_row([rep[i], self.DECL_N['singulier'][rep[i]], self.DECL_N['pluriel'][rep[i]]])
            except TypeError as e:
               table_decl = ""
               cond = False
         else:
            cond = False

         if cond:
            print(f"Déclinaison :")
            print(table_decl)
            print("\n")

         if "e" in self.affi:
            for i in range(len(self.DATA_M['exemple'])):
               print(f"\033[4mExemple n°{i+1} avec '{self.DATA_M['trad'][i]}'\033[0m : ")
               print(self.DATA_M['exemple'][i].replace(".",".\n").replace(self.DATA_M['mot'],f"\033[3;32m\033[3m{self.DATA_M['mot']}\033[0m").replace(self.DATA_M['trad'][i],f"\033[3;32m\033[3m{self.DATA_M['trad'][i]}\033[0m"))

      # si le mot est un adj
      elif self.DATA_M['type'] == "adjectif":

         if "m" in self.affi:
            table.field_names = [f"{bs}Mot{bf}", f"{bs}Traduction{bf}",f"{bs}Détails{bf}"]
            table.add_row([self.DATA_M['mot'], self.DATA_M['trad'][0], self.DATA_M['detail']])
            print(f"Information :")
            print(f"{table}\n")

         if "d" in self.affi:
            table_decl = PrettyTable()
            table_decl.field_names = [f"{bs}Cas{bf}", f"{bs}Masculin{bf}",f"{bs}Féminin{bf}",f"{bs}Neutre{bf}", f"{bs}Pluriel{bf}"]
            rep = ["Nominatif", "Accusatif In.", "Accusatif An.", "Génitif", "Datif", "Instrumental", "Locatif"]

            # Forme longue
            print("Table forme longue : ")
            for i in range(7):
               table_decl.add_row([rep[i], self.DECL_A['longue'][rep[i]]['Masculin'], self.DECL_A['longue'][rep[i]]['Féminin'], self.DECL_A['longue'][rep[i]]['Neutre'], self.DECL_A['longue'][rep[i]]['Pluriel']])
            print(table_decl)
            print("\n")

            table_decl2 = PrettyTable()
            table_decl2.field_names = [f"{bs}Cas{bf}", f"{bs}Masculin{bf}",f"{bs}Féminin{bf}",f"{bs}Neutre{bf}", f"{bs}Pluriel{bf}"]

            rep = ["Nominatif", "Accusatif In.", "Accusatif An.", "Génitif", "Datif", "Instrumental", "Locatif"]

            print("Table comparatif : ")
            for i in range(7):
               table_decl2.add_row([rep[i], self.DECL_A['comparatif'][rep[i]]['Masculin'], self.DECL_A['comparatif'][rep[i]]['Féminin'], self.DECL_A['comparatif'][rep[i]]['Neutre'], self.DECL_A['comparatif'][rep[i]]['Pluriel']])
            print(table_decl2)
            print("\n")

            print("Table forme courte : ")
            G = ["Masculin","Féminin","Neutre","Pluriel"]
            table_decl3 = PrettyTable()
            table_decl3.field_names = [f"{bs}Genre{bf}", f"{bs}Déclinaison{bf}"]
            for g in G:
               table_decl3.add_row([g,self.DECL_A['courte'][g]])
            print(table_decl3)
            print("\n")

            print("Table superlatif : ")
            table_decl4 = PrettyTable()
            table_decl4.field_names = [f"{bs}Superlatif{bf}"]
            table_decl4.add_row([self.DECL_A['superlatif']])
            print(table_decl4)
            print("\n")
         
         if "e" in self.affi:
            for i in range(len(self.DATA_M['exemple'])):
               print(f"\033[4mExemple n°{i+1} avec '{self.DATA_M['trad'][i]}'\033[0m : ")
               print(self.DATA_M['exemple'][i].replace(".",".\n").replace(self.DATA_M['mot'],f"\033[3;32m\033[3m{self.DATA_M['mot']}\033[0m").replace(self.DATA_M['trad'][i],f"\033[3;32m\033[3m{self.DATA_M['trad'][i]}\033[0m"))

      elif self.DATA_M['type'] == "verbe" and self.langue == "russe":

         if "m" in self.affi:
            table.field_names = [f"{bs}Mot{bf}", f"{bs}Traduction{bf}",f"{bs}Détails{bf}",f"{bs}Perfectif{bf}",f"{bs}Imperfectif{bf}"]

            table.add_row([self.DATA_M['mot'], self.DATA_M['trad'][0], self.DATA_M['detail'], self.DATA_M['aspect']['perfectif'], self.DATA_M['aspect']['imperfectif']])
            print("Information : ")
            print(table)
            print("\n")

         if "d" in self.affi:
            pron = ["Я", "Ты", "Он/Она", "Мы", "Вы", "Они"]

            print("Conjugaison à l'indicatif : ")
            table_conj1 = PrettyTable()
            table_conj1.field_names = [f"{bs}Personne{bf}", f"{bs}Passé{bf}", f"{bs}Présent{bf}",f"{bs}Futur{bf}"]
            for i in range(6):
               table_conj1.add_row([pron[i], self.CONJ['indicatif']['passé'][i], self.CONJ['indicatif']['présent'][i], self.CONJ['indicatif']['futur'][i]])
            print(table_conj1)
            print("\n")

            print("Conjugaison au conditionnel : ")
            table_conj2 = PrettyTable()
            table_conj2.field_names = [f"{bs}Personne{bf}", f"{bs}Conditionnel{bf}"]
            for i in range(6):
               table_conj2.add_row([pron[i], self.CONJ['conditionnel'][i]])
            print(table_conj2)
            print("\n")

            print("Conjugaison, les participes : ")
            table_conj3 = PrettyTable()
            table_conj3.field_names = [f"{bs}Participe{bf}", f"{bs}Présent{bf}", f"{bs}Passé{bf}"]

            table_conj3.add_row([f"{bs}Actif{bf}",self.CONJ['participes']['actif']['présent'],self.CONJ['participes']['actif']['passé']])
            table_conj3.add_row([f"{bs}Passif{bf}",self.CONJ['participes']['passif']['présent'],self.CONJ['participes']['passif']['passé']])
            print(table_conj3)
            print("\n")

            print("Conjugaison à l'impératif : ")
            table_conj4 = PrettyTable()
            table_conj4.field_names = [f"{bs}Pronom{bf}", f"{bs}Impératif{bf}"]

            table_conj4.add_row(["Ты",self.CONJ['impératif'][0]])
            table_conj4.add_row(["Вы",self.CONJ['impératif'][1]])
            print(table_conj4)
            print("\n")

            print("Conjugaison au gérondif : ")
            table_conj5 = PrettyTable()
            table_conj5.field_names = [f"{bs}Gérondif{bf}"]

            table_conj5.add_row([self.CONJ['gérondif']])
            print(table_conj5)
            print("\n")

         if "e" in self.affi:
            for i in range(len(self.DATA_M['exemple'])):
               print(f"\033[4mExemple n°{i+1} avec '{self.DATA_M['trad'][i]}'\033[0m : ")
               print(self.DATA_M['exemple'][i].replace(".",".\n").replace(self.DATA_M['mot'],f"\033[3;32m\033[3m{self.DATA_M['mot']}\033[0m").replace(self.DATA_M['trad'][i],f"\033[3;32m\033[3m{self.DATA_M['trad'][i]}\033[0m"))

      else:
         table.field_names = [f"{bs}Mot{bf}", f"{bs}Traduction{bf}",f"{bs}Détails{bf}",f"{bs}Type{bf}"]

         if len(self.DATA_M['trad']) !=0:
            table.add_row([self.DATA_M['mot'], self.DATA_M['trad'][0], self.DATA_M['detail'], f"\033[91m{self.DATA_M['type']}\033[0m"])
         else:
            table.add_row([self.DATA_M['mot'], self.DATA_M['trad'], self.DATA_M['detail'], f"\033[91m{self.DATA_M['type']}\033[0m"])
         print(f"Information :")
         print(table)
         print("\n")
         if "e" in self.affi:
            for i in range(len(self.DATA_M['exemple'])):
               print(f"\033[4mExemple n°{i+1} avec '{self.DATA_M['trad'][i]}'\033[0m : ")
               print(self.DATA_M['exemple'][i].replace(".",".\n").replace("?","?\n").replace("!","!\n").replace(self.DATA_M['mot'],f"\033[3;32m\033[3m{self.DATA_M['mot']}\033[0m").replace(self.DATA_M['trad'][i],f"\033[3;32m\033[3m{self.DATA_M['trad'][i]}\033[0m"))


if __name__ == "__main__":
   list_langue = ["espagnol","russe",'chinois',"japonais",'allemand','italien','portugais','grecque','hindi','anglais','coréen','turc','arabe']
   cond = True
   try:
      if sys.argv[3]:
         cond = False
         traducteur = traduction(str(sys.argv[2]), user_agent, [str(sys.argv[3])])
         traducteur.trad(str(sys.argv[1]))
         traducteur.afficher()
      else:
         if sys.argv[2] in list_langue:
            cond = False
            traducteur = traduction(str(sys.argv[2]), user_agent, affi=["mde"])
            traducteur.trad(str(sys.argv[1]))
            traducteur.afficher()
         else:
            cond = False
            traducteur = traduction(langue_defaut, user_agent, [str(sys.argv[2])])
            traducteur.trad(str(sys.argv[1]))
            traducteur.afficher()

   except IndexError as e:
      if cond:
         try:
            if not sys.argv[2]:
               traducteur = traduction(langue_defaut, user_agent, ["mde"])
               traducteur.trad(str(sys.argv[1]))
               traducteur.afficher()
            else:
               traducteur = traduction(langue_defaut, user_agent, [sys.argv[2]])
               traducteur.trad(str(sys.argv[1]))
               traducteur.afficher()
         except IndexError as e:
            pass
      pass

      try:
         if sys.argv[2]:
            print("\033[91mx UNE ERREUR EST SURVENUE\033[0m ???")
      except IndexError as e:
         traducteur = traduction(langue_defaut, user_agent, ["mde"])
         traducteur.trad(str(sys.argv[1]))
         traducteur.afficher()

   
