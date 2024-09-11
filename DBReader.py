import sqlite3
# Initialize SQLite database connection
db = sqlite3.connect("KoboReader.sqlite")


getBookListQuery = (
    "SELECT DISTINCT content.ContentId, content.Title, content.Subtitle, content.Attribution AS Author, " +
    "content.DateLastRead, content.TimeSpentReading, content.Description, " +
    "content.Publisher, content.___PercentRead, content.LastTimeFinishedReading, " +
    "content.ISBN " +
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
    def __init__(self, id, title, subtitle, author, date_last_read, time_spent_reading, description, publisher, percent_read, last_time_finished_reading, isbn):
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.date_last_read = date_last_read
        self.time_spent_reading = time_spent_reading
        self.description = description
        self.publisher = publisher
        self.percent_read = percent_read
        self.last_time_finished_reading = last_time_finished_reading
        self.isbn = isbn

    def get_id(self):
        return self.id

    def get_title(self):
        return self.title

    def get_subtitle(self):
        return self.subtitle

    def get_author(self):
        return self.author

    def get_date_last_read(self):
        return self.date_last_read

    def get_time_spent_reading(self):
        return self.time_spent_reading

    def get_description(self):
        return self.description

    def get_publisher(self):
        return self.publisher

    def get_percent_read(self):
        return self.percent_read

    def get_last_time_finished_reading(self):
        return self.last_time_finished_reading

    def get_isbn(self):
        return self.isbn



def getBookInfoFromDB():
    try:
        bookList = []
        cursor = db.execute(getBookListQuery)
        
        for row in cursor.fetchall():
            # 解包查詢結果中的所有欄位
            id, title, subtitle, author, date_last_read, time_spent_reading, description, publisher, percent_read, last_time_finished_reading, isbn = row
            
            # 創建 Book 物件，傳入所有所需參數
            book = Book(
                id=id,
                title=title,
                subtitle=subtitle,
                author=author,
                date_last_read=date_last_read,
                time_spent_reading=time_spent_reading,
                description=description,
                publisher=publisher,
                percent_read=percent_read,
                last_time_finished_reading=last_time_finished_reading,
                isbn=isbn
            )
            
            # 將 Book 物件加入列表
            bookList.append(book)
    
    except Exception as e:
        print(f"Error getBookInfoFromDB: {e}")
    
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
    