#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 13:55:08 2023

@author: matep
"""


import tkinter as tk
# from tkinter import ttk
import tkinterDnD  # Importing the tkinterDnD module
from tkinter import messagebox
import traceback
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas
import os
from io import BytesIO
from copy import copy

ADD_EXTRA_COPIES = 3
POS_X_SHIFT = -15
POS_Y_SHIFT = 15
ALIGN = 'RIGHT'

DEFAULT_TEXT = 'Ovdje zalijepi tablicu iz "Postavke provjere" (kartica "Studenata u dvorani") s FERweba!\n\
\n\
Na primjer:\n\n\
A-101 	32 	32\n\
A-102 	32 	32\n\
A-104 	11 	11\n\
A-109 	20 	20\n\
A-110 	20 	20\n\
A-111 	40 	40\n\
A-201 	40 	40\n\
A-202 	40 	40\n\
A-209 	30 	30\n\
A-210 	30 	30\n\
A-211 	40 	40\n\
A-301 	40 	40\n\
A-302 	40 	40\n\
A-304 	24 	24\n\
A-309 	20 	20\n\
A-310 	20 	20\n\
A-311 	16 	16\n\
Neraspoređen 	- 	0'


class Dots:
    def __init__(self, N):
        self.total = N
        self.i = 0

    def __str__(self):
        self.i += 1
        return '.'*int(30*self.i/self.total)


def main():
    try:

        # You have to use the tkinterDnD.Tk object for super easy initialization,
        # and to be able to use the main window as a dnd widget
        root = tkinterDnD.Tk()
        root.geometry('800x800+200+100')
        root.title("Numeriranje ispita")

        stringvar1 = tk.StringVar()
        stringvar1.set('Dovuci pdf datoteku s ispitom ovdje!')
        stringvar2 = tk.StringVar()
        stringvar2.set('')

        def drop(event):
            # This function is called, when stuff is dropped into a widget
            stringvar1.set(event.data)

        # def drag_command(event):
        #     # This function is called at the start of the drag,
        #     # it returns the drag type, the content type, and the actual content
        #     print(tkinterDnD.COPY, "DND_Text", "Some nice dropped text!")
        #     return (tkinterDnD.COPY, "DND_Text", "Some nice dropped text!")

        # Without DnD hook you need to register the widget for every purpose,
        # and bind it to the function you want to call
        label_1 = tk.Label(root, height=5,
                           textvar=stringvar1, relief="solid")
        label_1.pack(fill="both", padx=10, pady=10)

        label_1.register_drop_target("*")
        label_1.bind("<<Drop>>", drop)

        # With DnD hook you just pass the command to the proper argument,
        # and tkinterDnD will take care of the rest
        # NOTE: You need a ttk widget to use these arguments
        # label_2 = ttk.Label(root, ondrop=drop,
        #                     textvar=stringvar1, padding=50, relief="solid")
        # label_2.pack(fill="both", expand=True, padx=10, pady=10)

        def on_click(event):
            if entry1.get('1.0', tk.END).strip() == DEFAULT_TEXT:
                event.widget.delete('1.0', tk.END)
                entry1.config(foreground='black')
            else:
                entry1.config(foreground='black')

        entry1 = tk.Text(root, fg='gray')
        entry1.insert(tk.END, DEFAULT_TEXT)
        entry1.bind("<Button-1>", on_click)
        entry1.bind("<FocusIn>", on_click)
        entry1.pack(fill="both", expand=True, padx=10, pady=10)

        def parse(TABLE):
            tmp = []
            for row in TABLE.split('\n'):
                row = row.strip()
                tmp_row_list = []
                for el in row.split():
                    el = el.strip()
                    if el != '':
                        tmp_row_list.append(el)
                if len(tmp_row_list) == 0:
                    continue
                elif len(tmp_row_list) != 3:
                    return tmp_row_list, 1
                elif not str.isnumeric(tmp_row_list[2]):
                    return tmp_row_list, 2
                else:
                    tmp.append((tmp_row_list[0], int(tmp_row_list[2])))
            return tmp, 0

        def generiraj():
            INPUT_FILE = stringvar1.get()
            if INPUT_FILE[0] == '{':
                INPUT_FILE = INPUT_FILE[1:-1]
            try:
                existing_pdf = PdfReader(INPUT_FILE)
                NUM_PAGES = len(existing_pdf.pages)
            except Exception as e:
                print(e)
                messagebox.showinfo("Greška!",
                                    f"<<{INPUT_FILE}>> nije valjana pdf datoteka.")
                return

            OUTPUT_FILE = os.path.join(
                os.path.dirname(INPUT_FILE), 'print.pdf')
            if os.path.exists(OUTPUT_FILE):
                messagebox.showinfo(
                    "Upozorenje!", f"Datoteka <<{OUTPUT_FILE}>> već postoji i bit će prebrisana.")

            TABLE = entry1.get('1.0', tk.END)
            list_TABLE, info = parse(TABLE)
            if info == 1:
                messagebox.showinfo("Greška!",
                                    f"Redak <<{list_TABLE}>> nema 3 komponente.")
                return
            if info == 2:
                messagebox.showinfo("Greška!",
                                    f"Redak <<{list_TABLE}>> nema cijeli broj kao 3. komponentu.")
                return

            ###############
            # Kreiraj Pdf #
            ###############

            PAGE_WIDTH = existing_pdf.pages[0].mediabox.width
            PAGE_HEIGHT = existing_pdf.pages[0].mediabox.height
            POS_X = POS_X_SHIFT % PAGE_WIDTH
            POS_Y = POS_Y_SHIFT % PAGE_HEIGHT
            output = PdfWriter()

            for dvorana, num in list_TABLE:
                if num == 0:
                    continue
                num += ADD_EXTRA_COPIES

                dots = Dots(num)

                DIGITS = len(str(num))
                for i in range(1, num+1):
                    STR = f'{dvorana} {i:0{DIGITS}}/{num}'
                    stringvar2.set(f'Obrađujem {STR} {dots}')
                    root.update_idletasks()
                    packet = BytesIO()
                    canvas = Canvas(packet, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

                    if ALIGN == 'RIGHT':
                        canvas.drawRightString(POS_X, POS_Y, STR)
                    else:
                        canvas.drawLeftString(POS_X, POS_Y, STR)

                    canvas.save()
                    packet.seek(0)

                    new_page = copy(existing_pdf.pages[0])
                    new_page.merge_page(PdfReader(packet).pages[0])
                    output.add_page(new_page)

                    for i in range(NUM_PAGES-1):
                        output.add_page(existing_pdf.pages[i+1])
            with open(OUTPUT_FILE, 'wb') as f:
                output.write(f)

            ###############
            ###############

            messagebox.showinfo("Obrada završena!",
                                f"Uspješno je generirana datoteka <<{OUTPUT_FILE}>>")
            root.destroy()

        gen_button = tk.Button(text='Generiraj', command=generiraj)

        status = tk.Label(root,
                          textvar=stringvar2)

        status.pack(side=tk.LEFT, padx=10, pady=10)
        gen_button.pack(side=tk.RIGHT, padx=10, pady=10)

        root.mainloop()

    except Exception as e:
        root.destroy()
        root = tk.Tk()
        root.withdraw()
        with open('error_log.txt', 'w') as f:
            f.write(f'{e}\n'+''.join(traceback.format_tb(e.__traceback__)))
        messagebox.showerror(
            'Kritična greška!', f'Error: {e}')
        root.destroy()
        raise e


if __name__ == "__main__":
    main()
