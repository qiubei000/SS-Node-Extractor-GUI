import customtkinter as ctk
from tkinter import messagebox
import requests
import base64
import json
import pyaes
import binascii
from datetime import datetime
import threading
import pyperclip
import os
import yaml
from urllib.parse import quote

# 设置主题和颜色模式
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SSExtractorGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("SS Node Extractor")
        self.root.geometry("700x640")
        
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.nodes = []
        self.setup_ui()
    
    def setup_ui(self):
        # 标题卡片
        self.title_card = ctk.CTkFrame(self.main_frame)
        self.title_card.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            self.title_card, 
            text="SS Node Extractor",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            self.title_card,
            text="Version: 1.0",
            font=ctk.CTkFont(size=14)
        ).pack(pady=2)
        
        ctk.CTkLabel(
            self.title_card,
            text="作者: Loong",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(2, 20))
        
        # 操作按钮卡片
        self.button_card = ctk.CTkFrame(self.main_frame)
        self.button_card.pack(fill="x", padx=20, pady=(0, 20))
        
        # 主要操作按钮
        button_frame = ctk.CTkFrame(self.button_card)
        button_frame.pack(pady=20)
        
        self.extract_btn = ctk.CTkButton(
            button_frame,
            text="提取节点",
            command=self.start_extraction,
            width=120
        )
        self.extract_btn.pack(side="left", padx=10)
        
        self.copy_btn = ctk.CTkButton(
            button_frame,
            text="复制节点",
            command=self.copy_nodes,
            state="disabled",
            width=120
        )
        self.copy_btn.pack(side="left", padx=10)
        
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="保存到文件",
            command=self.save_to_file,
            state="disabled",
            width=120
        )
        self.save_btn.pack(side="left", padx=10)
        
        # 转换按钮
        convert_frame = ctk.CTkFrame(self.button_card)
        convert_frame.pack(pady=(0, 20))
        
        self.clash_btn = ctk.CTkButton(
            convert_frame,
            text="保存为Clash配置",
            command=self.save_clash_config,
            state="disabled",
            width=180
        )
        self.clash_btn.pack(side="left", padx=10)
        
        self.base64_btn = ctk.CTkButton(
            convert_frame,
            text="保存为Base64订阅",
            command=self.save_base64_subscription,
            state="disabled",
            width=180
        )
        self.base64_btn.pack(side="left", padx=10)
        
        # 进度条
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.pack(fill="x", padx=20, pady=(0, 20))
        self.progress.set(0)
        
        # 结果显示卡片
        self.result_card = ctk.CTkFrame(self.main_frame)
        self.result_card.pack(fill="both", expand=True, padx=20)
        
        self.result_text = ctk.CTkTextbox(
            self.result_card,
            wrap="none",
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.result_text.pack(fill="both", expand=True, padx=20, pady=20)


    def decrypt_data(self, encrypted_data, key, iv):
        decryptor = pyaes.AESModeOfOperationCBC(key, iv=iv)
        decrypted = b''.join(decryptor.decrypt(encrypted_data[i:i+16]) for i in range(0, len(encrypted_data), 16))
        return decrypted[:-decrypted[-1]]

    def extract_nodes(self):
        try:
            url = 'http://api.skrapp.net/api/serverlist'
            headers = {
                'accept': '/',
                'accept-language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
                'appversion': '1.3.1',
                'user-agent': 'SkrKK/1.3.1 (iPhone; iOS 13.5; Scale/2.00)',
                'content-type': 'application/x-www-form-urlencoded',
                'Cookie': 'PHPSESSID=fnffo1ivhvt0ouo6ebqn86a0d4'
            }
            data = {'data': '4265a9c353cd8624fd2bc7b5d75d2f18b1b5e66ccd37e2dfa628bcb8f73db2f14ba98bc6a1d8d0d1c7ff1ef0823b11264d0addaba2bd6a30bdefe06f4ba994ed'}
            key = b'65151f8d966bf596'
            iv = b'88ca0f0ea1ecf975'

            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                encrypted_text = response.text.strip()
                encrypted_data = binascii.unhexlify(encrypted_text)
                decrypted_data = self.decrypt_data(encrypted_data, key, iv)
                nodes_data = json.loads(decrypted_data)
                
                self.nodes = []
                for node in nodes_data['data']:
                    ss_url = f"aes-256-cfb:{node['password']}@{node['ip']}:{node['port']}"
                    ss_base64 = base64.b64encode(ss_url.encode('utf-8')).decode('utf-8')
                    ss_link = f"ss://{ss_base64}#{node['title']}"
                    self.nodes.append(ss_link)
                
                self.root.after(0, self.update_ui_after_extraction)
            else:
                self.root.after(0, lambda: self.show_error("请求失败"))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"错误: {str(e)}"))

    def start_extraction(self):
        self.extract_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.result_text.delete("1.0", "end")
        
        # 开始进度条动画
        self.progress.start()
        
        thread = threading.Thread(target=self.extract_nodes)
        thread.daemon = True
        thread.start()

    def update_ui_after_extraction(self):
        # 停止进度条动画
        self.progress.stop()
        self.progress.set(1)  # 设置为完成状态
        
        # 重新启用按钮
        self.extract_btn.configure(state="normal")
        self.copy_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.clash_btn.configure(state="normal")
        self.base64_btn.configure(state="normal")
        
        # 更新结果显示
        self.result_text.delete("1.0", "end")
        for node in self.nodes:
            self.result_text.insert("end", node + '\n')

    def copy_nodes(self):
        nodes_text = '\n'.join(self.nodes)
        pyperclip.copy(nodes_text)
        self.show_message("节点已复制到剪贴板")

    def save_to_file(self):
        if not self.nodes:
            return
            
        filename = f"ss_nodes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.nodes))
        self.show_message(f"节点已保存到文件: {filename}")

    def show_message(self, message):
        messagebox.showinfo("提示", message)

    def show_error(self, message):
        self.progress.stop()
        self.progress.set(0)  # 重置进度条
        self.extract_btn.configure(state="normal")
        messagebox.showerror("错误", message)

    def save_clash_config(self):
        if not self.nodes:
            self.show_error("没有可用的节点")
            return
        
        try:
            nodes_text = '|'.join(self.nodes)
            encoded_nodes = quote(nodes_text)
            
            web_url = (
                "https://suburl.v1.mk/"
                f"#/sub?target=clash"
                f"&url={encoded_nodes}"
                "&insert=false"
                "&config=https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online_Full_NoAuto.ini"
                "&emoji=true"
                "&list=false"
                "&udp=false"
                "&tfo=false"
                "&expand=true"
                "&scv=false"
                "&fdn=false"
                "&new_name=true"
            )
            
            import webbrowser
            webbrowser.open(web_url)
            self.show_message("已打开转换网页，请点击下载按钮保存配置文件")
                
        except Exception as e:
            self.show_error(f"打开网页失败: {str(e)}")

    def convert_to_base64(self):
        if not self.nodes:
            self.show_error("没有可用的节点")
            return
        
        nodes_text = '\n'.join(node.strip() for node in self.nodes if node.strip())
        if not nodes_text.endswith('\n'):
            nodes_text += '\n'
        return base64.b64encode(nodes_text.encode('utf-8')).decode('utf-8')

    def save_base64_subscription(self):
        try:
            nodes_text = '\n'.join(node.strip() for node in self.nodes if node.strip())
            if not nodes_text.endswith('\n'):
                nodes_text += '\n'
            
            base64_content = base64.b64encode(nodes_text.encode('utf-8')).decode('utf-8')
            
            filename = f"subscription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                f.write(base64_content)
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    test_content = f.read().strip()
                    decoded = base64.b64decode(test_content).decode('utf-8')
                    if not any(line.startswith('ss://') for line in decoded.splitlines()):
                        raise ValueError("订阅内容格式错误")
            except Exception as e:
                os.remove(filename)
                raise ValueError(f"订阅文件验证失败: {str(e)}")
                
            self.show_message(f"Base64订阅已保存到文件: {filename}\n"
                             f"共 {len(self.nodes)} 个节点\n"
                             "可直接导入到V2rayN使用")
            
        except Exception as e:
            self.show_error(f"生成Base64订阅失败: {str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SSExtractorGUI()
    app.run()