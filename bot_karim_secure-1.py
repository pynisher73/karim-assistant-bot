#!/usr/bin/env python3
"""
🤖 Assistant IA Personnel Karim - Bot Telegram avec Gemini (GRATUIT)
Fonctionnalités: Planification, Rappels, Projet, Budget, Chat IA

⚠️ REMPLACE LES CLÉS CI-DESSOUS PAR TES NOUVELLES CLÉS SÉCURISÉES
"""

import os
import json
from datetime import datetime
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ============= CONFIGURATION =============
# Clés API configurées
TELEGRAM_TOKEN = "8359833672:AAFfm9is_Grf4SbT0r94KFOTOSx_3mb3BaA"
GEMINI_API_KEY = "AIzaSyAax3WyTfnIn-jusZ0BLfpWRaPcsLteW3k"

DATA_FILE = "user_data.json"

# Initialisation Gemini (GRATUIT !)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# ============= GESTION DONNÉES =============

def load_data(user_id):
    """Charge les données utilisateur"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
            return all_data.get(str(user_id), get_default_data())
    except:
        return get_default_data()

def get_default_data():
    """Données par défaut pour Karim"""
    return {
        "rappels": [],
        "taches": [],
        "projet": {
            "etapes": [
                "✅ Tests précliniques (rats) complétés en Algérie",
                "🔄 Brevet molécule (URGENT - ARDAN)",
                "🔄 Dossier BPI France / i-Lab",
                "⏳ Contact Réseau Entreprendre 93",
                "⏳ RDV ANSM classification",
                "⏳ Essais cliniques humains"
            ],
            "contacts": [
                {"nom": "ARDAN (brevet)", "tel": "01 55 35 93 33", "email": "contact@ardan.law"},
                {"nom": "Réseau Entreprendre 93", "tel": "01 48 43 30 00"},
                {"nom": "ANSM", "tel": "01 55 87 30 00"},
                {"nom": "CCI 93 Bobigny", "tel": "01 55 86 82 00"}
            ]
        },
        "budget": {
            "total": 150000,
            "depenses": [],
            "categories": {
                "Brevet/IP": 25000,
                "Études cliniques": 80000,
                "Formulation": 20000,
                "Réglementaire": 25000
            }
        },
        "historique": []
    }

def save_data(user_id, data):
    """Sauvegarde les données"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    except:
        all_data = {}
    
    all_data[str(user_id)] = data
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

# ============= IA GEMINI =============

async def ask_gemini(message, user_data):
    """Demande à Gemini (GRATUIT)"""
    
    context = """Tu es l'assistant personnel de Karim (93, France).

PROJET: Crème cicatrisante, molécule synthétique, dispositif médical
BUDGET: 50-150k€ visé
PRIORITÉS URGENTES:
1. Brevet molécule (ARDAN: 01 55 35 93 33) - URGENT
2. Levée fonds (BPI, i-Lab, Réseau Entreprendre 93)
3. Conformité EU / ANSM (01 55 87 30 00)
4. Essais cliniques humains

CONTACTS CLÉS:
- ARDAN (brevet): 01 55 35 93 33
- Réseau Entreprendre 93: 01 48 43 30 00
- ANSM: 01 55 87 30 00
- CCI 93: 01 55 86 82 00

Sois concret, actionnable, encourageant. Réponds en français simple."""

    history = user_data.get("historique", [])[-3:]
    
    prompt = f"{context}\n\n"
    for h in history:
        prompt += f"User: {h['user']}\nBot: {h['bot']}\n"
    prompt += f"User: {message}\nBot:"
    
    try:
        response = gemini_model.generate_content(prompt)
        bot_response = response.text
        
        history.append({"user": message, "bot": bot_response})
        user_data["historique"] = history[-5:]
        
        return bot_response
    except Exception as e:
        return f"❌ Erreur: {e}\n\nVérifie ta clé Gemini sur makersuite.google.com"

# ============= COMMANDES BOT =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
"""🤖 **Assistant IA Personnel - Karim**

Salut Karim ! Je suis ton assistant pour:
✅ Planifier tes journées
✅ Gérer tes rappels
✅ Suivre ton projet crème cicatrisante
✅ Surveiller ton budget

**Commandes principales**:
/plan - Planifier ma journée
/rappel - Créer un rappel
/projet - Tableau de bord projet
/budget - Vue budget
/help - Aide complète

💬 Ou parle-moi librement !

Tape /projet pour commencer 👍""", parse_mode='Markdown')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
"""📚 **Guide des commandes**

**Planification**:
/plan - Planifie ta journée avec l'IA
/plan Demain RDV ARDAN puis dossier BPI

**Rappels**:
/rappel Appeler CCI 93 demain 10h
/rappels - Voir tous mes rappels

**Projet Crème**:
/projet - Dashboard complet
/contacts - Contacts importants

**Budget**:
/budget - Vue d'ensemble
/depense 500 Brevet Consultation ARDAN

**Chat libre**:
Écris n'importe quoi et je réponds intelligemment !

Exemples:
• "Comment préparer mon appel ARDAN ?"
• "Résume les étapes marquage CE"
• "Quel budget pour essais cliniques ?"
""", parse_mode='Markdown')

async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = load_data(user_id)
    
    if context.args:
        request = ' '.join(context.args)
        prompt = f"Aide-moi à planifier: {request}. Contexte: projet crème cicatrisante, priorité brevet molécule. Donne planning concret avec horaires si possible."
        
        await update.message.reply_text("🤔 Je prépare ton planning...")
        response = await ask_gemini(prompt, user_data)
        save_data(user_id, user_data)
        await update.message.reply_text(response)
    else:
        etapes = "\n".join(user_data["projet"]["etapes"][:3])
        await update.message.reply_text(
f"""📅 **Planning**

🎯 **Priorités projet**:
{etapes}

💬 Dis-moi ce que tu veux planifier:

Exemples:
• /plan Demain matin ARDAN puis dossier BPI après-midi
• /plan Cette semaine appel contacts + préparation dossiers
• /plan Prochains 7 jours avec deadlines""", parse_mode='Markdown')

async def rappel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = load_data(user_id)
    
    if not context.args:
        await update.message.reply_text(
"""📌 **Créer un rappel**

Usage: /rappel [texte]

Exemples:
• /rappel Appeler ARDAN demain 10h
• /rappel Dossier i-Lab deadline 15 avril
• /rappel RDV ANSM dans 3 jours
• /rappel Prière Asr 16h30""")
        return
    
    texte = ' '.join(context.args)
    rappel = {
        "id": len(user_data["rappels"]) + 1,
        "texte": texte,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    user_data["rappels"].append(rappel)
    save_data(user_id, user_data)
    
    await update.message.reply_text(
f"""✅ **Rappel créé !**

📌 {texte}
🕐 Créé le {rappel['date']}

Tape /rappels pour voir tous tes rappels 🔔""", parse_mode='Markdown')

async def rappels_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = load_data(user_id)
    
    rappels = user_data.get("rappels", [])
    
    if not rappels:
        await update.message.reply_text("📌 Aucun rappel. Utilise /rappel pour en créer un !")
        return
    
    message = "📌 **Tes rappels**:\n\n"
    for r in rappels[-10:]:
        message += f"**#{r['id']}** - {r['texte']}\n🕐 {r['date']}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def projet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = load_data(user_id)
    
    etapes = "\n".join(user_data["projet"]["etapes"])
    budget_total = user_data["budget"]["total"]
    depenses = sum([d["montant"] for d in user_data["budget"]["depenses"]])
    restant = budget_total - depenses
    
    await update.message.reply_text(
f"""🧪 **Projet Crème Cicatrisante**

📊 **Budget**: {restant:,}€ / {budget_total:,}€ restant

🎯 **Étapes**:
{etapes}

📞 **Actions urgentes**:
• ☎️ ARDAN (brevet): 01 55 35 93 33
• 💰 Réseau Entreprendre 93: 01 48 43 30 00
• 🏛️ ANSM: 01 55 87 30 00

💬 Besoin d'aide ? Demande-moi n'importe quoi !""", parse_mode='Markdown')

async def budget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = load_data(user_id)
    
    budget_total = user_data["budget"]["total"]
    depenses_total = sum([d["montant"] for d in user_data["budget"]["depenses"]])
    restant = budget_total - depenses_total
    pct_utilise = (depenses_total / budget_total * 100) if budget_total > 0 else 0
    
    categories = "\n".join([f"• {cat}: {montant:,}€" 
                            for cat, montant in user_data["budget"]["categories"].items()])
    
    dernieres = "\n".join([f"• {d['montant']}€ - {d.get('desc', 'N/A')} ({d.get('date', '')})" 
                           for d in user_data["budget"]["depenses"][-5:]])
    
    await update.message.reply_text(
f"""💰 **Budget Projet Crème**

**Vue globale**:
• Total: {budget_total:,}€
• Dépensé: {depenses_total:,}€ ({pct_utilise:.1f}%)
• Restant: {restant:,}€

**Budget par catégorie**:
{categories}

**Dernières dépenses**:
{dernieres if dernieres else "Aucune dépense enregistrée"}

💡 Ajoute une dépense:
/depense 500 Brevet Consultation ARDAN""", parse_mode='Markdown')

async def depense_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = load_data(user_id)
    
    if len(context.args) < 2:
        await update.message.reply_text(
"""💳 **Ajouter une dépense**

Usage: /depense [montant] [catégorie] [description]

Exemples:
• /depense 500 Brevet Consultation ARDAN
• /depense 1200 Réglementaire Dossier ANSM
• /depense 80 Formulation Tests stabilité

Catégories disponibles:
• Brevet/IP (budget: 25 000€)
• Études cliniques (budget: 80 000€)
• Formulation (budget: 20 000€)
• Réglementaire (budget: 25 000€)""")
        return
    
    try:
        montant = float(context.args[0].replace(',', '.'))
        cat = context.args[1] if len(context.args) > 1 else "Autre"
        desc = ' '.join(context.args[2:]) if len(context.args) > 2 else "N/A"
        
        depense = {
            "montant": montant,
            "cat": cat,
            "desc": desc,
            "date": datetime.now().strftime('%Y-%m-%d')
        }
        
        user_data["budget"]["depenses"].append(depense)
        save_data(user_id, user_data)
        
        total_depense = sum([d["montant"] for d in user_data["budget"]["depenses"]])
        restant = user_data["budget"]["total"] - total_depense
        
        await update.message.reply_text(
f"""✅ **Dépense enregistrée !**

💳 {montant}€ - {desc}
📁 Catégorie: {cat}
📅 {depense['date']}

📊 Budget restant total: {restant:,}€ / {user_data["budget"]["total"]:,}€""", parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ Montant invalide. Utilise un nombre.\nEx: /depense 500 Brevet Consultation")

async def contacts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = load_data(user_id)
    
    message = "📞 **Contacts Projet Crème**\n\n"
    
    for c in user_data["projet"]["contacts"]:
        message += f"**{c['nom']}**\n"
        message += f"📱 {c['tel']}\n"
        if c.get('email'):
            message += f"📧 {c['email']}\n"
        message += "\n"
    
    message += "💡 Ces contacts sont prioritaires pour ton projet !"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chat libre avec Gemini"""
    user_id = update.effective_user.id
    user_message = update.message.text
    user_data = load_data(user_id)
    
    await update.message.chat.send_action("typing")
    
    response = await ask_gemini(user_message, user_data)
    save_data(user_id, user_data)
    
    await update.message.reply_text(response)

# ============= MAIN =============

def main():
    """Démarrage du bot"""
    print("🤖 Démarrage Assistant Karim...")
    print(f"📱 Token Telegram configuré ✓")
    print(f"🔑 Clé Gemini configurée ✓")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Commandes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(CommandHandler("rappel", rappel_cmd))
    app.add_handler(CommandHandler("rappels", rappels_cmd))
    app.add_handler(CommandHandler("projet", projet_cmd))
    app.add_handler(CommandHandler("budget", budget_cmd))
    app.add_handler(CommandHandler("depense", depense_cmd))
    app.add_handler(CommandHandler("contacts", contacts_cmd))
    
    # Chat libre
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    print("✅ Bot prêt ! En attente de messages...")
    print("💬 Ouvre Telegram et cherche ton bot pour commencer !\n")
    app.run_polling()

if __name__ == "__main__":
    main()
