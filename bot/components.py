from discord import Interaction, ButtonStyle, TextStyle, ui
from utils import Resource


class AddResourceModal(ui.Modal, title='Add a Resource'):
    def __init__(self, topic_name: str, author_id: int, status: str):
        super().__init__()
        self.topic_name = topic_name
        self.author_id = author_id
        self.status = status
        
    url = ui.TextInput(label='URL', placeholder='Enter the URL of the resource', required=True, style=TextStyle.paragraph)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer()
        await Resource.addResource(self.topic_name, self.author_id, self.status, self.url.value)
        success_message = f"Successfully added a new resource to the topic: {self.topic_name}"
        await interaction.followup.send(success_message, ephemeral=True)

class AddResourceView(ui.View):
    def __init__(self, topic_name: str, author_id: int, status: str):
        super().__init__(timeout=None)
        self.topic_name = topic_name
        self.author_id = author_id
        self.status = status

    @ui.button(label='Add Resource', style=ButtonStyle.primary)
    async def add_resource(self, interaction: Interaction, button: ui.Button):
        # Send a modal with a form to add a new resource
        await interaction.response.send_modal(AddResourceModal(self.topic_name, self.author_id, self.status))