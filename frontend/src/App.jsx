import { useState } from "react";
import html2pdf from "html2pdf.js";

function App() {
  const [grammar, setGrammar] = useState(`Struct  -> struct Nombre { Comps }
Nombre  -> id
Comps   -> Comp Comps'
Comps'  -> ; Comp Comps'
Comps'  -> !
Comp    -> Type id
Type    -> Typep
Type    -> struct id
Type    -> Pointer
Typep   -> int
Typep   -> char
Typep   -> bool
Typep   -> float
Pointer -> * id`);  

  const [input, setInput] = useState("struct id { int id ; struct id id ; * id id }");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch("https://o7h7oxk1w1.execute-api.us-east-1.amazonaws.com/dev/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grammar, input }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert("Error al analizar");
    }
    setLoading(false);
  };

  const handleDownloadPDF = () => {
    const element = document.getElementById("pdf-content");

    // Mostrar temporalmente los elementos solo para PDF
    document.querySelectorAll(".only-pdf").forEach(el => {
      el.style.display = "block";
    });

    html2pdf()
      .set({
        margin: 0.5,
        filename: "ll1-parser.pdf",
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
      })
      .from(element)
      .save()
      .then(() => {
        // Ocultar nuevamente tras generar PDF
        document.querySelectorAll(".only-pdf").forEach(el => {
          el.style.display = "none";
        });
      });
  };

  return (
    <div className="container">
      <style>{`
        .only-pdf {
          display: none;
        }
      `}</style>

      <h1>LL(1) Parser</h1>

      <div style={{ display: "flex", alignItems: "flex-start", gap: "2rem" }}>
        <div style={{ flex: 2 }}>
          <label>Gramática:</label>
          <textarea
            value={grammar}
            onChange={(e) => setGrammar(e.target.value)}
            style={{ height: "300px", width: "100%", fontSize: "16px" }}
          />

          <div style={{ marginTop: "1rem" }}>
            <label>Cadena de entrada:</label>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              style={{ height: "80px", width: "100%", fontSize: "16px" }}
            />
          </div>
        </div>

        <div style={{ flex: 1, fontSize: "16px", lineHeight: "1.6", fontFamily: "Times New Roman, serif" }}>
          <p><strong>Reglas:</strong></p>
          <ul style={{ marginTop: 0, paddingLeft: "1.2rem" }}>
            <li> Usar la siguiente flecha: <code>-&gt;</code> para las derivaciones</li>
            <li> Usa <code>!</code> para representar ε (vacío)</li>
            <li> Cada producción en una línea distinta</li>
            <li> No terminales: deben comenzar con letras mayúsculas (A-Z)</li>
            <li> Terminales: deben comenzar con letras minúsculas (a-z) o ser simbolos</li>
            <li> Sin símbolo <code>|</code>, usa líneas separadas</li>
            <li> En la esquina inferior derecha del recuadro se puede ajustar la altura del recuadro</li>
          </ul>
        </div>
      </div>

      <div style={{ marginTop: "1rem" }}>
        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? "Analizando..." : "Analizar"}
        </button>

        {result && (
          <button onClick={handleDownloadPDF} style={{ marginLeft: "1rem" }}>
            Exportar como PDF
          </button>
        )}
      </div>

      {result && (
        <div id="pdf-content">
          <div className="only-pdf">
            <h2>Gramática utilizada</h2>
            <pre style={{ background: "#f4f4f4", padding: "1rem", fontFamily: "monospace" }}>
              {grammar}
            </pre>

            
          </div>

          <h2>First & Follow</h2>
          <table>
            <thead>
              <tr>
                <th>No Terminal</th>
                <th>FIRST</th>
                <th>FOLLOW</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(result.grammar.first).map((nt) => (
                <tr key={nt}>
                  <td>{nt}</td>
                  <td>{result.grammar.first[nt].join(", ")}</td>
                  <td>{result.grammar.follow[nt]?.join(", ") || ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
          

          <div className="only-pdf">
            <h2>Cadena de entrada</h2>
            <p style={{ fontFamily: "monospace", fontSize: "16px" }}>{input}</p>

          </div>
          
          <h2>Análisis paso a paso</h2>
          <table>
            <thead>
              <tr>
                <th>Pila</th>
                <th>Entrada</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {result.parse_result.steps.map((step, idx) => (
                <tr key={idx}>
                  <td>{step.stack.join(" ")}</td>
                  <td>{step.input.join(" ")}</td>
                  <td>{step.action}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <p className={`result ${result.parse_result.valid ? "valid" : "invalid"}`}>
            Resultado: {result.parse_result.valid ? "Cadena válida ✅" : "Cadena inválida ❌"}
          </p>
        </div>
      )}

      <footer style={{ marginTop: "3rem", textAlign: "center", fontSize: "14px", color: "#555" }}>
        Creado por <strong>Michael Hinojosa</strong> — UTEC 2025
      </footer>
    </div>
  );
}

export default App;
