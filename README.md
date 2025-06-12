# Pokemon Game

**Integrantes:** Juan Miguel Palacios, Nicolas Rodriguez Romero, Jhon Alexis Ruiz Quiceno

Un simulador de combate estratégico Pokémon desarrollado en Python que enfrenta a un jugador humano contra una inteligencia artificial basada en el algoritmo Minimax.

## 🎮 Descripción del Proyecto

Este proyecto implementa un sistema de combate por turnos entre entrenadores Pokémon, donde:

- **Jugador Humano:** Controla un entrenador y toma decisiones estratégicas manualmente
- **Inteligencia Artificial:** Utiliza el algoritmo Minimax para tomar decisiones óptimas de combate

El objetivo es crear una experiencia de combate desafiante donde la IA pueda competir estratégicamente contra jugadores humanos mediante la evaluación de múltiples movimientos futuros.

## 🚀 Características Principales

- **Sistema de Combate por Turnos:** Mecánicas clásicas de combate Pokémon
- **IA con Algoritmo Minimax:** Inteligencia artificial que evalúa las mejores jugadas posibles
- **Interfaz Interactiva:** Sistema de menús para que el jugador tome decisiones
- **Mecánicas Pokémon:** Implementación de tipos, movimientos, puntos de vida y estadísticas
- **Evaluación Estratégica:** La IA considera múltiples escenarios antes de actuar

## Pasos para Ejecutar el Proyecto

Para correr el proyecto, asegúrate de tener instalado Python 3.9 o superior

Primero, debes crear un entorno virtual para el proyecto. Puedes hacerlo con el siguiente comando (Dependiendo de tu sistema operativo):

```bash
python -m venv .venv
```

Posteriormente, activa el entorno virtual (En linux):

```bash
source .venv/bin/activate
```

Después, instala las dependencias necesarias ejecutando desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

Luego, puedes ejecutar el script principal con:

```bash
python -m src.main
```
