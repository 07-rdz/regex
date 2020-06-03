import re
import sqlite3
from fractions import Fraction
import matplotlib.pyplot as plt
#Подключение к БД
conn = sqlite3.connect('tab2.sqlite')
cursor = conn.cursor()

#Регулярным выражением разбираем строку на коэффициенты и элементы
print("Введите реакцию: ",end='')
eq=input().replace(" ","").split('=')
ls=eq[0]
rs=eq[1]
pattern=r"([\d\.?/\d]+)?(\w+(\(\w\))?)"
ls_matches=re.findall(pattern,ls)
rs_matches=re.findall(pattern,rs)
print("Совпадения в левой части",ls_matches)
print("Совпадения в правой части",rs_matches)

#Получаем коэффициенты при элементах и сами элементы в виде списка
l_k=[]
l_el=[]
for i in ls_matches:
    l_k.append(list(i)[0])
    l_el.append(list(i)[1])
r_k=[]
r_el=[]
for i in rs_matches:
    r_k.append(list(i)[0])
    r_el.append(list(i)[1])

#Замена пустых значений коэффициентов и преобразование из строки в флоат для расчета
def koeff(spisok_koeff):
    result = []
    for n, i in enumerate(spisok_koeff):
        if i == '':
            spisok_koeff[n] = str(1)
    for i in spisok_koeff:
        result.append(float(Fraction(i)))
    return result
ll_k = koeff(l_k)
rr_k = koeff(r_k)

#Получаем значения энтальпий и энтропий для каждого елемента
def zapros_H(spisok_elementov):
    result = []
    result2 = []
    for i in spisok_elementov:
        cursor.execute("SELECT H_298_kJ_mol FROM chem WHERE Formula= :lim",{"lim":i})
        result.append(cursor.fetchall())
    for i in result:
        for x in i:
            result2.append(list(x)[0])
    return result2

def zapros_S(spisok_elementov):
    result = []
    result2 = []
    for i in spisok_elementov:
        cursor.execute("SELECT S_298_J_mol_K FROM chem WHERE Formula= :lim",{"lim":i})
        result.append(cursor.fetchall())
    for i in result:
        for x in i:
            result2.append(list(x)[0])
    return result2

l_h = zapros_H(l_el)
l_s = zapros_S(l_el)
r_h = zapros_H(r_el)
r_s = zapros_S(r_el)

print("Энтальпия слева", l_h)
print("Энтропия слева", l_s)
print("Энталипия справа", r_h)
print("Энтропия справа", r_s)
print (" Левая часть",ll_k,l_el)
print (" Правая часть",rr_k,r_el)


#Рассчитываем общую энтальпию и энтропию реакции
tot_h=sum([x * y for x, y in zip(r_h, rr_k)])-sum([x * y for x, y in zip(l_h, ll_k)])
tot_s=sum([x * y for x, y in zip(r_s, rr_k)])-sum([x * y for x, y in zip(l_s, ll_k)])
G=[]
for i in range(273,1574,100):
    G.append(((tot_h*1000)-((tot_s*i)))/1000)
print (tot_h,tot_s)
print(G)
t_o=((tot_h*1000)/(tot_s))
plt.plot(range(273,1574,100),G)
plt.xlabel('Temperature,[K]')
plt.ylabel('Gibbs energy, [kJ]')
plt.title('Gibbs energy for reaction:\n {}=>{} \n G={},kJ - {},J/K * T,K | Reaction starts after {},K'.format(ls,rs,round(tot_h,2),round(tot_s,2),round(t_o,2)))        
plt.grid(True)
plt.show()

conn.close()
