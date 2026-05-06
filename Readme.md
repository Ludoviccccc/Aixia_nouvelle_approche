New approach for interference source identification

* A faire:
Créer historique pour les différents composants de la DDR

Espace de paramètres:
{(RD l), (WR l)}
U (union)
{(RD l, RD l) (WR l, RD l) (RD l, WR l), (WD l, WD l)  }  =  {WR l1, RD l1}2
U
{(RD l, SQ, RD l) (WR l,SQ, RD l) (RD l,SQ, WR l), (WD l, SQ,WD l)} où SQ est une séquence faisant intervenir les autres lignes.



| **Option** | **Description Espace**                                                                                               | **Méthode distance**                                                                                                                                                                             | Diversité                    |
|------------|----------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| 1          | (avec  M = Nb max instructions) (Nb miss pour instructions numérotées [$ j\cdot step $,$j\cdot step+step$] pour  j dans [1,M//step]) | Nombre de coordonées en commun entre deux vecteurs Les vecteurs ont tous la meme taille.                                                                                                         | Nombre de vecteurs distincts |
| 2          | {Hit l1, Miss l1}  U  {Hit l1, Miss l1} 2   U ...U  {Hit l1,...,  Miss l1} max(longueur SQ)+2                        | Nombre de coordonées en commun entre deux vecteurs.  Comme les vecteurs ne sont pas tous de meme tailles on pourra prendre des sous-sequences des outcomes avec leur sequences de odes associées | Nombre de vecteurs distincts |



