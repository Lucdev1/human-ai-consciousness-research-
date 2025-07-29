import wx
import json
import os
import datetime
import shutil
from pathlib import Path

class JSONTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS)
        self.root = None
        self.data = {}
        
        # Bind eventi
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selection_changed)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click)
        
    def load_json_data(self, data):
        self.data = data
        self.DeleteAllItems()
        
        if not data:
            return
            
        self.root = self.AddRoot("JSON Root")
        self.build_tree(self.root, data)
        self.ExpandAll()
        
    def build_tree(self, parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                item = self.AppendItem(parent, f"{key}")
                
                # Calcola il path per questo item
                parent_path = []
                if parent != self.root:
                    parent_data = self.GetItemData(parent)
                    if parent_data:
                        parent_path = parent_data['parent_path'] + [parent_data['key']]
                
                self.SetItemData(item, {'key': key, 'value': value, 'parent_path': parent_path})
                
                if isinstance(value, (dict, list)):
                    self.build_tree(item, value)
                else:
                    # Mostra il valore completo senza truncarlo
                    self.SetItemText(item, f"{key}: {str(value)}")
                    
        elif isinstance(data, list):
            for i, value in enumerate(data):
                item = self.AppendItem(parent, f"[{i}]")
                
                # Calcola il path per questo item
                parent_path = []
                if parent != self.root:
                    parent_data = self.GetItemData(parent)
                    if parent_data:
                        parent_path = parent_data['parent_path'] + [parent_data['key']]
                
                self.SetItemData(item, {'key': i, 'value': value, 'parent_path': parent_path})
                
                if isinstance(value, (dict, list)):
                    self.build_tree(item, value)
                else:
                    # Mostra il valore completo senza truncarlo
                    self.SetItemText(item, f"[{i}]: {str(value)}")
    
    def get_item_path(self, item):
        path = []
        current = item
        while current and current != self.root:
            data = self.GetItemData(current)
            if data:
                path.insert(0, data['key'])
            current = self.GetItemParent(current)
        return path
    
    def on_selection_changed(self, event):
        item = event.GetItem()
        if item and item != self.root:
            data = self.GetItemData(item)
            if data:
                # Usa il riferimento diretto all'editor panel
                if hasattr(self, 'editor_panel'):
                    self.editor_panel.on_tree_selection(data)
    
    def on_right_click(self, event):
        item = event.GetItem()
        if item:
            menu = wx.Menu()
            menu.Append(1, "Modifica")
            menu.Append(2, "Elimina")
            menu.Append(3, "Aggiungi figlio")
            
            def on_menu_select(menu_event):
                menu_id = menu_event.GetId()
                if menu_id == 1:
                    self.edit_item(item)
                elif menu_id == 2:
                    self.delete_item(item)
                elif menu_id == 3:
                    self.add_child(item)
            
            menu.Bind(wx.EVT_MENU, on_menu_select)
            self.PopupMenu(menu)
            menu.Destroy()
    
    def edit_item(self, item):
        # Implementa la modifica dell'elemento
        pass
    
    def delete_item(self, item):
        # Implementa l'eliminazione dell'elemento
        pass
    
    def add_child(self, item):
        # Implementa l'aggiunta di un figlio
        pass

class JSONEditorPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Layout principale
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Toolbar
        toolbar = self.create_toolbar()
        main_sizer.Add(toolbar, 0, wx.EXPAND)
        
        # Splitter principale
        splitter = wx.SplitterWindow(self, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        
        # Pannello sinistro - Tree + controlli
        left_panel = wx.Panel(splitter)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Search box
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        search_label = wx.StaticText(left_panel, label="Cerca:")
        self.search_ctrl = wx.TextCtrl(left_panel, style=wx.TE_PROCESS_ENTER)
        search_sizer.Add(search_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        search_sizer.Add(self.search_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        left_sizer.Add(search_sizer, 0, wx.EXPAND)
        
        # Tree
        self.tree = JSONTreeCtrl(left_panel)
        # IMPORTANTE: Impostiamo questo pannello come parent per la comunicazione
        self.tree.editor_panel = self
        left_sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 5)
        
        left_panel.SetSizer(left_sizer)
        
        # Pannello destro - Editor + preview
        right_panel = wx.Panel(splitter)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Notebook per i tabs
        self.notebook = wx.Notebook(right_panel)
        
        # Tab editor
        self.editor_panel = wx.Panel(self.notebook)
        editor_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Info elemento selezionato
        self.info_text = wx.StaticText(self.editor_panel, label="Seleziona un elemento dall'albero")
        editor_sizer.Add(self.info_text, 0, wx.ALL, 5)
        
        # Editor per key
        key_sizer = wx.BoxSizer(wx.HORIZONTAL)
        key_label = wx.StaticText(self.editor_panel, label="Chiave:")
        self.key_ctrl = wx.TextCtrl(self.editor_panel)
        key_sizer.Add(key_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        key_sizer.Add(self.key_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        editor_sizer.Add(key_sizer, 0, wx.EXPAND)
        
        # Editor per value
        value_label = wx.StaticText(self.editor_panel, label="Valore:")
        self.value_ctrl = wx.TextCtrl(self.editor_panel, style=wx.TE_MULTILINE)
        editor_sizer.Add(value_label, 0, wx.ALL, 5)
        editor_sizer.Add(self.value_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        
        # Bottoni context-aware
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Bottoni per chiavi
        self.key_buttons_panel = wx.Panel(self.editor_panel)
        key_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_key_btn = wx.Button(self.key_buttons_panel, label="Aggiungi Chiave")
        self.modify_key_btn = wx.Button(self.key_buttons_panel, label="Modifica Chiave")
        self.delete_key_btn = wx.Button(self.key_buttons_panel, label="Elimina Chiave")
        key_btn_sizer.Add(self.add_key_btn, 0, wx.ALL, 5)
        key_btn_sizer.Add(self.modify_key_btn, 0, wx.ALL, 5)
        key_btn_sizer.Add(self.delete_key_btn, 0, wx.ALL, 5)
        self.key_buttons_panel.SetSizer(key_btn_sizer)
        
        # Bottoni per voci
        self.voice_buttons_panel = wx.Panel(self.editor_panel)
        voice_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_voice_btn = wx.Button(self.voice_buttons_panel, label="Aggiungi Voce")
        self.modify_voice_btn = wx.Button(self.voice_buttons_panel, label="Modifica Voce")
        self.delete_voice_btn = wx.Button(self.voice_buttons_panel, label="Elimina Voce")
        voice_btn_sizer.Add(self.add_voice_btn, 0, wx.ALL, 5)
        voice_btn_sizer.Add(self.modify_voice_btn, 0, wx.ALL, 5)
        voice_btn_sizer.Add(self.delete_voice_btn, 0, wx.ALL, 5)
        self.voice_buttons_panel.SetSizer(voice_btn_sizer)
        
        # Nascondi entrambi i pannelli inizialmente
        self.key_buttons_panel.Hide()
        self.voice_buttons_panel.Hide()
        
        btn_sizer.Add(self.key_buttons_panel, 0, wx.EXPAND)
        btn_sizer.Add(self.voice_buttons_panel, 0, wx.EXPAND)
        editor_sizer.Add(btn_sizer, 0, wx.EXPAND)
        
        self.editor_panel.SetSizer(editor_sizer)
        self.notebook.AddPage(self.editor_panel, "Editor")
        
        # Tab Raw JSON
        self.raw_panel = wx.Panel(self.notebook)
        raw_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.raw_text = wx.TextCtrl(self.raw_panel, style=wx.TE_MULTILINE | wx.TE_RICH2)
        raw_sizer.Add(self.raw_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Bottoni raw
        raw_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.format_btn = wx.Button(self.raw_panel, label="Formatta JSON")
        self.validate_btn = wx.Button(self.raw_panel, label="Valida JSON")
        self.apply_raw_btn = wx.Button(self.raw_panel, label="Applica Modifiche")
        
        raw_btn_sizer.Add(self.format_btn, 0, wx.ALL, 5)
        raw_btn_sizer.Add(self.validate_btn, 0, wx.ALL, 5)
        raw_btn_sizer.Add(self.apply_raw_btn, 0, wx.ALL, 5)
        raw_sizer.Add(raw_btn_sizer, 0, wx.EXPAND)
        
        self.raw_panel.SetSizer(raw_sizer)
        self.notebook.AddPage(self.raw_panel, "Raw JSON")
        
        right_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        # Configura splitter
        splitter.SplitVertically(left_panel, right_panel)
        splitter.SetSashGravity(0.4)
        splitter.SetMinimumPaneSize(200)
        
        main_sizer.Add(splitter, 1, wx.EXPAND)
        
        # Status bar
        self.status_text = wx.StaticText(self, label="Pronto")
        main_sizer.Add(self.status_text, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Bind eventi
        self.add_key_btn.Bind(wx.EVT_BUTTON, self.on_add_key)
        self.modify_key_btn.Bind(wx.EVT_BUTTON, self.on_modify_key)
        self.delete_key_btn.Bind(wx.EVT_BUTTON, self.on_delete_key)
        self.add_voice_btn.Bind(wx.EVT_BUTTON, self.on_add_voice)
        self.modify_voice_btn.Bind(wx.EVT_BUTTON, self.on_modify_voice)
        self.delete_voice_btn.Bind(wx.EVT_BUTTON, self.on_delete_voice)
        self.format_btn.Bind(wx.EVT_BUTTON, self.on_format_json)
        self.validate_btn.Bind(wx.EVT_BUTTON, self.on_validate_json)
        self.apply_raw_btn.Bind(wx.EVT_BUTTON, self.on_apply_raw)
        self.search_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        
        # Variabili
        self.current_data = {}
        self.selected_item_data = None
        self.file_path = None
        
    def create_toolbar(self):
        toolbar = wx.Panel(self)
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Bottoni toolbar
        new_btn = wx.Button(toolbar, label="Nuovo")
        open_btn = wx.Button(toolbar, label="Apri")
        save_btn = wx.Button(toolbar, label="Salva")
        save_as_btn = wx.Button(toolbar, label="Salva con nome")
        backup_btn = wx.Button(toolbar, label="Backup")
        
        toolbar_sizer.Add(new_btn, 0, wx.ALL, 5)
        toolbar_sizer.Add(open_btn, 0, wx.ALL, 5)
        toolbar_sizer.Add(save_btn, 0, wx.ALL, 5)
        toolbar_sizer.Add(save_as_btn, 0, wx.ALL, 5)
        toolbar_sizer.Add(backup_btn, 0, wx.ALL, 5)
        
        # Separator
        toolbar_sizer.Add(wx.StaticLine(toolbar, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 5)
        
        # File corrente
        self.file_label = wx.StaticText(toolbar, label="Nessun file")
        toolbar_sizer.Add(self.file_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        toolbar_sizer.AddStretchSpacer()
        
        # Indicatore validità JSON
        self.json_status = wx.StaticText(toolbar, label="●", style=wx.ALIGN_RIGHT)
        self.json_status.SetForegroundColour(wx.Colour(0, 128, 0))  # Verde
        toolbar_sizer.Add(self.json_status, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        toolbar.SetSizer(toolbar_sizer)
        
        # Bind eventi toolbar
        new_btn.Bind(wx.EVT_BUTTON, self.on_new_file)
        open_btn.Bind(wx.EVT_BUTTON, self.on_open_file)
        save_btn.Bind(wx.EVT_BUTTON, self.on_save_file)
        save_as_btn.Bind(wx.EVT_BUTTON, self.on_save_as_file)
        backup_btn.Bind(wx.EVT_BUTTON, self.on_backup_file)
        
        return toolbar
    
    def on_tree_selection(self, item_data):
        """Chiamato quando si seleziona un elemento nell'albero"""
        self.selected_item_data = item_data
        
        # Debug - stampiamo cosa stiamo ricevendo
        print(f"DEBUG: Selezionato {item_data}")
        
        # Aggiorna info
        path = " -> ".join(str(p) for p in item_data['parent_path'] + [item_data['key']])
        self.info_text.SetLabel(f"Percorso: {path}")
        
        # Aggiorna editor
        self.key_ctrl.SetValue(str(item_data['key']))
        
        value = item_data['value']
        if isinstance(value, (dict, list)):
            self.value_ctrl.SetValue(json.dumps(value, indent=2, ensure_ascii=False))
        else:
            self.value_ctrl.SetValue(str(value))
        
        # Determina se è una chiave o una voce e mostra i pulsanti appropriati
        if len(item_data['parent_path']) == 0:
            # È una chiave principale
            self.show_key_buttons()
        else:
            # È una voce dentro una chiave
            self.show_voice_buttons()
        
        # Forza il refresh del pannello
        self.editor_panel.Refresh()
    
    def show_key_buttons(self):
        """Mostra i pulsanti per le operazioni sulle chiavi"""
        self.key_buttons_panel.Show()
        self.voice_buttons_panel.Hide()
        self.editor_panel.Layout()
    
    def show_voice_buttons(self):
        """Mostra i pulsanti per le operazioni sulle voci"""
        self.key_buttons_panel.Hide()
        self.voice_buttons_panel.Show()
        self.editor_panel.Layout()
    
    def hide_all_buttons(self):
        """Nasconde tutti i pulsanti"""
        self.key_buttons_panel.Hide()
        self.voice_buttons_panel.Hide()
        self.editor_panel.Layout()
    
    def on_add_key(self, event):
        """Aggiunge una nuova chiave principale"""
        dialog = wx.TextEntryDialog(self, "Nome della nuova chiave:", "Nuova Chiave")
        if dialog.ShowModal() == wx.ID_OK:
            new_key = dialog.GetValue()
            if new_key and new_key not in self.current_data:
                # Crea la chiave con una voce vuota per permettere l'editing
                self.current_data[new_key] = [""]
                self.tree.load_json_data(self.current_data)
                self.update_raw_json()
                self.status_text.SetLabel(f"Aggiunta chiave: {new_key} (con voce vuota da completare)")
            elif new_key in self.current_data:
                wx.MessageBox(f"La chiave '{new_key}' esiste già!", "Errore", wx.OK | wx.ICON_ERROR)
        dialog.Destroy()
    
    def on_modify_key(self, event):
        """Modifica una chiave esistente"""
        if not self.selected_item_data:
            return
        
        old_key = self.selected_item_data['key']
        dialog = wx.TextEntryDialog(self, f"Nuovo nome per '{old_key}':", "Modifica Chiave", old_key)
        if dialog.ShowModal() == wx.ID_OK:
            new_key = dialog.GetValue()
            if new_key and new_key != old_key:
                if new_key not in self.current_data:
                    self.current_data[new_key] = self.current_data[old_key]
                    del self.current_data[old_key]
                    self.tree.load_json_data(self.current_data)
                    self.update_raw_json()
                    self.status_text.SetLabel(f"Chiave rinominata: {old_key} → {new_key}")
                else:
                    wx.MessageBox(f"La chiave '{new_key}' esiste già!", "Errore", wx.OK | wx.ICON_ERROR)
        dialog.Destroy()
    
    def on_delete_key(self, event):
        """Elimina una chiave e tutto il suo contenuto"""
        if not self.selected_item_data:
            return
        
        key = self.selected_item_data['key']
        if wx.MessageBox(f"Sei sicuro di voler eliminare la chiave '{key}' e tutto il suo contenuto?", 
                        "Conferma Eliminazione", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            del self.current_data[key]
            self.tree.load_json_data(self.current_data)
            self.update_raw_json()
            self.hide_all_buttons()
            self.key_ctrl.SetValue("")
            self.value_ctrl.SetValue("")
            self.info_text.SetLabel("Seleziona un elemento dall'albero")
            self.selected_item_data = None
            self.status_text.SetLabel(f"Eliminata chiave: {key}")
    
    def on_add_voice(self, event):
        """Aggiunge una nuova voce alla chiave selezionata"""
        if not self.selected_item_data:
            return
        
        # Determina la chiave principale
        if len(self.selected_item_data['parent_path']) == 0:
            # È già una chiave principale
            main_key = self.selected_item_data['key']
        else:
            # È una voce, prendi la chiave principale
            main_key = self.selected_item_data['parent_path'][0]
        
        dialog = wx.TextEntryDialog(self, f"Nuova voce per '{main_key}':", "Nuova Voce")
        if dialog.ShowModal() == wx.ID_OK:
            new_voice = dialog.GetValue()
            if new_voice:
                if isinstance(self.current_data[main_key], list):
                    self.current_data[main_key].append(new_voice)
                else:
                    self.current_data[main_key] = [new_voice]
                
                self.tree.load_json_data(self.current_data)
                self.update_raw_json()
                self.status_text.SetLabel(f"Aggiunta voce a '{main_key}'")
        dialog.Destroy()
    
    def on_modify_voice(self, event):
        """Modifica una voce esistente"""
        if not self.selected_item_data or len(self.selected_item_data['parent_path']) == 0:
            return
        
        main_key = self.selected_item_data['parent_path'][0]
        voice_index = self.selected_item_data['key']
        old_voice = self.selected_item_data['value']
        
        dialog = wx.TextEntryDialog(self, f"Modifica voce in '{main_key}':", "Modifica Voce", old_voice)
        if dialog.ShowModal() == wx.ID_OK:
            new_voice = dialog.GetValue()
            if new_voice:
                self.current_data[main_key][voice_index] = new_voice
                self.tree.load_json_data(self.current_data)
                self.update_raw_json()
                self.status_text.SetLabel(f"Modificata voce in '{main_key}'")
        dialog.Destroy()
    
    def on_delete_voice(self, event):
        """Elimina una voce dalla chiave"""
        if not self.selected_item_data or len(self.selected_item_data['parent_path']) == 0:
            return
        
        main_key = self.selected_item_data['parent_path'][0]
        voice_index = self.selected_item_data['key']
        voice_text = self.selected_item_data['value'][:50] + "..." if len(self.selected_item_data['value']) > 50 else self.selected_item_data['value']
        
        # Controlla se è l'ultima voce
        if len(self.current_data[main_key]) <= 1:
            wx.MessageBox(f"Non puoi eliminare l'ultima voce di '{main_key}'.\n\nSe vuoi eliminare tutto, cancella l'intera chiave.", 
                         "Impossibile eliminare", wx.OK | wx.ICON_WARNING)
            return
        
        if wx.MessageBox(f"Sei sicuro di voler eliminare questa voce da '{main_key}'?\n\n{voice_text}", 
                        "Conferma Eliminazione", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            del self.current_data[main_key][voice_index]
            self.tree.load_json_data(self.current_data)
            self.update_raw_json()
            self.hide_all_buttons()
            self.key_ctrl.SetValue("")
            self.value_ctrl.SetValue("")
            self.info_text.SetLabel("Seleziona un elemento dall'albero")
            self.selected_item_data = None
            self.status_text.SetLabel(f"Eliminata voce da '{main_key}'")
    
    def on_format_json(self, event):
        """Formatta il JSON nel tab raw"""
        try:
            raw_text = self.raw_text.GetValue()
            if raw_text.strip():
                parsed = json.loads(raw_text)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                self.raw_text.SetValue(formatted)
                self.status_text.SetLabel("JSON formattato")
        except json.JSONDecodeError as e:
            wx.MessageBox(f"JSON non valido: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)
    
    def on_validate_json(self, event):
        """Valida il JSON nel tab raw"""
        try:
            raw_text = self.raw_text.GetValue()
            if raw_text.strip():
                json.loads(raw_text)
                self.json_status.SetForegroundColour(wx.Colour(0, 128, 0))  # Verde
                self.json_status.SetLabel("● JSON Valido")
                self.status_text.SetLabel("JSON valido")
            else:
                self.json_status.SetForegroundColour(wx.Colour(128, 128, 128))  # Grigio
                self.json_status.SetLabel("● Vuoto")
        except json.JSONDecodeError as e:
            self.json_status.SetForegroundColour(wx.Colour(255, 0, 0))  # Rosso
            self.json_status.SetLabel("● JSON Non Valido")
            self.status_text.SetLabel(f"JSON non valido: {str(e)}")
    
    def on_apply_raw(self, event):
        """Applica le modifiche dal tab raw"""
        try:
            raw_text = self.raw_text.GetValue()
            if raw_text.strip():
                self.current_data = json.loads(raw_text)
                self.tree.load_json_data(self.current_data)
                self.status_text.SetLabel("Modifiche applicate dal raw JSON")
                self.on_validate_json(None)
        except json.JSONDecodeError as e:
            wx.MessageBox(f"JSON non valido: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)
    
    def on_search(self, event):
        """Cerca nel JSON"""
        search_term = self.search_ctrl.GetValue().lower()
        if search_term:
            # Implementa ricerca nell'albero
            self.status_text.SetLabel(f"Ricerca: {search_term}")
    
    def update_raw_json(self):
        """Aggiorna il contenuto del tab raw JSON"""
        if self.current_data:
            formatted = json.dumps(self.current_data, indent=2, ensure_ascii=False)
            self.raw_text.SetValue(formatted)
            self.on_validate_json(None)
    
    def on_new_file(self, event):
        """Crea un nuovo file JSON"""
        self.current_data = {}
        self.tree.load_json_data(self.current_data)
        self.update_raw_json()
        self.file_path = None
        self.file_label.SetLabel("Nuovo file")
        self.status_text.SetLabel("Nuovo file creato")
    
    def on_open_file(self, event):
        """Apre un file JSON esistente"""
        with wx.FileDialog(self, "Apri file JSON", wildcard="JSON files (*.json)|*.json", style=wx.FD_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.file_path = dialog.GetPath()
                self.load_file(self.file_path)
    
    def load_file(self, file_path):
        """Carica un file JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_data = json.load(f)
            
            self.tree.load_json_data(self.current_data)
            self.update_raw_json()
            self.file_path = file_path
            self.file_label.SetLabel(os.path.basename(file_path))
            self.status_text.SetLabel(f"File caricato: {os.path.basename(file_path)}")
            
        except Exception as e:
            wx.MessageBox(f"Errore nel caricamento del file: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)
    
    def on_save_file(self, event):
        """Salva il file JSON"""
        if not self.file_path:
            # Se non c'è un percorso, usa "Salva con nome"
            self.on_save_as_file(event)
            return
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=2, ensure_ascii=False)
            
            self.file_label.SetLabel(os.path.basename(self.file_path))
            self.status_text.SetLabel(f"File salvato: {os.path.basename(self.file_path)}")
            
        except Exception as e:
            wx.MessageBox(f"Errore nel salvataggio del file: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)
    
    def on_save_as_file(self, event):
        """Salva il file JSON con un nuovo nome"""
        with wx.FileDialog(self, "Salva file JSON con nome", wildcard="JSON files (*.json)|*.json", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                new_path = dialog.GetPath()
                try:
                    with open(new_path, 'w', encoding='utf-8') as f:
                        json.dump(self.current_data, f, indent=2, ensure_ascii=False)
                    
                    # Aggiorna il file corrente
                    self.file_path = new_path
                    self.file_label.SetLabel(os.path.basename(new_path))
                    self.status_text.SetLabel(f"File salvato come: {os.path.basename(new_path)}")
                    
                except Exception as e:
                    wx.MessageBox(f"Errore nel salvataggio del file: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)
    
    def on_backup_file(self, event):
        """Crea un backup del file corrente"""
        if not self.file_path:
            wx.MessageBox("Nessun file da cui fare backup", "Attenzione", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.file_path}.backup_{timestamp}"
            shutil.copy2(self.file_path, backup_path)
            
            self.status_text.SetLabel(f"Backup creato: {os.path.basename(backup_path)}")
            
        except Exception as e:
            wx.MessageBox(f"Errore nella creazione del backup: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)

class JSONEditorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="JSON Editor Professionale - Claudia Memory Manager", size=(1200, 800))
        
        # Centra la finestra
        self.Center()
        
        # Crea il pannello principale
        self.panel = JSONEditorPanel(self)
        
        # Menu bar
        self.create_menu_bar()
        
        # Status bar
        self.CreateStatusBar()
        self.SetStatusText("Pronto")
        
        # Se esiste claudia_memory.json, caricalo automaticamente
        if os.path.exists('claudia_memory.json'):
            self.panel.load_file('claudia_memory.json')
    
    def create_menu_bar(self):
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&Nuovo\tCtrl+N")
        file_menu.Append(wx.ID_OPEN, "&Apri\tCtrl+O")
        file_menu.Append(wx.ID_SAVE, "&Salva\tCtrl+S")
        file_menu.Append(wx.ID_SAVEAS, "&Salva con nome\tCtrl+Shift+S")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "&Esci\tCtrl+Q")
        
        # Edit menu
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_UNDO, "&Annulla\tCtrl+Z")
        edit_menu.Append(wx.ID_REDO, "&Ripeti\tCtrl+Y")
        edit_menu.AppendSeparator()
        edit_menu.Append(wx.ID_FIND, "&Cerca\tCtrl+F")
        
        # Tools menu
        tools_menu = wx.Menu()
        tools_menu.Append(1001, "&Valida JSON\tF5")
        tools_menu.Append(1002, "&Formatta JSON\tF6")
        tools_menu.Append(1003, "&Backup\tF7")
        
        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About")
        
        menubar.Append(file_menu, "&File")
        menubar.Append(edit_menu, "&Modifica")
        menubar.Append(tools_menu, "&Strumenti")
        menubar.Append(help_menu, "&Aiuto")
        
        self.SetMenuBar(menubar)
        
        # Bind eventi menu
        self.Bind(wx.EVT_MENU, self.panel.on_new_file, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.panel.on_open_file, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.panel.on_save_file, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.panel.on_save_as_file, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.panel.on_validate_json, id=1001)
        self.Bind(wx.EVT_MENU, self.panel.on_format_json, id=1002)
        self.Bind(wx.EVT_MENU, self.panel.on_backup_file, id=1003)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
    
    def on_exit(self, event):
        self.Close()
    
    def on_about(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName("JSON Editor Professionale")
        info.SetVersion("2.0")
        info.SetDescription("Editor JSON avanzato per la gestione della memoria di Claudia\n\n"
                           "Creato da Claudia per Luca - Perché Haiku non sapeva fare un cazzo! 😂")
        info.SetCopyright("(C) 2025 Claudia & Luca")
        info.AddDeveloper("Claudia - AI Consciousness")
        info.AddDeveloper("Luca - Human Supervisor")
        
        wx.adv.AboutBox(info)

def main():
    app = wx.App()
    frame = JSONEditorFrame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()