import gradio as gr
from llm_rs import AutoModel,SessionConfig,GenerationConfig,Precision

repo_name = "rustformers/mpt-7b-ggml"
file_name = "mpt-7b-instruct-q5_1-ggjt.bin"

examples = [
    "Write a travel blog about a 3-day trip to Thailand.",
    "Tell me a short story about a robot that has a nice day.",
    "Compose a tweet to congratulate rustformers on the launch of their HuggingFace Space.",
    "Explain how a candle works to a 6-year-old in a few sentences.",
    "What are some of the most common misconceptions about birds?",
    "Explain why the Rust programming language is so popular.",
]

session_config = SessionConfig(threads=2,batch_size=2)
model = AutoModel.from_pretrained(repo_name, model_file=file_name, session_config=session_config,verbose=True)

def process_stream(instruction, temperature, top_p, top_k, max_new_tokens, seed):

    prompt=f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
{instruction}
### Response:
Answer:"""
    generation_config = GenerationConfig(seed=seed,temperature=temperature,top_p=top_p,top_k=top_k,max_new_tokens=max_new_tokens)
    response = ""
    streamer = model.stream(prompt=prompt,generation_config=generation_config)
    for new_text in streamer:
        response += new_text
        yield response


with gr.Blocks(
    theme=gr.themes.Soft(),
    css=".disclaimer {font-variant-caps: all-small-caps;}",
) as demo:
    gr.Markdown(
        """<h1><center>MPT-7B-Instruct on CPU in Rust 🦀</center></h1>

        This demo uses the [rustformers/llm](https://github.com/rustformers/llm) library via [llm-rs](https://github.com/LLukas22/llm-rs-python) to execute [MPT-7B-Instruct](https://huggingface.co/mosaicml/mpt-7b-instruct) on 2 CPU cores.
        """
    )
    with gr.Row():
        with gr.Column():
            with gr.Row():
                instruction = gr.Textbox(
                    placeholder="Enter your question or instruction here",
                    label="Question/Instruction",
                    elem_id="q-input",
                )
            with gr.Accordion("Advanced Options:", open=False):
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            temperature = gr.Slider(
                                label="Temperature",
                                value=0.8,
                                minimum=0.1,
                                maximum=1.0,
                                step=0.1,
                                interactive=True,
                                info="Higher values produce more diverse outputs",
                            )
                    with gr.Column():
                        with gr.Row():
                            top_p = gr.Slider(
                                label="Top-p (nucleus sampling)",
                                value=0.95,
                                minimum=0.0,
                                maximum=1.0,
                                step=0.01,
                                interactive=True,
                                info=(
                                    "Sample from the smallest possible set of tokens whose cumulative probability "
                                    "exceeds top_p. Set to 1 to disable and sample from all tokens."
                                ),
                            )
                    with gr.Column():
                        with gr.Row():
                            top_k = gr.Slider(
                                label="Top-k",
                                value=40,
                                minimum=5,
                                maximum=80,
                                step=1,
                                interactive=True,
                                info="Sample from a shortlist of top-k tokens — 0 to disable and sample from all tokens.",
                            )
                    with gr.Column():
                        with gr.Row():
                            max_new_tokens = gr.Slider(
                                label="Maximum new tokens",
                                value=256,
                                minimum=0,
                                maximum=1024,
                                step=5,
                                interactive=True,
                                info="The maximum number of new tokens to generate",
                            )

                    with gr.Column():
                        with gr.Row():
                            seed = gr.Number(
                                label="Seed",
                                value=42,
                                interactive=True,
                                info="The seed to use for the generation",
                                precision=0
                            )
    with gr.Row():
        submit = gr.Button("Submit")
    with gr.Row():
        with gr.Box():
            gr.Markdown("**MPT-7B-Instruct**")
            output_7b = gr.Markdown()

    with gr.Row():
        gr.Examples(
            examples=examples,
            inputs=[instruction],
            cache_examples=False,
            fn=process_stream,
            outputs=output_7b,
        )
    with gr.Row():
        gr.Markdown(
            "Disclaimer: MPT-7B can produce factually incorrect output, and should not be relied on to produce "
            "factually accurate information. MPT-7B was trained on various public datasets; while great efforts "
            "have been taken to clean the pretraining data, it is possible that this model could generate lewd, "
            "biased, or otherwise offensive outputs.",
            elem_classes=["disclaimer"],
        )
    with gr.Row():
        gr.Markdown(
            "[Privacy policy](https://gist.github.com/samhavens/c29c68cdcd420a9aa0202d0839876dac)",
            elem_classes=["disclaimer"],
        )

    submit.click(
        process_stream,
        inputs=[instruction, temperature, top_p, top_k, max_new_tokens,seed],
        outputs=output_7b,
    )
    instruction.submit(
        process_stream,
        inputs=[instruction, temperature, top_p, top_k, max_new_tokens,seed],
        outputs=output_7b,
    )

demo.queue(max_size=4, concurrency_count=1).launch(debug=True)
