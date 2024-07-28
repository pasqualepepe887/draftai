#DraftAI by Pasquale Pepe pasqualepepe887@gmail.com
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import google.generativeai as genai
import logging
import re

global idee_1, idee_2, idee_3,sample_file , url_1, url_2, url_3

def extract_materials_and_instructions(text):
    parts = text.split('%')

    if len(parts) > 2:
        materials = parts[1].strip()
        instructions = parts[2].strip()
    else:
        materials = ""
        instructions = ""

    instructions_list = instructions.split('.')
    formatted_instructions = ''
    for item in instructions_list:
        if item.strip():
            formatted_instructions += f'<h1 class="instruction_class">{item.strip()}</h1>\n'
    
    return materials, formatted_instructions.strip()


def extract_ideas_and_descriptions(text):
   
    parts = text.split(') ')
    ideas = []

    for part in parts[1:]:

        if ' % ' in part:
            title_description = part.split(' % ')
            if len(title_description) == 2:
                title = title_description[0].strip()
                description = title_description[1].strip()
                ideas.append([title, description])
    
    while len(ideas) < 3:
        ideas.append(["", ""])
    
    return ideas[0], ideas[1], ideas[2]

# Configure the API key and model
genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-1.5-flash')
prompt="Answer in English and without adding bold or *. Looking at this image, give me 3 ideas that allow me to reuse it to build DIY projects in an eco-friendly way. Give me only the titles of the ideas without explaining the process and numbers. Then add a subtitle in which you give me a short title in English for a DIY tutorial. Format the result following this scheme: ideanumber) idea title % English title,"


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG) 
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['POST','GET'])
def index():
    app.logger.info("INDEX")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global idee_1, idee_2, idee_3 ,sample_file, url_1, url_2, url_3 
    if 'file' not in request.files:
        app.logger.info("NO FILE")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
      
        sample_file = genai.upload_file(file_path)
     
        response = model.generate_content([prompt, sample_file])
        response_text = response.text  
        idee_1, idee_2, idee_3 = extract_ideas_and_descriptions(response_text)
    
    # Costruisci l'URL dell'immagine
        url_1 = f'https://image.pollinations.ai/prompt/{idee_1[1].replace(" ", "")}'
        url_2 = f'https://image.pollinations.ai/prompt/{idee_2[1].replace(" ", "")}'
        url_3 = f'https://image.pollinations.ai/prompt/{idee_3[1].replace(" ", "")}'

       
        return jsonify({ "idea1_T": idee_1[0],
                         "idea2_T": idee_2[0],
                         "idea3_T": idee_3[0],
                         "idea1_I": url_1,
                         "idea2_I": url_2,
                         "idea3_I": url_3, 
                         "total": response_text 
                         })

@app.route('/info',methods=['POST'])
def info():
     global idee_1, idee_2, idee_3, sample_file, url_1, url_2, url_3

     selected_idea  = request.form.get('data_idea', 'Nessun dato ricevuto')
     app.logger.info(selected_idea)

     if selected_idea== "1":
        second_prompt="Describe to me in points the instructions to build " +str(idee_1[0])+ " starting from this image as if it were a tutorial then I will go into more detail. Format the result like this %Materials: material1, material2, material3% instruction number) instruction text."  
        selected_url_image=url_1
        selected_idea_var=idee_1[0]

     elif selected_idea== "2":
        second_prompt="Describe to me in points the instructions to build " +str(idee_2[0])+ " starting from this image as if it were a tutorial then I will go into more detail. Format the result like this %Materials: material1, material2, material3% instruction number) instruction text."   
        selected_url_image=url_2
        selected_idea_var=idee_2[0]

     elif selected_idea== "3":
        second_prompt="Describe to me in points the instructions to build " +str(idee_3[0])+ " starting from this image as if it were a tutorial then I will go into more detail. Format the result like this %Materials: material1, material2, material3% instruction number) instruction text." 
        selected_url_image=url_3
        selected_idea_var=idee_3[0]

     response = model.generate_content([ second_prompt, sample_file])
     materials, instructions = extract_materials_and_instructions(response.text)
     return render_template('info_page.html',selected_url=selected_url_image,selected_idea_title=selected_idea_var,materials_idea_selected=materials,instruction_selected=instructions, )

if __name__ == '__main__':
    app.run(debug=True)
