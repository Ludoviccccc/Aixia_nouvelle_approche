New approach for interference source identification.
The goal is to collect a diversity of behaviors when programs are running in a single core of the architecture.
run `python3 main_option1.py` to run imgep
run `python3 analyze.py` to see analysis plots



## Approach Option1
**Parameter space**
{(RD l), (WR l)}
U (union)
{(RD l, RD l) (WR l, RD l) (RD l, WR l), (WD l, WD l)  }  =  {WR l1, RD l1}2
U
{(RD l, SQ, RD l) (WR l,SQ, RD l) (RD l,SQ, WR l), (WD l, SQ,WD l)} où SQ est une séquence faisant intervenir les autres lignes.
* **Observation space**: periodical data (hit/miss) (i.e every P instruction of a program)
**On going**:
* Trying to identify clusters with HDSCBAN in `analyze.py`--> clusters do not allow a good segmentatino of mechanisms (i.e hit/miss data)
* Trying to fit a simple vae model on imgep data cloud to then identify clusters.
* Will try to change the mutator operator for less bias in mutation. Produce parameter sequences consist of too many instructions.--> An llm model could satisfy these needs.

## Approach Option2 
* **Observation spacce**:log description constitute observation points for each experiment
* same parameter space.
* An llm-encoder encodes logs in a long-dimension-vector space.
**On going**:
* Currently vide coding a function that generates goal. Question: What knowledge will be used to build this space.





| **Option** | **Description Espace**                                                                                               | **Méthode distance**                                                                                                                                                                             | Diversité                    |
|------------|----------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| 1          | (with  M = Nb max instructions) (Nb miss for each instruction [j $\times$ step ,j $\times$ step+step] for  j in [1,M//step]) | L2 distance                                                                                                         | Nombre de vecteurs distincts |
| 2          | Log description of the execution                        | distance between log embeddings | some suited distance like euclidian or cosinus |



