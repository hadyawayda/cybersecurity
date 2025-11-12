#!/usr/bin/env python3
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ExifTags
import piexif, traceback
NAME2ID={v:k for k,v in ExifTags.TAGS.items()}; ID2NAME={k:v for k,v in ExifTags.TAGS.items()}
class ScorpionGUI(tk.Tk):
 def __init__(self):
  super().__init__(); self.title('Scorpion — Metadata Manager'); self.geometry('1000x650'); self._build_ui(); self.current_path=None; self.current_exif=None
 def _build_ui(self):
  bar=tk.Frame(self); bar.pack(fill='x'); tk.Button(bar,text='Open…',command=self.open_file).pack(side='left',padx=4,pady=4); tk.Button(bar,text='Save',command=self.save_file).pack(side='left',padx=4); tk.Button(bar,text='Wipe EXIF',command=self.wipe_exif).pack(side='left',padx=4); tk.Button(bar,text='About',command=self.show_about).pack(side='right',padx=4)
  main=tk.PanedWindow(self,orient='horizontal'); main.pack(fill='both',expand=True)
  self.preview=tk.Label(main,text='Open an image…',anchor='center'); main.add(self.preview)
  right=tk.Frame(main); main.add(right)
  self.tree=ttk.Treeview(right,columns=('value',),show='tree headings',selectmode='browse'); self.tree.heading('#0',text='Tag'); self.tree.heading('value',text='Value'); self.tree.column('#0',width=200); self.tree.column('value',width=400); self.tree.pack(side='top',fill='both',expand=True,padx=6,pady=6)
  form=tk.Frame(right); form.pack(fill='x',padx=6,pady=6)
  tk.Label(form,text='Tag name:').grid(row=0,column=0,sticky='e'); self.entry_tag=tk.Entry(form,width=32); self.entry_tag.grid(row=0,column=1,sticky='we',padx=4)
  tk.Label(form,text='Value:').grid(row=1,column=0,sticky='e'); self.entry_val=tk.Entry(form,width=64); self.entry_val.grid(row=1,column=1,sticky='we',padx=4)
  btns=tk.Frame(form); btns.grid(row=0,column=2,rowspan=2,padx=6); tk.Button(btns,text='Set/Update',command=self.set_tag).pack(fill='x'); tk.Button(btns,text='Delete',command=self.del_tag).pack(fill='x',pady=4)
  form.grid_columnconfigure(1,weight=1)
 def show_about(self): messagebox.showinfo('About','Scorpion GUI — view/edit EXIF for JPEG/TIFF.')
 def open_file(self):
  path=filedialog.askopenfilename(title='Open image',filetypes=[('Images','*.jpg *.jpeg *.tif *.tiff *.png')]);
  if not path: return
  self.load_image(path)
 def load_image(self, path:str):
  try:
   self.current_path=path
   with Image.open(path) as im:
    im_thumb=im.copy(); im_thumb.thumbnail((480,480)); self._photo=ImageTk.PhotoImage(im_thumb); self.preview.configure(image=self._photo)
   try: 
    exif_dict=piexif.load(path)
    # Check if there's any actual EXIF data
    has_data = any(exif_dict.get(ifd, {}) for ifd in ('0th','Exif','GPS','1st'))
    if not has_data:
     messagebox.showinfo('No Metadata', 'This image has no EXIF metadata.')
   except Exception as e: 
    messagebox.showwarning('EXIF Load Error', f'Could not load EXIF data: {e}')
    exif_dict={'0th':{},'Exif':{},'GPS':{},'1st':{}}
   self.current_exif=exif_dict; self._refresh_tree()
  except Exception as e:
   messagebox.showerror('Error', f'Failed to load: {e}\n{traceback.format_exc()}')
 def _refresh_tree(self):
  self.tree.delete(*self.tree.get_children())
  if not self.current_exif: return
  def add_ifd(name,d):
   parent=self.tree.insert('', 'end', text=name, values=(f'[{name}]',))
   for tag_id,val in d.items():
    tag_name=ID2NAME.get(tag_id,f'Tag_{tag_id}')
    if isinstance(val,bytes):
     try: val=val.decode('utf-8','ignore')
     except Exception: pass
    self.tree.insert(parent,'end',text=tag_name,values=(val,),iid=f'{name}:{tag_name}')
  for ifd in ('0th','Exif','GPS','1st'): add_ifd(ifd,self.current_exif.get(ifd,{}))
  for item in self.tree.get_children():
   self.tree.item(item, open=True)
 def set_tag(self):
  tag=self.entry_tag.get().strip(); val=self.entry_val.get()
  if not tag: messagebox.showwarning('Set tag','Enter a tag name'); return
  tid=NAME2ID.get(tag)
  if tid is None: messagebox.showerror('Unknown tag', f'No such EXIF tag: {tag}'); return
  target_ifd='0th' if tid in piexif.TAGS['0th'] else 'Exif'
  self.current_exif[target_ifd][tid]=val.encode('utf-8','ignore'); self._refresh_tree()
 def del_tag(self):
  tag=self.entry_tag.get().strip()
  if not tag: messagebox.showwarning('Delete tag','Enter a tag name'); return
  tid=NAME2ID.get(tag)
  if tid is None: return
  for ifd in ('0th','Exif','GPS','1st'): self.current_exif.get(ifd, {}).pop(tid, None)
  self._refresh_tree()
 def wipe_exif(self):
  if not self.current_exif: return
  for ifd in ('0th','Exif','GPS','1st'): self.current_exif[ifd]={}
  self._refresh_tree()
 def save_file(self):
  if not self.current_path or not self.current_exif: return
  try:
   with Image.open(self.current_path) as im: fmt=(im.format or '').upper()
   if fmt not in ('JPEG','TIFF'):
    messagebox.showerror('Unsupported','Write supported only for JPEG/TIFF'); return
   exif_bytes=piexif.dump(self.current_exif); piexif.insert(exif_bytes, self.current_path)
   messagebox.showinfo('Saved','Metadata saved successfully.')
  except Exception as e:
   messagebox.showerror('Error', f'Failed to save: {e}\n{traceback.format_exc()}')

def main(): ScorpionGUI().mainloop()
if __name__=='__main__': main()
