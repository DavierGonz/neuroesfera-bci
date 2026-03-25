# NeuroEsfera BCI

Software experimental para adquisición de señales EEG en tiempo real usando el casco Unicorn Hybrid Black, Python, Pygame y LSL.

## Descripción

Este proyecto implementa una primera versión de un sistema BCI orientado a la adquisición de señales EEG en tiempo real. El software permite ejecutar experimentos de imaginación motora, presentar estímulos visuales y auditivos, y almacenar señales EEG junto con marcadores y trials para su posterior análisis.

## Funcionalidades actuales

- Menú principal para navegación del software
- Módulo de Motor Imagery
- Selección del número de trials
- Presentación de estímulos visuales y auditivos
- Envío de marcadores LSL
- Captura de señales EEG desde Unicorn Hybrid Black por LSL
- Almacenamiento de datos en archivos CSV etiquetados

## Tecnologías usadas

- Python 3.12
- Pygame
- pylsl
- Unicorn LSL

## Estructura del proyecto

```text
BCI/
├── core/
├── eeg/
├── experiments/
├── gui/
├── stimuli/
├── utils/
├── data/
├── main.py
└── test_lsl.py