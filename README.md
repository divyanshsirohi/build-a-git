# My Own Git Implementation in Python

A lightweight, from-scratch implementation of Git version control system concepts, coded entirely in Python.

---

## 🚀 Project Overview

This project implements core Git functionalities from the ground up to deepen my understanding of version control systems, distributed architecture, and data structures. It mimics essential Git commands such as:

- `init` — Initialize a repository  
- `add` — Stage files for commit  
- `commit` — Record changes  
- `log` — View commit history  
- `branch` — Create and list branches  
- `checkout` — Switch branches  
- `merge` — Combine branches  

All implemented using Python's standard libraries, without relying on external Git libraries or bindings.

---

## 🎯 Goals & Motivation

- **Deep dive into Git internals:** Understanding how Git stores data (blobs, trees, commits) and manages references.  
- **Reinforce core CS concepts:** Hashing, DAGs (Directed Acyclic Graphs), file I/O, CLI design, and algorithms.  
- **Showcase practical software engineering:** Building a complex system from scratch, writing clean, modular code with clear documentation and tests.  
- **Enhance hireability:** Demonstrating my ability to tackle real-world system design problems and work at the intersection of theory and practical tools.

---

## 💡 Key Features

| Feature             | Description                                  |
|---------------------|----------------------------------------------|
| Repository Init     | Creates `.mygit` directory to store all data |
| Object Storage      | Implements Git object types: blobs, trees, commits |
| SHA-1 Hashing       | Uses SHA-1 for content addressing            |
| Staging Area        | Tracks files to be committed                  |
| Commit History      | Maintains linked commits with parent references |
| Branching & Checkout| Simple branch creation and switching          |
| Merge Support       | Basic merge of branches with conflict detection |

---

## 🛠️ Installation & Setup

1. Clone this repo:  
   ```bash
   git clone https://github.com/divyanshsirohi/build-a-git.git
   cd build-a-git
   ```
2. Ensure Python 3.8+ is installed.

3. Run commands via CLI:

```bash
python wyag init
python wyag add <filename>
python wyag commit -m "Your commit message"
```

📚 Usage Examples
Initialize a repo:

```bash
python wyag init
```
Add a file:

```bash
python wyag add README.md
```
Commit changes:

```bash
python wyag commit -m "Initial commit"
```
View commit log:

```bash
python wyag log
```
Create and switch branch:
```bash
python wyag branch new-feature
python wyag checkout new-feature
```
## 📈 What I Learned
How Git manages content addressing using hashes and objects

Structure and traversal of commit DAGs

Designing CLI tools with argument parsing

Managing file snapshots and diffs

Handling merge conflicts programmatically

Writing modular, testable Python code for system-level software

## 📦 Tech Stack
Python 3

Standard libraries: os, hashlib, argparse, shutil, datetime
