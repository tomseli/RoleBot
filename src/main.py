import os
import discord
from discord import app_commands
from log import log_warning, log_info
from client import MyClient
from database import Data

print("Hello world!")

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
if AUTH_TOKEN is None:
    log_warning("Auth. token failed to load from environment variables")
    exit(1)
else:
    log_info("Auth. token successfully loaded.")

# TODO:
# - Organize the code
# - Make a docker image that runs this
# - Start a docker compose on the server

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    client = MyClient(intents=intents)

    @client.tree.command(
        name="register",
        description="Registers the server and a role to assign upon a member joining",
    )
    @app_commands.describe(roleless="The role to give to a roleless")
    @app_commands.describe(
        replacement="The role to that triggers removal of the roleless role"
    )
    async def register(itx: discord.Interaction, roleless: str, replacement: str):
        roleless_id = client.verify_role(itx, roleless)
        await client.handle_role_errors(itx, roleless_id, roleless)
        replacement_id = client.verify_role(itx, replacement)
        await client.handle_role_errors(itx, replacement_id, replacement)

        # check if the server is already added, if it is, remove it
        for x in client.db.get():
            if x.server_id == itx.guild.id:
                client.db.pop(x)

        # add role to database. serialize it and then respond
        client.db.add(Data(itx.guild.id, roleless_id, replacement_id))
        log_info(f"Registered {itx.guild.name} with {roleless}, which gets unassigned upon receiving {replacement}")
        await itx.response.send_message(f"Registered server with {roleless}, which gets unassigned upon receiving {replacement}")

    @client.tree.command(
        name="deregister",
        description="Deregisters the server, disables automatic role assignment",
    )
    async def deregister(itx: discord.Interaction):
        for x in client.db.get():
            if x.server_id == itx.guild.id:
                client.db.pop(x)

        log_info(f"Succesfully deregisterd {itx.guild.name}.")
        await itx.response.send_message("Succesfully deregisterd server.")

    @client.tree.command(
        name="status",
        description="Gets the status of the current server, this command _will_ ping that role!",
    )
    async def status(itx: discord.Interaction):
        data = client.db.get()

        res = None
        for x in data:
            if x.server_id == itx.guild.id:
                res = x

        if res is not None:
            await itx.response.send_message(
                f"{itx.guild.name} has the role {client.id_to_role(x.role_id)}, which is to be removed after {client.id_to_role(x.roleless_id)}, registered"
            )
        else:
            await itx.response.send_message(
                "This server is not registered, use `/register @role` to register this server"
            )

    try:
        client.run(AUTH_TOKEN)
    finally:
        log_info("Serializing database")
        client.db.serialize_data()
        log_info("Exited")
