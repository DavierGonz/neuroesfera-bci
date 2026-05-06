# Manual de usuario NeuroEsfera BCI

## Informacion del documento

**Software:** NeuroEsfera BCI  
**Version del entorno:** Python 3.10  
**Sistema operativo recomendado:** Windows 10/11  
**Formato de salida:** XDF  
**Equipo EEG:** Unicorn Hybrid Black  
**Librerias principales:** PsychoPy, pylsl, pyxdf  
**Herramientas externas:** Unicorn LSL, LabRecorder

Este manual describe como preparar el sistema, ejecutar los experimentos,
guardar el dataset y revisar los markers generados por NeuroEsfera BCI.

## 1. Objetivo del software

NeuroEsfera BCI es una aplicacion experimental para adquisicion de senales EEG.
El sistema presenta estimulos visuales y auditivos mediante PsychoPy, envia
markers por LSL y guarda EEG + markers en archivos XDF usando LabRecorder.

La version actual esta orientada a tres experimentos:

- Experimento 1: Motor Imagery izquierda/derecha.
- Experimento 2: combinacion de MI, MO y AW para brazos/piernas.
- Experimento 3: LM con MI, MO, AW y ME para brazos/piernas, organizado por
  bloques experimentales.

El software no realiza clasificacion BCI online en esta version.

## 2. Requisitos previos

Antes de ejecutar una sesion se debe contar con:

- Windows 10/11.
- Python 3.10.
- Entorno virtual `.venv` creado en la carpeta del proyecto.
- Unicorn Suite Hybrid Black.
- Unicorn LSL.
- LabRecorder.
- Casco Unicorn Hybrid Black cargado y funcional.
- Dongle Bluetooth del casco conectado.
- Electrodos, gel conductor y accesorios para mastoides.

La ruta esperada de LabRecorder se configura en:

```text
core/config.py
```

Por defecto:

```text
C:\LSL\LabRecorder\LabRecorder.exe
```

Si LabRecorder esta en otra carpeta, actualizar `LABRECORDER_PATH`.

## 3. Instalacion del entorno

Desde PowerShell:

```powershell
cd C:\Proyects\BCI_workspace\BCI
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si PowerShell bloquea la activacion:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## 4. Preparacion del casco EEG

El proyecto usa el siguiente mapeo para los 8 canales EEG del Unicorn Hybrid
Black:

```text
Canal 1 -> Fz
Canal 2 -> C3
Canal 3 -> Cz
Canal 4 -> C4
Canal 5 -> Pz
Canal 6 -> PO7
Canal 7 -> Oz
Canal 8 -> PO8
```

Antes de ejecutar el software:

1. Encender el casco.
2. Verificar conexion en Unicorn Suite.
3. Revisar que las senales EEG se vean estables.
4. Revisar impedancia/contacto de electrodos.
5. Verificar mastoides izquierda y derecha.

## 5. Publicacion del stream EEG por LSL

Abrir Unicorn LSL y seguir estos pasos:

1. Seleccionar el dispositivo disponible.
2. Presionar `Open`.
3. Presionar `Start`.
4. Mantener Unicorn LSL abierto durante toda la adquisicion.

Se recomienda publicar cada senal por separado cuando Unicorn LSL lo permita.
Asi suele aparecer un stream EEG de 8 canales:

```text
UN-XXXX_EEG
```

Para verificar que el stream LSL esta visible:

```powershell
.\.venv\Scripts\python.exe tests\inspect_lsl_stream.py
```

## 6. Ejecucion del software

Iniciar NeuroEsfera BCI con:

```powershell
.\.venv\Scripts\python.exe main.py
```

PsychoPy puede mostrar un mensaje de medicion de frame rate al inicio. Es
normal.

## 7. Menu principal

El menu principal ya no muestra seleccion manual de `Left vs Right` o
`Arm vs Leg`. Cada experimento tiene su objetivo definido internamente.

Experimentos disponibles:

```text
Experimento 1 -> Motor Imagery, izquierda/derecha
Experimento 2 -> MI + MO + AW, brazos/piernas
Experimento 3 -> LM: MI + MO + AW + ME, brazos/piernas
```

## 8. Configuracion de la sesion

Luego de seleccionar un experimento, el software muestra la pantalla de
configuracion.

Parametros disponibles:

- Numero de sujeto.
- Genero de videos MO cuando el experimento incluye Motor Observation.
- Bloque experimental solo para Experimento 3.

El numero de sesion se calcula automaticamente leyendo el dataset existente.

## 9. Bloques del Experimento 3

El Experimento 3 esta organizado en tres bloques:

```text
Bloque 1 - Sin tSCS
Bloque 2 - Con tSCS
Bloque 3 - Medicion de MEP
```

Al seleccionar Experimento 3 se debe escoger uno de estos bloques. El archivo se
guarda dentro del bloque seleccionado.

La numeracion de sesiones del Experimento 3 se calcula revisando los tres
bloques del mismo sujeto. Ejemplo:

```text
dataset/experimento_3/hombre/1/Bloque 1 - Sin tSCS/LM-AL-H-SUJETO01-SESION01-40-060526.xdf
```

Si luego se guarda una nueva sesion del mismo sujeto en:

```text
dataset/experimento_3/hombre/1/Bloque 3 - Medicion de MEP/
```

el software detecta la sesion previa y guarda la nueva como:

```text
SESION02
```

## 10. Estructura temporal de un trial

Todos los experimentos usan la misma secuencia temporal:

```text
BASELINE  3.0 s   fondo negro
CUE       4.5 s   cue del paradigma + beep desde el segundo 3.0
CROSS     5.0 s   cruz o video MO, segun modalidad
ITI       5.0 s   fondo negro entre trials
```

Al finalizar, aparece:

```text
Fin del experimento
```

durante aproximadamente 3 segundos.

## 11. Fondo y estimulos visuales

Durante la ejecucion de los experimentos el fondo es negro.

Estimulos por modalidad:

- `MI`: texto o flecha de imaginacion motora.
- `AW`: palabra de accion.
- `MO`: en la fase `CUE` se muestra `stimuli/Estimulo_MO.png`; en la fase
  `CROSS` se muestra el video MO correspondiente.
- `ME`: por ahora muestra `BRAZOS` o `PIERNAS`.

Los videos MO se escalan para ocupar el maximo espacio posible sin deformar su
relacion de aspecto.

## 12. Distribucion de trials por experimento

### Experimento 1

```text
Modalidad: MI
Clases: LEFT, RIGHT
Trials totales: 40
```

Con `20` trials por clase:

```text
20 MI_LEFT
20 MI_RIGHT
```

### Experimento 2

```text
Modalidades: MI, MO, AW
Clases: ARM, LEG
Trials totales: 120
```

Con `20` trials por clase y modalidad:

```text
20 MI_ARM
20 MI_LEG
20 MO_ARM
20 MO_LEG
20 AW_ARM_<PALABRA>
20 AW_LEG_<PALABRA>
```

### Experimento 3

```text
Modalidades: MI, MO, AW, ME
Clases: ARM, LEG
Trials totales: 40
```

La combinacion de paradigmas cambia aleatoriamente al momento de la cue. La
distribucion por sesion es:

```text
10 MI
10 MO
10 AW
10 ME
```

Dentro de cada paradigma se balancean brazos y piernas:

```text
5 ARM
5 LEG
```

El orden se mezcla de forma aleatoria y se evita repetir la misma clase mas de
3 veces consecutivas cuando es posible.

## 13. Grabacion con LabRecorder

Al iniciar una sesion, el software:

1. Crea el stream LSL de markers `NeuroEsferaMarkers`.
2. Abre LabRecorder en segundo plano.
3. Actualiza la lista de streams.
4. Selecciona los streams disponibles.
5. Define carpeta y nombre del XDF.
6. Inicia la grabacion.

En consola se muestra una linea como:

```text
Grabando dataset en: C:\Proyects\BCI_workspace\BCI\dataset\experimento_3\hombre\1\Bloque 1 - Sin tSCS\LM-AL-H-SUJETO01-SESION01-40-060526.xdf
```

## 14. Organizacion del dataset

El dataset se guarda en tres carpetas principales, una por experimento:

```text
dataset/
  experimento_1/
  experimento_2/
  experimento_3/
```

### Experimento 1

```text
dataset/experimento_1/<genero>/<sujeto>/
```

Ejemplo:

```text
dataset/experimento_1/hombre/1/
```

### Experimento 2

```text
dataset/experimento_2/<genero>/<sujeto>/
```

Ejemplo:

```text
dataset/experimento_2/mujer/2/
```

### Experimento 3

```text
dataset/experimento_3/<genero>/<sujeto>/<bloque>/
```

Ejemplo:

```text
dataset/experimento_3/hombre/1/Bloque 1 - Sin tSCS/
dataset/experimento_3/hombre/1/Bloque 2 - Con tSCS/
dataset/experimento_3/hombre/1/Bloque 3 - Medicion de MEP/
```

## 15. Nombre de los archivos XDF

El nombre del archivo usa el formato:

```text
<PROTOCOLO>-<OBJETIVO>-<GENERO>-SUJETO<NN>-SESION<NN>-<TRIALS>-<FECHA>.xdf
```

Ejemplos:

```text
MI-LR-H-SUJETO01-SESION01-40-060526.xdf
AW-AL-M-SUJETO02-SESION03-120-060526.xdf
LM-AL-H-SUJETO01-SESION02-40-060526.xdf
```

Codigos:

```text
MI  Motor Imagery
AW  Action Words / Experimento 2
LM  Experimento 3
LR  Left vs Right
AL  Arm vs Leg
H   Hombre
M   Mujer
```

## 16. Markers generales

Al inicio de cada sesion:

```text
TARGET_LEFT_VS_RIGHT
GENDER_HOMBRE
```

o:

```text
TARGET_ARM_VS_LEG
GENDER_MUJER
```

En cada trial:

```text
TRIAL_<N>
CLASS_<CLASE>
BASELINE
CUE
<MARKER_DE_ESTIMULO>
CROSS
ITI
```

Al finalizar:

```text
END
```

Si la sesion se finaliza desde el boton `Finalizar` o con `ESC`, tambien puede
aparecer:

```text
END_EARLY
```

## 17. Markers por experimento

### Experimento 1

Objetivo fijo:

```text
TARGET_LEFT_VS_RIGHT
```

Clases:

```text
CLASS_LEFT
CLASS_RIGHT
```

Markers de estimulo:

```text
MI_LEFT
MI_RIGHT
```

Ejemplo de trial:

```text
TRIAL_1
CLASS_LEFT
BASELINE
CUE
MI_LEFT
CROSS
ITI
```

### Experimento 2

Objetivo fijo:

```text
TARGET_ARM_VS_LEG
```

Clases:

```text
CLASS_ARM
CLASS_LEG
```

Markers de estimulo:

```text
MI_ARM
MI_LEG
MO_ARM
MO_LEG
AW_ARM_<PALABRA>
AW_LEG_<PALABRA>
```

Ejemplos:

```text
AW_ARM_APLAUDIR
AW_LEG_CAMINAR
MO_ARM
MI_LEG
```

### Experimento 3

Objetivo fijo:

```text
TARGET_ARM_VS_LEG
```

Clases:

```text
CLASS_ARM
CLASS_LEG
```

Markers de estimulo:

```text
MI_ARM
MI_LEG
MO_ARM
MO_LEG
AW_ARM_<PALABRA>
AW_LEG_<PALABRA>
ME_ARM
ME_LEG
```

Ejemplo de orden de estimulos dentro de una sesion:

```text
1. AW_ARM_APLAUDIR
2. MO_LEG
3. MI_ARM
4. ME_LEG
```

El notebook muestra este orden en formato simplificado, por ejemplo:

```text
AW_ARMS
MO_LEGS
MI_ARMS
ME_LEGS
```

## 18. Finalizacion de la sesion

Al finalizar, el software:

1. Envia `END`.
2. Detiene LabRecorder.
3. Cierra LabRecorder.
4. Muestra pantalla de resumen.

La pantalla final muestra:

- Formato.
- Archivo.
- Objetivo.
- Bloque, si aplica.
- Sujeto.
- Sesion.
- Stream EEG.
- Canales.

## 19. Verificacion de tiempos

Para verificar duraciones desde markers:

```powershell
.\.venv\Scripts\python.exe tests\verify_xdf_timing.py ruta\al\archivo.xdf
```

Si no se indica ruta, usa el XDF mas reciente en `dataset/`:

```powershell
.\.venv\Scripts\python.exe tests\verify_xdf_timing.py
```

Intervalos esperados:

```text
BASELINE_TO_CUE            3.0 s
CUE_TO_CROSS               4.5 s
CROSS_TO_ITI               5.0 s
ITI_TO_NEXT_TRIAL_OR_END   5.0 s
```

## 20. Exploracion del dataset

Abrir el notebook:

```powershell
.\.venv\Scripts\jupyter.exe notebook notebooks\dataset_explorer.ipynb
```

El notebook permite:

- Seleccionar uno o varios archivos XDF.
- Ver canales etiquetados en metadata.
- Ver canales mostrados cuando el XDF no trae etiquetas.
- Ver la secuencia completa de markers.
- Ver el orden de estimulos por trial.
- Ver conteos por modalidad `MI`, `MO`, `AW`, `ME`.

## 21. Solucion de problemas

### No aparecen streams LSL

Revisar:

- Casco encendido.
- Unicorn LSL abierto.
- Boton `Start` presionado en Unicorn LSL.
- Dongle Bluetooth conectado.

Verificar con:

```powershell
.\.venv\Scripts\python.exe tests\inspect_lsl_stream.py
```

### LabRecorder no inicia

Revisar que `LABRECORDER_PATH` en `core/config.py` apunte a
`LabRecorder.exe`, no a `UnicornLSL.exe`.

### El XDF pesa muy poco

Puede indicar que:

- No habia stream EEG activo.
- Solo se grabaron markers.
- La sesion fue interrumpida.
- Unicorn LSL no estaba en `Start`.

### El XDF no trae labels reales de electrodos

Algunas versiones de Unicorn LSL no publican labels en metadata. En ese caso se
usa el mapeo esperado del proyecto:

```text
Fz, C3, Cz, C4, Pz, PO7, Oz, PO8
```

## 22. Flujo resumido

```text
1. Encender casco
2. Verificar senal en Unicorn Suite
3. Abrir Unicorn LSL
4. Presionar Open y Start
5. Ejecutar main.py
6. Seleccionar experimento
7. Configurar sujeto, genero de videos y bloque si aplica
8. Verificar sesion automatica
9. Presionar espacio para iniciar
10. Esperar fin del experimento
11. Revisar XDF en dataset/
12. Explorar XDF en notebook
13. Verificar tiempos si es necesario
```

## 23. Recomendaciones para una sesion real

Antes de iniciar:

- Confirmar comodidad del sujeto.
- Confirmar que el casco no se mueve.
- Confirmar senales EEG estables.
- Confirmar que Unicorn LSL publica el stream.
- Confirmar espacio suficiente en `dataset/`.

Durante la sesion:

- Evitar hablarle al sujeto.
- Evitar movimientos innecesarios.
- No cerrar Unicorn LSL.
- No cerrar la ventana de PsychoPy.

Despues de la sesion:

- Confirmar que se genero el XDF.
- Revisar peso del archivo.
- Verificar markers o tiempos si es necesario.
- Registrar incidentes experimentales.
