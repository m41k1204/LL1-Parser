import re


def scanner(der: str):
    tokens = []
    i = 0
    while i < len(der):
        c = der[i]

        if c.isspace():
            i += 1
            continue

        if i + 1 < len(der):
            two_char = der[i:i+2]
            if two_char in {'==', '!=', '<=', '>='}:
                tokens.append(two_char)
                i += 2
                continue

        if c == '!':
            tokens.append('!')
            i += 1

        elif c.isalpha():
            start = i
            i += 1
            while i < len(der) and (der[i].isalnum() or der[i] in "_'"):
                i += 1
            tokens.append(der[start:i])

        else:
            tokens.append(c)
            i += 1

    return tokens


def analizar_gramatica(grammar_text: str, input_text: str):
    sent = [line.strip() for line in grammar_text.strip().split('\n') if line.strip() != ""]

    reglas = {}
    for i in range(len(sent)):
        partes = sent[i].split("->", 1)
        izq = partes[0].strip()
        der = scanner(partes[1])

        reglas["regla" + str(i + 1)] = {"Izq": izq, "Der": der}

    start = sent[0].split("->", 1)[0].strip()

    variables = set()
    for regla in reglas.values():
        izq = regla["Izq"]
        if izq != start:
            variables.add(izq)

    for regla in reglas.values():
        for sym in regla["Der"]:
            if sym != "!" and sym[0].isupper() and sym != start:
                variables.add(sym)

    terminales = []
    for regla in reglas.values():
        for sym in regla["Der"]:
            if sym != "!" and sym != start and sym not in variables and sym not in terminales:
                terminales.append(sym)

    grammar = {}
    grammar[start] = {"tipo": "I", "first": [], "follow": ["$"]}
    for v in variables:
        grammar[v] = {"tipo": "V", "first": [], "follow": []}
    for t in terminales:
        grammar[t] = {"tipo": "T", "first": []}
    grammar['!'] = {"tipo": "T", "first": ["!"]}

    ## ---------------------------------- Calcular los FIRST ------------------------------------------

    def nuevos_first(indice, regla, grammar):
        firsts = grammar[regla[indice]]['first']
        nuevos = [i for i in firsts if i != "!"]
        return nuevos

    for i in grammar.keys():
        if grammar[i]['tipo'] == "T":
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
                        l += 1

                    if vacio and "!" not in grammar[i]['first']:
                        grammar[i]['first'].append("!")

    ## ---------------------------------- Calculo de los FOLLOWS ------------------------------------------

    for g in range(len(sent)):
        for i in reglas.keys():
            for j in range(len(reglas[i]['Der']) - 1):
                if grammar[reglas[i]['Der'][j]]['tipo'] == "V" and grammar[reglas[i]['Der'][j + 1]]['tipo'] == "V":
                    hay_vacio = True
                    l = j + 1
                    while hay_vacio and l < len(reglas[i]['Der']):
                        if "!" not in grammar[reglas[i]['Der'][l]]['first']:
                            hay_vacio = False
                        for k in grammar[reglas[i]['Der'][l]]['first']:
                            if k != "!" and k not in grammar[reglas[i]['Der'][j]]['follow']:
                                grammar[reglas[i]['Der'][j]]['follow'].append(k)
                        l += 1

        for i in reglas.keys():
            if grammar[reglas[i]['Der'][-1]]['tipo'] == "V":
                for j in grammar[reglas[i]['Izq']]['follow']:
                    if j not in grammar[reglas[i]['Der'][-1]]['follow']:
                        grammar[reglas[i]['Der'][-1]]['follow'].append(j)

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
                if grammar[reglas[i]['Der'][j]]['tipo'] in ['I', 'V'] and reglas[i]['Der'][j + 1] in terminales:
                    if reglas[i]['Der'][j + 1] not in grammar[reglas[i]['Der'][j]]['follow']:
                        grammar[reglas[i]['Der'][j]]['follow'].append(reglas[i]['Der'][j + 1])

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

    ################# ANÁLISIS ##################

    entrada_tokens = input_text.strip().split()
    cadena = entrada_tokens + ["$"]
    pila = [start]

    steps = []
    cadena_valida = True
    while True:

        if not pila and cadena[0] != "$":
            steps.append({"stack": [], "input": cadena.copy(), "action": "Pila vacía, análisis terminado"})
            cadena_valida = False
            break

        if not pila and cadena and cadena[0] == "$":
            break

        elif pila[-1] == "!":
            steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": "Pop: ε"})
            pila.pop()

        else:
            if cadena[0] not in terminales:
                FIRST_TOP = []
                for f in grammar[pila[-1]]['first']:
                    if f != "!":
                        FIRST_TOP.append(f)                
                FOLLOW_TOP = grammar[pila[-1]]['follow']
                

                if grammar[pila[-1]]["tipo"] == "T":
                    steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": f"Error terminal, EXPLORAR '{cadena[0]}'"})
                    cadena.pop(0)
                    cadena_valida = False

                elif cadena[0] == "$" and grammar[pila[-1]]['tipo'] in ["I", "V"]:
                    if "!" in grammar[pila[-1]]['first']:
                        prod = tabla[pila[-1]][cadena[0]][0]
                        prod_str = f"{prod['Izq']} → {' '.join(prod['Der'])}"
                        steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": f"Regla: {prod_str} Pop: ε (!)"})
                        pila.pop()

                elif "!" in grammar[pila[-1]]['first'] and (cadena[0] in FOLLOW_TOP or cadena[0] == "$"):
                    steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": f"Error en '{pila[-1]}', EXTRAER"})
                    pila.pop()
                    cadena_valida = False

                elif cadena[0] not in FIRST_TOP and cadena[0] not in FOLLOW_TOP and cadena[0] != "$":
                    steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": f"Error en '{pila[-1]}', EXPLORAR"})
                    while cadena and cadena[0] not in FIRST_TOP + FOLLOW_TOP + ["$"]:
                        steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": f"Skip '{cadena[0]}'"})
                        cadena.pop(0)
                    cadena_valida = False

            elif grammar[pila[-1]]['tipo'] in ["I", "V"] and tabla[pila[-1]][cadena[0]]:
                prod = tabla[pila[-1]][cadena[0]][0]
                prod_str = f"{prod['Izq']} → {' '.join(prod['Der'])}"
                steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": f"Regla: {prod_str}"})
                pila.pop()
                if prod['Der'] != ["!"]:
                    for X in reversed(prod['Der']):
                        pila.append(X)

            elif grammar[pila[-1]]['tipo'] == "T" and pila[-1] == cadena[0]:
                steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": f"Match: {cadena[0]}"})
                pila.pop()
                cadena.pop(0)

            else:
                cadena_valida = False
                steps.append({"stack": pila.copy(), "input": cadena.copy(), "action": f"Error en '{pila[-1]}', EXTRAER"})
                pila.pop()

    return {
        "grammar": {
            "start": start,
            "first": {k: v["first"] for k, v in grammar.items() if grammar[k]["tipo"] in ["I", "V"]},
            "follow": {k: v["follow"] for k, v in grammar.items() if grammar[k]["tipo"] in ["I", "V"]}
        },
        "parse_result": {
            "valid": cadena_valida,
            "steps": steps
        }
    }
