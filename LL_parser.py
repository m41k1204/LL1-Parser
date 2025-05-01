import re
import json

archivo = open("grammar.txt","r")
sent = archivo.readlines()

print("Gramatica: ")
for i in sent:
    print(i)
print("\n")

variables = []
terminales = []
start = [sent[0][0]]

for i in range(len(sent)):
    sent[i] = re.sub('[^\\w!]', '', sent[i])
    sent[i] = re.sub(r'\s+', '', sent[i])

print("Gramatica cambiada: ")
for i in sent:
    print(i)
print("\n")


for i in sent:
    for j in i:
        if j==j.upper() and j != "!":
            if not(j in variables) and not(j in start):
                variables.append(j)
        else:
            if not(j in terminales):
                terminales.append(j)

#gramatica
grammar = {}

for i in start:
    grammar[i]={"tipo":"I","first":[],"follow":["$"]}

for j in terminales:
    grammar[j]={"tipo":"T","first":[]}

for j in variables:
    grammar[j]={"tipo":"V","first":[],"follow":[]}


archivo = open("grammar.txt","r")
sent = archivo.readlines()
reglas ={}


for i in range(len(sent)):
    reglas['regla'+str(i+1)] = {}

j = 0

for i in reglas.keys():
    reglas[i]['Izq'] = sent[j][0]
    j+=1

for i in range(len(sent)):
    sent[i]= sent[i][2:]

j=0

for i in reglas.keys():
    reglas[i]['Der'] = []
    for k in sent[j]:
        if k in grammar.keys():
            reglas[i]['Der'].append(k)
    j+=1

## ---------------------------------- Calcular los FIRST ------------------------------------------

def imprimir_tabla():
    print("TABLA")
    print("\n")
    print(f"{'Símbolo':<10} {'Tipo':<8} {'FIRST':<20} {'FOLLOW':<20}")
    print("-" * 60)

    for simbolo, datos in grammar.items():
        tipo = datos['tipo']
        first = ", ".join(datos.get('first', []))
        follow = ", ".join(datos.get('follow', [])) if 'follow' in datos else "-"
        print(f"{simbolo:<10} {tipo:<8} {first:<20} {follow:<20}")


def nuevos_first(indice, regla, grammar):
    firsts = grammar[regla[indice]]['first']
    nuevos = []
    for i in firsts:
        if i != "!":
            nuevos.append(i)
    return nuevos


for i in grammar.keys():
    if grammar[i]['tipo']=="T":
        grammar[i]['first'].append(i)

for g in range(len(sent)):
    for i in grammar.keys():
        for k in reglas.keys():
            if reglas[k]['Izq'] == i:
                regla = reglas[k]['Der']
                l = 0
                vacio = True
                
                while l < len(regla):
                    nuevos = nuevos_first(l, regla, grammar)
                    grammar[i]['first'] = list(set(grammar[i]['first']) | set(nuevos))

                    if "!" not in grammar[regla[l]]['first']:
                        vacio = False
                        break
                    l+=1

                if vacio and "!" not in grammar[i]['first']:
                    grammar[i]['first'].append("!")

# imprimir_tabla()

## ---------------------------------- Calculo de los FOLLOWS ------------------------------------------


for i in reglas.keys():
    for j in range(len(reglas[i]['Der'])-1):
        if grammar[reglas[i]['Der'][j]]["tipo"]=="V" and grammar[reglas[i]['Der'][j+1]]["tipo"]=="V":
            hay_vacio = True
            l = j+1
            while hay_vacio and l < len(reglas[i]['Der']):
                if "!" not in grammar[reglas[i]['Der'][l]]["first"]:
                    hay_vacio = False
                for k in grammar[reglas[i]['Der'][l]]["first"]:
                    if k != "!":
                        if k not in grammar[reglas[i]['Der'][j]]["follow"]: 
                            grammar[reglas[i]['Der'][j]]["follow"].append(k)
                l+=1    

# imprimir_tabla()  
# print("Grammar")
# print(grammar)
# print("\n")
for i in reglas.keys():
    if grammar[reglas[i]['Der'][-1]]['tipo'] == "V":
        for j in grammar[reglas[i]['Izq']]['follow']: 
            if j not in grammar[reglas[i]['Der'][-1]]["follow"]:  
                grammar[reglas[i]['Der'][-1]]["follow"].append(j)

# imprimir_tabla()
# print("Grammar")
# print(grammar)


for i in reglas.keys():
    for j in range(len(reglas[i]['Der'])):
        if grammar[reglas[i]['Der'][j]]['tipo'] == "V": 
            puede_vaciarse = True
            for k in range(j + 1, len(reglas[i]['Der'])):
                if "!" not in grammar[reglas[i]['Der'][k]]['first']:
                    puede_vaciarse = False
                    break

                if puede_vaciarse:
                    for l in grammar[reglas[i]['Izq']]['follow']:
                        if l not in grammar[reglas[i]['Der'][j]]['follow']:
                            grammar[reglas[i]['Der'][j]]['follow'].append(l)


## Tabla LL1 

tabla = {}

for i in start + variables:
    tabla[i]={}
    for j in terminales:
        tabla[i][j]=[]
    tabla[i]["$"]=[]

for i in reglas.keys():
    for j in  grammar[reglas[i]['Der'][0]]['first']:
        tabla[reglas[i]['Izq'][0]][j].append(reglas[i])


print("\n")
print("REGLAS")
print(reglas)
print("\n")


#################


imprimir_tabla()

##################
print("\n")
print("\n")
print("MATRIZ")

terminales.append("$")
print(f"{'':20}", end="")
for t in terminales:
    print(f"{t:<20}", end="")
print()

print("-" * (12 + 20 * len(terminales)))
for no_terminal, reglas in tabla.items():
    print(f"{no_terminal:20}", end="")
    for t in terminales:
        producciones = reglas[t]
        if producciones:
            produccion_strs = ["{} → {}".format(p["Izq"], " ".join(p["Der"])) for p in producciones]
            print(f"{' / '.join(produccion_strs):<20}", end="")
        else:
            print(f"{'-':<20}", end="")
    print()


# ###########
# code = open("input.txt","r")
# sent = code.readlines()

# cadena = sent[0]+"$"
# pila = start

# ##################
# print("\n")
# print("\n")
# print("ANALISIS")

# while True:
#     pila_str = ' '.join(pila)
#     entrada_str = ''.join(cadena)
#     if (len(cadena)==1) and (len(pila)==0):
#         print("CADENA VALIDA")
#         break
#     if (grammar[pila[-1]]["tipo"] in ["I","V"]) and (len(tabla[pila[-1]][cadena[0]])>=1):
#         produccion = tabla[pila[-1]][cadena[0]][0]
#         produccion_str = f"{produccion['Izq']} → {' '.join(produccion['Der'])}"
#         print(f"{pila_str:<30} {entrada_str:<30} {'Regla: ' + produccion_str}")
#         a = pila[-1]
#         pila.pop()
#         pila+=tabla[a][cadena[0]][0]['Der'][::-1]
#     elif (grammar[pila[-1]]["tipo"]=="T") and pila[-1]==cadena[0]:
#         print(f"{pila_str:<30} {entrada_str:<30} {'Match: ' + cadena[0]}")
#         pila.pop()
#         cadena = cadena[1:] 
#     else:
#         print("Cadena no valida")
#         break