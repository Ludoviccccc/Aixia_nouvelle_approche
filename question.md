# Contexte pour ma question
Les intructions executables par le simulateur sont de la forme **{cycle:(type,addresse)}**.
Dans le simulateur, les addresses physiques sont des numérotées de 0 à un certain maximum. 

Lorsque les intructions arrivent dans un cache, les deux fonctions suivantes permettent de savoir ou chercher où une information est stockée:

`CacheLevel_index = lambda addr:(addr // self.line_size) % self.num_sets`


`CacheLevel_tag = lambda ddr: addr // (self.line_size * self.num_sets)`


Lorsqu'une instruction est recue par la DDR, deux fonctions `DDRMemory._set_bank` et `DDRMemory._get_row` permettent de determiner dans quel *row* et dans quelle *bank* aller chercher la donnée.

ligne 414: self.ddr.request(best_req) --> ligne 468:def request(self, req)



`_get_bank = lambda addr:addr % self.num_banks`

`_get_row = lambda addr:addr//16`


# Ma question
Dans cette phase on s'interesse aux sources d'IF qui emergent de la DDR seulement.

Voulons-nous: **1. Cibler des comportements démontrés par des addresses physiques** OU **2. Cibler des comportements des endroits de la DDR Memory i.e paires (bank,row)** ? 


Si la réponse est **1.**, alors on pourra continuer à exploiter les séquences d'intructions de la forme **{cycle:(type,addresse)}**. 
Les travaux précedent pour faire des mutations aléatoires des séquences d'intructions pourront servir

Si la réponse **2.**, alors il faudra peut être **repenser la forme des séquences d'instructions**. 
Si on construit des instructions de la forme **{cycle:type,(bank,row)}** pour cibler des endroits de la DDR ? 
--> Etant donné qu'il n'y a pas de fonction qui envoie l'espace des paires (bank,row) de la DDR vers les l'espace des paires (block,set) des caches, on ne peut envoyer au cache une instruction de la forme **{cycle:type,(bank,row)}**. 

Dans l'optique de viser des paires **(bank,row)** dans la DDR, j'ai commencé à exploiter l'application qui mappe l'ensemble des paires **(bank,row)** vers l'ensemble des adresses physiques. Une paire correspond à plusieurs adresses physiques et une addresse physique correspond à une seule paire ... En prenant cette voie, plusieurs options sont possibles pour solliciter ces paires **(row,bank)**.


**Bien entendu, je suis peut être en train de prendre une direction, bizarre, et si l'objectif est 1. alors c'est tant mieux comme les travaux seront plus simple!**


# Complement pour ma question
La suite ci-dessous montre la forme choix intermédiaires pour les espaces de paramètres et de comportements au coeur de la phase d'**activation des mecanismes potentiellement sources d'IF**.



## Espace de paramètres
On souhaite connaitre les comportements relatifs à chaque adresse (ou ligne de memoire) L de la DDR. Pour tous L, on associe un espace de comportement C:


$$C = {\{\mbox{WR } L, \mbox{RD } L\}}^{2}$$

$$\cup \cdots \cup \{(\mbox{RD } L, \mbox{SQ }, \mbox{RD } L), (\mbox{WR } L,\mbox{SQ }, \mbox{RD } L),(\mbox{RD } L,\cdots, \mbox{WR } L), (\mbox{WR } L, \mbox{SQ },\mbox{WR } L)\} $$
où SQ est une séquence qui constituée de plusieurs instructions faisant intervenir les autres lignes.
<br>
<br>
<br>


## Espace de comportement

| **Opt°** | **Espace comport.**                                                                                               | **Méthode distance**                                                                                                                                                                             | Diversité                    |
|------------|----------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| A          | $\{\mbox{Hit } l1, \mbox{Miss } l1\}  \cup  \{\mbox{Hit } l1, \mbox{Miss } l1\} 2   \cup \cdots \cup  {\{\mbox{Hit } l1,...,  \mbox{Miss } l1\}}^{max(longth SQ)+2}$                       | Nb de coord differentes entre deux vect. Les vect. ne sont pas tous de meme tailles. On pourra prendre des sous-sequences d'instr. pour exploiter cette distance | Nb de vecteurs distincts ?|
| B          | (avec  M = Nb max instructions) (Nb miss pour instr. [$j\cdot step$,$j\cdot step+step$] pour  j dans [1,M//step]) | Nb de coord. différentes entre deux vect. Les vect. ont tous la meme taille.                                                                                                         | Nb de vecteurs distincts ?|

