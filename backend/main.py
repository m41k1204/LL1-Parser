from parser import analizar_gramatica

if __name__ == "__main__":
    grammar = """
    S   -> if ( E ) S S'
    S'  -> else S
    S'  -> !
    S   -> stmt
    E   -> id == id
    """

    input_text = "if ( id == id ) stmt else stmt"

    resultado = analizar_gramatica(grammar, input_text)

    # Imprimir resultado bonito
    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

