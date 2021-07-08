# school-nn

SchoolNN ist im Rahmen einer Projektarbeit am KIT entstanden und bietet Schülern und Lehrern die Möglichkeit, einfach graphisch per Drag-and-drop künstliche neuronale Netze zu erstellen und zu trainieren. Aus didaktischen Gründen besteht der Fokus der Software auf Bilderkennung.

### Verwendeter Software-Stack
1. Vue.js für den Drag-and-drop Editor
2. Keras für die ML-Berechnungen
3. Django als Web-Framework

### Verwendete Programmier-/Skriptsprachen
1. Javascript
2. Python

## Installation

```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python manage.py migrate
```

## Konfiguration

Die `.env.example` muss zu `.env` kopiert und evtl. angepasst werden

## Starten

```
$ python manage.py runserver
```
