from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import ST7735
from gui import main
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage
import numpy as np

disp = ST7735.ST7735(port=0, cs=0, dc=24, backlight=None, rst=25, width=128, height=160, rotation=0, invert=False)

WIDTH = disp.width
HEIGHT = disp.height

# img = Image.new('RGB', (WIDTH, HEIGHT))
# draw = ImageDraw.Draw(img)

# # Load default font.
# font = ImageFont.load_default()

# # Write some text
# draw.text((5, 5), "Hello World!", font=font, fill=(255, 255, 255))

# # Write buffer to display hardware, must be called to make things visible on the
# # display!
# disp.display(img)

# Function to render the PyQt window to the ST7735 display
def display_pyqt_on_st7735():
    app = QApplication([])
    from gui import MainWindow
    window = MainWindow()
    window.resize(WIDTH, HEIGHT)
    window.show()
    # Process events to ensure the window is rendered
    app.processEvents()
    # Render window to QImage
    qimage = QImage(window.size(), QImage.Format_RGB888)
    window.render(qimage)
    # Convert QImage to numpy array
    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    arr = np.array(ptr).reshape(qimage.height(), qimage.width(), 3)
    # Convert numpy array to PIL Image
    pil_img = Image.fromarray(arr, 'RGB')
    disp.display(pil_img)
    window.close()
    app.quit()

if __name__ == "__main__":
    display_pyqt_on_st7735()