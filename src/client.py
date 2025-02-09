import discord
from discord import app_commands
from log import log_assign, log_join, log_warning, log_info, log_remove
from database import Database
import re

INVALID_STRING = -1
UNKNOWN_ROLE = -2


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Database("data.json")
        self.tree = app_commands.CommandTree(self)

    def verify_role(self, itx: discord.Interaction, role: str) -> int:
        id = self.str_to_id(role)
        if id is None:
            return INVALID_STRING
        if not self.role_exists(itx, id):
            return UNKNOWN_ROLE
        return id

    def str_to_id(self, role: str) -> int | None:
        m = re.search("(?<=<@&)\\d+(?=>)", role)
        if m is not None:
            return int(m.group(0))
        else:
            return None

    def id_to_role(self, id: int) -> str:
        return f"<@&{id}>"

    def get_role_ids(self, roles: list[discord.Role]):
        # res = []
        # for role in roles:
        #     res.append(role.id)
        # return res
        return [role.id for role in roles]

    def role_exists(self, itx: discord.Interaction, id: int) -> bool:
        return id in self.get_role_ids(itx.guild.roles)

    async def handle_role_errors(self, itx: discord.Interaction, id: int, role: str):
        if id == INVALID_STRING:
            await itx.response.send_message(role + " is not a valid role!")
            raise Exception("Purposeful early exception")
        elif id == UNKNOWN_ROLE:
            await itx.response.send_message(role + " is not a role in this server!")
            raise Exception("Purposeful early exception")

    async def on_ready(self):
        try:
            synced = await self.tree.sync()
            log_info(f"Synced {len(synced)} commands globally.")
        except Exception as e:
            log_warning(f"Failed syncing: {e}")

    async def on_resume(self):
        try:
            synced = await self.tree.sync()
            log_info(f"Synced {len(synced)} commands globally.")
        except Exception as e:
            log_warning(f"Failed syncing: {e}")

    async def on_member_join(self, member: discord.Member):
        log_join(member.guild.name, member.name)

        data = self.db.get()

        # If member joined guild with activated system, look up that DataObject
        guild = None
        for x in data:
            if x.server_id == member.guild.id:
                guild = x
                break
        if guild is None:
            log_warning(
                f"{member.name} in {member.guild.name} is not in activated server."
            )
            return

        # Verify that member has no role
        if not len(member.roles) <= 1:
            log_warning(
                f"{member.name} in {member.guild.name} already has roles assigned to them."
            )
            return

        # Add role
        role = member.guild.get_role(guild.role_id)
        if role is None:
            log_warning(
                f"{guild.role_id} in {member.guild.id} ({member.guild.name}) failed to get_role()."
            )

        await member.add_roles(role, reason="Automatically assigned by Role Bot")
        log_assign(member.guild.name, member.name, role)

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles == after.roles:
            log_info("No roles changed")
            return
        
        for d in self.db.data:
            print(type(d), d.server_id)
            if d.server_id == after.guild.id:
                data = d

        if data.role_id in self.get_role_ids(after.roles):
            role = after.guild.get_role(data.roleless_id)
            await after.remove_roles(role, reason="Automatically unassigned by Role Bot")
        
        log_remove(after.guild.name, after.name, data.roleless_id)
