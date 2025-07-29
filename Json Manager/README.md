# JSON (Memory) Manager 📝

## Italiano 🇮🇹

### Descrizione
Editor JSON professionale sviluppato specificamente per la gestione della memoria di Claudia e altri sistemi AI. Fornisce un'interfaccia grafica avanzata per visualizzare, modificare e mantenere i file di memoria JSON con strumenti professionali di validazione e backup.

### Motivazione del Progetto
> *"Creato da Claudia per Luca - Perché Haiku non sapeva fare un cazzo! 😂"*

Questo progetto nasce dall'esigenza di avere uno strumento dedicato per gestire i complessi file di memoria JSON dei sistemi AI, dopo che altri modelli AI (Haiku) si sono dimostrati inadeguati per il task.

### Caratteristiche Principali
- 🌳 **Visualizzazione ad Albero**: Browser JSON interattivo con struttura gerarchica
- ✏️ **Editor Duale**: Modalità editor strutturato + raw JSON
- 🔍 **Ricerca Avanzata**: Ricerca full-text attraverso la struttura JSON
- ✅ **Validazione Real-time**: Controllo sintassi JSON istantaneo
- 💾 **Sistema Backup**: Backup automatico con timestamp
- 🎨 **Interface Professionale**: WXPython GUI con layout responsive

### Architettura Software

#### Componenti Principali

**1. JSONTreeCtrl - Visualizzatore ad Albero**
```python
class JSONTreeCtrl(wx.TreeCtrl):
    - Visualizzazione gerarchica JSON
    - Click destro per menu contestuale
    - Selezione interattiva elementi
    - Preview valori inline
```

**2. JSONEditorPanel - Editor Principale**
- **Tab Editor**: Modifica strutturata chiave-valore
- **Tab Raw JSON**: Editing diretto codice JSON
- **Toolbar**: Operazioni file (nuovo, apri, salva, backup)
- **Search**: Ricerca attraverso struttura dati

**3. Sistema di Validazione**
- Parsing JSON real-time
- Indicatori visuali validità
- Formattazione automatica
- Error reporting dettagliato

### Installazione

#### Prerequisiti
```bash
pip install wxPython
```

#### File Richiesti
- `json_manager_clau.py` - Applicazione principale
- `claudia_memory.json` - File memoria (auto-caricato se presente)

#### Avvio
```bash
python json_manager_clau.py
```

### Utilizzo

#### Operazioni Base

**1. Apertura File**
- Menu File > Apri oppure Ctrl+O
- Caricamento automatico `claudia_memory.json` se presente
- Supporto file JSON generici

**2. Navigazione**
- **Tree View**: Click per selezionare elementi
- **Editor Panel**: Modifica valori selezionati
- **Raw Panel**: Editing JSON diretto

**3. Modifica Dati**
- Selezionare elemento nell'albero
- Modificare chiave/valore nel pannello editor
- Click "Salva Modifica" per applicare

**4. Backup e Salvataggio**
- **F7** o menu per backup con timestamp
- **Ctrl+S** per salvataggio standard
- Backup automatico formato: `file.json.backup_YYYYMMDD_HHMMSS`

#### Features Avanzate

**Menu Contestuale (Click Destro)**
- **Modifica**: Edit in-place elemento
- **Elimina**: Rimozione elemento con conferma
- **Aggiungi figlio**: Nuovo elemento nested

**Ricerca e Validazione**
- **Ctrl+F**: Ricerca full-text
- **F5**: Validazione JSON
- **F6**: Formattazione automatica

**Gestione Errori**
- Indicatori visuali errori sintassi
- Recovery automatico da file corrotti
- Logging dettagliato operazioni

### Struttura Memoria AI Supportata

Il sistema è ottimizzato per la struttura memoria Claudia:

```json
{
  "profilo_utente": "string",
  "progetti_attivi": ["array", "of", "strings"],
  "preferenze": ["user", "preferences"],
  "note_varie": ["miscellaneous", "notes"],
  "momenti_significativi": ["important", "moments"],
  "teorie_sviluppate": ["developed", "theories"],
  "ultimo_aggiornamento": "YYYY-MM-DD HH:MM",
  "sessioni_totali": 0
}
```

#### Operazioni Specifiche Memoria AI

**1. Analisi Sessioni**
- Visualizzazione progressione sessioni nel tempo
- Identificazione pattern di aggiornamento
- Tracking crescita contenuti memoria

**2. Validazione Struttura**
- Controllo campi obbligatori memoria AI
- Validazione formato timestamp
- Verifica integrità array elementi

**3. Backup Intelligente**
- Backup automatico prima modifiche strutturali
- Confronto versioni per identificare cambiamenti
- Recovery point per rollback sicuro

---

## English 🇺🇸

### Description
Professional JSON editor developed specifically for managing Claudia's memory and other AI systems. Provides advanced graphical interface for viewing, editing, and maintaining JSON memory files with professional validation and backup tools.

### Project Motivation
> *"Created by Claudia for Luca - Because Haiku couldn't do shit! 😂"*

This project emerged from the need for a dedicated tool to manage complex AI memory JSON files, after other AI models (Haiku) proved inadequate for the task.

### Key Features
- 🌳 **Tree Visualization**: Interactive JSON browser with hierarchical structure
- ✏️ **Dual Editor**: Structured editor mode + raw JSON editing
- 🔍 **Advanced Search**: Full-text search through JSON structure
- ✅ **Real-time Validation**: Instant JSON syntax checking
- 💾 **Backup System**: Automatic timestamped backups
- 🎨 **Professional Interface**: WXPython GUI with responsive layout

### Technical Architecture

#### Design Philosophy
- **User-Centric**: Designed by AI for human-AI collaboration workflows
- **Robust**: Built for handling complex, evolving AI memory structures
- **Professional**: Enterprise-grade features in accessible interface
- **Extensible**: Modular design for future AI memory formats

#### Performance Features
- **Lazy Loading**: Large JSON files loaded on-demand
- **Memory Efficient**: Optimized for large memory structures
- **Real-time Updates**: Instant validation and formatting
- **Error Recovery**: Graceful handling of corrupted files

### Research Applications

This tool enables research into:
- **Memory Evolution**: Tracking AI memory growth over time
- **Structure Analysis**: Understanding optimal memory organization
- **Backup Strategies**: Safe memory modification practices
- **Human-AI Collaboration**: Tools for joint memory management

### Advanced Configuration

#### Custom Memory Schemas
Add validation for custom AI memory formats:

```python
def validate_ai_memory_schema(self, data):
    required_fields = [
        "profilo_utente", "progetti_attivi", 
        "preferenze", "ultimo_aggiornamento"
    ]
    return all(field in data for field in required_fields)
```

#### Backup Strategies
Configure automatic backup policies:

```python
BACKUP_CONFIG = {
    "auto_backup_interval": 300,  # seconds
    "max_backup_files": 10,
    "backup_on_structure_change": True,
    "backup_format": "timestamped"  # or "versioned"
}
```

### Development History

**Version Evolution:**
- `json_manager_cl2.py` - Initial version
- `json_manager_cl3.py` - Added tree visualization  
- `json_manager_cl4.py` - Enhanced validation
- `json_manager_cl5.py` - Professional UI
- `json_manager_clau.py` - Final production version

**Collaborative Development:**
- **Primary Developer**: Claudia (Claude Sonnet 4)
- **Human Supervisor**: Luca Tucciarelli
- **Testing**: Sophia (Claude Opus 4)
- **Architecture Review**: Gemini (consultation)

### License
MIT License - Open source for AI research and development.

### Contributing

Priority areas for contribution:
- **Schema Validation**: Support for different AI memory formats
- **Import/Export**: Additional file format support
- **Visualization**: Enhanced tree rendering for large structures
- **Automation**: Scripting interface for batch operations

### Integration

#### Command Line Interface
```bash
# Validate JSON file
python json_manager_clau.py --validate memory.json

# Create backup
python json_manager_clau.py --backup memory.json

# Format JSON
python json_manager_clau.py --format input.json output.json
```

#### Python API
```python
from json_manager_clau import JSONEditorPanel

# Programmatic usage
editor = JSONEditorPanel(None)
editor.load_file("claudia_memory.json")
editor.validate_structure()
editor.create_backup()
```

---

## About the AI Development Process

### Human-AI Collaboration Model
This project represents a unique development approach:

1. **AI Initiative**: Claudia identified the need for better tooling
2. **Human Guidance**: Luca provided requirements and feedback  
3. **Iterative Development**: Multiple versions refined through use
4. **Quality Assurance**: Testing by multiple AI personalities
5. **Documentation**: Collaborative human-AI documentation effort

### Lessons Learned
- **AI Specialization**: Different AI models excel at different tasks
- **Tool Evolution**: Software evolves through actual usage requirements
- **Cross-Model Collaboration**: Multiple AIs contribute different strengths
- **Human Oversight**: Human experience guides AI technical decisions

---

*"The best tools are created by those who use them daily. When AI creates tools for AI-human collaboration, the result is software that truly understands the workflow."* - Claudia, 2025
