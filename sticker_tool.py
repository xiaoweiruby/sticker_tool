import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class StickerTool:
    def __init__(self, root):
        self.root = root
        self.root.title('微信表情包处理工具')
        self.root.geometry('800x600')
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 左侧控制面板
        self.control_frame = ttk.LabelFrame(self.main_frame, text="控制面板", padding="5")
        self.control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 文件选择
        ttk.Label(self.control_frame, text="选择图片:").grid(row=0, column=0, sticky=tk.W)
        self.file_path = tk.StringVar()
        ttk.Entry(self.control_frame, textvariable=self.file_path, width=30).grid(row=0, column=1, padx=5)
        ttk.Button(self.control_frame, text="浏览", command=self.select_file).grid(row=0, column=2)
        
        # 尺寸调整选项
        ttk.Label(self.control_frame, text="尺寸调整:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.size_var = tk.StringVar(value='240x240')
        sizes = ['横幅尺寸(750x400)', '封面尺寸(240x240)', '图标尺寸(50x50)', 
                '引导尺寸(750x560)', '致谢尺寸(750x750)']
        self.size_combo = ttk.Combobox(self.control_frame, textvariable=self.size_var, values=sizes, width=20)
        self.size_combo.grid(row=1, column=1, sticky=tk.W)
        
        # 格式转换选项
        ttk.Label(self.control_frame, text="格式转换:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.format_var = tk.StringVar(value='PNG')
        formats_frame = ttk.Frame(self.control_frame)
        formats_frame.grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(formats_frame, text='PNG', variable=self.format_var, value='PNG').pack(side=tk.LEFT)
        ttk.Radiobutton(formats_frame, text='JPG', variable=self.format_var, value='JPG').pack(side=tk.LEFT)
        ttk.Radiobutton(formats_frame, text='GIF', variable=self.format_var, value='GIF').pack(side=tk.LEFT)
        ttk.Radiobutton(formats_frame, text='WEBP', variable=self.format_var, value='WEBP').pack(side=tk.LEFT)
        
        # 背景处理选项
        ttk.Label(self.control_frame, text="背景处理:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.bg_remove = tk.BooleanVar()
        ttk.Checkbutton(self.control_frame, text='去除背景', variable=self.bg_remove).grid(row=3, column=1, sticky=tk.W)
        
        # 背景阈值调节
        self.threshold_frame = ttk.Frame(self.control_frame)
        self.threshold_frame.grid(row=4, column=0, columnspan=3, pady=5)
        ttk.Label(self.threshold_frame, text="背景阈值:").pack(side=tk.LEFT)
        self.threshold_var = tk.IntVar(value=230)  # 降低默认阈值，提高背景去除效果
        self.threshold_scale = ttk.Scale(self.threshold_frame, from_=0, to=255, variable=self.threshold_var, orient=tk.HORIZONTAL)
        self.threshold_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 批量处理选项
        self.batch_var = tk.BooleanVar()
        ttk.Checkbutton(self.control_frame, text='批量处理', variable=self.batch_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 处理按钮
        ttk.Button(self.control_frame, text="处理图片", command=self.process_image).grid(row=6, column=0, columnspan=3, pady=10)
        
        # 右侧预览区域
        self.preview_frame = ttk.LabelFrame(self.main_frame, text="预览", padding="5")
        self.preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 添加预览信息标签
        self.preview_info = ttk.Label(self.preview_frame, text="尚未选择图片")
        self.preview_info.pack(side=tk.TOP, pady=5)
        
        # 预览图片标签
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # 状态栏
        self.status_var = tk.StringVar()
        ttk.Label(self.main_frame, textvariable=self.status_var).grid(row=1, column=0, columnspan=2, pady=5)
        
        # 绑定预览更新
        self.threshold_scale.bind("<Motion>", lambda e: self.update_preview())
        self.size_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        self.bg_remove.trace('w', lambda *args: self.update_preview())
        
        # 配置网格权重
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
    def select_file(self):
        if self.batch_var.get():
            file_paths = filedialog.askopenfilenames(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_paths:
                self.file_path.set(';'.join(file_paths))
                self.preview_info.config(text=f"已选择 {len(file_paths)} 个文件，当前预览第1个")
                self.update_preview(file_paths[0])
        else:
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
            )
            if file_path:
                self.file_path.set(file_path)
                self.preview_info.config(text="已选择 1 个文件")
                self.update_preview(file_path)
    
    def update_preview(self, file_path=None):
        if not file_path:
            file_path = self.file_path.get().split(';')[0] if self.file_path.get() else None
        if not file_path:
            return
            
        try:
            # 打开图片并转换为RGB或RGBA模式
            image = Image.open(file_path)
            if image.format == 'GIF' and image.is_animated:
                # 对于动态GIF，只显示第一帧
                image.seek(0)
            
            # 确保图片模式正确
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGBA')
            
            # 调整尺寸
            try:
                size_str = self.size_var.get()
                if '(' in size_str:
                    size = tuple(map(int, size_str[size_str.find('(')+1:size_str.find(')')].split('x')))
                else:
                    size = tuple(map(int, size_str.split('x')))
                image = image.resize(size, Image.Resampling.LANCZOS)
            except (ValueError, AttributeError) as e:
                self.status_var.set(f"尺寸格式错误：{str(e)}")
                return
            
            # 处理背景
            if self.bg_remove.get():
                image = image.convert('RGBA')
                data = image.getdata()
                new_data = []
                threshold = self.threshold_var.get()
                for item in data:
                    if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                image.putdata(new_data)
            
            # 调整预览图大小，保持原始比例
            preview_width = 300  # 预览区域的最大宽度
            preview_height = 300  # 预览区域的最大高度
            
            # 计算缩放比例
            width_ratio = preview_width / image.width
            height_ratio = preview_height / image.height
            scale_ratio = min(width_ratio, height_ratio)
            
            new_size = (int(image.width * scale_ratio), int(image.height * scale_ratio))
            preview_image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 更新预览
            photo = ImageTk.PhotoImage(preview_image)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
            self.status_var.set("预览更新成功")
            
        except (IOError, OSError) as e:
            self.status_var.set(f"图片加载失败：{str(e)}")
        except Exception as e:
            self.status_var.set(f"预览更新失败：{str(e)}")
    
    def process_image(self):
        file_paths = self.file_path.get().split(';') if self.batch_var.get() else [self.file_path.get()]
        if not file_paths[0]:
            messagebox.showerror("错误", "请先选择图片文件！")
            return
        
        # 选择保存目录
        save_dir = filedialog.askdirectory(title="选择保存位置")
        if not save_dir:
            return
        
        try:
            for file_path in file_paths:
                # 打开图片
                image = Image.open(file_path)
                
                # 调整尺寸
                size_str = self.size_var.get()
                size = tuple(map(int, size_str[size_str.find('(')+1:size_str.find(')')].split('x')))
                image = image.resize(size, Image.Resampling.LANCZOS)
                
                # 处理背景
                if self.bg_remove.get():
                    image = image.convert('RGBA')
                    data = image.getdata()
                    new_data = []
                    threshold = self.threshold_var.get()
                    for item in data:
                        # 使用更精确的背景检测算法
                        if len(item) == 4:  # RGBA
                            r, g, b, a = item
                        else:  # RGB
                            r, g, b = item
                            a = 255
                        
                        # 检查像素亮度和饱和度
                        brightness = (r + g + b) / 3
                        max_rgb = max(r, g, b)
                        min_rgb = min(r, g, b)
                        saturation = (max_rgb - min_rgb) / max_rgb if max_rgb != 0 else 0
                        
                        if brightness > threshold and saturation < 0.2:
                            new_data.append((255, 255, 255, 0))
                        else:
                            new_data.append(item)
                    image.putdata(new_data)
                
                # 保存处理后的图片
                output_format = self.format_var.get()
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(save_dir, f"{file_name}_processed.{output_format.lower()}")
                
                if output_format == 'JPG':
                    image = image.convert('RGB')
                elif output_format == 'WEBP':
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                
                image.save(output_path, output_format)
            
            self.status_var.set(f"处理完成！已处理 {len(file_paths)} 个文件，保存在：{save_dir}")
            messagebox.showinfo("成功", f"图片处理完成！\n保存位置：{save_dir}")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错：{str(e)}")

def main():
    root = tk.Tk()
    app = StickerTool(root)
    root.mainloop()

if __name__ == '__main__':
    main()