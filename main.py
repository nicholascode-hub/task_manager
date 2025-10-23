"""
Gerenciador de Tarefas Pro - Versão Melhorada
Com suporte a textos longos e melhor visualização
"""

import tkinter as tk
from tkinter import messagebox, colorchooser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import json
import os
from datetime import datetime, timedelta
from plyer import notification
import threading
import time

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Tarefas Pro")
        self.root.geometry("1400x800")  # Aumentado para melhor visualização
        
        # Variável para rastrear último dia checado
        self.last_check_day = datetime.now().date()
        
        # Thread de notificações
        self.notification_thread = None
        self.stop_notifications = False
        
        # Carregar dados e configurações
        self.data_file = "tasks_data.json"
        self.config_file = "app_config.json"
        self.tasks = self.load_data()
        self.config = self.load_config()
        
        # Validar tema
        valid_themes = ["darkly", "solar", "superhero", "cyborg", "vapor", 
                       "flatly", "journal", "litera", "lumen", "minty", "pulse",
                       "cosmo", "morph", "simplex", "cerculean", "sandstone",
                       "yeti", "united", "sketchy"]
        
        self.current_theme = self.config.get("theme", "darkly")
        
        if self.current_theme not in valid_themes and self.current_theme != "purple-dark":
            self.current_theme = "darkly"
        
        # Aplicar tema
        if self.current_theme == "purple-dark":
            self.style = ttk.Style(theme="darkly")
        else:
            self.style = ttk.Style(theme=self.current_theme)
        
        # Criar interface
        self.create_menu()
        self.create_widgets()
        self.apply_custom_styles()
        self.refresh_tree()
        
        # Iniciar thread de notificações
        self.start_notification_service()
        
        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=4, ensure_ascii=False)
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme = config.get("theme", "darkly")
                    valid_themes = ["darkly", "solar", "superhero", "cyborg", "vapor", 
                                   "flatly", "journal", "litera", "lumen", "minty", "pulse",
                                   "cosmo", "morph", "simplex", "cerculean", "sandstone",
                                   "yeti", "united", "sketchy", "purple-dark"]
                    if theme not in valid_themes:
                        config["theme"] = "darkly"
                    return config
            except:
                return {"theme": "darkly"}
        return {"theme": "darkly"}
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Arquivo", menu=file_menu)
        file_menu.add_command(label="Sair", command=self.on_closing)
        
        # Menu Temas
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎨 Temas", menu=theme_menu)
        
        themes = [
            ("Darkly (Escuro)", "darkly"),
            ("Solar", "solar"),
            ("Superhero", "superhero"),
            ("Cyborg", "cyborg"),
            ("Vapor", "vapor"),
            ("Flatly (Claro)", "flatly"),
            ("Journal", "journal"),
            ("Litera", "litera"),
            ("Lumen", "lumen"),
            ("Minty", "minty"),
            ("Pulse", "pulse"),
            ("Cosmo", "cosmo"),
            ("Morph", "morph"),
            ("Simplex", "simplex")
        ]
        
        for theme_label, theme_name in themes:
            theme_menu.add_command(
                label=theme_label,
                command=lambda t=theme_name: self.change_theme(t)
            )
        
        theme_menu.add_separator()
        theme_menu.add_command(label="🟣 Roxo Escuro (Personalizado)", 
                              command=lambda: self.apply_purple_theme())
        
        # Menu Visualização
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="👁️ Visualização", menu=view_menu)
        view_menu.add_command(label="Ver Detalhes da Tarefa", command=self.show_task_details)
    
    def create_widgets(self):
        # Container principal com padding
        main_container = ttk.Frame(self.root, padding=15)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=X, pady=(0, 15))
        
        title_label = ttk.Label(
            header_frame,
            text="📋 Gerenciador de Tarefas Pro",
            font=("Segoe UI", 20, "bold"),
            bootstyle="inverse-primary"
        )
        title_label.pack(side=LEFT)
        
        # Contador de tarefas
        self.task_count_label = ttk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary"
        )
        self.task_count_label.pack(side=RIGHT, padx=10)
        
        # Frame de entrada com card style
        input_card = ttk.LabelFrame(
            main_container,
            text="➕ Adicionar Nova Tarefa",
            padding=15,
            bootstyle="primary"
        )
        input_card.pack(fill=X, pady=(0, 15))
        
        # Grid para inputs
        input_grid = ttk.Frame(input_card)
        input_grid.pack(fill=X)
        
        ttk.Label(input_grid, text="Tarefa:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky=W, pady=5
        )
        
        # Frame para entrada de texto com scrollbar
        entry_frame = ttk.Frame(input_grid)
        entry_frame.grid(row=0, column=1, padx=10, pady=5, sticky=EW)
        
        self.task_entry = tk.Text(entry_frame, height=2, width=50, font=("Segoe UI", 10), wrap=tk.WORD)
        entry_scroll = ttk.Scrollbar(entry_frame, orient=VERTICAL, command=self.task_entry.yview)
        self.task_entry.configure(yscrollcommand=entry_scroll.set)
        
        self.task_entry.pack(side=LEFT, fill=BOTH, expand=YES)
        entry_scroll.pack(side=RIGHT, fill=Y)
        
        # Bind para Ctrl+Enter adicionar tarefa
        self.task_entry.bind('<Control-Return>', lambda e: self.add_task())
        
        ttk.Label(input_grid, text="Data Limite:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=2, sticky=W, pady=5, padx=(20, 0)
        )
        
        date_frame = ttk.Frame(input_grid)
        date_frame.grid(row=0, column=3, padx=10, pady=5)
        
        self.day_var = tk.StringVar(value=str(datetime.now().day))
        self.month_var = tk.StringVar(value=str(datetime.now().month))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        
        ttk.Entry(date_frame, textvariable=self.day_var, width=3).pack(side=LEFT, padx=2)
        ttk.Label(date_frame, text="/").pack(side=LEFT)
        ttk.Entry(date_frame, textvariable=self.month_var, width=3).pack(side=LEFT, padx=2)
        ttk.Label(date_frame, text="/").pack(side=LEFT)
        ttk.Entry(date_frame, textvariable=self.year_var, width=5).pack(side=LEFT, padx=2)
        
        self.add_btn = ttk.Button(
            input_grid,
            text="✚ Adicionar",
            command=self.add_task,
            bootstyle="success",
            width=15
        )
        self.add_btn.grid(row=0, column=4, padx=10, pady=5)
        
        input_grid.columnconfigure(1, weight=1)
        
        # Dica de uso
        tip_label = ttk.Label(
            input_card,
            text="💡 Dica: Use Ctrl+Enter para adicionar rapidamente | Clique duplo na tarefa para ver detalhes completos",
            font=("Segoe UI", 8, "italic"),
            bootstyle="secondary"
        )
        tip_label.pack(pady=(5, 0))
        
        # Frame da árvore com card style
        tree_card = ttk.LabelFrame(
            main_container,
            text="📝 Suas Tarefas",
            padding=10,
            bootstyle="secondary"
        )
        tree_card.pack(fill=BOTH, expand=YES)
        
        # Container do Treeview
        tree_container = ttk.Frame(tree_card)
        tree_container.pack(fill=BOTH, expand=YES)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient=VERTICAL, bootstyle="primary-round")
        vsb.pack(side=RIGHT, fill=Y)
        
        hsb = ttk.Scrollbar(tree_container, orient=HORIZONTAL, bootstyle="primary-round")
        hsb.pack(side=BOTTOM, fill=X)
        
        # Treeview com largura maior para a coluna de tarefa
        self.tree = ttk.Treeview(
            tree_container,
            columns=("Status", "Prazo", "Criada", "Dias Restantes"),
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            bootstyle="primary",
            height=15
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.heading("#0", text="📌 Tarefa (Duplo clique para detalhes)")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Prazo", text="⏰ Data Limite")
        self.tree.heading("Criada", text="📅 Criada em")
        self.tree.heading("Dias Restantes", text="⏳ Dias Restantes")
        
        # Aumentar largura da coluna de tarefa
        self.tree.column("#0", width=600, minwidth=300)
        self.tree.column("Status", width=130, anchor=CENTER)
        self.tree.column("Prazo", width=130, anchor=CENTER)
        self.tree.column("Criada", width=150, anchor=CENTER)
        self.tree.column("Dias Restantes", width=150, anchor=CENTER)
        
        self.tree.pack(fill=BOTH, expand=YES)
        
        # Bind duplo clique para mostrar detalhes
        self.tree.bind('<Double-1>', lambda e: self.show_task_details())
        
        # Frame de botões com estilo moderno
        btn_card = ttk.Frame(main_container)
        btn_card.pack(fill=X, pady=(15, 0))
        
        btn_left = ttk.Frame(btn_card)
        btn_left.pack(side=LEFT)
        
        self.add_subtask_btn = ttk.Button(
            btn_left,
            text="➕ Adicionar Subtarefa",
            command=self.add_subtask,
            bootstyle="info-outline",
            width=20
        )
        self.add_subtask_btn.pack(side=LEFT, padx=5)
        
        self.toggle_btn = ttk.Button(
            btn_left,
            text="✓ Concluir",
            command=self.toggle_status,
            bootstyle="success-outline",
            width=15
        )
        self.toggle_btn.pack(side=LEFT, padx=5)
        
        self.edit_btn = ttk.Button(
            btn_left,
            text="✏️ Editar",
            command=self.edit_task,
            bootstyle="warning-outline",
            width=15
        )
        self.edit_btn.pack(side=LEFT, padx=5)
        
        self.delete_btn = ttk.Button(
            btn_left,
            text="🗑️ Excluir",
            command=self.delete_task,
            bootstyle="danger-outline",
            width=15
        )
        self.delete_btn.pack(side=LEFT, padx=5)
        
        # Botões à direita
        btn_right = ttk.Frame(btn_card)
        btn_right.pack(side=RIGHT)
        
        self.details_btn = ttk.Button(
            btn_right,
            text="👁️ Ver Detalhes",
            command=self.show_task_details,
            bootstyle="info",
            width=18
        )
        self.details_btn.pack(side=LEFT, padx=5)
        
        self.notify_btn = ttk.Button(
            btn_right,
            text="🔔 Notificar Agora",
            command=self.send_notification,
            bootstyle="primary",
            width=18
        )
        self.notify_btn.pack(side=LEFT, padx=5)
    
    def show_task_details(self):
        """Mostrar detalhes completos da tarefa em janela popup"""
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Selecione uma tarefa!", "Aviso")
            return
        
        item_id = selected[0]
        task = self.find_task_by_id(item_id)
        
        if not task:
            return
        
        # Criar janela de detalhes
        details_window = tk.Toplevel(self.root)
        details_window.title("📋 Detalhes da Tarefa")
        details_window.geometry("700x500")
        
        # Frame principal
        main_frame = ttk.Frame(details_window, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            title_frame,
            text="Detalhes Completos",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        ).pack()
        
        # Frame com scroll para o texto
        text_frame = ttk.LabelFrame(main_frame, text="📝 Descrição da Tarefa", padding=10)
        text_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=RIGHT, fill=Y)
        
        text_widget = tk.Text(
            text_frame,
            font=("Segoe UI", 11),
            wrap=tk.WORD,
            yscrollcommand=text_scroll.set,
            height=10
        )
        text_widget.pack(fill=BOTH, expand=YES)
        text_scroll.config(command=text_widget.yview)
        
        # Inserir texto da tarefa
        text_widget.insert("1.0", task["text"])
        text_widget.config(state=tk.DISABLED)
        
        # Informações adicionais
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Informações", padding=10)
        info_frame.pack(fill=X, pady=(0, 10))
        
        # Calcular dias restantes
        if "deadline_timestamp" in task:
            deadline = datetime.fromtimestamp(task["deadline_timestamp"])
            days_left = (deadline - datetime.now()).days
            
            if days_left < 0:
                days_info = f"❌ Atrasado há {abs(days_left)} dia(s)"
                days_color = "danger"
            elif days_left == 0:
                days_info = "⚠️ PRAZO HOJE!"
                days_color = "warning"
            elif days_left <= 3:
                days_info = f"⚠️ {days_left} dia(s) restante(s)"
                days_color = "warning"
            else:
                days_info = f"✓ {days_left} dia(s) restante(s)"
                days_color = "success"
        else:
            days_info = "Sem prazo definido"
            days_color = "secondary"
        
        status_icon = "✅" if task["status"] == "Concluída" else "⏳"
        status_color = "success" if task["status"] == "Concluída" else "warning"
        
        info_labels = [
            ("📊 Status:", f"{status_icon} {task['status']}", status_color),
            ("📅 Criada em:", task["created"], "info"),
            ("⏰ Prazo:", task.get("deadline", "—"), "primary"),
            ("⏳ Tempo restante:", days_info, days_color)
        ]
        
        for i, (label, value, color) in enumerate(info_labels):
            row_frame = ttk.Frame(info_frame)
            row_frame.pack(fill=X, pady=3)
            
            ttk.Label(
                row_frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                width=20
            ).pack(side=LEFT)
            
            ttk.Label(
                row_frame,
                text=value,
                font=("Segoe UI", 10),
                bootstyle=color
            ).pack(side=LEFT)
        
        # Subtarefas
        if task.get("subtasks"):
            subtask_frame = ttk.LabelFrame(main_frame, text=f"📌 Subtarefas ({len(task['subtasks'])})", padding=10)
            subtask_frame.pack(fill=X)
            
            for i, subtask in enumerate(task["subtasks"][:5], 1):  # Mostrar até 5
                status_icon = "✅" if subtask["status"] == "Concluída" else "⏳"
                subtask_text = subtask["text"][:80] + "..." if len(subtask["text"]) > 80 else subtask["text"]
                
                ttk.Label(
                    subtask_frame,
                    text=f"{i}. {status_icon} {subtask_text}",
                    font=("Segoe UI", 9)
                ).pack(anchor=W, pady=2)
            
            if len(task["subtasks"]) > 5:
                ttk.Label(
                    subtask_frame,
                    text=f"... e mais {len(task['subtasks']) - 5} subtarefa(s)",
                    font=("Segoe UI", 9, "italic"),
                    bootstyle="secondary"
                ).pack(anchor=W, pady=2)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=(15, 0))
        
        ttk.Button(
            btn_frame,
            text="✏️ Editar Tarefa",
            command=lambda: [details_window.destroy(), self.edit_task()],
            bootstyle="warning",
            width=20
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="✕ Fechar",
            command=details_window.destroy,
            bootstyle="secondary",
            width=15
        ).pack(side=RIGHT, padx=5)
    
    def show_notification(self, title, message, timeout=10):
        """Exibir notificação do Windows"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Gerenciador de Tarefas Pro",
                timeout=timeout
            )
        except Exception as e:
            print(f"Erro ao exibir notificação: {e}")
    
    def apply_custom_styles(self):
        """Aplicar estilos personalizados adicionais"""
        self.style.configure('Treeview', rowheight=35, font=("Segoe UI", 10))
        self.style.configure('Treeview.Heading', font=("Segoe UI", 10, "bold"))
    
    def apply_purple_theme(self):
        """Aplicar tema roxo e preto personalizado"""
        self.style = ttk.Style()
        
        colors = {
            'primary': '#9c27b0',
            'secondary': '#7b1fa2',
            'success': '#66bb6a',
            'info': '#ba68c8',
            'warning': '#ffa726',
            'danger': '#ef5350',
            'bg': '#0d0d0d',
            'fg': '#e0e0e0',
            'selectbg': '#7b1fa2',
            'selectfg': '#ffffff',
            'border': '#9c27b0',
            'inputbg': '#1a1a1a',
            'inputfg': '#e0e0e0'
        }
        
        self.root.configure(bg=colors['bg'])
        self.style = ttk.Style(theme='darkly')
        self.style.configure('.', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TButton', borderwidth=2, relief='flat')
        
        self.current_theme = "purple-dark"
        self.config["theme"] = "purple-dark"
        self.save_config()
        
        Messagebox.show_info("Tema Roxo Escuro aplicado com sucesso!", "Tema Aplicado")
    
    def add_task(self):
        task_text = self.task_entry.get("1.0", tk.END).strip()
        if not task_text:
            Messagebox.show_warning("Digite uma tarefa!", "Aviso")
            return
        
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            deadline = datetime(year, month, day)
            
            if deadline < datetime.now():
                Messagebox.show_warning("A data limite deve ser futura!", "Data Inválida")
                return
                
        except ValueError:
            Messagebox.show_warning("Data inválida! Use o formato DD/MM/AAAA", "Erro de Data")
            return
        
        task = {
            "id": self.generate_id(),
            "text": task_text,
            "status": "Pendente",
            "created": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "deadline": deadline.strftime("%d/%m/%Y"),
            "deadline_timestamp": deadline.timestamp(),
            "subtasks": []
        }
        
        self.tasks.append(task)
        self.save_data()
        self.refresh_tree()
        self.task_entry.delete("1.0", tk.END)
        
        # Texto curto para notificação
        short_text = task_text[:50] + "..." if len(task_text) > 50 else task_text
        self.show_notification(
            "✅ Tarefa Adicionada",
            f"{short_text}\n⏰ Prazo: {deadline.strftime('%d/%m/%Y')}"
        )
    
    def add_subtask(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Selecione uma tarefa!", "Aviso")
            return
        
        # Dialog para subtarefa
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Subtarefa")
        dialog.geometry("600x400")
        
        content = ttk.Frame(dialog, padding=20)
        content.pack(fill=BOTH, expand=YES)
        
        ttk.Label(content, text="Subtarefa:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        
        # Text widget para subtarefa
        text_frame = ttk.Frame(content)
        text_frame.pack(fill=BOTH, expand=YES, pady=(0, 15))
        
        subtask_text = tk.Text(text_frame, height=6, font=("Segoe UI", 10), wrap=tk.WORD)
        text_scroll = ttk.Scrollbar(text_frame, orient=VERTICAL, command=subtask_text.yview)
        subtask_text.configure(yscrollcommand=text_scroll.set)
        
        subtask_text.pack(side=LEFT, fill=BOTH, expand=YES)
        text_scroll.pack(side=RIGHT, fill=Y)
        subtask_text.focus()
        
        ttk.Label(content, text="Data Limite:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        
        date_frame = ttk.Frame(content)
        date_frame.pack(anchor=W, pady=(0, 15))
        
        sub_day = tk.StringVar(value=str(datetime.now().day))
        sub_month = tk.StringVar(value=str(datetime.now().month))
        sub_year = tk.StringVar(value=str(datetime.now().year))
        
        ttk.Entry(date_frame, textvariable=sub_day, width=4).pack(side=LEFT, padx=2)
        ttk.Label(date_frame, text="/").pack(side=LEFT)
        ttk.Entry(date_frame, textvariable=sub_month, width=4).pack(side=LEFT, padx=2)
        ttk.Label(date_frame, text="/").pack(side=LEFT)
        ttk.Entry(date_frame, textvariable=sub_year, width=6).pack(side=LEFT, padx=2)
        
        def save_subtask():
            subtask_content = subtask_text.get("1.0", tk.END).strip()
            if not subtask_content:
                Messagebox.show_warning("Digite uma subtarefa!", "Aviso")
                return
            
            try:
                day = int(sub_day.get())
                month = int(sub_month.get())
                year = int(sub_year.get())
                deadline = datetime(year, month, day)
                
                if deadline < datetime.now():
                    Messagebox.show_warning("A data limite deve ser futura!", "Data Inválida")
                    return
            except ValueError:
                Messagebox.show_warning("Data inválida!", "Erro")
                return
            
            item_id = selected[0]
            parent_id = self.tree.parent(item_id)
            
            subtask = {
                "id": self.generate_id(),
                "text": subtask_content,
                "status": "Pendente",
                "created": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "deadline": deadline.strftime("%d/%m/%Y"),
                "deadline_timestamp": deadline.timestamp(),
                "subtasks": []
            }
            
            if not parent_id:
                task_index = int(item_id.split('_')[1])
                self.tasks[task_index]["subtasks"].append(subtask)
            else:
                parent_index = int(parent_id.split('_')[1])
                current_item_index = int(item_id.split('_')[-1])
                self.tasks[parent_index]["subtasks"][current_item_index]["subtasks"].append(subtask)
            
            self.save_data()
            self.refresh_tree()
            dialog.destroy()
        
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="✓ Adicionar", command=save_subtask, 
                  bootstyle="success", width=15).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="✕ Cancelar", command=dialog.destroy,
                  bootstyle="secondary", width=15).pack(side=LEFT)
        
        subtask_text.bind('<Control-Return>', lambda e: save_subtask())
    
    def toggle_status(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Selecione uma tarefa!", "Aviso")
            return
        
        item_id = selected[0]
        task = self.find_task_by_id(item_id)
        
        if task:
            task["status"] = "Concluída" if task["status"] == "Pendente" else "Pendente"
            self.save_data()
            self.refresh_tree()
            
            status_emoji = "✅" if task["status"] == "Concluída" else "⏸️"
            short_text = task['text'][:50] + "..." if len(task['text']) > 50 else task['text']
            self.show_notification(
                f"{status_emoji} Status Atualizado",
                f"{short_text}\nStatus: {task['status']}"
            )
    
    def edit_task(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Selecione uma tarefa!", "Aviso")
            return
        
        item_id = selected[0]
        task = self.find_task_by_id(item_id)
        
        if not task:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Tarefa")
        dialog.geometry("600x400")
        
        content = ttk.Frame(dialog, padding=20)
        content.pack(fill=BOTH, expand=YES)
        
        ttk.Label(content, text="Tarefa:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        
        # Text widget para edição
        text_frame = ttk.Frame(content)
        text_frame.pack(fill=BOTH, expand=YES, pady=(0, 15))
        
        edit_text = tk.Text(text_frame, height=8, font=("Segoe UI", 10), wrap=tk.WORD)
        text_scroll = ttk.Scrollbar(text_frame, orient=VERTICAL, command=edit_text.yview)
        edit_text.configure(yscrollcommand=text_scroll.set)
        
        edit_text.pack(side=LEFT, fill=BOTH, expand=YES)
        text_scroll.pack(side=RIGHT, fill=Y)
        
        edit_text.insert("1.0", task["text"])
        edit_text.focus()
        
        def save_edit():
            new_text = edit_text.get("1.0", tk.END).strip()
            if not new_text:
                Messagebox.show_warning("Digite um texto!", "Aviso")
                return
            
            task["text"] = new_text
            self.save_data()
            self.refresh_tree()
            dialog.destroy()
        
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill=X)
        
        ttk.Button(btn_frame, text="💾 Salvar", command=save_edit,
                  bootstyle="success", width=15).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="✕ Cancelar", command=dialog.destroy,
                  bootstyle="secondary", width=15).pack(side=LEFT)
        
        edit_text.bind('<Control-Return>', lambda e: save_edit())
    
    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Selecione uma tarefa!", "Aviso")
            return
        
        result = Messagebox.yesno("Deseja excluir esta tarefa?", "Confirmar Exclusão")
        if result == "Yes":
            item_id = selected[0]
            self.remove_task_by_id(item_id)
            self.save_data()
            self.refresh_tree()
    
    def send_notification(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Selecione uma tarefa!", "Aviso")
            return
        
        item_id = selected[0]
        task = self.find_task_by_id(item_id)
        
        if task:
            deadline = datetime.fromtimestamp(task.get("deadline_timestamp", time.time()))
            days_left = (deadline - datetime.now()).days
            
            short_text = task['text'][:100] + "..." if len(task['text']) > 100 else task['text']
            msg = f"📝 {short_text}\n📊 Status: {task['status']}\n⏰ Prazo: {task['deadline']}\n⏳ {days_left} dias restantes"
            
            self.show_notification("🔔 Lembrete de Tarefa", msg)
    
    def start_notification_service(self):
        """Serviço de notificações automáticas para tarefas pendentes"""
        def notification_worker():
            while not self.stop_notifications:
                try:
                    current_time = datetime.now()
                    current_date = current_time.date()
                    
                    # Verificar se é um novo dia
                    if current_date > self.last_check_day:
                        print(f"Novo dia detectado! Verificando tarefas pendentes...")
                        self.last_check_day = current_date
                        
                        # Notificar sobre todas as tarefas pendentes do dia
                        for task in self.tasks:
                            self.check_task_deadline(task, current_time, force_notify=True)
                    
                    # Verificação regular (sem forçar notificação)
                    for task in self.tasks:
                        self.check_task_deadline(task, current_time, force_notify=False)
                    
                    # Verificar a cada 1 hora
                    time.sleep(3600)
                    
                except Exception as e:
                    print(f"Erro no serviço de notificações: {e}")
                    time.sleep(300)
        
        self.notification_thread = threading.Thread(target=notification_worker, daemon=True)
        self.notification_thread.start()
    
    def check_task_deadline(self, task, current_time, force_notify=False):
        """Verificar deadline de uma tarefa e suas subtarefas"""
        if task["status"] == "Pendente" and "deadline_timestamp" in task:
            deadline = datetime.fromtimestamp(task["deadline_timestamp"])
            days_left = (deadline - current_time).days
            
            # Definir quando notificar
            should_notify = False
            
            if force_notify:
                # Forçar notificação em novo dia para tarefas próximas ou atrasadas
                should_notify = days_left <= 7
            else:
                # Notificar em momentos específicos
                should_notify = days_left in [7, 3, 1, 0] or days_left < 0
            
            if should_notify:
                short_text = task['text'][:80] + "..." if len(task['text']) > 80 else task['text']
                
                if days_left >= 0:
                    if days_left == 0:
                        msg = f"⚠️ {short_text}\n🚨 PRAZO HOJE! Não esqueça!"
                        title = "🚨 PRAZO HOJE!"
                    else:
                        msg = f"⚠️ {short_text}\n⏳ Faltam {days_left} dia(s) para o prazo!"
                        title = "⏰ Lembrete de Prazo"
                else:
                    msg = f"🚨 {short_text}\n❌ Prazo vencido há {abs(days_left)} dia(s)!"
                    title = "🚨 PRAZO VENCIDO"
                
                # Usar thread para não bloquear
                threading.Thread(
                    target=lambda: self.show_notification(title, msg, timeout=8),
                    daemon=True
                ).start()
        
        # Verificar subtarefas recursivamente
        for subtask in task.get("subtasks", []):
            self.check_task_deadline(subtask, current_time, force_notify)
    
    def find_task_by_id(self, item_id):
        parts = item_id.split('_')
        
        if len(parts) == 2:
            index = int(parts[1])
            return self.tasks[index]
        else:
            task_index = int(parts[1])
            task = self.tasks[task_index]
            
            for i in range(2, len(parts)):
                subtask_index = int(parts[i])
                task = task["subtasks"][subtask_index]
            
            return task
    
    def remove_task_by_id(self, item_id):
        parts = item_id.split('_')
        
        if len(parts) == 2:
            index = int(parts[1])
            del self.tasks[index]
        else:
            task_index = int(parts[1])
            task = self.tasks[task_index]
            
            for i in range(2, len(parts) - 1):
                subtask_index = int(parts[i])
                task = task["subtasks"][subtask_index]
            
            del task["subtasks"][int(parts[-1])]
    
    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        pending_count = 0
        completed_count = 0
        
        for i, task in enumerate(self.tasks):
            counts = self.insert_task(task, "", f"task_{i}")
            pending_count += counts[0]
            completed_count += counts[1]
        
        total = pending_count + completed_count
        self.task_count_label.config(
            text=f"📊 Total: {total} | ⏳ Pendentes: {pending_count} | ✅ Concluídas: {completed_count}"
        )
    
    def insert_task(self, task, parent, item_id):
        """Inserir tarefa e retornar (pendentes, concluídas)"""
        # Calcular dias restantes
        if "deadline_timestamp" in task:
            deadline = datetime.fromtimestamp(task["deadline_timestamp"])
            days_left = (deadline - datetime.now()).days
            
            if days_left < 0:
                days_text = f"❌ Atrasado ({abs(days_left)}d)"
                tag = "overdue"
            elif days_left == 0:
                days_text = "⚠️ Hoje!"
                tag = "urgent"
            elif days_left <= 3:
                days_text = f"⚠️ {days_left} dias"
                tag = "urgent"
            else:
                days_text = f"✓ {days_left} dias"
                tag = "normal"
        else:
            days_text = "—"
            tag = "normal"
        
        status_symbol = "✅" if task["status"] == "Concluída" else "⏳"
        
        # Truncar texto para exibição na árvore
        display_text = task["text"][:150] + "..." if len(task["text"]) > 150 else task["text"]
        
        self.tree.insert(
            parent, tk.END, item_id,
            text=display_text,
            values=(f"{status_symbol} {task['status']}", task.get("deadline", "—"), 
                   task["created"], days_text),
            tags=(task["status"].lower(), tag)
        )
        
        pending = 1 if task["status"] == "Pendente" else 0
        completed = 1 if task["status"] == "Concluída" else 0
        
        for j, subtask in enumerate(task.get("subtasks", [])):
            counts = self.insert_task(subtask, item_id, f"{item_id}_{j}")
            pending += counts[0]
            completed += counts[1]
        
        # Configurar tags
        self.tree.tag_configure("concluída", foreground="#66bb6a")
        self.tree.tag_configure("pendente", foreground="#ffa726")
        self.tree.tag_configure("overdue", background="#3d1f1f")
        self.tree.tag_configure("urgent", background="#3d2a1f")
        
        return (pending, completed)
    
    def generate_id(self):
        return str(datetime.now().timestamp())
    
    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.config["theme"] = theme_name
        self.save_config()
        
        # Recriar a interface com novo tema
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.style = ttk.Style(theme=theme_name)
        self.create_menu()
        self.create_widgets()
        self.apply_custom_styles()
        self.refresh_tree()
        
        Messagebox.show_info(f"Tema '{theme_name}' aplicado com sucesso!", "Tema Alterado")
    
    def on_closing(self):
        self.stop_notifications = True
        self.save_data()
        self.save_config()
        
        if self.notification_thread and self.notification_thread.is_alive():
            # Dar tempo para a thread encerrar
            time.sleep(0.5)
        
        self.root.destroy()

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = TaskManagerApp(root)
    root.mainloop()