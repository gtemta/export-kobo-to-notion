import os
import DBReader
from notion_client import Client
import logging
from datetime import datetime
import math


# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()


# Get environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)
database = notion.databases.retrieve(NOTION_DATABASE_ID)
enableLog = 1

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
logger = logging.getLogger()

# Define your custom functions getTitleWithoutSubtitle, checkBookSyncStatus, addEntryByTitle,
# getUnSyncTarget, syncBookHighlights, updateBookLRTime, updateBookSpendTime as needed


def get_title_without_subtitle(title):
    if ":" in title:
        return title.split(":")[0].strip()
    return title.strip()

def check_target(title, isExportDone=True):
    try:
        filter_property = "Exported" if isExportDone else "Exported"
        filter_value = True if isExportDone else False

        target = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={
                "and": [
                    {"property": "Title", "rich_text": {"contains": title}},
                    {"property": filter_property, "checkbox": {"equals": filter_value}},
                ],
            },
        )

        if "results" in target:
            # print(f"{'Synced' if isExportDone else 'Exported'} target:")
            is_target_valid = len(target["results"]) == 1
            return {
                "is_target_valid": is_target_valid,
                "pageId": target["results"][0]["id"],
            }
        else:
            # print("Response does not have 'results' attribute:", target)
            return {
                "is_target_valid": False,
                "pageId": None,
            }
    except Exception as e:
        # print(f"Error in {'check' if isExportDone else 'get_unsync'}_target:", str(e))
        return {
            "is_target_valid": False,
            "pageId": None,
        }


def update_book_lr_time(page_id, lastReadTime):
    notion.pages.update(
        page_id=page_id,
        properties={
            "LastReadDate": {
                "date": {
                    "start": lastReadTime,
                },
            },
        },
    )

def update_book_spend_time(page_id, bookSpendingTime):
    hours = math.floor(bookSpendingTime / 3600)
    minutes = math.floor((bookSpendingTime % 3600) / 60)
    seconds = bookSpendingTime % 60
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

    notion.pages.update(
        page_id=page_id,
        properties={
            "SpendReadingTime": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": formatted_time,
                        },
                    },
                ],
            },
        },
    )

def sync_book_highlights(page_id, highlights_list):
    # print(f"Start Sync Highlights for pageId: {page_id}")
    blocks = []

    blocks.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": "Highlights"}}],
        },
    })
    print("Append Title")
    print(len(highlights_list))

    for highlight in highlights_list:
        if highlight is not None:
            # print(highlight)
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": highlight}}],
                },
            })

        if len(blocks) > 90:
            # print(f"Over {len(blocks)} append children first")
            append_blocks_to_page(page_id, blocks)
            blocks.clear()
            # print(f"Clear Block to {len(blocks)}")

    append_blocks_to_page(page_id, blocks)

    notion.pages.update(
        page_id=page_id,
        properties={"Exported": {"checkbox": True}},
    )


def add_entry_by_title(book_title):
    try:
        # Create a new entry in the Notion database
        response = notion.pages.create(
            parent={
                "database_id": NOTION_DATABASE_ID,
            },
            properties={
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": book_title,
                            },
                        },
                    ],
                },
            },
        )
        print(f"Entry {book_title} added successfully!")
        return True
    except Exception as error:
        print("Error adding entry:", error)
        return False

def append_blocks_to_page(page_id, blocks):
    notion.blocks.children.append(
        block_id=page_id,
        children=blocks,
    )


def export_highlights():
    print("exportHighlights++")
    
    bookList = DBReader.getBookInfoFromDB()
    print(f"Books Count: {len(bookList)}")
    for book in bookList:
        print(f"Book Title: {book.get_title()}")
        print(f"Author: {book.get_author()}")
        print(f"Date Last Read: {book.get_date_last_read()}")
        print(f"Read Time Spent: {book.get_time_spent_reading()} seconds")
        print("-----------------------------------")
        try:
            title = get_title_without_subtitle(book.get_title())
            bookStatus = check_target(title, True)
            if bookStatus["is_target_valid"]:
                print("Already Exported. only update reading Time")
                update_book_lr_time(bookStatus["pageId"], book.get_date_last_read())
                update_book_spend_time(bookStatus["pageId"], book.get_time_spent_reading())
            else:
                unDoneObj = check_target(title, False)
                page_id = unDoneObj["pageId"]
                if (not unDoneObj["is_target_valid"]):
                    print(f"{title} doesn't exist. Try adding an entry for it")
                    valid = add_entry_by_title(title)
                    newObj = check_target(title, False)
                    page_id = newObj["pageId"]
                else :
                    print(f"{title} exist. Append HL after original HL")

                highlights_list = DBReader.getHLFromDB(book.get_id())

                sync_book_highlights(page_id, highlights_list)
                update_book_lr_time(page_id, book.get_date_last_read())
                update_book_spend_time(page_id, book.get_time_spent_reading())
        except Exception as error:
            print(f"Error with {book.get_title()}: {error}")


def main():
    export_highlights()

if __name__ == "__main__":
    main()