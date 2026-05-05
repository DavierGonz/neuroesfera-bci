# NeuroEsfera BCI

Software experimental para adquisicion de senales EEG en tiempo real usando el casco Unicorn Hybrid Black, Python, PsychoPy y LSL.

## Descripcion

Este proyecto implementa una primera version de un sistema BCI orientado a la adquisicion de senales EEG en tiempo real. El software permite ejecutar experimentos de imaginacion motora, presentar estimulos visuales y auditivos con PsychoPy, y almacenar senales EEG junto con marcadores y trials para su posterior analisis.

## Funcionalidades actuales

- Menu principal para navegacion del software
- Seleccion de objetivo experimental: Arm vs Leg o Left vs Right
- Menu de experimentos: Experimento 1, Experimento 2, Experimento 3 y Experimento 4
- 10 trials por clase fijos para todos los experimentos
- Seleccion de genero para videos de Motor Observation
- Numeracion automatica de sesion segun la carpeta del sujeto
- Presentacion de estimulos visuales y auditivos
- Envio de marcadores LSL
- Captura de senales EEG desde Unicorn Hybrid Black por LSL
- Almacenamiento de datos en XDF via LabRecorder
- Resumen de sesion en pantalla con archivo generado y electrodos detectados

## Mapeo de canales EEG

Cuando el stream LSL/XDF no expone labels reales de canal, el proyecto usa este
mapeo configurado para los 8 canales EEG:

- Canal 1 -> Fz
- Canal 2 -> C3
- Canal 3 -> Cz
- Canal 4 -> C4
- Canal 5 -> Pz
- Canal 6 -> PO7
- Canal 7 -> Oz
- Canal 8 -> PO8

## Tecnologias usadas

- Python 3.10 recomendado para la app con PsychoPy
- PsychoPy
- pylsl
- Unicorn LSL

## Protocolos

El flujo actual permite escoger primero el objetivo de clasificacion:

- `Arm vs Leg`
- `Left vs Right`

Luego se escoge el experimento:

- `Experimento 1`: Motor Imagery
- `Experimento 2`: Action Words
- `Experimento 3`: Motor Observation
- `Experimento 4`: MI + AW + MO

Los trials usan una secuencia base de `3 s` de pantalla negra, `1.5 s` de cue
con beep, `5 s` de cruz central y `1.5 s` de pantalla negra entre trials.

## Instalacion

PsychoPy funciona mejor en un entorno de `Python 3.10`. La documentacion oficial
de PsychoPy recomienda `3.10` para instalaciones con `pip`, porque versiones mas
nuevas pueden no tener ruedas compatibles para todas sus dependencias.

```bash
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecucion

Para correr la aplicacion:

```bash
.\.venv\Scripts\python.exe main.py
```

Para revisar los trials sin casco, sin LabRecorder y sin generar XDF:

```bash
.\.venv\Scripts\python.exe main.py --preview
```

Para hacer una prueba rapida con menos trials por clase:

```bash
.\.venv\Scripts\python.exe main.py --preview --preview-trials-per-class 1
```

Para listar streams LSL disponibles:

```bash
.\.venv\Scripts\python.exe tests/test_lsl.py
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
|   `-- motor_observation/
|       |-- arm_vs_leg/
|       |   |-- hombre/
|       |   `-- mujer/
|       `-- left_vs_right/
|-- dataset/
|-- docs/
|   `-- source_materials/
|-- main.py
`-- requirements.txt
```

## Documentacion tecnica

- Arquitectura del proyecto: `docs/ARCHITECTURE.md`
- Flujo de trabajo del software: `docs/WORKFLOW.md`
- Manual de usuario: `docs/MANUAL_USUARIO.md`

## Notas de interfaz

- La app corre con `PsychoPy`
- `core/app_controller.py` contiene el flujo activo de pantallas
- `gui/ui_theme.py` conserva la paleta y constantes visuales compartidas

## Utilidades de pruebas

- `tests/test_lsl.py`: lista los streams LSL visibles
- `tests/verify_xdf_timing.py`: verifica los tiempos reales de markers en un XDF
- `notebooks/dataset_explorer.ipynb`: explora la ultima sesion, markers y comparacion izquierda vs derecha

## Exploracion de dataset

Si quieres explorar una sesion guardada en Jupyter:

```bash
.\.venv\Scripts\jupyter.exe notebook notebooks/dataset_explorer.ipynb
```

Para verificar que los tiempos de un XDF coincidan con el protocolo:

```bash
.\.venv\Scripts\python.exe tests/verify_xdf_timing.py ruta\al\archivo.xdf
```

## Notas del repositorio

- `dataset/` esta ignorado en git y no se sube al repositorio
- Los archivos XDF se generan localmente durante las sesiones
- La estructura de guardado es `dataset/<objetivo>/<protocolo>/<genero>/<sujeto>/`.
- Ejemplo: `dataset/arm_vs_leg/mi/hombre/1/MI-AL-H-SUJETO01-SESION01-10-030526.xdf`.
