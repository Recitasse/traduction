# traduction
## Installation
Vous devrez installer les bibliothèques suivantes pour le bon fonctionnement du programme :

    python3 -m pip install bs4
    python3 -m pip install prettytable
    python3 -m pip install enchant

**/!\** Utilisation des codes ANSI pour l'affichage. 

Introduction du *user agent*. Pour effectuer des requêtes sur le web vous devez renseigner votre user agent. Vous pouvez l'obtenir ici : https://www.whatismybrowser.com/fr/detect/what-is-my-user-agent/.

Dans mon c'est *"Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"*, à vous de le remplacer par le votre.

## Paramétrage
Les seules variables que vous pouvez modifier sont dans l'encadré *Info* au début du code :

    # ------------------ Info ---------------------
    langue_defaut = "russe"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
    # ----------------------------------------------

La langue à traduire est par défaut le russe. Vous pouvez changer celle-ci pour éviter de l'indiquer dans le code.

## Les arguments
Le code prend 3 paramètres maximum :

    python3 traduction.py строить russe med
   
 Où le premier argument est **toujours** le mot à traduire.

Ensuite vous pouvez ou non spécifier la langue à traduire (si vous ne l'avez pas indiquée par défaut).

Le dernier paramètre *med* concerne l'affichage.
*m* est l'affichage du mot (traduction).
*e* est l'affichage des exemples d'utilisations.
*d* est l'affichage des déclinaisons ou conjugaisons.

## Exemple

    python3 traduction.py строить russe med
 
Affichage de tout les éléments de traduction pour строить

    python3 traduction.py строить me
    
Affichage de la traduction et des exemples pour строить avec le russe définie comme langue par défaut

## Informations complémentaires
Le programme ne fonctionne pas en **offline**.
Le programme corrige automatiquement les fautes de frappes.

Vous pouvez traduire d'autre langue également, mais la conjugaison pour les langues latines ne fonctionnent pas.
