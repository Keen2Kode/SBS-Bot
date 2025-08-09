import os
import discord
from discord.ext import commands
from google.oauth2.service_account import Credentials
import gspread

class SheetContext:
    """
    Encapsulates Google Sheets to an object accessible to jam commands
    """
    HEADER_ROW = 4
    COL_ID = "Song ID"
    COL_TITLE = "Song Title"
    COL_VOTE_RANK = "Vote Rank"
    COL_STATUS = "Status"

    def __init__(self, url):
        creds = Credentials.from_service_account_file(
        filename="gcloud-service-account-credentials.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        gc = gspread.authorize(creds)
        self.url = "https://docs.google.com/spreadsheets/d/1B8CsbHZFHbz49ceJteTEL4s1_xq1G9WrqjtV0cBO8aw/edit?usp=sharing"
        self.sheet = gc.open_by_url(self.url)

    def set_worksheet(self, sheet_name: str):
        # build header map for flexible column lookup
        sheet_name = sheet_name.capitalize()
        self.worksheet = self.sheet.worksheet(sheet_name)
        headers = self.worksheet.row_values(SheetContext.HEADER_ROW)
        self.header_map = {name: idx+1 for idx, name in enumerate(headers) if name}

    def get_header_map(self) -> dict:
        """Return the header-to-column-index map (1-based)."""
        return self.header_map

    def get_existing_ids(self) -> list:
        """Return all existing IDs from COL_ID column."""
        last_row = self.worksheet.get_last_row()
        id_col = self.header_map.get(SheetContext.COL_ID)
        if not id_col or last_row <= SheetContext.HEADER_ROW:
            return []
        num_rows = last_row - SheetContext.HEADER_ROW
        id_range = self.worksheet.get_values(
            f"{id_col}{SheetContext.HEADER_ROW+1}:{id_col}{last_row}"
        )
        # Flatten and return
        return [row[0] for row in id_range if row]

    def get_all_records(self) -> list:
        """Return all rows as list of dicts, using headers from HEADER_ROW."""
        # Use gspread's head parameter to specify HEADER_ROW as header
        return self.worksheet.get_all_records(head=SheetContext.HEADER_ROW)