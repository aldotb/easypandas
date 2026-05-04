 
from easypandas import *
P=easypandas('easydata.xlsx')
P.head()
P.summary()
P.qty()
P.family('Color')
P.subclases('coLor') # easy pandas help you to automatix find the real field name 
P.family('Sex')
P.family('ItEm')
P.where("Sex=='Male'")
P.where("Sex=='Male'").qty()
P.qty('NaN')
P.qty()
# 103 vs 3 then... delete or delete!!!! bad register whit...
P.cleanNaN()
Pm=P.where("Sex=='Male'")
Pf=P.where("Sex=='Female'")
Pm.qty()
Pf.qty()
Pm.where("Age>18")
Pm.where("Age>18").qty()
Pm.qty()
type(Pmale)

