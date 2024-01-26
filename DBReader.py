import sqlite3
# Initialize SQLite database connection
db = sqlite3.connect("KoboReader.sqlite")


getBookListQuery = (
    "SELECT DISTINCT content.ContentId, content.Title, content.Attribution AS Author, " +
    "content.DateLastRead, content.TimeSpentReading " +
    "FROM Bookmark " +
    "INNER JOIN content ON Bookmark.VolumeID = content.ContentID " +
    "ORDER BY content.Title"
)

getHighlightsQuery = (
    "SELECT Bookmark.Text FROM Bookmark " +
    "INNER JOIN content ON Bookmark.VolumeID = content.ContentID " +
    "WHERE content.ContentID = ? "
)


class Book:
    def __init__(self, id, title, author, date_last_read, time_spent_reading):
        self.id = id
        self.title = title
        self.author = author
        self.date_last_read = date_last_read
        self.time_spent_reading = time_spent_reading

    def get_id(self):
        return self.id

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_date_last_read(self):
        return self.date_last_read

    def get_time_spent_reading(self):
        return self.time_spent_reading


def getBookInfoFromDB() :
    try:
        bookList = []
        cursor = db.execute(getBookListQuery)
        for row in cursor.fetchall():
            id, title, author, date_last_read, time_spent_reading = row
            book = Book(id, title, author, date_last_read, time_spent_reading)
            bookList.append(book)
    except Exception as e:
        print(f"Error getBookInfoFromDB : {e}")
    return bookList

def getHLFromDB(content_id) :
    highlights_list = []
    cursor = db.execute(getHighlightsQuery, (content_id,))
    for row in cursor.fetchall():
        # print(row[0])
        highlights_list.append(row[0])
    # print(len(highlights_list))
    # print("============================================")
    return highlights_list
    