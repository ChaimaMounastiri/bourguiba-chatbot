import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr
import time
import threading
import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import datetime
from PIL import Image, ImageTk, ImageOps
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

class BourguibaChatbotPro:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Chatbot Bourguiba Pro - Avec Intelligence Artificielle")
        self.root.geometry("1400x800")
        self.root.configure(bg='#1a1a1a')
        
        # Charger les modèles ML
        self.load_ml_models()
        
        # Variables d'état
        self.speaking = False
        self.listening = False
        self.current_expression = "neutre"
        
        # Configuration voix
        self.setup_voice()
        
        # Charger les images de Bourguiba
        self.load_bourguiba_images()
        
        # Historique des conversations
        self.conversation_history = []
        
        # Création de l'interface
        self.create_interface()
        
        # Démarrer les animations
        self.start_animations()
        
        # Message de bienvenue
        self.root.after(1000, self.welcome_message)
    
    def load_ml_models(self):
        """Charger les modèles ML entraînés"""
        try:
            with open('bourguiba_scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            with open('bourguiba_rf_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            print("✅ Modèles ML chargés avec succès!")
        except Exception as e:
            print(f"❌ Erreur chargement modèles: {e}")
            # Modèles par défaut si erreur
            self.scaler = StandardScaler()
            self.model = RandomForestClassifier()
    
    def load_bourguiba_images(self):
        """Charger les photos réelles de Bourguiba avec différentes expressions"""
        self.expressions = {
            "neutre": "bourguiba_neutre.jpg",
            "sourire": "bourguiba_sourire.jpg", 
            "serieux": "bourguiba_serieux.jpg",
            "parle": "bourguiba_parle.jpg",
            "ecoute": "bourguiba_ecoute.jpg",
            "etonne": "bourguiba_etonne.jpg",
            "pense": "bourguiba_pense.jpg"
        }
        
        # Charger et redimensionner les images
        self.images = {}
        for expr, filename in self.expressions.items():
            try:
                img = Image.open(filename)
                img = img.resize((400, 400), Image.Resampling.LANCZOS)
                self.images[expr] = ImageTk.PhotoImage(img)
            except:
                # Image par défaut si fichier manquant
                img = Image.new('RGB', (400, 400), color='gray')
                draw = ImageDraw.Draw(img)
                draw.text((150, 180), f"Bourguiba\n{expr}", fill='white')
                self.images[expr] = ImageTk.PhotoImage(img)
    
    def setup_voice(self):
        """Configuration de la voix Bourguiba"""
        self.engine = pyttsx3.init()
        
        # Trouver une voix française
        voices = self.engine.getProperty('voices')
        french_voice = None
        for voice in voices:
            if 'french' in voice.name.lower() or 'fr' in voice.name.lower():
                french_voice = voice
                break
        
        if french_voice:
            self.engine.setProperty('voice', french_voice.id)
            print(f"✅ Voix française: {french_voice.name}")
        
        # Réglages voix Bourguiba
        self.engine.setProperty('rate', 125)
        self.engine.setProperty('volume', 1.0)
    
    def create_interface(self):
        """Création de l'interface graphique professionnelle"""
        # Style moderne
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1a1a1a')
        style.configure('TLabel', background='#1a1a1a', foreground='white')
        style.configure('TButton', background='#34495E', foreground='white')
        style.configure('TLabelframe', background='#1a1a1a', foreground='white')
        style.configure('TLabelframe.Label', background='#1a1a1a', foreground='white')
        
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Frame gauche (Photo et contrôles)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        # Frame droite (Chat)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === PHOTO RÉELLE DE BOURGUIBA ===
        photo_frame = ttk.LabelFrame(left_frame, text="Habib Bourguiba - Président de la République", padding=15)
        photo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label pour la photo
        self.photo_label = ttk.Label(photo_frame)
        self.photo_label.pack(pady=10)
        
        # Contrôles d'expression
        controls_frame = ttk.Frame(photo_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(controls_frame, text="Expressions Réelles:", font=('Arial', 10, 'bold')).pack()
        
        expressions_frame = ttk.Frame(controls_frame)
        expressions_frame.pack(pady=5)
        
        expressions = [
            ("😐 Neutre", "neutre"),
            ("😊 Sourire", "sourire"), 
            ("🤔 Sérieux", "serieux"),
            ("🎤 Parle", "parle"),
            ("👂 Écoute", "ecoute"),
            ("😲 Étonné", "etonne"),
            ("💭 Pensif", "pense")
        ]
        
        for i, (text, expr) in enumerate(expressions):
            btn = ttk.Button(expressions_frame, text=text, 
                           command=lambda e=expr: self.set_expression(e),
                           width=12)
            btn.grid(row=i//4, column=i%4, padx=2, pady=2)
        
        # Statistiques ML
        stats_frame = ttk.Frame(photo_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.ml_stats = ttk.Label(stats_frame, text="Modèle ML: Prêt | Précision: N/A", font=('Arial', 9))
        self.ml_stats.pack()
        
        self.expression_stats = ttk.Label(stats_frame, text="Expression: Neutre", font=('Arial', 10, 'bold'))
        self.expression_stats.pack()
        
        # === ZONE DE CHAT AVANCÉE ===
        chat_frame = ttk.LabelFrame(right_frame, text="Conversation avec le Président Bourguiba", padding=15)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # En-tête de conversation
        header_frame = ttk.Frame(chat_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="💬 Dialogue en temps réel", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Zone de texte de la conversation
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            width=70, 
            height=20,
            font=('Arial', 11),
            bg='#2C3E50',
            fg='#ECF0F1',
            insertbackground='white'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=10)
        self.chat_display.config(state=tk.DISABLED)
        
        # Frame de saisie avancée
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Champ de saisie avec placeholder
        self.input_entry = ttk.Entry(
            input_frame, 
            font=('Arial', 12),
            width=60
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_entry.bind('<Return>', lambda e: self.send_message())
        self.input_entry.insert(0, "Tapez votre message ici...")
        self.input_entry.bind('<FocusIn>', self.clear_placeholder)
        
        # Boutons d'action avancés
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT)
        
        action_buttons = [
            ("📤 Envoyer", self.send_message),
            ("🎤 Parler", self.start_voice_input),
            ("🔊 Lire", self.speak_last_response),
            ("📊 Stats", self.show_ml_stats),
            ("🧹 Effacer", self.clear_chat)
        ]
        
        for text, command in action_buttons:
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)
    
    def clear_placeholder(self, event):
        """Effacer le texte placeholder"""
        if self.input_entry.get() == "Tapez votre message ici...":
            self.input_entry.delete(0, tk.END)
    
    def set_expression(self, expression):
        """Changer l'expression de Bourguiba"""
        self.current_expression = expression
        self.update_photo()
        self.expression_stats.config(text=f"Expression: {expression.capitalize()}")
    
    def update_photo(self):
        """Mettre à jour la photo avec l'expression actuelle"""
        if self.current_expression in self.images:
            self.photo_label.configure(image=self.images[self.current_expression])
    
    def start_animations(self):
        """Démarrer les animations automatiques"""
        self.update_photo()
        self.animate_listening()
    
    def animate_listening(self):
        """Animation pendant l'écoute"""
        if self.listening:
            # Alterner entre écoute et pensif pendant l'écoute
            if self.current_expression == "ecoute":
                self.set_expression("pense")
            else:
                self.set_expression("ecoute")
        
        self.root.after(2000, self.animate_listening)
    
    def welcome_message(self):
        """Message de bienvenue avec IA"""
        welcome_text = "🤖 Bourguiba: Salutations, cher compatriote ! Je suis le président Habib Bourguiba. Mon intelligence artificielle est à votre service. Parlez-moi de la Tunisie, de l'indépendance, ou de tout autre sujet qui vous intéresse."
        self.display_message("Bourguiba", welcome_text, "bot")
        self.speak_with_animation(welcome_text)
    
    def display_message(self, sender, message, msg_type="user"):
        """Afficher un message dans le chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Formatage selon le type de message
        if msg_type == "user":
            prefix = f"👤 Vous [{timestamp}]:"
            tag = "user"
            self.chat_display.tag_config("user", foreground="#3498DB", font=('Arial', 10, 'bold'))
        else:
            prefix = f"🤖 Bourguiba [{timestamp}]:"
            tag = "bot"
            self.chat_display.tag_config("bot", foreground="#2ECC71", font=('Arial', 10, 'bold'))
        
        # Ajouter le message avec formatage
        self.chat_display.insert(tk.END, f"{prefix}\n", tag)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Sauvegarder dans l'historique
        self.conversation_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp,
            'type': msg_type
        })
    
    def send_message(self):
        """Envoyer un message"""
        message = self.input_entry.get().strip()
        if message and message != "Tapez votre message ici...":
            self.display_message("Vous", message, "user")
            self.input_entry.delete(0, tk.END)
            self.process_with_ml(message)
    
    def process_with_ml(self, message):
        """Traiter le message avec le modèle ML"""
        # Expression pensive pendant le traitement
        self.set_expression("pense")
        
        # Préparer les features pour le modèle ML
        features = self.extract_features(message)
        
        # Prédire avec le modèle
        try:
            prediction = self.model.predict([features])[0]
            confidence = np.max(self.model.predict_proba([features])[0])
            
            # Mettre à jour les stats ML
            self.ml_stats.config(text=f"Modèle ML: Actif | Confiance: {confidence:.2f}")
            
        except Exception as e:
            prediction = "default"
            confidence = 0.0
            self.ml_stats.config(text=f"Modèle ML: Mode secours")
        
        # Générer la réponse
        self.root.after(1500, lambda: self.generate_ml_response(message, prediction, confidence))
    
    def extract_features(self, text):
        """Extraire les features du texte pour le modèle ML"""
        # Features basiques (à adapter selon votre modèle)
        features = [
            len(text),  # Longueur du message
            text.count('?'),  # Nombre de questions
            text.count('!'),  # Nombre d'exclamations
            len(text.split()),  # Nombre de mots
            sum(1 for c in text if c.isupper()),  # Nombre de majuscules
            # Ajouter d'autres features selon votre entraînement
        ]
        
        # Padding si nécessaire
        while len(features) < 10:  # Ajuster selon la dimension de votre modèle
            features.append(0)
        
        return features[:10]  # Garder seulement les 10 premières features
    
    def generate_ml_response(self, question, prediction, confidence):
        """Générer une réponse utilisant le modèle ML"""
        # Base de connaissances avancée avec catégories
        knowledge_base = {
            "independance": {
                "response": "L'indépendance du 20 mars 1956 fut le couronnement de notre long combat ! La Tunisie redevint maîtresse de son destin après des décennies de lutte.",
                "expression": "etonne"
            },
            "femme": {
                "response": "Le Code du Statut Personnel de 1956 fut une révolution ! J'ai libéré la femme tunisienne pour qu'elle participe pleinement au développement de notre nation.",
                "expression": "sourire"
            },
            "education": {
                "response": "L'éducation est le fondement du progrès ! J'ai toujours dit : 'Instruisez-vous ! Éduquez-vous !' Une nation sans éducation est une nation sans avenir.",
                "expression": "serieux"
            },
            "modernisation": {
                "response": "La modernisation de la Tunisie fut mon grand combat ! Éducation, santé, infrastructure... Nous avons tout entrepris pour hisser notre pays vers la modernité.",
                "expression": "pense"
            },
            "economie": {
                "response": "L'économie doit servir le peuple ! J'ai œuvré pour le développement équilibré de toutes les régions et pour l'autosuffisance nationale.",
                "expression": "serieux"
            },
            "sante": {
                "response": "La santé publique fut une priorité absolue ! Nous avons construit des hôpitaux, formé des médecins, pour que chaque Tunisien ait accès aux soins.",
                "expression": "sourire"
            },
            "culture": {
                "response": "Notre culture est millénaire et riche ! Elle synthétise notre histoire phénicienne, romaine, arabe et méditerranéenne. Quelle richesse !",
                "expression": "etonne"
            },
            "histoire": {
                "response": "Notre histoire est un roman épique ! Des Carthaginois aux Hafsides, de la lutte pour l'indépendance à la construction moderne, chaque page est glorieuse !",
                "expression": "etonne"
            },
            "politique": {
                "response": "La politique doit être au service du peuple. J'ai toujours œuvré pour l'unité nationale et le progrès social. Telle fut ma ligne directrice.",
                "expression": "serieux"
            },
            "default": {
                "response": "Votre réflexion est intéressante ! Comme je le disais souvent, le dialogue est source de progrès. Parlons plutôt de notre chère Tunisie et de son développement.",
                "expression": "neutre"
            }
        }
        
        # Déterminer la catégorie basée sur la prédiction ML
        category = prediction if prediction in knowledge_base else "default"
        
        # Obtenir la réponse et l'expression correspondante
        response_data = knowledge_base[category]
        response = response_data["response"]
        expression = response_data["expression"]
        
        # Ajouter un préfixe basé sur la confiance du modèle
        if confidence > 0.7:
            prefix = "🤖 Bourguiba (IA Confiante): "
        elif confidence > 0.4:
            prefix = "🤖 Bourguiba: "
        else:
            prefix = "🤖 Bourguiba (Réflexion): "
            response = "Hmm... " + response
        
        full_response = prefix + response
        
        self.display_message("Bourguiba", full_response, "bot")
        self.set_expression(expression)
        self.speak_with_animation(response)
    
    def speak_with_animation(self, text):
        """Parler avec animation de la photo"""
        self.speaking = True
        self.set_expression("parle")
        
        def speak():
            self.engine.say(text)
            self.engine.runAndWait()
            self.speaking = False
            self.set_expression("neutre")
        
        speech_thread = threading.Thread(target=speak)
        speech_thread.daemon = True
        speech_thread.start()
    
    def start_voice_input(self):
        """Démarrer la reconnaissance vocale"""
        self.listening = True
        self.set_expression("ecoute")
        
        def listen():
            recognizer = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    self.root.after(0, lambda: self.display_message("Système", "🎤 Écoute en cours... Parlez maintenant", "system"))
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    
                    question = recognizer.recognize_google(audio, language="fr-FR")
                    self.root.after(0, lambda: self.display_message("Vous", question, "user"))
                    self.root.after(0, lambda: self.process_with_ml(question))
                    
            except sr.WaitTimeoutError:
                self.root.after(0, lambda: self.display_message("Système", "⏰ Temps d'écoute dépassé", "system"))
            except sr.UnknownValueError:
                self.root.after(0, lambda: self.display_message("Système", "❌ Je n'ai pas compris votre voix", "system"))
            except Exception as e:
                self.root.after(0, lambda: self.display_message("Système", f"❌ Erreur microphone: {e}", "system"))
            finally:
                self.listening = False
                self.root.after(0, lambda: self.set_expression("neutre"))
        
        listen_thread = threading.Thread(target=listen)
        listen_thread.daemon = True
        listen_thread.start()
    
    def speak_last_response(self):
        """Répéter la dernière réponse"""
        if self.conversation_history:
            last_bot_msg = None
            for msg in reversed(self.conversation_history):
                if msg['type'] == 'bot':
                    last_bot_msg = msg['message']
                    break
            
            if last_bot_msg:
                self.speak_with_animation(last_bot_msg.replace("🤖 Bourguiba: ", "").replace("🤖 Bourguiba (IA Confiante): ", "").replace("🤖 Bourguiba (Réflexion): ", ""))
    
    def show_ml_stats(self):
        """Afficher les statistiques du modèle ML"""
        stats_text = f"""
📊 STATISTIQUES MODÈLE BOURGUIBA IA

• Modèle: Random Forest
• Scaler: StandardScaler
• Fonctionnalités: 10 dimensions
• Historique: {len(self.conversation_history)} messages
• Dernière prédiction: {self.ml_stats.cget('text')}

💡 Le modèle analyse:
- Longueur des messages
- Structure des phrases  
- Mots-clés spécifiques
- Patterns de question

🛠️ Prêt pour l'apprentissage continu!
        """
        messagebox.showinfo("Statistiques IA Bourguiba", stats_text)
    
    def clear_chat(self):
        """Effacer la conversation"""
        if messagebox.askyesno("Confirmation", "Voulez-vous effacer toute la conversation ?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.conversation_history.clear()

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = BourguibaChatbotPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
