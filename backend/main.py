from parser import analizar_gramatica

if __name__ == "__main__":
    grammar = """
    S -> a A
    A -> b
    A -> !
    """

    input_text = "a b c"

    resultado = analizar_gramatica(grammar, input_text)

    # Imprimir resultado bonito
    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

