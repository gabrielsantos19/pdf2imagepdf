#!/usr/bin/python3
# Author: Gabriel Santos
# Date: 2025-02-21
import pathlib
import shutil
import os
import io
import sys
import pdf2image
import pypdf
from pdf2image.exceptions import PDFInfoNotInstalledError


SCRIPT_PATH = pathlib.Path(__file__).resolve(strict=True)
SCRIPT_DIR = SCRIPT_PATH.parent
TMP_DIR = SCRIPT_DIR / '_temporario'
SAIDA_DIR = SCRIPT_DIR / 'saida'


def get_poppler_path_on_windows():
    paths = sorted(SCRIPT_DIR.glob('**/poppler-*/Library/bin'))
    if len(paths) != 0:
        return paths[0]
    return None


def get_poppler_path():
    if os.name == 'nt':
        return get_poppler_path_on_windows()
    return None


def convert_pdf_pages_to_new_pdf_bytes(pdf_pages):
    writer = pypdf.PdfWriter()
    for page in pdf_pages:
        writer.add_page(page)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes


def convert_pdf_bytes_to_image_list(pdf_bytes, page_number_offset, poppler_path):
    pdfs_filepaths = []
    images = pdf2image.convert_from_bytes(
        pdf_bytes.getvalue(),
        dpi=110,
        poppler_path=poppler_path)
    for i, image in enumerate(images):
        path = TMP_DIR / f'page_{page_number_offset+i+1}.pdf'
        pdfs_filepaths.append(path)
        image.save(path, "PDF")
        image.close()
    return pdfs_filepaths


def convert_each_pdffile_page_to_pdf_image(filename):
    reader = pypdf.PdfReader(filename)
    number_of_pages = len(reader.pages)
    poppler_path=get_poppler_path()
    pdfs_filepaths = []
    batch_size = 10
    for i in range(0, number_of_pages, batch_size):
        print(f'\rConvertendo página {i} de {number_of_pages}', end='')
        pdf_bytes = convert_pdf_pages_to_new_pdf_bytes(reader.pages[i:i+batch_size])
        new_pdfs_filepaths = convert_pdf_bytes_to_image_list(pdf_bytes, i, poppler_path)
        pdfs_filepaths.extend(new_pdfs_filepaths)
    print('')
    return pdfs_filepaths


def merge_pdfs(input_filenames, output_filename):
    merger = pypdf.PdfWriter()
    for pdf in input_filenames:
        merger.append(pdf)
    merger.write(output_filename)
    merger.close()


def setup_folders():
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)


def delete_tmp_folder():
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)


def print_script_wellcome_message():
    print('=========================================================================')
    print('===                            PDF2PDFIMAGE                           ===')
    print('===                                                                   ===')
    print('===   - Desenvolvido por: Gabriel Santos                              ===')
    print('===   - Créditos: Python, pdf2image, pypdf, ...                       ===')
    print('=========================================================================')


def prompt_for_filename():
    filename = input()
    if not pathlib.Path(filename).exists():
        raise FileNotFoundError()
    return filename


def main():
    try:
        print_script_wellcome_message()
        print('\n=> Insira o nome completo do arquivo a ser convertido:')
        input_filename = prompt_for_filename()
        print('\n=> Iniciando programa')
        setup_folders()
        print('\n=> Pré-processando arquivo')
        pdfs = convert_each_pdffile_page_to_pdf_image(input_filename)
        print('\n=> Escrevendo arquivo final')
        merge_pdfs(pdfs, SAIDA_DIR / 'resultado.pdf')
    except FileNotFoundError:
        print('O arquivo inserido não foi encontrado')
    except PDFInfoNotInstalledError:
        print('\n[ERRO] Poppler nao encontrado')
    finally:
        print('\n=> Encerrando programa')
        delete_tmp_folder()


if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    main()
