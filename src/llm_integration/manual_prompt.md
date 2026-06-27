Manual Prompt für LLM-Optimization
================

Zweck
-----
Diese Datei beschreibt einen manuellen Prompt, der verwendet wurde, wenn die Datei `production.log` zusammen mit einem LLM (z. B. OpenAI) geschickt wurde, um Verbesserungsvorschläge für die Produktionslinie zu erhalten.

Wichtiger Hinweis: Die hier beschriebene Vorgehensweise ist experimentell und wurde nur manuell getestet. Die LLM-Integration im Projekt ist eine Beispielimplementierung.

Vorbereitung
-----------
1. Erzeuge / sammle die `production.log` aus dem Projektstamm (aktueller Log-Stand der Simulation).
2. Optional: Kürze die Log-Datei, falls sie sehr groß ist (z. B. nur die letzten N Zeilen oder die letzten X Minuten).
3. Ergänze die Frage/Anweisung an das LLM mit Kontext (z. B. Ziel-KPIs, Beschränkungen).

Beispiel-Prompt (auf Englisch, kann auch auf Deutsch verwendet werden)
---------------------------------------------------------------------
You are an expert production systems engineer and simulation analyst. I will provide you with a simulation log file (production.log) from a simple production line. Analyze the log and provide concrete, prioritized improvement suggestions for the production line configuration and control parameters.

Please provide your answer in five sections:

1) Short summary (2-4 sentences) — main issues you detect.
2) Findings — list of observed problems, with evidence (log timestamps / lines / metrics).
3) Suggested parameter changes (prioritized) — for example: change SIMULATION_SPEED, adjust BUFFER1_CAPACITY, modify machine failure / repair thresholds. For each suggestion include:
   - exact parameter name and suggested value
   - why this helps (1-2 sentences)
   - expected effect on KPIs (throughput, cycle time, utilization)
4) Suggested experiments to validate changes — step-by-step simulation runs to test the suggestion (e.g., "run 1000 cycles with BUFFER1_CAPACITY=80 and compare throughput").
5) Potential risks and caveats — what to watch out for and what additional data would be helpful.

When you refer to log evidence, quote short log snippets and line numbers or timestamps. If you cannot find clear evidence for a recommendation, mark it as speculative.

Appendix: paste the relevant parts of the log below (or attach the full `production.log`).

Beispielaugabe (kurz)
---------------
Summary:
- Buffer B1 frequently blocks machines A and C (evidence: repeated "buffer full" messages at timestamps ...).
Suggested change:
- BUFFER1_CAPACITY=80 (was 50) — increases buffer capacity to reduce blocking; expected increase in throughput of ~5-12% in simulation.

Wie die Antwort nutzen
----------------------
- Implementiere eine Änderung jeweils einzeln, führe definierte Simulationsexperimente durch und vergleiche Metriken (Throughput, mittlere Durchlaufzeit, Maschinen-Auslastung).
- Nutze die Vorschläge als Hypothesen; validiere sie mit echten Simulationläufen.
