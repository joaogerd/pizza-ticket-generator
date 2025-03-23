import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QFormLayout,
    QFileDialog, QMessageBox, QHBoxLayout
)
from fpdf import FPDF
import sys
import os
# Desabilita o cache de fontes
import fpdf
fpdf.set_global("FPDF_CACHE_MODE", 1) # Isso desabilita todos os caches de fontes


def find_data_file(filename):
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)

class CustomPDF(FPDF):
    """CustomPDF estende a classe FPDF para adicionar métodos utilitários de inserção de texto."""
    
    def insert_text(self, x, y, text):
        """
        Insere um texto no PDF em uma coordenada específica, ajustando a posição para levar em conta a largura do texto e a altura da fonte.

        Args:
            x (float): Coordenada x para posicionamento do texto.
            y (float): Coordenada y para posicionamento do texto.
            text (str): Texto a ser inserido.
        """
        text_width = self.get_string_width(text)
        font_height = self.font_size  # Altura da fonte definida pelo tamanho da fonte
        xpos = x - text_width
        ypos = y - font_height
        self.set_xy(xpos, ypos)
        self.cell(text_width, font_height, text)

    def add_font(self, family, style='', fname='', uni=False):
        """
        Sobrescreve o método add_font para não gerar o arquivo de cache .pkl.
        A fonte será carregada diretamente sem a necessidade de cache.
        """
        # Adiciona a fonte diretamente sem cache
        super().add_font(family, style, fname, uni)
def create_ticket_pdf(
    ticket_width,
    ticket_height,
    margin_x,
    margin_y,
    spacing_x,
    spacing_y,
    max_tickets,
    image_path=find_data_file('data/pizza.png'),
    output_filename='vale_pizza_escoteiro.pdf',
    page_format='A4',
    orientation='L',
    internal_margin_x=None,
    internal_margin_y=None,
    font_family="Arial",
    ticket_number_font=find_data_file('data/Helvetica-Bold.ttf'),
    ticket_date="12/04/2025",
    ticket_value="R$ 25,00"
):
    """
    Gera um arquivo PDF contendo uma grade de tickets, onde cada ticket exibe uma imagem de fundo, número do ticket, valor e textos adicionais.

    Args:
        ticket_width (float): Largura de cada ticket (mm).
        ticket_height (float): Altura de cada ticket (mm).
        margin_x (float): Margem horizontal da página (mm).
        margin_y (float): Margem vertical da página (mm).
        spacing_x (float): Espaçamento horizontal entre tickets (mm).
        spacing_y (float): Espaçamento vertical entre tickets (mm).
        max_tickets (int): Número total de tickets a serem gerados.
        image_path (str, optional): Caminho para a imagem de fundo do ticket. Defaults to 'pizza.png'.
        output_filename (str, optional): Nome do arquivo PDF de saída. Defaults to 'vale_pizza_escoteiro.pdf'.
        page_format (str, optional): Formato da página. Defaults to 'A4'.
        orientation (str, optional): Orientação da página ('P' para retrato ou 'L' para paisagem). Defaults to 'L'.
        internal_margin_x (float, optional): Margem interna para posicionamento do texto (mm). Defaults to 5.
        internal_margin_y (float, optional): Margem interna vertical para posicionamento do texto (mm). Defaults to 5.
        font_family (str, optional): Fonte utilizada para os textos (exceto número do ticket). Defaults to "Arial".
        ticket_number_font (str, optional): Fonte customizada para o número do ticket. Defaults to "HelveticaBold".
        ticket_date (str, optional): Texto que indica o dia da pizza. Defaults to "Dia 12/04/2025".
        ticket_value (str, optional): Texto que indica o valor do ticket. Defaults to "R$ 25,00".

    Returns:
        str: O caminho do arquivo PDF gerado.
    """
    if internal_margin_x == None or internal_margin_y == None:
        internal_margin_x = ticket_width*0.037
        internal_margin_y = ticket_height*0.10

    # Define as dimensões da página para A4 em paisagem
    if page_format.upper() == 'A4' and orientation.upper() == 'L':
        page_width = 297
        page_height = 210
    else:
        temp_pdf = FPDF(orientation, 'mm', page_format)
        page_width, page_height = temp_pdf.w, temp_pdf.h

    # Calcula o número de colunas e linhas que cabem na página
    columns = (page_width - 2 * margin_x + spacing_x) // (ticket_width + spacing_x)
    rows = (page_height - 2 * margin_y + spacing_y) // (ticket_height + spacing_y)
    tickets_per_page = int(columns * rows)
    
    # Calcula o número de páginas necessárias (arredondamento para cima)
    pages = math.ceil(max_tickets / tickets_per_page)
    
    print(f"Total tickets: {max_tickets}, Columns: {int(columns)}, Rows: {int(rows)}, Pages: {pages}")

    pdf = CustomPDF(orientation=orientation, unit='mm', format=page_format)
    pdf.set_auto_page_break(auto=True, margin=10)
    
    # Adiciona a fonte customizada para o número do ticket.
    # Certifique-se de que 'Helvetica-Bold.ttf' esteja no mesmo diretório.
    pdf.add_font('ticket_number_font', '', ticket_number_font, uni=True)

    ticket_number = 1
    for _ in range(pages):
        pdf.add_page()
        for row in range(int(rows)):
            for col in range(int(columns)):
                if ticket_number > max_tickets:
                    break

                # Calcula a posição do ticket
                x = margin_x + col * (ticket_width + spacing_x)
                y = margin_y + row * (ticket_height + spacing_y)

                # Desenha o retângulo do ticket
                pdf.rect(x, y, ticket_width, ticket_height, style='D')

                # Insere a imagem de fundo
                pdf.image(image_path, x=x, y=y, w=ticket_width, h=ticket_height)

                # Insere o número do ticket (usando a fonte customizada, em vermelho)
                pdf.set_font('ticket_number_font', size=12)
                pdf.set_text_color(255, 0, 0)
                ticket_str = f"{ticket_number:03d}"
                # Primeira posição: centralizada horizontalmente na base do ticket
                xpos = x + ticket_width / 2 - internal_margin_x
                ypos = y + ticket_height - internal_margin_y
                pdf.insert_text(xpos, ypos, ticket_str)
                # Segunda posição: alinhada à direita na mesma linha
                xpos = x + ticket_width - internal_margin_x
                ypos = y + ticket_height - internal_margin_y
                pdf.insert_text(xpos, ypos, ticket_str)

                # Insere o valor do ticket (em verde)
                pdf.set_font(font_family, style='B', size=12)
                font_height = pdf.font_size
                pdf.set_text_color(0, 127, 103)
                xpos = x + ticket_width - internal_margin_x
                ypos = y + ticket_height / 2
                pdf.insert_text(xpos, ypos, ticket_value)
                value_y_position = ypos + font_height / 1.5

                # Insere os textos adicionais (em preto)
                pdf.set_font(font_family, size=6.5)
                font_height = pdf.font_size
                pdf.set_text_color(0, 0, 0)
                additional_texts = [
                    f"Dia {ticket_date}",                  # Data customizada da pizza
                    "Retirar a partir das 16h",
                    " ",
                    "R. José Norberto, 169",
                    "Vila Ana Rosa - Cruzeiro/SP"
                ]
                for i, line in enumerate(additional_texts):
                    xpos = x + ticket_width - internal_margin_x
                    ypos = value_y_position + i * (font_height + font_height * 0.25)
                    pdf.insert_text(xpos, ypos, line)

                ticket_number += 1

    pdf.output(output_filename)
    return output_filename


class TicketApp(QWidget):
    """
    Interface gráfica utilizando PyQt5 para geração de tickets em PDF.
    Permite ao usuário inserir os parâmetros necessários e selecionar os arquivos de imagem e saída.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tickets Pizza - Grupo Escoteiro")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        # Campos de entrada com valores padrão
#        self.ticket_width_edit = QLineEdit("135")
#        self.ticket_height_edit = QLineEdit("50")
#        self.margin_x_edit = QLineEdit("12")
#        self.margin_y_edit = QLineEdit("20")
#        self.spacing_x_edit = QLineEdit("3")
#        self.spacing_y_edit = QLineEdit("3")
        self.max_tickets_edit = QLineEdit("100")
        self.ticket_date_edit = QLineEdit("12/04/2025")
        self.ticket_value_edit = QLineEdit("R$ 25,00")

#        self.image_path_edit = QLineEdit("")
        self.output_filename_edit = QLineEdit("vale_pizza_escoteiro.pdf")

#        layout.addRow("Largura do Ticket (mm):", self.ticket_width_edit)
#        layout.addRow("Altura do Ticket (mm):", self.ticket_height_edit)
#        layout.addRow("Margem Horizontal (mm):", self.margin_x_edit)
#        layout.addRow("Margem Vertical (mm):", self.margin_y_edit)
#        layout.addRow("Espaçamento Horizontal (mm):", self.spacing_x_edit)
#        layout.addRow("Espaçamento Vertical (mm):", self.spacing_y_edit)
        layout.addRow("Número de Tickets:", self.max_tickets_edit)
        layout.addRow("Data da Pizza:", self.ticket_date_edit)
        layout.addRow("Valor da Pizza:", self.ticket_value_edit)

#        # Layout horizontal para seleção do caminho da imagem
#        image_layout = QHBoxLayout()
#        image_layout.addWidget(self.image_path_edit)
#        self.image_browse_btn = QPushButton("Selecionar...")
#        self.image_browse_btn.clicked.connect(self.browse_image)
#        image_layout.addWidget(self.image_browse_btn)
#        layout.addRow("Imagem de Fundo:", image_layout)

        # Layout horizontal para seleção do arquivo de saída
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_filename_edit)
        self.output_browse_btn = QPushButton("Selecionar...")
        self.output_browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_browse_btn)
        layout.addRow("Nome do Arquivo de Saída:", output_layout)

        # Botão para gerar o PDF
        self.generate_btn = QPushButton("Gerar PDF")
        self.generate_btn.clicked.connect(self.generate_pdf)
        layout.addRow(self.generate_btn)

        self.setLayout(layout)

    def browse_image(self):
        """Abre um diálogo para seleção da imagem de fundo."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Selecione a Imagem de Fundo", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if filename:
            self.image_path_edit.setText(filename)

    def browse_output(self):
        """Abre um diálogo para seleção do nome e local do arquivo PDF de saída."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF Como", "", 
            "PDF Files (*.pdf);;All Files (*)"
        )
        if filename:
            self.output_filename_edit.setText(filename)

    def generate_pdf(self):
        """Coleta os dados do formulário, gera o PDF e exibe uma mensagem informando o resultado."""
        try:
#            ticket_width = float(self.ticket_width_edit.text())
#            ticket_height = float(self.ticket_height_edit.text())
#            margin_x = float(self.margin_x_edit.text())
#            margin_y = float(self.margin_y_edit.text())
#            spacing_x = float(self.spacing_x_edit.text())
#            spacing_y = float(self.spacing_y_edit.text())
            ticket_width = 135
            ticket_height = 50
            margin_x = 12
            margin_y = 20
            spacing_x = 3
            spacing_y = 3

            max_tickets = int(self.max_tickets_edit.text())
            ticket_date = self.ticket_date_edit.text()
            ticket_value = self.ticket_value_edit.text()
            
#            # Verifica se o caminho da imagem está vazio
#            image_path = self.image_path_edit.text()
#            if not image_path:  # Se estiver vazio, passa valor padrao
#                image_path = find_data_file('data/pizza.png')
            image_path = find_data_file('data/pizza.png')

            output_filename = self.output_filename_edit.text()

            generated_file = create_ticket_pdf(
                ticket_width,
                ticket_height,
                margin_x,
                margin_y,
                spacing_x,
                spacing_y,
                max_tickets,
                image_path=image_path,
                output_filename=output_filename,
                ticket_date=ticket_date,
                ticket_value=ticket_value
            )

            QMessageBox.information(
                self, "Sucesso", f"PDF gerado com sucesso!\nArquivo: {generated_file}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicketApp()
    window.show()
    sys.exit(app.exec_())

