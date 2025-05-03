import re
import json


def tokenizar(rhs: str):
    tokens = []
    i = 0
    while i < len(rhs):
        c = rhs[i]
        if c.isspace():
            i += 1
        elif c == '!':
            tokens.append('!')
            i += 1
        elif c.isalpha():
            start = i
            i += 1
            while i < len(rhs) and (rhs[i].isalnum() or rhs[i] in "_'"):
                i += 1
            tokens.append(rhs[start:i])
        else:
            tokens.append(c)
            i += 1
    return tokens


archivo = open("grammar-5.txt", "r")
sent = []
for linea in archivo:
    linea = linea.strip()
    if linea != "":
        sent.append(linea)
archivo.close()

print("Gramática original:")
for prod in sent:
    print(" ", prod)
print()

reglas = {}

for i in range(len(sent)):
    partes = sent[i].split("->", 1)
    print("partes: ", partes)
    lhs = partes[0].strip()
    rhs = partes[1]

    der = tokenizar(rhs)

    reglas["regla" + str(i+1)] = {"Izq": lhs, "Der": der}


start = sent[0].split("->",1)[0].strip()
start_list = [ start ]

variables = set()
for regla in reglas.values():
    lhs = regla["Izq"]
    if lhs != start:
        variables.add(lhs)

for regla in reglas.values():
    for sym in regla["Der"]:
        if sym != "!" and sym[0].isupper() and sym != start :
            variables.add(sym)

terminales = []
for regla in reglas.values():
    for sym in regla["Der"]:
        if sym != "!" and sym != start and sym not in variables and sym not in terminales:
            terminales.append(sym)


print("No terminales:", variables)
print("Terminales:", terminales)
print("Símbolo inicial:", start, "\n")

grammar = {}
grammar[start] = {"tipo":"I", "first":[],"follow":["$"]}
for v in variables:
    grammar[v] = {"tipo":"V", "first":[],"follow":[]}
for t in terminales:
    grammar[t] = {"tipo":"T", "first":[]}    
grammar['!'] = {"tipo":"T", "first":["!"]}      


## ---------------------------------- Calcular los FIRST ------------------------------------------

def imprimir_tabla():
    print("TABLA")
    print("\n")
    print(f"{'Símbolo':<10} {'Tipo':<8} {'FIRST':<40} {'FOLLOW':<20}")
    print("-" * 80)

    for simbolo, datos in grammar.items():
        tipo = datos['tipo']
        first = ", ".join(datos.get('first', []))
        follow = ", ".join(datos.get('follow', [])) if 'follow' in datos else "-"
        print(f"{simbolo:<10} {tipo:<8} {first:<40} {follow:<20}")


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

# el for g es necesario porque hay firsts que requieren de otros firsts 
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
# el for g es necesario porque hay follows que requieren de otros follows, entonces no basta con una sola iteracion
# y a lo mucho habra len(sent) iteraciones ya que esa es la cantidad de relaciones que puede haber
for g in range(len(sent)):
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

    # follow cuando hay S -> a A b, es decir cuando hay un terminal despues de un no terminal
    for i in reglas.keys():
        for j in range(len(reglas[i]['Der']) - 1):
            if grammar[reglas[i]['Der'][j]]['tipo'] in ['I','V'] and reglas[i]['Der'][j+1] in terminales:
                if reglas[i]['Der'][j+1] not in grammar[reglas[i]['Der'][j]]['follow']:
                    grammar[reglas[i]['Der'][j]]['follow'].append(reglas[i]['Der'][j+1])


## Tabla LL1 

if "!" in terminales:
    terminales.remove("!")

tabla = {}
for i in [start] + list(variables):
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



with open("input-5.txt") as f:              
    line = f.readline().strip()           
entrada_tokens = line.split()             
cadena = entrada_tokens + ["$"]           
pila = [start]                            

print("\nANÁLISIS\n")

cadena_valida = True
while True:
    pila_str    = ' '.join(pila)
    entrada_str = ' '.join(cadena)       
    
    if not pila and cadena and cadena[0] == "$":
        break

    if pila[-1] == "!":
        print(f"{pila_str:<30}{entrada_str:<60}Pop: ε")
        pila.pop()

    else:
        if cadena[0] not in terminales:
            FIRST_TOP = []
            for f in grammar[pila[-1]]['first']:
                if f != "!":
                    FIRST_TOP.append(f)
            FOLLOW_TOP = grammar[pila[-1]]['follow']

            cadena_valida = False

            #EXPLORAR
            if grammar[pila[-1]]["tipo"] == "T":
                print(f"{pila_str:<30}{entrada_str:<60}Error terminal, EXPLORAR '{cadena[0]}'")
                cadena.pop(0)
            
            elif cadena[0] == "$" and grammar[pila[-1]]["tipo"] in ["I","V"]:
                print(f"{pila_str:<30}{entrada_str:<60}Pop: ε (EOF)")  
                pila.pop()                                            

            #EXTRAER
            elif "!" in grammar[pila[-1]]['first'] and (cadena[0] in FOLLOW_TOP or cadena[0] == "$"):
                print(f"{pila_str:<30}{entrada_str:<60}Error en '{pila[-1]}', EXTRAER")
                pila.pop()
                
            #EXPLORAR
            elif cadena[0] not in FIRST_TOP and cadena[0] not in FOLLOW_TOP and cadena[0] != "$":
                print(f"{pila_str:<30}{entrada_str:<60}Error en '{pila[-1]}', EXPLORAR")
                while cadena and cadena[0] not in FIRST_TOP + FOLLOW_TOP + ["$"]:
                    print(f"{'':60}Skip '{cadena[0]}'")
                    cadena.pop(0)

        elif grammar[pila[-1]]["tipo"] in ["I","V"] and tabla[pila[-1]][cadena[0]]:
            prod = tabla[pila[-1]][cadena[0]][0]
            prod_str = f"{prod['Izq']} → {' '.join(prod['Der'])}"
            print(f"{pila_str:<30} {entrada_str:<60} Regla: {prod_str}")
            pila.pop()
            if prod['Der'] != ["!"]:
                for X in reversed(prod['Der']):
                    pila.append(X)

        elif grammar[pila[-1]]["tipo"] == "T" and pila[-1] == cadena[0]:
            print(f"{pila_str:<30}{entrada_str:<60}Match: {cadena[0]}")
            pila.pop()
            cadena.pop(0)

        #EXTRAER
        else:
            cadena_valida = False
            print(f"{pila_str:<30}{entrada_str:<60}Error en '{pila[-1]}', EXTRAER")
            pila.pop()


if cadena_valida:
    print("CADENA VALIDA")
else:
    print("CADENA INVALIDA")
