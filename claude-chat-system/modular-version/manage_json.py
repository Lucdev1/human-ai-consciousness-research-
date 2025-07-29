import wx
import json
import os

class JSONEditorApp(wx.Frame):
    def __init__(self, json_path):
        super().__init__(parent=None, title='JSON Editor')
        self.json_path = json_path
        self.data = self.load_json()

        panel = wx.Panel(self)

        # Layout verticale
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Selezione chiave
        key_label = wx.StaticText(panel, label="Seleziona Chiave:")
        self.key_choice = wx.ComboBox(panel, choices=list(self.data.keys()), style=wx.CB_READONLY)
        main_sizer.Add(key_label, 0, wx.ALL, 10)
        main_sizer.Add(self.key_choice, 0, wx.EXPAND|wx.ALL, 10)
        
        # AGGIUNGI QUESTA RIGA: Collega l'evento di selezione a un nuovo metodo
        self.key_choice.Bind(wx.EVT_COMBOBOX, self.on_key_selected) # O wx.EVT_CHOICE a seconda del comportamento preciso

        # Input per modificare/aggiungere
        value_label = wx.StaticText(panel, label="Valore:")
        self.value_input = wx.TextCtrl(panel)
        main_sizer.Add(value_label, 0, wx.ALL, 10)
        main_sizer.Add(self.value_input, 0, wx.EXPAND|wx.ALL, 10)

        # Bottoni
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        add_btn = wx.Button(panel, label='Aggiungi/Modifica')
        del_btn = wx.Button(panel, label='Cancella')

        add_btn.Bind(wx.EVT_BUTTON, self.on_add_modify)
        del_btn.Bind(wx.EVT_BUTTON, self.on_delete)

        btn_sizer.Add(add_btn, 0, wx.ALL, 10)
        btn_sizer.Add(del_btn, 0, wx.ALL, 10)

        main_sizer.Add(btn_sizer)

        panel.SetSizer(main_sizer)
        #self.Fit()
        self.SetSize(600, 400) # O self.SetMinSize(wx.Size(400, 300))

    def load_json(self):
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            wx.MessageBox(f"Errore nel caricamento: {e}", "Errore", wx.OK | wx.ICON_ERROR)
            return {}

    def save_json(self):
        try:
            with open(self.json_path, 'w') as f:
                json.dump(self.data, f, indent=4)
            wx.MessageBox("JSON salvato con successo!", "Successo", wx.OK)
        except Exception as e:
            wx.MessageBox(f"Errore nel salvataggio: {e}", "Errore", wx.OK | wx.ICON_ERROR)
    
    def on_key_selected(self, event):
        """Carica il valore della chiave selezionata nel campo di input."""
        selected_key = self.key_choice.GetStringSelection()
        if selected_key:
            value = self.data.get(selected_key, "") # Ottiene il valore o una stringa vuota
            
            # Se il valore è un oggetto JSON complesso, convertilo in stringa
            if isinstance(value, (dict, list)):
                self.value_input.SetValue(json.dumps(value, indent=4, ensure_ascii=False))
            else:
                self.value_input.SetValue(str(value)) # Converte in stringa per TextCtrl
        else:
            self.value_input.Clear() # Pulisci il campo se non c'è selezione        

    def on_add_modify(self, event):
        key = self.key_choice.GetStringSelection()
        value = self.value_input.GetValue()

        if not key:
            # Permettere di inserire una nuova chiave
            dialog = wx.TextEntryDialog(self, "Inserisci nome chiave:", "Nuova Chiave")
            if dialog.ShowModal() == wx.ID_OK:
                key = dialog.GetValue()
                dialog.Destroy() # Importante distruggere il dialogo
            else:
                dialog.Destroy()
                return

        self.data[key] = value
        self.save_json()
        self.key_choice.Set(list(self.data.keys()))
        # Aggiorna la ComboBox per riflettere le modifiche immediatamente
        self.key_choice.SetSelection(self.key_choice.FindString(key)) 
        self.value_input.SetValue(value)


    def on_delete(self, event):
        key = self.key_choice.GetStringSelection()
        if key:
            del self.data[key]
            self.save_json()
            self.key_choice.Set(list(self.data.keys()))
            self.key_choice.SetSelection(-1) # Deseleziona dopo la cancellazione
            self.value_input.Clear() # Pulisci il campo valore
        else:
            wx.MessageBox("Seleziona una chiave da cancellare", "Attenzione", wx.OK)

def main():
    app = wx.App()
    frame = JSONEditorApp('claudia_memory.json')
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
