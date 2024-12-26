

Furniture Control Model
This folder contains the finetuned model specifically for furniture control.

Pretrained Model: llama3.1:8b

Dataset Path: Main_LLM_model\dataset\dataset.json

Quantization Method: q4_k_m

Finetune Colab: [Link to Finetune the Model](https://tinyurl.com/bdzxhy5n)

Model Type: gguf

Instructions
Download Ollama: Ensure you have Ollama installed.

Modify Modelfile.txt: Adjust the parameters and settings as needed.

Create the Model: Run the following command in the Ollama terminal:

bash
ollama create furniture_llama3.1 -f Main_LLM_model\model\Modelfile
