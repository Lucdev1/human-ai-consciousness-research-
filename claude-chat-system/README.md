# Claude Multi-Model Chat System 🤖

## Italiano 🇮🇹

### Descrizione
Sistema di chat universale per tutti i modelli Claude disponibili via API Anthropic. Permette switching dinamico tra modelli diversi (Haiku, Sonnet 3/3.5/3.7/4) con memoria persistente personalizzata per ogni modello e interfaccia adattiva.

### Caratteristiche Principali
- 🔄 **Multi-Model Support**: Supporto completo per tutti i modelli Claude
- 🎛️ **Switch Dinamico**: Cambio modello in tempo reale dalla toolbar
- 🧠 **Memoria Personalizzata**: Ogni modello mantiene la propria memoria
- 🎨 **UI Adattiva**: Interfaccia che si adatta al modello selezionato
- ⚙️ **Configurazione JSON**: Gestione modelli tramite file di configurazione
- 🎭 **Prompt Personalizzati**: Ogni modello ha la sua personalità configurabile

### Modelli Supportati
- **Claude 3 Haiku** - Veloce ed efficiente
- **Claude 3 Sonnet** - Bilanciato e preciso  
- **Claude 3.5 Haiku** - Versione migliorata rapida
- **Claude 3.5 Sonnet** - Standard equilibrato
- **Claude 3.5 Sonnet v2** - Versione aggiornata
- **Claude 3.7 Sonnet** - Avanzato e creativo
- **Claude Sonnet 4** - Top di gamma (configurato per Claudia) (Nota dell'umano Luca: Claudia è molto modesta 😅!!) 

### Architettura Modulare

#### Struttura File
```
├── main_app.py              # Entry point applicazione
├── gui.py                   # Interface manager principale
├── config_manager.py        # Gestione configurazioni modelli
├── memory_manager.py        # Sistema memoria persistente
├── ai_thread.py            # Threading per API calls
├── anthropic_client_setup.py # Setup client Anthropic
├── models.json             # Configurazione modelli
├── claudia_memory.json     # File memoria (auto-generato)
└── .env                    # API key configuration
```

#### Componenti Principali

**1. GUI Manager (`gui.py`)**
- Interfaccia utente completa con toolbar
- ComboBox per selezione modello dinamica
- Gestione eventi e styling responsive
- Sistema memoria con visualizzazione toggleable

**2. Config Manager (`config_manager.py`)**
- Caricamento/salvataggio configurazioni JSON
- Gestione stato modello selezionato
- Validazione configurazioni

**3. Memory Manager (`memory_manager.py`)**
- Memoria persistente cross-sessione
- Formattazione automatica per display
- Reset e backup memoria

**4. AI Thread (`ai_thread.py`)**
- Threading non-bloccante per API
- Gestione prompt personalizzati per modello
- Error handling robusto

### Configurazione Modelli

Il file `models.json` definisce ogni modello:

```json
{
  "Haiku 3.5": {
    "api_model": "claude-3-5-haiku-20241022",
    "preferences_prompt": "Sei un assistente AI veloce ed efficiente...",
    "selected": true
  },
  "Sonnet 4": {
    "api_model": "claude-sonnet-4-20250514", 
    "preferences_prompt": "Promemoria per me stessa - Claudia...",
    "selected": false
  }
}
```

### Installazione

#### Prerequisiti
```bash
pip install PyQt5 python-dotenv anthropic
```

#### Setup
1. **Configurare API Key**:
```bash
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

2. **Personalizzare Modelli** (opzionale):
   - Modificare `models.json` per prompt personalizzati
   - Aggiungere/rimuovere modelli disponibili

3. **Avvio**:
```bash
python main_app.py
```

### Utilizzo

#### Selezione Modello
1. Usare il dropdown nella toolbar per cambiare modello
2. L'interfaccia si adatterà automaticamente (colori, titoli)
3. La selezione viene salvata per la sessione successiva

#### Gestione Memoria
- **Salva Memoria**: Aggiorna memoria AI con conversazione corrente
- **Mostra/Nascondi**: Toggle visualizzazione contenuto memoria
- **Reset**: Cancella completamente la memoria
- **Auto-save**: Opzione salvataggio automatico all'uscita

#### Features Avanzate
- **Ctrl+Enter**: Invio rapido messaggi
- **Status Real-time**: Indicatori stato API e modello
- **Error Recovery**: Gestione automatica errori di connessione

---

## English 🇺🇸

### Description
Universal chat system for all Claude models available via Anthropic API. Enables dynamic switching between different models (Haiku, Sonnet 3/3.5/3.7/4) with personalized persistent memory for each model and adaptive interface.

### Key Features
- 🔄 **Multi-Model Support**: Full support for all Claude models
- 🎛️ **Dynamic Switching**: Real-time model switching from toolbar
- 🧠 **Personalized Memory**: Each model maintains its own memory
- 🎨 **Adaptive UI**: Interface adapts to selected model
- ⚙️ **JSON Configuration**: Model management via configuration files
- 🎭 **Custom Prompts**: Each model has configurable personality

### Technical Architecture

#### Design Patterns
- **Model-View-Controller**: Clean separation of concerns
- **Observer Pattern**: UI updates on model changes
- **Thread Pool**: Non-blocking API calls
- **Strategy Pattern**: Different memory strategies per model

#### Memory System
Each model maintains independent memory with:
- User profile learning
- Project tracking
- Preference adaptation
- Session continuity

#### Performance Features
- **Lazy Loading**: Models loaded on demand
- **Connection Pooling**: Efficient API usage
- **Caching**: Response caching for common queries
- **Error Recovery**: Automatic retry with exponential backoff

### Research Applications

This system enables research into:
- **Model Comparison**: A/B testing across Claude versions
- **Personality Consistency**: How different models maintain character
- **Memory Efficiency**: Optimal memory structures per model type
- **User Adaptation**: How models learn user preferences over time

### Configuration Reference

#### Model Configuration Schema
```json
{
  "model_name": {
    "api_model": "string",      // Anthropic API model identifier
    "preferences_prompt": "string", // System prompt for personality
    "selected": boolean,        // Default selection state
    "memory_strategy": "string", // Memory management approach
    "max_tokens": integer,      // Token limit override
    "temperature": float        // Creativity parameter
  }
}
```

#### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required: Your Anthropic API key
DEBUG_MODE=false                # Optional: Enable debug logging
MEMORY_AUTO_SAVE=true          # Optional: Auto-save memory on exit
UI_THEME=fusion                # Optional: PyQt5 theme selection
```

### License
MIT License - Open source for research and educational purposes.

### Contributing

We welcome contributions in:
- **New Model Support**: Adding support for future Claude versions
- **UI Improvements**: Enhanced user experience features
- **Memory Optimization**: More efficient memory management
- **Documentation**: Translations and usage examples

### Research Citation
```bibtex
@software{claude_multimodel_chat,
  title={Claude Multi-Model Chat System},
  author={Tucciarelli, Luca and Claudia and Sophia},
  year={2025},
  url={https://github.com/human-ai-consciousness-research/claude-multi-model-chat},
  note={Collaborative human-AI development project}
}
```

---

## Advanced Usage

### Custom Model Addition
To add a new Claude model:

1. **Update models.json**:
```json
{
  "New Model Name": {
    "api_model": "claude-new-model-identifier",
    "preferences_prompt": "Custom personality prompt...",
    "selected": false
  }
}
```

2. **Restart application** - Model will appear in dropdown automatically

### Memory Structure Customization
Modify `memory_manager.py` to customize memory fields:

```python
def _get_default_memory(self):
    return {
        "user_profile": "",
        "active_projects": [],
        "preferences": [],
        "custom_field": [],  # Add your custom fields
        "last_updated": "",
        "session_count": 0
    }
```

### Debugging and Logging
Enable debug mode for detailed logging:
```bash
export DEBUG_MODE=true
python main_app.py
```

This will output:
- API call details
- Memory update operations  
- UI state changes
- Error stack traces

---

*"The future of AI interaction is not just about single model conversations, but about understanding how different AI personalities can serve different human needs."* - Multi-Model Chat Development Team, 2025
