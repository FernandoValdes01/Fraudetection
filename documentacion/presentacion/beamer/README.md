# Versión Beamer

Esta es la versión anterior del protocolo principal, escrita en LaTeX con Beamer.

- [PDF compilado](defensa_fraude.pdf).
- [Fuente editable LaTeX](defensa_fraude.tex).

La [versión Canva](../canva/README.md) tiene otro diseño y sus propias copias locales. El PowerPoint automático `defensa_fraude.pptx` está en [contexto](../../contexto/presentaciones_anteriores/defensa_fraude.pptx); no se genera desde esta fuente LaTeX.

## Compilar

Desde la raíz del repositorio, con Docker y la imagen `blang/latex:ubuntu`:

```bash
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work -w /work/documentacion/presentacion/beamer \
  blang/latex:ubuntu \
  latexmk -pdf -interaction=nonstopmode -halt-on-error defensa_fraude.tex
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work -w /work/documentacion/presentacion/beamer \
  blang/latex:ubuntu latexmk -c defensa_fraude.tex
```

Los gráficos se leen desde `resultados/graficos/`. El protocolo y sus cifras se explican en la [exploración](../../contexto/exploracion.md).
