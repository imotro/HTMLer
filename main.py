import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import zipfile
import re
import base64
import os

def extract_src_href_attributes(html_content):
    script_srcs = re.findall(r'<script\s[^>]*src=["\']([^"\']*)["\']', html_content)
    link_hrefs = re.findall(r'<link\s[^>]*href=["\']([^"\']*)["\']', html_content)
    return script_srcs, link_hrefs

def modify_index_html(zip_file_path):
  try:
      with zipfile.ZipFile(zip_file_path, 'r') as zipf:
          if "index.html" in zipf.namelist():
              html_content = zipf.read("index.html").decode('utf-8')

              # Extract the link elements
              link_elements = re.findall(r'<link[^>]*>', html_content)
              for link_element in link_elements:
                  stylesheet_href_match = re.search(r'href=["\'](.+?)["\']', link_element)
                  if stylesheet_href_match:
                      stylesheet_href = stylesheet_href_match.group(1)
                      stylesheet_content = zipf.read(stylesheet_href).decode('utf-8')
                      # Create a style element with the content of the stylesheet
                      style_element = f'<style>\n{stylesheet_content}\n</style>'
                      # Replace the link element with the style element
                      html_content = html_content.replace(link_element, style_element)

              # Extract the script elements
              script_elements = re.findall(r'<script[^>]*>.*?</script>', html_content, re.DOTALL)
              for script_element in script_elements:
                  # Extract the script content from between the script tags
                  script_content_match = re.search(r'<script[^>]*>(.*?)</script>', script_element, re.DOTALL)
                  if script_content_match:
                      script_content = script_content_match.group(1)
                      # Replace the entire script element with the script content
                      html_content = html_content.replace(script_element, script_content)

              script_srcs, _ = extract_src_href_attributes(html_content)

              for script_src in script_srcs:
                  script_content = zipf.read(script_src).decode('utf-8')
                  # Create a new script element with the content of the external script
                  script_element = f'<script>\n{script_content}\n</script>'
                  # Replace the script src with the new script element
                  html_content = html_content.replace(f'<script src="{script_src}"', script_element)

              img_tags = re.findall(r'<img\s[^>]*src=["\'](.+?)["\']', html_content)
              for img_tag in img_tags:
                  image_data = zipf.read(img_tag)
                  encoded_image = base64.b64encode(image_data).decode('utf-8')
                  html_content = html_content.replace(f'<img src="{img_tag}"', f'<img src="data:image/png;base64,{encoded_image}"')

              return html_content
  except Exception as e:
      return str(e)


def update_zip_info(zip_file_path):
    zip_name = os.path.basename(zip_file_path)
    zip_size = os.path.getsize(zip_file_path) // 1024  # Size in KB

    with zipfile.ZipFile(zip_file_path, 'r') as zipf:
        images = [f for f in zipf.namelist() if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        scripts = [f for f in zipf.namelist() if f.lower().endswith('.js')]
        stylesheets = [f for f in zipf.namelist() if f.lower().endswith('.css')]

        images_size = {img: os.path.getsize(zipf.extract(img)) // 1024 for img in images}
        scripts_size = {script: os.path.getsize(zipf.extract(script)) // 1024 for script in scripts}
        stylesheets_size = {css: os.path.getsize(zipf.extract(css)) // 1024 for css in stylesheets}

    return zip_name, zip_size, len(images), len(scripts), len(stylesheets), images, scripts, stylesheets, images_size, scripts_size, stylesheets_size

def upload_zip_file():
    file_path = filedialog.askopenfilename(title="Select a ZIP file", filetypes=[("ZIP files", "*.zip")])
    if file_path:
        modified_html_content = modify_index_html(file_path)
        if modified_html_content:
            with open("modified_index.html", "w", encoding="utf-8") as output_file:
                output_file.write(modified_html_content)
            result_label.config(text="HTML file modified and saved as 'modified_index.html'")
        else:
            result_label.config(text="Error: Failed to modify the 'index.html' file in the ZIP archive.")

        zip_name, zip_size, num_images, num_scripts, num_stylesheets, images, scripts, stylesheets, images_size, scripts_size, stylesheets_size = update_zip_info(file_path)

        zip_info_tree.delete(*zip_info_tree.get_children())  # Clear the previous data
        zip_info_tree.insert('', 'end', values=("Name", zip_name))
        zip_info_tree.insert('', 'end', values=("Size (KB)", zip_size))
        zip_info_tree.insert('', 'end', values=("Number of Images", num_images))
        zip_info_tree.insert('', 'end', values=("Number of Scripts", num_scripts))
        zip_info_tree.insert('', 'end', values=("Number of Stylesheets", num_stylesheets))

        for img in images:
            zip_info_tree.insert('', 'end', values=("Image", img, f"{images_size[img]} KB"))

        for script in scripts:
            zip_info_tree.insert('', 'end', values=("Script", script, f"{scripts_size[script]} KB"))

        for css in stylesheets:
            zip_info_tree.insert('', 'end', values=("Stylesheet", css, f"{stylesheets_size[css]} KB"))
    else:
        result_label.config(text="No ZIP file selected.")

app = tk.Tk()
app.title("ZIP File Modifier")

upload_button = tk.Button(app, text="Upload ZIP File", command=upload_zip_file)
upload_button.pack(pady=20)

result_label = tk.Label(app, text="")
result_label.pack()

zip_info_tree = ttk.Treeview(app, columns=("Property", "Value", "Size"))
zip_info_tree.heading('#1', text="Property")
zip_info_tree.heading('#2', text="Value")
zip_info_tree.heading('#3', text="Size")
zip_info_tree.pack(padx=10, pady=10)

app.mainloop()
