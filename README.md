# NeuroEsfera BCI

Software experimental para adquisicion de senales EEG en tiempo real usando el casco Unicorn Hybrid Black, Python, Pygame y LSL.

## Descripcion

Este proyecto implementa una primera version de un sistema BCI orientado a la adquisicion de senales EEG en tiempo real. El software permite ejecutar experimentos de imaginacion motora, presentar estimulos visuales y auditivos, y almacenar senales EEG junto con marcadores y trials para su posterior analisis.

## Funcionalidades actuales

- Menu principal para navegacion del software
- Modulo de Motor Imagery
- Seleccion del numero de trials
- Presentacion de estimulos visuales y auditivos
- Envio de marcadores LSL
- Captura de senales EEG desde Unicorn Hybrid Black por LSL
- Almacenamiento de datos en XDF via LabRecorder cuando esta disponible
- Respaldo automatico a CSV etiquetado si XDF no esta disponible
- Resumen de sesion con archivo generado y electrodos detectados

## Tecnologias usadas

- Python 3.12
- Pygame
- pylsl
- Unicorn LSL

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecucion

Para correr la aplicacion:

```bash
python main.py
```

Para listar streams LSL disponibles:

```bash
python tests/test_lsl.py
```

## Estructura del proyecto

```text
BCI/
|-- core/
|-- eeg/
|-- experiments/
|-- gui/
|-- services/
|-- tests/
|-- stimuli/
|-- dataset/
|-- docs/
|-- main.py
`-- requirements.txt
```

## Documentacion tecnica

- Arquitectura del proyecto: `docs/ARCHITECTURE.md`

## Utilidades de pruebas

- `tests/test_lsl.py`: lista los streams LSL visibles
- `tests/explore_dataset.py`: resume y explora los archivos generados en `dataset/`
- `notebooks/dataset_explorer.ipynb`: explora la ultima sesion, markers y comparacion izquierda vs derecha

## Exploracion de dataset

Si quieres explorar una sesion guardada:

```bash
python tests/explore_dataset.py
```

Si prefieres explorarla visualmente en Jupyter:

```bash
jupyter notebook notebooks/dataset_explorer.ipynb
```

## Notas del repositorio

- `dataset/` esta ignorado en git y no se sube al repositorio
- Los archivos XDF y summaries se generan localmente durante las sesiones
