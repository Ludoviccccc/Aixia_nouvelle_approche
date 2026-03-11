# Contexte pour ma question
Les intructions executables par le simulateur sont de l forme {cycle:(type,addresse)} 
Dans le simulateur, les addresses physiques sont des numéros de 0 à un certain maximum. 

Lorsque les intructions arrivent dans un cache, les deux fonctions suivantes permettent de savoir ou chercher où une information est stockée:
`CacheLevel_index = lambda addr:(addr // self.line_size) % self.num_sets`
`CacheLevel_tag = lambda ddr: addr // (self.line_size * self.num_sets)`

Lorsqu'une instruction doit finit par être recu par le DDR, deux `DDRMemory._set_bank` et `DDRMemory._get_row` permettent de determiner dans quel row et dans quel bank chercher la donnée

ligne 414: self.ddr.request(best_req) --> ligne 468:def request(self, req)

`_get_bank = lambda addr:addr % self.num_banks`
`_get_row = lambda addr:addr//16`

# Ma question
Dans cette phase on s'interesse aux sources d'IF dans la DDR seulement, 
Est-ce que l'on veut, c'est bien cibler des comportements des endroits de la DDR Memory i.e paires (bank,row) ou plutot des comportements démontrés par des addresses physiques? 

Si la réponse est cibler des comportements exhibées par des addresses physiques, alors je peux continuer à exploiter uniquement les programs de la forme {cycle:(type,addresse)}. Et je peux faire comme dans les travaux précedent lorsqu'il s'agit de faire des mutations aléatoires de programmes (séquences d'intructions).

Si la réponse est cibler des comportements exhibées par des paires (bank,row), alors il me faut selectionner des séquences d'instructions appropriées. Car étant donné qu'il n'y a pas de fonction depuis l'espace des paires (bank,row) vers les l'espace des paires (block,set), je ne peux pas envoyer au cache une instruction du genre {cycle:type,(bank,row)}.


#Complement pour ma question
Pour es espaces de parametres et de comportement, et suite à une réunion qu'on avait eu tous ensemble, j'ai choisi de faire comme suit, mais il me manque à préciser ce que sera une addresse avec la réponse à ma question ci-dessus.


## Espace de paramètres
{(RD l), (WR l)}
U (union)
{(RD l, RD l) (WR l, RD l) (RD l, WR l), (WD l, WD l)  }  =  {WR l1, RD l1}2
U
{(RD l, SQ, RD l) (WR l,SQ, RD l) (RD l,SQ, WR l), (WD l, SQ,WD l)} où SQ est une séquence faisant intervenir les autres lignes.

## Espace de comportement

| **Option** | **Description Espace**                                                                                               | **Méthode distance**                                                                                                                                                                             | Diversité                    |
|------------|----------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| A          | {Hit l1, Miss l1}  U  {Hit l1, Miss l1} 2   U ...U  {Hit l1,...,  Miss l1} max(longueur SQ)+2                        | Nombre de coordonées en commun entre deux vecteurs.  Comme les vecteurs ne sont pas tous de meme tailles on pourra prendre des sous-sequences des outcomes avec leur sequences de odes associées | Nombre de vecteurs distincts |
| B          | (avec  M = Nb max instructions) (Nb miss pour instructions numérotées [$$j\cdot step$$,$j\cdot step+step$] pour  j dans [1,M//step]) | Nombre de coordonées en commun entre deux vecteurs Les vecteurs ont tous la meme taille.                                                                                                         | Nombre de vecteurs distincts |

