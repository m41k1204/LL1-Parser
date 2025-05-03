import re
import json

archivo = open("grammar-3.txt","r")
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


archivo = open("grammar-3.txt","r")
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

for i in reglas.keys():
    if grammar[reglas[i]['Der'][-1]]['tipo'] == "V":
        for j in grammar[reglas[i]['Izq']]['follow']: 
            if j not in grammar[reglas[i]['Der'][-1]]["follow"]:  
                grammar[reglas[i]['Der'][-1]]["follow"].append(j)


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

for i in reglas.keys():
    for j in range(len(reglas[i]['Der']) - 1):
        if grammar[reglas[i]['Der'][j]]['tipo'] in ['I','V'] and reglas[i]['Der'][j+1] in terminales:
            if reglas[i]['Der'][j+1] not in grammar[reglas[i]['Der'][j]]['follow']:
                grammar[reglas[i]['Der'][j]]['follow'].append(reglas[i]['Der'][j+1])



## Tabla LL1 

if "!" in terminales:
    terminales.remove("!")

tabla = {}
for i in start + variables:
    tabla[i] = {}
    for t in terminales + ["$"]:
        tabla[i][t] = [] 

for regla in reglas.values():
    izq = regla['Izq']
    der = regla['Der']

    first_der = set()
    puede_vaciarse = True
    for i in der:
        for f in grammar[i]['first']:
            if f != "!":
                first_der.add(f)
        if "!" not in grammar[i]['first']:
            puede_vaciarse = False
            break

    for i in first_der:
        tabla[izq][i].append(regla)

    if puede_vaciarse:
        for i in grammar[izq]['follow']:
            tabla[izq][i].append(regla)



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


###########
code = open("input-3.txt","r")
sent = code.readlines()

cadena = sent[0]+"$"
pila = start

##################
print("\n")
print("\n")
print("ANALISIS")

cadena_valida = True
while True:
    pila_str    = ' '.join(pila)
    entrada_str = ''.join(cadena)

    if len(cadena) == 1 and not pila:
        break

    if pila and pila[-1] == "!":
        print(f"{pila_str:<30} {entrada_str:<30} Pop: ε")
        pila.pop()
        
    else:
        if cadena[0] not in terminales:
            cadena_valida = False

            FIRST_TOP  = set(grammar[pila[-1]]["first"]) - {"!"}
            FOLLOW_TOP = set(grammar[pila[-1]].get("follow", []))

            #EXTRAER
            if "!" in grammar[pila[-1]]["first"] and (cadena[0] in FOLLOW_TOP or cadena[0] == "$"):
                print(f"{pila_str:<30} {entrada_str:<30} Error en '{pila[-1]}', EXTRAER")
                pila.pop()
                

            #EXTRAER
            elif cadena[0] in FIRST_TOP:
                print(f"{pila_str:<30} {entrada_str:<30} Error en '{pila[-1]}', EXTRAER")
                pila.pop()
                
            
            #EXPLORAR
            elif cadena[0] not in FIRST_TOP and cadena[0] not in FOLLOW_TOP and cadena[0] != "$":
                print(f"{pila_str:<30} {entrada_str:<30} Error en '{pila[-1]}', EXPLORAR")
                while cadena and cadena[0] not in FIRST_TOP and cadena[0] not in FOLLOW_TOP and cadena[0] != "$":
                    print(f"{'':30} {'':30} EXPLORAR '{cadena[0]}'")
                    cadena = cadena[1:]
                
        elif grammar[pila[-1]]["tipo"] in ["I","V"] and tabla[pila[-1]][cadena[0]]:
            prod = tabla[pila[-1]][cadena[0]][0]
            prod_str = f"{prod['Izq']} → {' '.join(prod['Der'])}"
            print(f"{pila_str:<30} {entrada_str:<30} Regla: {prod_str}")
            pila.pop()
            if prod['Der'] != ["!"]:
                for X in reversed(prod['Der']):
                    pila.append(X)

        elif grammar[pila[-1]]["tipo"] == "T" and pila[-1] == cadena[0]:
            print(f"{pila_str:<30} {entrada_str:<30} Match: {cadena[0]}")
            pila.pop()
            cadena = cadena[1:]

        #EXTRAER
        else: 
            cadena_valida = False
            print(f"{pila_str:<30} {entrada_str:<30} Error en '{pila[-1]}', EXTRAER")
            pila.pop()

if cadena_valida:
    print("CADENA VALIDA")
else:
    print("CADENA INVALIDA")