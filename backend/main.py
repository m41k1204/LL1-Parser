from parser import analizar_gramatica

if __name__ == "__main__":
    grammar = """
    S -> A B
    A -> a A
    A -> !
    B -> b B
    B -> !
    """

    input_text = "c"

    resultado = analizar_gramatica(grammar, input_text)

    # Imprimir resultado bonito
    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

