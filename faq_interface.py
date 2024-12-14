import gradio as gr

class FAQInterface:
    def __init__(self):
        self.html_content = self._generate_faq_html()

    def _generate_faq_html(self) -> str:
        # Concatenating all FAQ items into one HTML string
        html_content = '''
        <ul>
            <li><a href="https://yourdomain.com/faq1" target="_blank">When was FSG founded?</a></li>
            <li><a href="https://yourdomain.com/faq2" target="_blank">How can I order Fulham products?</a></li>
        </ul>
        '''
        return html_content

def setup_interface():
    faq_interface = FAQInterface()

    # Create the Gradio interface
    with gr.Blocks() as demo:
        gr.Markdown("### Frequently Asked Questions")
        # Use gr.HTML to display HTML content correctly
        gr.HTML(value=faq_interface.html_content)

    return demo

# Launch the Gradio interface
if __name__ == "__main__":
    demo = setup_interface()
    demo.launch()

